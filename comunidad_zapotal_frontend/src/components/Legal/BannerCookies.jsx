import React, { useState, useEffect, useRef, useCallback } from 'react';
import { FaCookieBite, FaTimes, FaCheck } from 'react-icons/fa';
import api from '../../api';
import './BannerCookies.css';

/**
 * Banner de consentimiento de cookies (hardened 2026-06-29).
 *
 * Storage v2:
 *   {
 *     version: 2,
 *     preferencias: { necesarias: bool, preferencias: bool, analiticas: bool },
 *     politica_version: string,
 *     fecha: ISO-8601,
 *     fuente: 'banner' | 'perfil' | 'footer' | 'auto-dnt' | 'auto-gpc' | 'auto-version'
 *   }
 *
 * API publica (expuesta en window.zapotalCookies):
 *   - openBannerCookies({ desde })
 *   - loadConditionalScript(src, categoria)
 *   - getCookiePreferences()
 *   - resetCookiePreferences()
 *   - COOKIE_STORAGE_KEY
 *   - COOKIE_STORAGE_VERSION
 */

export const COOKIE_STORAGE_KEY = 'zapotal_cookies_pref';
export const COOKIE_STORAGE_VERSION = 2;
// Version por defecto de la politica. Si el backend no responde, usamos esta.
const DEFAULT_POLICY_VERSION = '1.0';
// Categorias validas (necesarias NO es opt-out, siempre true).
const CATEGORIES = ['necesarias', 'preferencias', 'analiticas'];

const DEFAULT_PREFS = {
  necesarias: true,
  preferencias: true,
  analiticas: false,
};

function safeStorageGet(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}
function safeStorageSet(key, value) {
  try { localStorage.setItem(key, value); return true; }
  catch {
    // Safari incognito: localStorage a veces lanza. Fallback a sessionStorage.
    try { sessionStorage.setItem(key, value); return true; } catch { return false; }
  }
}
function safeStorageRemove(key) {
  try { localStorage.removeItem(key); } catch { /* noop */ }
  try { sessionStorage.removeItem(key); } catch { /* noop */ }
}

function dntOrGpcActive() {
  if (typeof navigator === 'undefined') return { dnt: false, gpc: false };
  const dnt = navigator.doNotTrack === '1' || window.doNotTrack === '1';
  const gpc = navigator.globalPrivacyControl === true;
  return { dnt, gpc };
}

export function getCookiePreferences() {
  const raw = safeStorageGet(COOKIE_STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object') return null;
    // Migracion silenciosa: si la version de storage no coincide, la decision
    // se considera "ausente" para forzar re-pregunta.
    if (parsed.version !== COOKIE_STORAGE_VERSION) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeCookiePreferences(prefs, fuente, opts = {}) {
  const payload = {
    version: COOKIE_STORAGE_VERSION,
    preferencias: {
      necesarias: true, // siempre true por diseno
      preferencias: !!prefs.preferencias,
      analiticas: !!prefs.analiticas,
    },
    politica_version: opts.politica_version || DEFAULT_POLICY_VERSION,
    fecha: new Date().toISOString(),
    fuente: fuente || 'banner',
  };
  const ok = safeStorageSet(COOKIE_STORAGE_KEY, JSON.stringify(payload));
  if (ok && typeof window !== 'undefined') {
    // Disparamos un storage-like event manualmente para que el listener
    // de esta misma pestana reaccione. El evento `storage` nativo solo
    // se dispara en OTRAS pestanas.
    window.dispatchEvent(new CustomEvent('zapotal:cookies:changed', { detail: payload }));
  }
  return payload;
}

export function resetCookiePreferences({ from } = {}) {
  safeStorageRemove(COOKIE_STORAGE_KEY);
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('zapotal:cookies:changed', { detail: null }));
    if (from === 'reopen') {
      openBannerCookies({ desde: 'reset' });
    }
  }
}

/**
 * Carga un <script> solo si la categoria de cookies esta permitida.
 * @param {string} src URL del script.
 * @param {'preferencias'|'analiticas'} categoria Categoria que gatea la carga.
 * @returns {boolean} true si se cargo, false si fue bloqueado.
 */
