import React from "react";
import "./Conocenos.css";

function Conocenos() {
  return (
    <main className="conocenos-page">
      <section className="conocenos-hero">
        <div className="conocenos-card">
          <span>Conócenos</span>
          <h1>Una comunidad viva y organizada</h1>
          <p>
            Trabajamos unidos para fortalecer la comunicación, la participación
            y el bienestar de todos nuestros comuneros.
          </p>
        </div>
      </section>

      <section className="conocenos-info">
        <div className="info-card">
          <h2>Participación</h2>
          <p>
            Promovemos la participación activa de jóvenes, adultos y autoridades
            en actividades comunales.
          </p>
        </div>

        <div className="info-card">
          <h2>Integración</h2>
          <p>
            Organizamos eventos, reuniones y jornadas que fortalecen los lazos
            entre vecinos.
          </p>
        </div>

        <div className="info-card">
          <h2>Desarrollo</h2>
          <p>
            Buscamos mejorar la calidad de vida de la comunidad mediante
            proyectos responsables.
          </p>
        </div>
      </section>

      <section className="conocenos-final">
        <div>
          <h2>Comprometidos con el futuro</h2>
          <p>
            Nuestra comunidad mira hacia adelante sin olvidar sus raíces.
            Creemos en el trabajo colectivo, la transparencia y la unión como
            camino para seguir creciendo.
          </p>
        </div>

        <img src="/img/Conocenos/conocenos-dt.png" alt="Comunidad Zapotal" />
      </section>
    </main>
  );
}

export default Conocenos;