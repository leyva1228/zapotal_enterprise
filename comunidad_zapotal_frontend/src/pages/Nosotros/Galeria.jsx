import { useState, useCallback, useEffect } from "react";
import {
  FaTimes, FaNewspaper, FaCalendarAlt, FaImages, FaFilter,
  FaChevronLeft, FaChevronRight,
  FaUsers, FaUserTie, FaStar, FaRoad, FaLeaf, FaLandmark, FaEllipsisH,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import useConfiguracion from "../../hooks/useConfiguracion";
import { useTextosSeccion } from "../../hooks/useTextosSeccion";
import api from "../../api";
import "./Galeria.css";

/**
 * /nosotros/galeria
 *
 * Pagina publica de la galeria de imagenes. Muestra cards de imagenes
 * filtrables por dos ejes combinables (AND):
 *   - tipo: Todas / Noticias (con_noticia=1) / Eventos (con_evento=1)
 *   - categoria: Todas / Comunidad / Autoridades / Festividades /
 *                Infraestructura / Naturaleza / Patrimonio / Otro
 *
 * Hero: titulo y subtitulo editables desde el panel admin institucional
 *       (campos galeria_titulo / galeria_subtitulo + seccion GALERIA_HERO).
 *
 * Lightbox: carrusel manual con flechas izq/der y teclado (flechas, ESC).
 *           "Noticia completa" o "Evento completo" si la imagen los tiene.
 */
const FILTROS = [
  { key: "TODOS",    label: "Todas",   icon: FaImages },
  { key: "NOTICIAS", label: "Noticias", icon: FaNewspaper },
  { key: "EVENTOS",  label: "Eventos",  icon: FaCalendarAlt },
];

// Categorias tematicas del modelo GaleriaImagen.Categoria (backend).
// Mantener sincronizado con apps/comunidad/models_institucionales.py.
const CATEGORIAS = [
  { key: "TODAS",          label: "Todas",         icon: FaImages },
  { key: "COMUNIDAD",      label: "Comunidad",     icon: FaUsers },
  { key: "AUTORIDADES",    label: "Autoridades",   icon: FaUserTie },
  { key: "FESTIVIDADES",   label: "Festividades",  icon: FaStar },
  { key: "INFRAESTRUCTURA", label: "Infraestructura", icon: FaRoad },
  { key: "NATURALEZA",     label: "Naturaleza",    icon: FaLeaf },
  { key: "PATRIMONIO",     label: "Patrimonio",    icon: FaLandmark },
  { key: "OTRO",           label: "Otro",          icon: FaEllipsisH },
];

export default function Galeria() {
  const [filtro, setFiltro] = useState("TODOS");
  const [categoria, setCategoria] = useState("TODAS");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lightboxIdx, setLightboxIdx] = useState(null); // indice en `items`, o null
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
  //   filtro (tipo)   -> TODOS: sin filtro / NOTICIAS: con_noticia=1 / EVENTOS: con_evento=1
  //   categoria       -> TODAS: sin filtro / <key>: ?categoria=<key>
  // Ambos ejes se combinan (AND) en el backend.
  const cargar = useCallback(async () => {
    setLoading(true);
    setError(null);
    const params = {};
    if (filtro === "NOTICIAS") params.con_noticia = 1;
    if (filtro === "EVENTOS")  params.con_evento = 1;
    if (categoria !== "TODAS") params.categoria = categoria;
    try {
      const { data } = await api.get("/galeria/", { params });
      setItems(data.results || data || []);
    } catch (e) {
      setError("No se pudieron cargar las imagenes.");
    } finally {
      setLoading(false);
    }
  }, [filtro, categoria]);

  useEffect(() => { cargar(); }, [cargar]);

  // Cuando cambia cualquier filtro, cierra el lightbox para evitar
  // inconsistencias (el lightboxIdx dejaria de apuntar al item correcto
  // si cambia la lista).
  useEffect(() => { setLightboxIdx(null); }, [filtro, categoria]);

  // Carrusel manual: prev / next en base al lightboxIdx.
  const lightbox = lightboxIdx !== null ? items[lightboxIdx] : null;
  const goPrev = useCallback(() => {
    setLightboxIdx((i) => (i === null ? null : (i - 1 + items.length) % items.length));
  }, [items.length]);
  const goNext = useCallback(() => {
    setLightboxIdx((i) => (i === null ? null : (i + 1) % items.length));
  }, [items.length]);

  // Atajos de teclado: Escape = cerrar, flechas = navegar.
  useEffect(() => {
    if (lightboxIdx === null) return;
    const onKey = (e) => {
      if (e.key === "Escape")        setLightboxIdx(null);
      else if (e.key === "ArrowLeft")  goPrev();
      else if (e.key === "ArrowRight") goNext();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [lightboxIdx, goPrev, goNext]);

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
        {/* Filtros: dos grupos combinables (tipo AND categoria).
            aria-pressed indica el estado del toggle (no es un tablist
            porque no hay paneles asociados, son filtros acumulativos). */}
        <div className="galeria-filtros" aria-label="Filtros de galeria">
          <div className="galeria-filtros__icon" aria-hidden="true">
            <FaFilter />
          </div>

          <div
            className="galeria-filtros__grupo"
            role="group"
            aria-label="Filtrar por tipo"
          >
            <span className="galeria-filtros__label" aria-hidden="true">Tipo</span>
            {FILTROS.map((f) => {
              const Icon = f.icon;
              const isActive = filtro === f.key;
              return (
                <button
                  key={f.key}
                  type="button"
                  aria-pressed={isActive}
                  className={`galeria-filtros__chip${isActive ? " galeria-filtros__chip--activo" : ""}`}
                  onClick={() => setFiltro(f.key)}
                >
                  <Icon className="galeria-filtros__chip-icon" />
                  <span>{f.label}</span>
                </button>
              );
            })}
          </div>

          <div
            className="galeria-filtros__grupo galeria-filtros__grupo--scroll"
            role="group"
            aria-label="Filtrar por categoria"
          >
            <span className="galeria-filtros__label" aria-hidden="true">Categoria</span>
            {CATEGORIAS.map((c) => {
              const Icon = c.icon;
              const isActive = categoria === c.key;
              return (
                <button
                  key={c.key}
                  type="button"
                  aria-pressed={isActive}
                  className={`galeria-filtros__chip${isActive ? " galeria-filtros__chip--activo" : ""}`}
                  onClick={() => setCategoria(c.key)}
                >
                  <Icon className="galeria-filtros__chip-icon" />
                  <span>{c.label}</span>
                </button>
              );
            })}
          </div>
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
            {items.map((it, idx) => (
              <article
                key={it.id}
                className="galeria-card"
                onClick={() => setLightboxIdx(idx)}
                role="button"
                tabIndex={0}
                aria-label={`Ver imagen: ${it.titulo}`}
                onKeyDown={(e) => {
                  if (e.key === "Enter") setLightboxIdx(idx);
                }}
              >
                <div className="galeria-card__img-wrap">
                  {it.imagen_url ? (
                    <img src={it.imagen_url} alt={it.titulo} loading="lazy" />
                  ) : (
                    <div className="galeria-card__placeholder">{it.titulo}</div>
                  )}
                  {it.categoria_display && (
                    <div className="galeria-card__cat-badge" aria-hidden="true">
                      {it.categoria_display}
                    </div>
                  )}
                  {(it.noticia || it.evento) && (
                    <div className="galeria-card__badge" aria-hidden="true">
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
          onClick={() => setLightboxIdx(null)}
          role="dialog"
          aria-modal="true"
          aria-label={lightbox.titulo || "Imagen de galeria"}
        >
          <button
            className="galeria-lightbox__close"
            onClick={() => setLightboxIdx(null)}
            aria-label="Cerrar"
          >
            <FaTimes />
          </button>

          {/* Contador posicion */}
          {items.length > 1 && (
            <div className="galeria-lightbox__counter" aria-live="polite">
              {(lightboxIdx ?? 0) + 1} / {items.length}
            </div>
          )}

          {/* Dots de navegacion */}
          {items.length > 1 && (
            <div className="galeria-lightbox__dots" aria-hidden="true">
              <div className="galeria-lightbox__dots-track">
                {items.map((_, i) => (
                  <button
                    key={i}
                    type="button"
                    className={`galeria-lightbox__dot${i === lightboxIdx ? " galeria-lightbox__dot--activo" : ""}`}
                    onClick={(e) => { e.stopPropagation(); setLightboxIdx(i); }}
                    aria-label={`Ir a imagen ${i + 1}`}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Flechas izq/der del carrusel (siempre visibles si hay mas de 1) */}
          {items.length > 1 && (
            <>
              <button
                type="button"
                className="galeria-lightbox__nav galeria-lightbox__nav--prev"
                onClick={(e) => { e.stopPropagation(); goPrev(); }}
                aria-label="Imagen anterior"
              >
                <FaChevronLeft />
              </button>
              <button
                type="button"
                className="galeria-lightbox__nav galeria-lightbox__nav--next"
                onClick={(e) => { e.stopPropagation(); goNext(); }}
                aria-label="Imagen siguiente"
              >
                <FaChevronRight />
              </button>
            </>
          )}

          {lightbox.imagen_url && (
            <img
              key={lightbox.id}
              src={lightbox.imagen_url}
              alt={lightbox.titulo}
              className="galeria-lightbox__img"
              onClick={(e) => e.stopPropagation()}
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
          <div className="galeria-lightbox__caption" onClick={(e) => e.stopPropagation()}>
            {lightbox.categoria_display && (
              <span className="galeria-lightbox__cat-badge">{lightbox.categoria_display}</span>
            )}
            <h3>{lightbox.titulo}</h3>
            {lightbox.descripcion && <p>{lightbox.descripcion}</p>}
          </div>
        </div>
      )}
    </main>
  );
}
