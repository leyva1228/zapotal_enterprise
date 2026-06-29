import React from "react";
import { FaHistory, FaMapMarkerAlt } from "react-icons/fa";
import useConfiguracion from "../../hooks/useConfiguracion";
import useHitosHistoricos from "../../hooks/useHitosHistoricos";
import { useTextosSeccion } from "../../hooks/useTextosSeccion";
import "./NuestraHistoria.css";

function NuestraHistoria() {
  const { data: cfg, loading: cfgLoading } = useConfiguracion();
  const { data: hitos, loading: hitosLoading } = useHitosHistoricos();

  // Antes: textos hardcoded en el JSX. Ahora vienen de la BD.
  const { data: textosHero } = useTextosSeccion({ seccion: 'HISTORIA_HERO' });
  const { data: textosContenido } = useTextosSeccion({ seccion: 'HISTORIA_CONTENIDO' });
  const { data: textosTimeline } = useTextosSeccion({ seccion: 'HISTORIA_TIMELINE' });

  const etiqueta = cfg?.historia_etiqueta || 'Origen comunal';
  const titulo = cfg?.historia_hero_titulo || 'Nuestra historia';
  const subtitulo = textosHero.find(t => t.key === 'historia.hero.subtitulo')?.contenido
    || cfg?.eslogan
    || 'Una comunidad construida con esfuerzo, union y respeto por sus tierras, costumbres y tradiciones.';
  const seccionTitulo = textosContenido.find(t => t.key === 'historia.contenido.titulo')?.contenido
    || cfg?.historia_seccion_titulo
    || 'Raices que fortalecen nuestra identidad';
  const timelineTitulo = textosTimeline.find(t => t.key === 'historia.timeline.titulo')?.contenido
    || cfg?.historia_timeline_titulo
    || 'Linea de tiempo';

  return (
    <main className="historia-page">
      <section className="historia-hero">
        <div className="hero-bg-extra"></div>
        <div className="historia-overlay">
          <span className="historia-label">
            {cfg ? cfg.nombre_oficial : 'Comunidad Campesina Nino Dios de Zapotal'}
          </span>
          <h1>{titulo}</h1>
          <p>{subtitulo}</p>
          {cfg && (
            <p style={{ fontSize: 14, opacity: 0.85, marginTop: 8 }}>
              <FaMapMarkerAlt /> {cfg.direccion_casa_comunal}
            </p>
          )}
        </div>
      </section>

      <section className="historia-contenido">
        <div className="historia-texto">
          <span>{etiqueta}</span>
          <h2>{seccionTitulo}</h2>
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
          <img src="/img/Historia-comunidad/Nuestra-historia.png" alt="Historia de la comunidad" />
        </div>
      </section>

      <section className="historia-timeline-section">
        <h2><FaHistory /> {timelineTitulo}</h2>
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
