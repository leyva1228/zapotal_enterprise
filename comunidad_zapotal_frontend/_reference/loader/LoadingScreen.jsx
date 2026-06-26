import React from "react";
import "./LoadingScreen.css";

const LOGO = "/img/img/Logo-comunidad/Logo-principal.png";

function LoadingScreen() {
  return (
    <div className="ls-screen" role="status" aria-label="Cargando sistema">

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
          Cargando sistema
          <span className="ls-dots" aria-hidden="true">
            <span /><span /><span />
          </span>
        </h2>
      </div>

    </div>
  );
}

export default LoadingScreen;