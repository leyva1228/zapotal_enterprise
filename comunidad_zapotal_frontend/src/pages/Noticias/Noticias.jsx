import React, { useEffect, useState, useMemo } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import {
  FaSearch, FaSlidersH, FaCamera, FaVideo,
} from "react-icons/fa";
import { BsShare } from "react-icons/bs";
import "./Noticias.css";

/* Noticias del grid secundario (después del bloque hero+2) por página */
const NOTICIAS_POR_PAGINA = 9;

const obtenerEtiquetaCategoria = (noticia) => {
  if (noticia.categoria_nombre)        return noticia.categoria_nombre.toUpperCase();
  if (noticia.categoria_data?.nombre)  return noticia.categoria_data.nombre.toUpperCase();
  const txt = `${noticia.titulo || ""} ${noticia.contenido || ""}`.toLowerCase();
  if (txt.includes("tecnología") || txt.includes("ciencia"))  return "CIENCIA, TECNOLOGÍA E INGENIERÍA";
  if (txt.includes("política")   || txt.includes("sociedad")) return "SOCIEDAD Y POLÍTICA";
  if (txt.includes("cultura")    || txt.includes("arte"))     return "CULTURA Y CREACIÓN";
  if (txt.includes("campus")     || txt.includes("comunidad"))return "CAMPUS Y COMUNIDAD";
  return "GENERAL";
};

const formatearFecha = (str) => {
  if (!str) return "";
  const d = new Date(str);
  if (isNaN(d)) return "";
  return `${d.getDate().toString().padStart(2,"0")}.${(d.getMonth()+1).toString().padStart(2,"0")}.${d.getFullYear()}`;
};

/* Primer elemento multimedia de tipo imagen o video */
const getMedia = (multimedia) => multimedia?.[0] || null;

