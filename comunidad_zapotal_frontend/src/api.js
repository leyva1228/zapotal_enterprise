import axios from 'axios';

/**
 * Resuelve la URL base de la API siguiendo este orden de prioridad:
 *  1. VITE_API_URL definido en .env (build-time) -> valor fijo de la API.
 *  2. Mismo origen del frontend pero en el subdominio `api.` (produccion).
 *     Ej: si el sitio corre en https://comunidadzapotal.org,
 *     automaticamente se usa https://api.comunidadzapotal.org/api/v1.
 *  3. localhost en puerto 8000 (desarrollo local sin .env).
 *
 * Esto permite que el MISMO bundle funcione tanto en local como en
 * produccion sin cambiar el .env entre entornos.
 */
function resolverApiBaseUrl() {
  // 1) Variable de entorno (prioridad maxima)
  if (
    typeof import.meta !== 'undefined' &&
    import.meta.env &&
    import.meta.env.VITE_API_URL
  ) {
    return import.meta.env.VITE_API_URL;
  }

  // 2) Auto-deteccion por hostname (solo en el browser, no en build-time)
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const host = window.location.hostname;
    const protocol = window.location.protocol;

    // Dominios de produccion conocidos -> apuntar a api.<dominio>
    const dominiosProduccion = [
      'comunidadzapotal.org',
      'www.comunidadzapotal.org',
    ];
    for (const d of dominiosProduccion) {
      if (host === d) {
        return `${protocol}//api.${d}/api/v1`;
      }
    }
    // Custom domain en Cloudflare Pages: si el subdominio actual es
    // "www" quitar el prefijo; si tiene cualquier otro prefijo, usarlo tal cual.
    if (host.endsWith('.comunidadzapotal.org')) {
      // Si es un subdominio que NO es "www" ni "api", no aplicar logica
      // de api.* (probablemente es el admin o un alias).
    }
    if (host.endsWith('.pages.dev')) {
      // Cloudflare Pages preview deployments: no hay backend,
      // pero al menos devolvemos algo sensato.
      return `${protocol}//api.comunidadzapotal.org/api/v1`;
    }

    // 3) localhost / 127.0.0.1 -> backend en :8000
    if (host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0') {
      return 'http://localhost:8000/api/v1';
    }
  }

  // Fallback final (build-time sin window, p.ej. tests de vitest)
  return 'http://127.0.0.1:8000/api/v1';
}

const API_BASE_URL = resolverApiBaseUrl();

export { API_BASE_URL, resolverApiBaseUrl };

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

let _isRefreshing = false;
let _refreshQueue = [];

function _processQueue(error, token = null) {
  _refreshQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  _refreshQueue = [];
}

function _getToken() {
  return sessionStorage.getItem('token') || '';
}

function _getRefresh() {
  return sessionStorage.getItem('refresh') || '';
}

function _setSession(user, access, refresh) {
  // Semantica explicita (3-way):
  //   undefined -> no tocar (preservar valor actual)
  //   null      -> borrar (logout intencional)
  //   valor     -> setear
  if (user !== undefined) {
    if (user === null) {
      sessionStorage.removeItem('usuario');
    } else {
      sessionStorage.setItem('usuario', JSON.stringify(user));
    }
  }
  if (access !== undefined) {
    if (access) {
      sessionStorage.setItem('token', access);
    } else {
      sessionStorage.removeItem('token');
    }
  }
  if (refresh !== undefined) {
    if (refresh) {
      sessionStorage.setItem('refresh', refresh);
    } else {
      sessionStorage.removeItem('refresh');
    }
  }
  // Limpia keys de auth en localStorage (sesion por pestana)
  try {
    localStorage.removeItem('usuario');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
    localStorage.removeItem('accionPendiente');
  } catch (e) { /* noop */ }
}

function _clearSession() {
  _setSession(null, null, null);
}

api.interceptors.request.use((config) => {
  const token = _getToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Algunas llamadas son best-effort (ej. marcar notificacion como
    // leida). Si fallan con 401 no queremos cerrar la sesion del
    // usuario ni redirigirlo al login. Esas llamadas pasan
    // { meta: { skipAuthRedirect: true } } en su config.
    const skipAuthRedirect = originalRequest?.meta?.skipAuthRedirect === true;
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('token/refresh') &&
      !skipAuthRedirect
    ) {
      if (_isRefreshing) {
        return new Promise((resolve, reject) => {
          _refreshQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }
      originalRequest._retry = true;
      _isRefreshing = true;
      const refresh = _getRefresh();
      if (!refresh) {
        _isRefreshing = false;
        // Sin refresh token: NO limpiamos la sesion agresivamente.
        // El componente que llamo decidira que hacer (RequireAuth
        // redirige a /login si el token esta expirado). Solo limpiamos
        // si el 401 viene de un endpoint protegido y NO tenemos
        // access token valido.
        if (!_getToken()) {
          _clearSession();
        }
        return Promise.reject(error);
      }
      try {
        const resp = await axios.post(`${API_BASE_URL}/token/refresh/`, { refresh });
        const newAccess = resp.data.access;
        const newRefresh = resp.data.refresh || refresh;
        sessionStorage.setItem('token', newAccess);
        sessionStorage.setItem('refresh', newRefresh);
        _processQueue(null, newAccess);
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return api(originalRequest);
      } catch (refreshError) {
        _processQueue(refreshError, null);
        // Solo limpiamos si el refresh fallo y el usuario esta en
        // una ruta protegida. NO hard-redirect para no romper UX.
        _clearSession();
        if (typeof window !== 'undefined'
            && window.location.pathname !== '/login') {
          // Dispara un evento en lugar de window.location.href para
          // que el AuthContext / RequireAuth reaccionen via state.
          window.dispatchEvent(new CustomEvent('zapotal:auth:expired', {
            detail: { from: window.location.pathname },
          }));
        }
        return Promise.reject(refreshError);
      } finally {
        _isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export const extractList = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.data)) return payload.data;
  if (payload && Array.isArray(payload.results)) return payload.results;
  return [];
};

export const SessionStore = {
  set: _setSession,
  clear: _clearSession,
  getUser: () => {
    try {
      const raw = sessionStorage.getItem('usuario');
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  },
  getToken: _getToken,
  getRefresh: _getRefresh,
};

export default api;
