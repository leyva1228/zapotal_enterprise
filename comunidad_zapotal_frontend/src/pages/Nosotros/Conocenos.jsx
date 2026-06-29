import React from "react";
import { FaBullseye, FaEye, FaHandHoldingHeart, FaMapMarkerAlt, FaImages } from "react-icons/fa";
import * as FaIcons from "react-icons/fa";
import useConfiguracion from "../../hooks/useConfiguracion";
import useGaleria from "../../hooks/useGaleria";
import "./Conocenos.css";

function getIcon(name) {
  if (!name) return FaHandHoldingHeart;
  return FaIcons[name] || FaHandHoldingHeart;
}

function Conocenos() {
  const { data: cfg, loading: cfgLoading } = useConfiguracion();
  const { data: galeria } = useGaleria('COMUNIDAD');

  // Helpers: textos que antes estaban hardcoded en el JSX. Ahora
  // vienen de la BD (modelo ConfiguracionComunidad, campos conocenos_*).
  // Si la BD no tiene valor configurado, usamos un fallback razonable.
  const etiqueta = cfg?.conocenos_etiqueta || 'Conocenos';
  const heroTitulo = cfg?.conocenos_hero_titulo || 'Una comunidad viva y organizada';
  const heroSubtitulo = cfg?.conocenos_hero_subtitulo
    || cfg?.eslogan
    || 'Trabajamos unidos para fortalecer la comunicacion, la participacion y el bienestar de todos nuestros comuneros.';
  const ubicacionTitulo = cfg?.conocenos_ubicacion_titulo || 'Donde estamos';
  const ctaTitulo = cfg?.conocenos_cta_titulo || 'Comprometidos con el futuro';
  const ctaDescripcion = cfg?.conocenos_cta_descripcion
    || cfg?.descripcion_corta
    || 'Nuestra comunidad mira hacia adelante sin olvidar sus raices.';

  return (
    <main className="conocenos-page">
      <section className="conocenos-hero">
        <div className="conocenos-card">
          <span>{etiqueta}</span>
          <h1>{heroTitulo}</h1>
          <p>{heroSubtitulo}</p>
        </div>
      </section>

      {/* MISION Y VISION - viene de ConfiguracionComunidad */}
      <section className="conocenos-mv">
        {cfg?.mision && (
          <div className="mv-card">
            <FaBullseye className="mv-icon" />
            <h2>Mision</h2>
            <p>{cfg.mision}</p>
          </div>
        )}
        {cfg?.vision && (
          <div className="mv-card">
            <FaEye className="mv-icon" />
            <h2>Vision</h2>
            <p>{cfg.vision}</p>
          </div>
        )}
      </section>

      {/* VALORES - viene de ConfiguracionComunidad.valores (JSONField) */}
      {cfg?.valores && cfg.valores.length > 0 && (
        <section className="conocenos-valores">
          <h2>Nuestros valores</h2>
          <div className="valores-grid">
            {cfg.valores.map((v, i) => {
              const Icon = getIcon(v.icono);
              return (
                <div key={i} className="valor-card">
                  <Icon className="valor-icon" />
                  <h3>{v.nombre}</h3>
                  <p>{v.descripcion}</p>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* DATOS DE UBICACION */}
      {cfg && (
        <section className="conocenos-ubicacion">
          <h2><FaMapMarkerAlt /> {ubicacionTitulo}</h2>
          <dl>
            <dt>Direccion</dt>
            <dd>{cfg.direccion_casa_comunal}</dd>
            <dt>Ubicacion</dt>
            <dd>{cfg.distrito}, {cfg.provincia}, {cfg.region} ({cfg.ubigeo})</dd>
            <dt>Coordenadas</dt>
            <dd>{cfg.coordenadas_lat}, {cfg.coordenadas_lng}</dd>
            {cfg.codigo_postal && (<><dt>Codigo postal</dt><dd>{cfg.codigo_postal}</dd></>)}
          </dl>
        </section>
      )}

      {/* GALERIA - viene de GaleriaImagen categoria=COMUNIDAD */}
      {galeria && galeria.length > 0 && (
        <section className="conocenos-galeria">
          <h2><FaImages /> {cfg?.galeria_titulo || 'Galeria'}</h2>
          <div className="galeria-grid">
            {galeria.map((g) => (
              <figure key={g.id} className="galeria-item">
                {g.imagen_url ? (
                  <img src={g.imagen_url} alt={g.titulo} loading="lazy" />
                ) : (
                  <div className="galeria-placeholder">{g.titulo}</div>
                )}
                <figcaption>
                  <strong>{g.titulo}</strong>
                  {g.descripcion && <span>{g.descripcion}</span>}
                </figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}

      {/* CTA final */}
      <section className="conocenos-final">
        <div>
          <h2>{ctaTitulo}</h2>
          <p>{ctaDescripcion}</p>
        </div>
        <img src="/img/Conocenos/conocenos-dt.png" alt="Comunidad Zapotal" />
      </section>

      {cfgLoading && (
        <p style={{ textAlign: 'center', padding: 20, color: '#6b7c72' }}>Cargando datos...</p>
      )}
    </main>
  );
}

export default Conocenos;