export function loadConditionalScript(src, categoria = 'analiticas') {
  if (!CATEGORIES.includes(categoria)) {
    // 'necesarias' nunca gatea; si pasan esa categoria, cargamos.
    if (categoria !== 'necesarias') {
      // categoria desconocida -> bloquear por seguridad
      return false;
    }
  }
  const decision = getCookiePreferences();
  // Sin decision previa, las necesarias siguen cargandose, el resto NO.
  if (categoria !== 'necesarias' && !decision) return false;
  if (categoria !== 'necesarias' && !decision.preferencias[categoria]) return false;
  if (typeof document === 'undefined') return false;
  // Idempotencia: si ya esta inyectado, no duplicar.
  const existing = document.querySelector(`script[data-zapotal-conditional="${categoria}"][src="${src}"]`);
  if (existing) return true;
  const s = document.createElement('script');
  s.src = src;
  s.async = true;
  s.defer = true;
  s.dataset.zapotalConditional = categoria;
  s.dataset.zapotalSrc = src;
  document.head.appendChild(s);
  return true;
}

/**
 * Dispara la re-apertura del banner. Funciona desde cualquier punto de la app
 * porque el banner escucha el CustomEvent 'zapotal:cookies:open'.
 */
export function openBannerCookies({ desde } = {}) {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent('zapotal:cookies:open', { detail: { desde } }));
}

