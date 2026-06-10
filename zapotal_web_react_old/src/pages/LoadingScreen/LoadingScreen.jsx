import React from "react";
import "./LoadingScreen.css";

function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-bg"></div>

      <div className="logo-build">
        <span className="piece piece-1"></span>
        <span className="piece piece-2"></span>
        <span className="piece piece-3"></span>
        <span className="piece piece-4"></span>

        <div className="logo-final">
          <img src="/img/Logo-comunidad/Logo-principal.png" alt="Logo Comunidad Zapotal" />
        </div>
      </div>

      <div className="loading-text">
        <h2>Cargando...</h2>
        <p>Preparando la plataforma comunitaria</p>
      </div>
    </div>
  );
}

export default LoadingScreen;