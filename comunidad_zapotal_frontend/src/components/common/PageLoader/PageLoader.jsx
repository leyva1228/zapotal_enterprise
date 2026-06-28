import React from "react";
import "./PageLoader.css";

const LOGO = "/img/Logo-comunidad/Logo-principal.png";

function PageLoader({ mensaje = "Cargando", variant = "section" }) {
  return (
    <div
      className={`pl-wrap pl-${variant}`}
      role="status"
      aria-live="polite"
      aria-label={mensaje}
    >
      <div className="pl-stage">
        <div className="pl-ring" />
        <div className="pl-core">
          <img src={LOGO} alt="" draggable="false" />
        </div>
        <div className="pl-spark pl-spark-1" />
        <div className="pl-spark pl-spark-2" />
        <div className="pl-spark pl-spark-3" />
        <div className="pl-spark pl-spark-4" />
      </div>
      <p className="pl-text">
        {mensaje}
        <span className="pl-dots" aria-hidden="true">
          <span />
          <span />
          <span />
        </span>
      </p>
    </div>
  );
}

export default PageLoader;
