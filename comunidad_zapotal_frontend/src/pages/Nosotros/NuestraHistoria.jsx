import React from "react";
import { FaHistory, FaMapMarkerAlt } from "react-icons/fa";
import useConfiguracion from "../../hooks/useConfiguracion";
import useHitosHistoricos from "../../hooks/useHitosHistoricos";
import "./NuestraHistoria.css";

function NuestraHistoria() {
  const { data: cfg, loading: cfgLoading } = useConfiguracion();
  const { data: hitos, loading: hitosLoading } = useHitosHistoricos();

  return (
    <main className="historia-page">

      {/* HERO */}
      <section className="historia-hero">
        <div className="hero-bg-extra"></div>
        <div className="historia-overlay">
          <span className="historia-label">
            {cfg ? cfg.nombre_oficial : 'Comunidad Campesina Zapotal'}
          </span>
          <h1>Nuestra historia</h1>
          <p>
            {cfg?.eslogan ||
              'Una comunidad construida con esfuerzo, unión y respeto por sus tierras, costumbres y tradiciones.'}
          </p>
          {cfg && (
            <p style={{ fontSize: 14, opacity: 0.85, marginTop: 8 }}>
              <FaMapMarkerAlt /> {cfg.direccion_casa_comunal}
            </p>
          )}
        </div>
      </section>

      {/* CONTENIDO - viene de ConfiguracionComunidad.historia_html */}
      <section className="historia-contenido">
        <div className="historia-texto">
          <span>Origen comunal</span>
          <h2>Raices que fortalecen nuestra identidad</h2>
          {cfgLoading ? (
            <p>Cargando...</p>
          ) : cfg?.historia_html ? (
            <div
              className="historia-html"
              dangerouslySetInnerHTML={{ __html: cfg.historia_html }}
            />
          ) : (
            <p>No hay contenido de historia configurado. Edita la Configuracion Institucional en el admin.</p>
          )}
        </div>
        <div className="historia-imagen">
          <img src="/img/fondo.png" alt="Historia de la comunidad" />
        </div>
      </section>

      {/* TIMELINE - viene de HitoHistorico */}
      <section className="historia-timeline-section">
        <h2><FaHistory /> Linea de tiempo</h2>
        {hitosLoading ? (
          <p>Cargando hitos...</p>
        ) : hitos.length === 0 ? (
          <p className="text-mute">Aun no hay hitos registrados.</p>
        ) : (
          <div className="historia-timeline">
            {hitos.map((h, idx) => (
              <div key={h.id} className="historia-timeline__item">
                <div className="historia-timeline__anio">{h.anio}</div>
                <div className="historia-timeline__contenido">
                  <h3>{String(idx + 1).padStart(2, '0')}</h3>
                  <h4>{h.titulo}</h4>
                  <p>{h.descripcion}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

    </main>
  );
}

export default NuestraHistoria;
