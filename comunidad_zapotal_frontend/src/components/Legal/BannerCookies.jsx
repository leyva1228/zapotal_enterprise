import React, { useState, useEffect } from 'react';
import { FaCookieBite, FaTimes, FaCheck } from 'react-icons/fa';
import './BannerCookies.css';

const STORAGE_KEY = 'zapotal_cookies_pref';

function readPreference() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function writePreference(value) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  } catch { /* ignore */ }
}

export default function BannerCookies() {
  const [visible, setVisible] = useState(false);
  const [showPersonalizar, setShowPersonalizar] = useState(false);
  const [prefs, setPrefs] = useState({
    necesarias: true, // siempre true
    preferencias: true,
    analiticas: false,
  });

  useEffect(() => {
    const existing = readPreference();
    if (!existing) {
      setVisible(true);
    } else {
      setPrefs(existing);
    }
  }, []);

  const handleAceptarTodo = () => {
    const v = { necesarias: true, preferencias: true, analiticas: true };
    writePreference(v);
    setPrefs(v);
    setVisible(false);
  };
  const handleRechazar = () => {
    const v = { necesarias: true, preferencias: false, analiticas: false };
    writePreference(v);
    setPrefs(v);
    setVisible(false);
  };
  const handleGuardar = () => {
    writePreference(prefs);
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="bc-banner" role="dialog" aria-live="polite" aria-label="Aviso de cookies">
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
          </a>.
        </p>

        {showPersonalizar && (
          <div className="bc-banner__prefs">
            <label className="bc-banner__pref">
              <input type="checkbox" checked disabled />
              <span><strong>Necesarias</strong> — Autenticacion, sesion, seguridad.</span>
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
              <span><strong>Analiticas</strong> — Trafico y uso del sitio (anonimo).</span>
            </label>
          </div>
        )}

        <div className="bc-banner__actions">
          {showPersonalizar ? (
            <button className="bc-btn bc-btn--primary" onClick={handleGuardar} type="button">
              <FaCheck /> Guardar preferencias
            </button>
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
