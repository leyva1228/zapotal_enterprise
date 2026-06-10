import React from "react";
import "./NuestraHistoria.css";

function NuestraHistoria() {
  return (
    <main className="historia-page">

      {/* HERO CON 3 IMÁGENES */}
      <section className="historia-hero">
        
        {/*  tercera imagen animada */}
        <div className="hero-bg-extra"></div>

        <div className="historia-overlay">
          <span className="historia-label">Comunidad Campesina Zapotal</span>

          <h1>Nuestra historia</h1>

          <p>
            Una comunidad construida con esfuerzo, unión y respeto por sus
            tierras, costumbres y tradiciones.
          </p>
        </div>
      </section>

      {/* CONTENIDO */}
      <section className="historia-contenido">
        <div className="historia-texto">
          <span>Origen comunal</span>

          <h2>Raíces que fortalecen nuestra identidad</h2>

          <p>
            La Comunidad Campesina Zapotal nació del trabajo colectivo de sus
            pobladores, quienes durante años defendieron sus tierras y
            fortalecieron su organización comunal.
          </p>

          <p>
            A través de faenas, reuniones y acuerdos, la comunidad ha mantenido
            viva su identidad, promoviendo el respeto, la solidaridad y el
            desarrollo sostenible.
          </p>
        </div>

        <div className="historia-imagen">
          <img src="/img/fondo.png" alt="Historia de la comunidad" />
        </div>
      </section>

      {/* TIMELINE */}
      <section className="historia-timeline">
        <div>
          <h3>01</h3>
          <p>Organización de los primeros comuneros.</p>
        </div>

        <div>
          <h3>02</h3>
          <p>Trabajo conjunto para proteger las tierras comunales.</p>
        </div>

        <div>
          <h3>03</h3>
          <p>Fortalecimiento de actividades sociales y productivas.</p>
        </div>
      </section>

    </main>
  );
}

export default NuestraHistoria;