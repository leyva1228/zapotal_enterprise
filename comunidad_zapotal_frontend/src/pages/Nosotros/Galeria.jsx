import React, { useState, useEffect, useCallback, useMemo } from "react";
import { FaTimes, FaNewspaper, FaCalendarAlt, FaImages, FaFilter } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import useConfiguracion from "../../hooks/useConfiguracion";
import { useTextosSeccion } from "../../hooks/useTextosSeccion";
import api from "../../api";
import "./Galeria.css";

/**
 * /nosotros/galeria
 *
 * Pagina publica de la galeria de imagenes. Solo muestra cards de imagenes
 * agrupadas por asociacion: "Noticias" (imagenes con FK a Noticia) y
 * "Eventos" (imagenes con FK a Evento). Las imagenes sin asociacion no
 * aparecen aca (la galeria interna del admin las mantiene).
 *
 * Hero: titulo y subtitulo editables desde el panel admin institucional
 *       (campos galeria_titulo / galeria_subtitulo + seccion GALERIA_HERO).
 *
 * Las categorias tematicas (COMUNIDAD, FESTIVIDADES, etc.) siguen existiendo
 * en el modelo GaleriaImagen.categoria, pero no se exponen al usuario publico.
 */
const FILTROS = [
  { key: "TODOS",    label: "Todas",   icon: FaImages },
  { key: "NOTICIAS", label: "Noticias", icon: FaNewspaper },
  { key: "EVENTOS",  label: "Eventos",  icon: FaCalendarAlt },
];

export default function Galeria() {
  const [filtro, setFiltro] = useState("TODOS");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lightbox, setLightbox] = useState(null);
  const navigate = useNavigate();

  // Textos editables: titulo y subtitulo del hero desde ConfiguracionComunidad
  // y/o TextoSeccionInterna (seccion GALERIA_HERO).
  const { data: cfg } = useConfiguracion();
  const { data: textosGaleria } = useTextosSeccion({ seccion: "GALERIA_HERO" });
  const titulo = cfg?.galeria_titulo || "Galeria";
  const subtitulo =
    textosGaleria.find((t) => t.key === "galeria.hero.subtitulo")?.contenido ||
    cfg?.galeria_subtitulo ||
    "Imagenes de la comunidad, sus autoridades, festividades, infraestructura y patrimonio cultural.";

  // Carga desde el backend. Filtros:
  //   TODOS    -> sin filtro extra
  //   NOTICIAS -> con_noticia=1
  //   EVENTOS  -> con_evento=1
  const cargar = useCallback(async () => {
    setLoading(true);
    setError(null);
    const params = {};
    if (filtro === "NOTICIAS") params.con_noticia = 1;
    if (filtro === "EVENTOS")  params.con_evento = 1;
    try {
      const { data } = await api.get("/galeria/", { params });
      setItems(data.results || data || []);
    } catch (e) {
      setError("No se pudieron cargar las imagenes.");
    } finally {
      setLoading(false);
    }
  }, [filtro]);

  useEffect(() => { cargar(); }, [cargar]);

  // Cierra el lightbox con Escape.
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") setLightbox(null); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  // Conteo por filtro para mostrar badges en los chips.
  const counts = useMemo(() => {
    const c = { TODOS: items.length, NOTICIAS: 0, EVENTOS: 0 };
    items.forEach((it) => {
      if (it.noticia) c.NOTICIAS += 1;
      if (it.evento)  c.EVENTOS  += 1;
    });
    return c;
  }, [items]);

  // empty state contextual segun el filtro
  const emptyText = {
    TODOS:    "Aun no hay imagenes en la galeria.",
    NOTICIAS: "No hay imagenes asociadas a noticias todavia.",
    EVENTOS:  "No hay imagenes asociadas a eventos todavia.",
  }[filtro];

  return (
    <main className="galeria-page">
      {/* HERO: titulo en verde navbar, subtitulo blanco, etiqueta en dorado */}
      <section className="galeria-hero">
        <div className="galeria-hero__overlay" />
        <div className="galeria-hero__content">
          <span className="galeria-hero__label">Nuestra galeria</span>
          <h1 className="galeria-hero__title">{titulo}</h1>
          <p className="galeria-hero__subtitle">{subtitulo}</p>
        </div>
      </section>

      <div className="galeria-container">
        {/* Filtros: Todas / Noticias / Eventos */}
        <div className="galeria-filtros" role="tablist" aria-label="Filtros de galeria">
          <div className="galeria-filtros__icon" aria-hidden="true">
            <FaFilter />
          </div>
          {FILTROS.map((f) => {
            const Icon = f.icon;
            const isActive = filtro === f.key;
            return (
              <button
                key={f.key}
                type="button"
                role="tab"
                aria-selected={isActive}
                className={`galeria-filtros__chip${isActive ? " galeria-filtros__chip--activo" : ""}`}
                onClick={() => setFiltro(f.key)}
              >
                <Icon className="galeria-filtros__chip-icon" />
                <span>{f.label}</span>
                {counts[f.key] > 0 && (
                  <span className="galeria-filtros__chip-count">{counts[f.key]}</span>
                )}
              </button>
            );
          })}
        </div>

        {loading ? (
          <div className="galeria-grid galeria-grid--skeleton" aria-busy="true">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="galeria-card galeria-card--skeleton">
                <div className="galeria-card__skeleton-img" />
                <div className="galeria-card__skeleton-line" />
                <div className="galeria-card__skeleton-line galeria-card__skeleton-line--short" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="galeria-empty" role="alert">
            {error}
          </div>
        ) : items.length === 0 ? (
          <div className="galeria-empty">{emptyText}</div>
        ) : (
          <div className="galeria-grid">
            {items.map((it) => (
              <article
                key={it.id}
                className="galeria-card"
                onClick={() => setLightbox(it)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === "Enter") setLightbox(it); }}
              >
                <div className="galeria-card__img-wrap">
                  {it.imagen_url ? (
                    <img src={it.imagen_url} alt={it.titulo} loading="lazy" />
                  ) : (
                    <div className="galeria-card__placeholder">{it.titulo}</div>
                  )}
                  {(it.noticia || it.evento) && (
                    <div className="galeria-card__badge">
                      {it.noticia ? <FaNewspaper /> : <FaCalendarAlt />}
                    </div>
                  )}
                </div>
                <div className="galeria-card__body">
                  <strong>{it.titulo}</strong>
                  {it.descripcion && <span>{it.descripcion}</span>}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>

      {lightbox && (
        <div
          className="galeria-lightbox"
          onClick={() => setLightbox(null)}
          role="dialog"
          aria-modal="true"
        >
          <button
            className="galeria-lightbox__close"
            onClick={() => setLightbox(null)}
            aria-label="Cerrar"
          >
            <FaTimes />
          </button>
          {lightbox.imagen_url && (
            <img
              src={lightbox.imagen_url}
              alt={lightbox.titulo}
              className="galeria-lightbox__img"
            />
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