export default function BannerCookies() {
  const [visible, setVisible] = useState(false);
  const [showPersonalizar, setShowPersonalizar] = useState(false);
  const [prefs, setPrefs] = useState(DEFAULT_PREFS);
  const [politicaVersion, setPoliticaVersion] = useState(DEFAULT_POLICY_VERSION);
  const politicaFetchedRef = useRef(false);
  const initialCheckRef = useRef(false);

  /**
   * Chequeo inicial: decide si el banner debe mostrarse.
   * Causales de re-mostrar:
   *  - No hay decision guardada.
   *  - La version de storage guardada no coincide (migracion).
   *  - El usuario envio DNT/GPC y la decision previa permitia analiticas.
   *  - La version de la politica legal cambio (best-effort, no bloqueante).
   */
  const runInitialCheck = useCallback(async () => {
    if (initialCheckRef.current) return;
    initialCheckRef.current = true;

    const existing = getCookiePreferences();
    if (existing) {
      setPrefs(existing.preferencias);
      setPoliticaVersion(existing.politica_version || DEFAULT_POLICY_VERSION);
    }

    const { dnt, gpc } = dntOrGpcActive();
    if ((dnt || gpc) && (!existing || existing.preferencias.analiticas)) {
      // Forzar opt-out de analiticas. Si no habia decision previa, dejamos que
      // el banner se muestre para que el usuario confirme. Si habia decision
      // previa, la actualizamos silenciosamente.
      const newPrefs = { ...(existing?.preferencias || DEFAULT_PREFS), analiticas: false };
      if (existing) {
        writeCookiePreferences(newPrefs, dnt ? 'auto-dnt' : 'auto-gpc', {
          politica_version: existing.politica_version || DEFAULT_POLICY_VERSION,
        });
        setPrefs(newPrefs);
        return; // no re-mostrar; el cambio es silencioso
      }
      setPrefs(newPrefs);
      setVisible(true);
      setShowPersonalizar(true);
      return;
    }

    if (!existing) {
      setVisible(true);
      return;
    }

    // Hay decision previa. Comprobar version de politica (best-effort).
    if (!politicaFetchedRef.current) {
      politicaFetchedRef.current = true;
      try {
        const resp = await Promise.race([
          api.get('/paginas-legales/cookies/'),
          new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1500)),
        ]);
        const serverVersion = resp?.data?.version;
        if (
          serverVersion &&
          existing.politica_version &&
          serverVersion !== existing.politica_version
        ) {
          // Politica cambio: re-mostrar banner en modo personalizar.
          setVisible(true);
          setShowPersonalizar(true);
          setPoliticaVersion(serverVersion);
        } else if (serverVersion) {
          setPoliticaVersion(serverVersion);
        }
      } catch (e) {
        // Fallo silencioso: no romper UX por un endpoint legal caido.
      }
    }
  }, []);

  useEffect(() => {
    runInitialCheck();
  }, [runInitialCheck]);

  // Listener de "abrir banner" desde footer/perfil/etc.
  useEffect(() => {
    const onOpen = () => {
      // Re-leer decision actual para precargar UI.
      const existing = getCookiePreferences();
      if (existing) setPrefs(existing.preferencias);
      setShowPersonalizar(true);
      setVisible(true);
    };
    window.addEventListener('zapotal:cookies:open', onOpen);
    return () => window.removeEventListener('zapotal:cookies:open', onOpen);
  }, []);

  // Sync entre pestanas: si otra pestana cambia la decision, reflejamos.
  useEffect(() => {
    const onStorage = (e) => {
      if (e.key !== COOKIE_STORAGE_KEY) return;
      const other = getCookiePreferences();
      if (other) {
        setPrefs(other.preferencias);
        // Si la otra pestana decidio, ocultamos aqui.
        setVisible(false);
      } else {
        // La otra pestana hizo reset: re-mostrar.
        setPrefs(DEFAULT_PREFS);
        setVisible(true);
      }
    };
    const onInternalChange = (e) => {
      if (e.detail) {
        setPrefs(e.detail.preferencias);
      }
    };
    window.addEventListener('storage', onStorage);
    window.addEventListener('zapotal:cookies:changed', onInternalChange);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('zapotal:cookies:changed', onInternalChange);
    };
  }, []);

  const handleAceptarTodo = () => {
    const v = { necesarias: true, preferencias: true, analiticas: true };
    writeCookiePreferences(v, 'banner', { politica_version: politicaVersion });
    setPrefs(v);
    setVisible(false);
  };
  const handleRechazar = () => {
    const v = { necesarias: true, preferencias: false, analiticas: false };
    writeCookiePreferences(v, 'banner', { politica_version: politicaVersion });
    setPrefs(v);
    setVisible(false);
  };
  const handleGuardar = () => {
    writeCookiePreferences(prefs, 'banner', { politica_version: politicaVersion });
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      className="bc-banner"
      role="dialog"
      aria-live="polite"
      aria-label="Aviso de cookies"
      data-zapotal-cookies-banner="1"
    >
      <div className="bc-banner__inner">
        <div className="bc-banner__header">
          <FaCookieBite className="bc-banner__icon" />
          <h2 className="bc-banner__title">Tu privacidad importa</h2>
          <button
            className="bc-banner__close"
            onClick={handleRechazar}
            aria-label="Cerrar y rechazar"
            type="button"
          >
            <FaTimes />
          </button>
        </div>
        <p className="bc-banner__text">
          Usamos cookies para mejorar tu experiencia, recordar tus preferencias y
          analizar el trafico del sitio. Puedes aceptar todas, rechazar las no
          esenciales, o personalizar tu eleccion. Lee nuestra{' '}
          <a href="/politica-cookies" target="_blank" rel="noopener noreferrer">
            Politica de Cookies
          </a>{' '}
          y{' '}
          <a href="/privacidad" target="_blank" rel="noopener noreferrer">
            Politica de Privacidad
          </a>
          .{politicaVersion && (
            <> Version de la politica: <strong>{politicaVersion}</strong>.</>
          )}
        </p>

        {showPersonalizar && (
          <div className="bc-banner__prefs">
            <label className="bc-banner__pref">
              <input type="checkbox" checked disabled />
              <span><strong>Necesarias</strong> — Autenticacion, sesion, seguridad. Siempre activas.</span>
            </label>
            <label className="bc-banner__pref">
              <input
                type="checkbox"
                checked={prefs.preferencias}
                onChange={(e) => setPrefs((p) => ({ ...p, preferencias: e.target.checked }))}
              />
              <span><strong>Preferencias</strong> — Idioma, tema, configuracion.</span>
            </label>
            <label className="bc-banner__pref">
              <input
                type="checkbox"
                checked={prefs.analiticas}
                onChange={(e) => setPrefs((p) => ({ ...p, analiticas: e.target.checked }))}
              />
              <span>
                <strong>Analiticas</strong> — Trafico y uso del sitio (anonimo).
                {' '}
                <a href="/politica-cookies" target="_blank" rel="noopener noreferrer">Mas info</a>
              </span>
            </label>
          </div>
        )}

        <div className="bc-banner__actions">
          {showPersonalizar ? (
            <>
              <button className="bc-btn" onClick={() => setShowPersonalizar(false)} type="button">
                Cancelar
              </button>
              <button className="bc-btn bc-btn--primary" onClick={handleGuardar} type="button">
                <FaCheck /> Guardar preferencias
              </button>
            </>
          ) : (
            <>
              <button className="bc-btn" onClick={() => setShowPersonalizar(true)} type="button">
                Personalizar
              </button>
              <button className="bc-btn" onClick={handleRechazar} type="button">
                Rechazar
              </button>
              <button className="bc-btn bc-btn--primary" onClick={handleAceptarTodo} type="button">
                <FaCheck /> Aceptar todo
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
