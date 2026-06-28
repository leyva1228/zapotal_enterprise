import React from "react";
import "./LoaderOverlay.css";

const LOGO = "/img/Logo-comunidad/Logo-principal.png";

function LoaderOverlay({ active, variant = "with-navbar", mensaje = "Cargando" }) {
  if (!active) return null;

  return (
    <div
      className={`lo-root lo-${variant}`}
      role="status"
      aria-live="assertive"
      aria-busy="true"
      aria-label={mensaje}
    >
      <div className="lo-bg" aria-hidden="true" />
      <div className="lo-stage">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
          <div key={n} className={`lo-sector lo-s${n}`}>
            <img src={LOGO} alt="" draggable="false" />
          </div>
        ))}
        {[10, 11, 12, 13, 14, 15].map((n) => (
          <div key={n} className="lo-spark" aria-hidden="true" />
        ))}
      </div>
      <p className="lo-text">
        {mensaje}
        <span className="lo-dots" aria-hidden="true">
          <span />
          <span />
          <span />
        </span>
      </p>
    </div>
  );
}

export default LoaderOverlay;