function Noticias() {
  const [noticias, setNoticias]   = useState([]);
  const [loading, setLoading]     = useState(true);
  const [busqueda, setBusqueda]   = useState("");
  const [orden, setOrden]         = useState("recientes");
  const [pagina, setPagina]       = useState(1);

  useEffect(() => {
    setLoading(true);
    axios.get("http://127.0.0.1:8000/api/v1/noticias/")
      .then((res) => {
        const datos = Array.isArray(res.data) ? res.data : res.data.results || [];
        setTimeout(() => { setNoticias(datos); setLoading(false); }, 800);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => { setPagina(1); }, [busqueda, orden]);

  const noticiasFiltradas = useMemo(() => {
    let lista = noticias.filter((n) => {
      const txt = `${n.titulo || ""} ${n.contenido || ""}`.toLowerCase();
      return busqueda.trim() === "" || txt.includes(busqueda.toLowerCase());
    });
    lista.sort((a, b) =>
      orden === "antiguos"
        ? new Date(a.fecha_publicacion) - new Date(b.fecha_publicacion)
        : new Date(b.fecha_publicacion) - new Date(a.fecha_publicacion)
    );
    return lista;
  }, [noticias, busqueda, orden]);

  /* ── Loader ── */
  if (loading) return (
    <div className="loader-container">
      <div className="loader-wrapper">
        <div className="loader-ring" />
        <div className="loader-ring ring-2" />
      </div>
      <h2 className="loader-title">Cargando publicaciones</h2>
      <p className="loader-subtitle">Espere un momento...</p>
    </div>
  );

  if (noticias.length === 0)
    return <p className="nc-vacio">No hay noticias disponibles.</p>;

  /* ── Layout especial: primera = hero grande, 2.ª y 3.ª = columna derecha ── */
  const heroNoticia   = noticiasFiltradas[0] || null;
  const laterales     = noticiasFiltradas.slice(1, 3);          // máx 2
  const resto         = noticiasFiltradas.slice(3);             // paginables

  const totalPaginas   = Math.max(1, Math.ceil(resto.length / NOTICIAS_POR_PAGINA));
  const paginaActual   = Math.min(pagina, totalPaginas);
  const inicio         = (paginaActual - 1) * NOTICIAS_POR_PAGINA;
  const noticiasPagina = resto.slice(inicio, inicio + NOTICIAS_POR_PAGINA);

  const cambiarPagina = (num) => {
    if (num < 1 || num > totalPaginas) return;
    setPagina(num);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  /* ── Render de una card lateral (compacta) ── */
  const CardLateral = ({ noticia }) => {
    const media     = getMedia(noticia.multimedia);
    const esVideo   = media?.tipo === "VIDEO";
    const categoria = obtenerEtiquetaCategoria(noticia);
    return (
      <article className="nc-card-lateral">
        <Link to={`/noticias/${noticia.id}`} className="nc-lateral__media-link">
          <div className="nc-lateral__media">
            {media?.tipo === "IMAGEN" && (
              <img src={media.archivo_url} alt={noticia.titulo} className="nc-lateral__img" loading="lazy" />
            )}
            {esVideo && (
              <video src={media.archivo_url} muted preload="metadata" className="nc-lateral__img" />
            )}
            {!media && <div className="nc-lateral__placeholder" />}
            {media && (
              <span className="nc-card__media-icon">
                {esVideo ? <FaVideo /> : <FaCamera />}
              </span>
            )}
          </div>
        </Link>
        <div className="nc-lateral__body">
          <div className="nc-card__top">
            <span className="nc-card__cat">{categoria}</span>
            <button className="nc-card__share" title="Compartir"><BsShare /></button>
          </div>
          <Link to={`/noticias/${noticia.id}`} className="nc-card__title-link">
            <h2 className="nc-lateral__title">{noticia.titulo}</h2>
          </Link>
          <p className="nc-card__date">{formatearFecha(noticia.fecha_publicacion)}</p>
        </div>
      </article>
    );
  };

  /* ── Render de una card del grid inferior ── */
  const CardGrid = ({ noticia }) => {
    const media     = getMedia(noticia.multimedia);
    const esVideo   = media?.tipo === "VIDEO";
    const categoria = obtenerEtiquetaCategoria(noticia);
    return (
      <article className="nc-card">
        <Link to={`/noticias/${noticia.id}`} className="nc-card__media-link">
          <div className="nc-card__media">
            {media?.tipo === "IMAGEN" && (
              <img src={media.archivo_url} alt={noticia.titulo} className="nc-card__img" loading="lazy" />
            )}
            {esVideo && (
              <video src={media.archivo_url} muted preload="metadata" className="nc-card__img" />
            )}
            {!media && <div className="nc-card__placeholder" />}
            {media && (
              <span className="nc-card__media-icon">
                {esVideo ? <FaVideo /> : <FaCamera />}
              </span>
            )}
          </div>
        </Link>
        <div className="nc-card__body">
          <div className="nc-card__top">
            <span className="nc-card__cat">{categoria}</span>
            <button className="nc-card__share" title="Compartir"><BsShare /></button>
          </div>
          <Link to={`/noticias/${noticia.id}`} className="nc-card__title-link">
            <h2 className="nc-card__title">{noticia.titulo}</h2>
          </Link>
          <p className="nc-card__date">{formatearFecha(noticia.fecha_publicacion)}</p>
        </div>
      </article>
    );
  };

  return (
    <main className="nc-page">

      {/* ── CABECERA con punto azul ── */}
      <div className="nc-cabecera">
        <h1 className="nc-cabecera__titulo">Noticias</h1>
      </div>

      {/* ── BLOQUE HERO: grande izquierda + 2 compactas derecha ── */}
      {heroNoticia && (
        <div className="nc-hero-layout">

          {/* Hero grande */}
          <article className="nc-hero">
            {(() => {
              const media     = getMedia(heroNoticia.multimedia);
              const esVideo   = media?.tipo === "VIDEO";
              const categoria = obtenerEtiquetaCategoria(heroNoticia);
              return (
                <>
                  <Link to={`/noticias/${heroNoticia.id}`} className="nc-hero__media-link">
                    <div className="nc-hero__media">
                      {media?.tipo === "IMAGEN" && (
                        <img src={media.archivo_url} alt={heroNoticia.titulo} className="nc-hero__img" loading="eager" />
                      )}
                      {esVideo && (
                        <video src={media.archivo_url} muted preload="metadata" className="nc-hero__img" />
                      )}
                      {!media && <div className="nc-hero__placeholder" />}
                      {media && (
                        <span className="nc-card__media-icon">
                          {esVideo ? <FaVideo /> : <FaCamera />}
                        </span>
                      )}
                    </div>
                  </Link>
                  <div className="nc-hero__body">
                    <div className="nc-card__top">
                      <span className="nc-card__cat">{categoria}</span>
                      <button className="nc-card__share" title="Compartir"><BsShare /></button>
                    </div>
                    <Link to={`/noticias/${heroNoticia.id}`} className="nc-card__title-link">
                      <h2 className="nc-hero__title">{heroNoticia.titulo}</h2>
                    </Link>
                    {heroNoticia.contenido && (
                      <p className="nc-hero__excerpt">
                        {heroNoticia.contenido.length > 220
                          ? heroNoticia.contenido.substring(0, 220) + "…"
                          : heroNoticia.contenido}
                      </p>
                    )}
                    <p className="nc-card__date">{formatearFecha(heroNoticia.fecha_publicacion)}</p>
                  </div>
                </>
              );
            })()}
          </article>

          {/* Columna derecha: 2 cards apiladas */}
          {laterales.length > 0 && (
            <div className="nc-lateral-col">
              {laterales.map(n => <CardLateral key={n.id} noticia={n} />)}
            </div>
          )}
        </div>
      )}

      {/* ── BARRA DE HERRAMIENTAS (debajo del hero, como en la imagen) ── */}
      <div className="nc-toolbar">
        <div className="nc-search-wrap">
          <FaSearch className="nc-search-icon" />
          <input
            type="text"
            placeholder="Buscar..."
            value={busqueda}
            onChange={e => setBusqueda(e.target.value)}
            className="nc-search-input"
          />
        </div>
        <div className="nc-toolbar-right">
          <div className="nc-select-wrap">
            <select value={orden} onChange={e => setOrden(e.target.value)} className="nc-select">
              <option value="recientes">Ordenar por ↓</option>
              <option value="recientes">Más recientes</option>
              <option value="antiguos">Más antiguos</option>
            </select>
          </div>
          <button className="nc-btn-filtrar"><FaSlidersH /> Filtrar</button>
        </div>
      </div>

      {/* ── GRID inferior (resto de noticias paginadas) ── */}
      {noticiasFiltradas.length === 0 ? (
        <p className="nc-vacio">No se encontraron noticias con esos filtros.</p>
      ) : noticiasPagina.length > 0 && (
        <div className="nc-grid">
          {noticiasPagina.map(n => <CardGrid key={n.id} noticia={n} />)}
        </div>
      )}

      {/* ── PAGINACIÓN ── */}
      {totalPaginas > 1 && (
        <div className="pagination">
          <button
            className={`page-btn${paginaActual === 1 ? " disabled" : ""}`}
            onClick={() => cambiarPagina(paginaActual - 1)}
            disabled={paginaActual === 1}
          >← Anterior</button>

          <div className="page-numbers">
            {Array.from({ length: totalPaginas }, (_, i) => i + 1).map(num => (
              <button
                key={num}
                className={`page-number${paginaActual === num ? " active" : ""}`}
                onClick={() => cambiarPagina(num)}
              >{num}</button>
            ))}
          </div>

          <button
            className={`page-btn${paginaActual === totalPaginas ? " disabled" : ""}`}
            onClick={() => cambiarPagina(paginaActual + 1)}
            disabled={paginaActual === totalPaginas}
          >Siguiente →</button>
        </div>
      )}

    </main>
  );
}

export default Noticias;
