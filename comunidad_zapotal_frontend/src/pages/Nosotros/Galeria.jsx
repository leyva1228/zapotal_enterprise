import React, { useState, useEffect } from "react";
import { FaTimes, FaNewspaper, FaCalendarAlt } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import useGaleria from "../../hooks/useGaleria";
import { useCategoriasGaleria, useTextosSeccion } from "../../hooks/useTextosSeccion";
import useConfiguracion from "../../hooks/useConfiguracion";
import "./Galeria.css";

export default function Galeria() {
  const [categoria, setCategoria] = useState(null);
  const [lightbox, setLightbox] = useState(null);
  const navigate = useNavigate();

  // Antes: las categorias estaban hardcodeadas en este archivo. Ahora
  // se sirven desde la BD via /api/v1/galerias/categorias/.
  const { data: categorias } = useCategoriasGaleria();
  const { data: cfg } = useConfiguracion();
  // Textos editables (titulo, subtitulo) desde ConfiguracionComunidad.
  const { data: textosGaleria } = useTextosSeccion({ seccion: 'GALERIA_HERO' });
  const titulo = cfg?.galeria_titulo || 'Galeria';
  const subtitulo = textosGaleria.find(t => t.key === 'galeria.hero.subtitulo')?.contenido
    || cfg?.galeria_subtitulo
    || 'Imagenes de la comunidad, sus autoridades, festividades, infraestructura y patrimonio cultural.';

  const { data: items, loading, error } = useGaleria(categoria);

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') setLightbox(null); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [lightbox]);

  return (
    <main className="galeria-page">
      <section className="galeria-hero">
        <div>
          <h1>{titulo}</h1>
          <p>{subtitulo}</p>
        </div>
      </section>
      <div className="galeria-container">
        <div className="galeria-filtros">
          {/* "Todas" siempre la primera opcion */}
          <button
            type="button"
            className={categoria === null ? 'activo' : ''}
            onClick={() => setCategoria(null)}
          >
            Todas
          </button>
          {/* Las demas categorias vienen de la BD */}
          {categorias && categorias.map((c) => (
            <button
              key={c.nombre}
              type="button"
              className={categoria === c.nombre ? 'activo' : ''}
              onClick={() => setCategoria(c.nombre)}
            >
              {c.label}
            </button>
          ))}
        </div>
        {loading ? (
          <div className="galeria-loading">Cargando imagenes...</div>
        ) : error ? (
          <div className="galeria-empty">No se pudieron cargar las imagenes.</div>
        ) : items.length === 0 ? (
          <div className="galeria-empty">Aun no hay imagenes en esta categoria.</div>
        ) : (
          <div className="galeria-grid">
            {items.map((it) => (
              <article
                key={it.id}
                className="galeria-card"
                onClick={() => setLightbox(it)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter') setLightbox(it); }}
              >
                {it.imagen_url ? (
                  <img src={it.imagen_url} alt={it.titulo} loading="lazy" />
                ) : (
                  <div className="galeria-placeholder">{it.titulo}</div>
                )}
                <figcaption>
                  <strong>{it.titulo}</strong>
                  {it.descripcion && <span>{it.descripcion}</span>}
                </figcaption>
              </article>
            ))}
          </div>
        )}
      </div>

      {lightbox && (
        <div className="galeria-lightbox" onClick={() => setLightbox(null)} role="dialog" aria-modal="true">
          <button className="galeria-lightbox__close" onClick={() => setLightbox(null)} aria-label="Cerrar">
            <FaTimes />
          </button>
          {lightbox.imagen_url && (
            <img src={lightbox.imagen_url} alt={lightbox.titulo} className="galeria-lightbox__img" />
          )}
          {(lightbox.noticia || lightbox.evento) && (
            <div className="galeria-lightbox__action">
              {lightbox.noticia && (
                <button
                  type="button"
                  className="galeria-lightbox__btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/noticias/${lightbox.noticia}`);
                  }}
                >
                  <FaNewspaper />
                  Ver noticia completa
                  {lightbox.noticia_titulo && (
                    <span className="galeria-lightbox__btn-sub">
                      {lightbox.noticia_titulo}
                    </span>
                  )}
                </button>
              )}
              {lightbox.evento && (
                <button
                  type="button"
                  className="galeria-lightbox__btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/eventos/${lightbox.evento}`);
                  }}
                >
                  <FaCalendarAlt />
                  Ver evento completo
                  {lightbox.evento_titulo && (
                    <span className="galeria-lightbox__btn-sub">
                      {lightbox.evento_titulo}
                    </span>
                  )}
                </button>
              )}
            </div>
          )}
          <div className="galeria-lightbox__caption">
            <h3>{lightbox.titulo}</h3>
            {lightbox.descripcion && <p>{lightbox.descripcion}</p>}
          </div>
        </div>
      )}
    </main>
  );
}
