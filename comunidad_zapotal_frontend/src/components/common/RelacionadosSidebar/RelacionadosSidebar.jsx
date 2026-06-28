import React from "react";
import { Link } from "react-router-dom";
import { FaNewspaper, FaCalendarAlt, FaPlay, FaTag } from "react-icons/fa";
import "./RelacionadosSidebar.css";

const DEFAULT_ICONS = {
  NOTICIA: FaNewspaper,
  EVENTO: FaCalendarAlt,
  DEFAULT: FaTag,
};

function formatearFecha(valor) {
  if (!valor) return "";
  const d = new Date(valor);
  if (isNaN(d.getTime())) return "";
  const dd = String(d.getDate()).padStart(2, "0");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  return `${dd}.${mm}.${d.getFullYear()}`;
}

function RelatedCard({ item, kind, linkBase, imagenPlaceholder, onImagenError }) {
  const Icon = DEFAULT_ICONS[kind] || DEFAULT_ICONS.DEFAULT;
  const multimedia = Array.isArray(item.multimedia) ? item.multimedia : [];
  const imagen = multimedia.find((m) => m.tipo === "IMAGEN");
  const src = imagen?.archivo_url || item.imagen_url || item.imagen || null;
  const tieneVideo = multimedia.some((m) => m.tipo === "VIDEO");
  const metaCanal =
    item.categoria_nombre || item.canal || (item.lugar ? item.lugar : "Comunidad");
  const fecha = item.fecha_publicacion || item.fecha_evento || item.fecha;
  const vistas = item.vistas;

  return (
    <Link to={`${linkBase}${item.id}`} className="relacionada-card-horizontal">
      <div className="relacionada-miniatura">
        {src ? (
          <img
            src={src}
            alt={item.titulo}
            onError={(e) => {
              if (onImagenError) onImagenError(e);
            }}
          />
        ) : (
          <div className="gm-thumb__placeholder">
            <Icon />
          </div>
        )}
        {tieneVideo && (
          <span className="video-badge-horizontal">
            <FaPlay />
          </span>
        )}
      </div>
      <div className="relacionada-contenido">
        <h5 className="relacionada-titulo-horizontal">{item.titulo}</h5>
        <div className="relacionada-meta">
          <span className="relacionada-canal-horizontal">{metaCanal}</span>
          {vistas != null && (
            <>
              <span className="relacionada-puntos">•</span>
              <span className="relacionada-views-horizontal">{vistas} vistas</span>
            </>
          )}
          {fecha && (
            <>
              <span className="relacionada-puntos">•</span>
              <span className="relacionada-fecha-horizontal">{formatearFecha(fecha)}</span>
            </>
          )}
        </div>
      </div>
    </Link>
  );
}

function RelacionadosSidebar({
  titulo = "Relacionados",
  icono,
  grupos = [],
  kind = "DEFAULT",
  linkBase = "/",
  imagenPlaceholder = "/images/placeholder-news.jpg",
}) {
  const Icon = icono || DEFAULT_ICONS[kind] || DEFAULT_ICONS.DEFAULT;
  const gruposValidos = (grupos || []).filter(
    (g) => g && Array.isArray(g.items) && g.items.length > 0
  );

  if (gruposValidos.length === 0) return null;

  return (
    <aside className="rs-root">
      <h4 className="rs-titulo">
        <Icon />
        <span>{titulo}</span>
      </h4>

      <div className="rs-grupos">
        {gruposValidos.map((grupo, idx) => {
          const label = grupo.label || grupo.categoria?.nombre || "General";
          const key = `${label}-${idx}`;
          return (
            <section className="rs-grupo" key={key}>
              <header className="rs-grupo__header">
                <span className="rs-grupo__punto" aria-hidden="true" />
                <h5 className="rs-grupo__titulo">{label}</h5>
              </header>
              <div className="relacionadas-lista">
                {grupo.items.map((item) => (
                  <RelatedCard
                    key={item.id}
                    item={item}
                    kind={kind}
                    linkBase={linkBase}
                    imagenPlaceholder={imagenPlaceholder}
                    onImagenError={(e) => {
                      e.currentTarget.src = imagenPlaceholder;
                    }}
                  />
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </aside>
  );
}

export default RelacionadosSidebar;
