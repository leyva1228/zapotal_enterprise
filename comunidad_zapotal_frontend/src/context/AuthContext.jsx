import React, { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react';
import { SessionStore } from '../api';

const AuthContext = createContext(null);

const REFRESH_KEYS = ['usuario', 'token', 'refresh', 'accionPendiente'];

function readSession() {
  const user = SessionStore.getUser();
  const token = SessionStore.getToken();
  return { user, token };
}

function clearAuthStorage() {
  REFRESH_KEYS.forEach((k) => sessionStorage.removeItem(k));
}

export function AuthProvider({ children }) {
  const [{ user, token }, setSession] = useState(readSession);
  const [loading, setLoading] = useState(false);

  const setAuth = useCallback((payload) => {
    // Semantica 3-way (definida en api.js):
    //   user/access/refresh: undefined -> preservar, null -> borrar, valor -> setear
    const newUser = payload?.user === undefined ? undefined : (payload?.user ?? null);
    const newAccess = payload?.access === undefined ? undefined : (payload?.access ?? null);
    const newRefresh = payload?.refresh === undefined ? undefined : (payload?.refresh ?? null);

    SessionStore.set(newUser, newAccess, newRefresh);

    // Actualizar el state de React: si no se pasaron tokens,
    // preservar los actuales leyendo del sessionStorage.
    setSession((prev) => ({
      user: newUser === undefined ? prev.user : newUser,
      token: newAccess === undefined
        ? SessionStore.getToken()
        : (newAccess || null),
    }));
  }, []);

  const clearAuth = useCallback(async () => {
    try {
      const refresh = SessionStore.getRefresh();
      if (refresh) {
        // Construir URL absoluta a partir de la base del API (definida en api.js).
        const base = (import.meta.env.VITE_API_URL) || 'http://127.0.0.1:8000/api/v1';
        await fetch(`${base}/token/blacklist/`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh }),
          }).catch(() => null);
      }
    } catch (e) { /* noop */ }
    clearAuthStorage();
    setSession({ user: null, token: null });
  }, []);

  useEffect(() => {
    const onStorage = (e) => {
      if (REFRESH_KEYS.includes(e.key)) {
        setSession(readSession());
      }
    };
    const onAuthExpired = () => {
      // Disparado por el interceptor de api.js cuando el refresh falla.
      // Limpiamos la sesion via state, no via window.location.
      clearAuthStorage();
      setSession({ user: null, token: null });
    };
    window.addEventListener('storage', onStorage);
    window.addEventListener('zapotal:auth:expired', onAuthExpired);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('zapotal:auth:expired', onAuthExpired);
    };
  }, []);

  const isAuthenticated = !!token && !!user;
  const isAdmin = !!user && (user.es_admin === true || user.tipo_usuario === 'ADMIN' || user.is_superuser === true);
  const esAutoridadAdmin = !!user && user.es_autoridad === true;

  const value = useMemo(() => ({
    user, token, loading,
    isAuthenticated, isAdmin, esAutoridadAdmin,
    setAuth, clearAuth, setLoading: setLoading,
  }), [user, token, loading, isAuthenticated, isAdmin, esAutoridadAdmin, setAuth, clearAuth]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return ctx;
}

export { clearAuthStorage };
