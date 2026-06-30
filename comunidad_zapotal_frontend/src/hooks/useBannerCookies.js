import { useCallback, useEffect, useState } from 'react';
import {
  getCookiePreferences,
  openBannerCookies as openBanner,
  resetCookiePreferences as resetFn,
  loadConditionalScript as loadScript,
  COOKIE_STORAGE_KEY,
  COOKIE_STORAGE_VERSION,
} from '../components/Legal/BannerCookies';

/**
 * Hook publico para que cualquier componente pueda:
 *  - re-abrir el banner de cookies,
 *  - leer la decision actual reactivamente,
 *  - resetear la decision (re-preguntar),
 *  - cargar scripts condicionalmente.
 *
 * No acopla a BannerCookies directamente: usa el CustomEvent que dispara.
 */
export function useBannerCookies() {
  const [decision, setDecision] = useState(() => getCookiePreferences());

  useEffect(() => {
    const onChange = (e) => {
      if (e && e.detail) setDecision(e.detail);
      else setDecision(null);
    };
    const onStorage = (e) => {
      if (e.key !== COOKIE_STORAGE_KEY) return;
      setDecision(getCookiePreferences());
    };
    window.addEventListener('zapotal:cookies:changed', onChange);
    window.addEventListener('storage', onStorage);
    return () => {
      window.removeEventListener('zapotal:cookies:changed', onChange);
      window.removeEventListener('storage', onStorage);
    };
  }, []);

  const open = useCallback((desde) => openBanner({ desde }), []);
  const reset = useCallback(() => {
    resetFn({ from: 'reopen' });
  }, []);
  const loadConditionalScript = useCallback(loadScript, []);

  return {
    open,
    reset,
    loadConditionalScript,
    prefs: decision?.preferencias || null,
    hasDecision: !!decision,
    fecha: decision?.fecha || null,
    fuente: decision?.fuente || null,
    politicaVersion: decision?.politica_version || null,
    storageVersion: COOKIE_STORAGE_VERSION,
  };
}

export default useBannerCookies;
