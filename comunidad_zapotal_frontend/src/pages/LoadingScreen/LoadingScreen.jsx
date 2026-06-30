import React from "react";
import "./LoadingScreen.css";

/**
 * LoadingScreen 2D — Animacion de gajos convergentes + chispas.
 *
 * Origen: _reference/loader/LoadingScreen.{jsx,css}
 * Adaptado a src/pages/LoadingScreen/ sin dependencias de Three.js.
 *
 * Duracion total visible ~1.04s:
 *   - 0.00s .. 0.60s : 8 gajos del logo vuelan desde afuera al centro
 *   - 0.60s .. 1.20s : 6 chispas doradas salen desde el centro a los bordes
 *   - infinito       : 3 puntos rebotando junto al texto
 */
const LOGO = "/img/img/Logo-comunidad/Logo-principal.png";

function LoadingScreen({ mensaje = "Cargando sistema" }) {
  return (
    <div
      className="ls-screen"
      role="status"
      aria-live="polite"
      aria-label={mensaje}
    >
      <div className="ls-stage">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
          <div key={n} className={`ls-sector ls-s${n}`}>
            <img src={LOGO} alt="" draggable="false" />
          </div>
        ))}
        {[10, 11, 12, 13, 14, 15].map((n) => (
          <div key={n} className="ls-spark" aria-hidden="true" />
        ))}
      </div>

      <div className="ls-info">
        <h2>
          {mensaje}
          <span className="ls-dots" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
        </h2>
      </div>
    </div>
  );
}

export default LoadingScreen;
