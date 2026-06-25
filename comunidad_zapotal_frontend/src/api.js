import axios from 'axios';

const API_BASE_URL =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ||
  'http://127.0.0.1:8000/api/v1';

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
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('token/refresh')
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

export { API_BASE_URL };
export default api;
