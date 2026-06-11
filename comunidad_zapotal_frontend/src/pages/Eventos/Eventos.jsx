import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { extractList } from "../../api";
import {
  FaCalendarAlt,
  FaSearch,
  FaThLarge,
  FaList,
  FaArrowRight,
  FaArrowLeft,
  FaVideo,
  FaMapMarkerAlt,
  FaChartBar,
  FaUsers,
  FaChalkboardTeacher,
  FaFutbol,
  FaTree,
  FaMicrophoneAlt,
  FaPalette,
  FaHandsHelping,
  FaTag,
  FaSort,
  FaSlidersH,
  FaExternalLinkAlt,
} from "react-icons/fa";
import { BsCalendarEvent, BsCalendarCheck, BsCalendarX } from "react-icons/bs";
import { GiPartyPopper } from "react-icons/gi";
import { MdLocationOn } from "react-icons/md";
import "./Eventos.css";

/* Cuántos eventos (sin el hero) se muestran por página */
const EVENTOS_POR_PAGINA = 10;

function Eventos() {
  const [eventos, setEventos]       = useState([]);
  const [mensaje, setMensaje]       = useState("Cargando eventos...");
  const [cargando, setCargando]     = useState(true);
  const [busqueda, setBusqueda]     = useState("");
  const [filtroFecha, setFiltroFecha] = useState("todos");
  const [vista, setVista]           = useState("grid");
  const [pagina, setPagina]         = useState(1);   // ← paginación

  useEffect(() => {
    setCargando(true);
    axios
      .get("http://127.0.0.1:8000/api/v1/eventos/")
      .then((respuesta) => {
        const datos = extractList(respuesta.data);
        setTimeout(() => {
          setEventos(datos);
          setMensaje("");
          setCargando(false);
        }, 800);
      })
      .catch(() => {
        setMensaje("Error al cargar eventos. Intenta nuevamente.");
        setCargando(false);
      });
  }, []);

  /* Resetear a página 1 cuando cambian filtros o búsqueda */
  useEffect(() => { setPagina(1); }, [busqueda, filtroFecha]);

  const eventosFiltrados = useMemo(() => {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    let resultado = eventos.filter((evento) => {
      const texto = `${evento.titulo || ""} ${evento.descripcion || ""} ${
        evento.ubicacion || ""
      }`.toLowerCase();
      const coincideBusqueda =
        busqueda.trim() === "" || texto.includes(busqueda.toLowerCase());

      const fechaEvento = new Date(evento.fecha_evento);
      fechaEvento.setHours(0, 0, 0, 0);
      const coincideFecha =
        filtroFecha === "todos" ||
        (filtroFecha === "proximos" && fechaEvento >= hoy) ||
        (filtroFecha === "pasados" && fechaEvento < hoy);

      return coincideBusqueda && coincideFecha;
    });

    resultado.sort(
      (a, b) => new Date(b.fecha_evento) - new Date(a.fecha_evento)
    );
    return resultado;
  }, [eventos, busqueda, filtroFecha]);

  // ============================================
  // FUNCIONES AUXILIARES
  // ============================================

  const formatearFecha = (fechaString) => {
    if (!fechaString) return "Fecha no disponible";
    const fecha = new Date(fechaString);
    if (isNaN(fecha.getTime())) return "Fecha no disponible";
    const diasSemana = [
      "Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado",
    ];
    const meses = [
      "Enero","Febrero","Marzo","Abril","Mayo","Junio",
      "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre",
    ];
    return `${diasSemana[fecha.getDay()]}, ${fecha.getDate()} de ${
      meses[fecha.getMonth()]
    } de ${fecha.getFullYear()}`;
  };

  const formatearFechaCorta = (fechaString) => {
    if (!fechaString) return "";
    const fecha = new Date(fechaString);
    if (isNaN(fecha.getTime())) return "";
    const dd = fecha.getDate().toString().padStart(2, "0");
    const mm = (fecha.getMonth() + 1).toString().padStart(2, "0");
    const yyyy = fecha.getFullYear();
    return `${dd}.${mm}.${yyyy}`;
  };

  const extraerFechaBadge = (fechaString) => {
    if (!fechaString) return { label: "HASTA", dia: "--", mes: "---" };
    const fecha = new Date(fechaString);
    if (isNaN(fecha.getTime())) return { label: "HASTA", dia: "--", mes: "---" };
    const meses = [
      "ENE","FEB","MAR","ABR","MAY","JUN",
      "JUL","AGO","SEP","OCT","NOV","DIC",
    ];
    return { label: "HASTA", dia: fecha.getDate(), mes: meses[fecha.getMonth()] };
  };

  const esEventoProximo = (fechaString) => {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const fechaEvento = new Date(fechaString);
    fechaEvento.setHours(0, 0, 0, 0);
    return fechaEvento >= hoy;
  };

  const obtenerIconoCategoria = (evento) => {
    const texto = `${evento.titulo || ""} ${evento.descripcion || ""}`.toLowerCase();
    if (texto.includes("reunión") || texto.includes("asamblea"))      return <FaUsers />;
    if (texto.includes("taller") || texto.includes("curso") || texto.includes("capacitación")) return <FaChalkboardTeacher />;
    if (texto.includes("fiesta") || texto.includes("celebración") || texto.includes("aniversario")) return <GiPartyPopper />;
    if (texto.includes("deporte") || texto.includes("torneo") || texto.includes("partido")) return <FaFutbol />;
    if (texto.includes("campaña") || texto.includes("limpieza") || texto.includes("reforestación")) return <FaTree />;
    if (texto.includes("conferencia") || texto.includes("charla"))    return <FaMicrophoneAlt />;
    if (texto.includes("cultural") || texto.includes("arte") || texto.includes("música")) return <FaPalette />;
    if (texto.includes("solidario") || texto.includes("donación"))    return <FaHandsHelping />;
    return <FaTag />;
  };

  const obtenerNombreCategoria = (evento) => {
    const texto = `${evento.titulo || ""} ${evento.descripcion || ""}`.toLowerCase();
    if (texto.includes("reunión") || texto.includes("asamblea"))      return "Reunión";
    if (texto.includes("taller") || texto.includes("curso") || texto.includes("capacitación")) return "Taller";
    if (texto.includes("fiesta") || texto.includes("celebración") || texto.includes("aniversario")) return "Celebración";
    if (texto.includes("deporte") || texto.includes("torneo") || texto.includes("partido")) return "Deporte";
    if (texto.includes("campaña") || texto.includes("limpieza") || texto.includes("reforestación")) return "Campaña";
    if (texto.includes("conferencia") || texto.includes("charla"))    return "Conferencia";
    if (texto.includes("cultural") || texto.includes("arte") || texto.includes("música")) return "Cultural";
    if (texto.includes("solidario") || texto.includes("donación"))    return "Solidario";
    return "Evento";
  };

  // ============================================
  // LOADING
  // ============================================

  if (cargando) {
    return (
      <div className="contenedor-carga">
        <div className="animacion-carga">
          <div className="anillo-carga"></div>
          <div className="anillo-carga anillo-2"></div>
        </div>
        <h2 className="titulo-carga">Cargando eventos</h2>
        <p className="subtitulo-carga">Espere un momento...</p>
      </div>
    );
  }

  // ============================================
  // DATOS PROCESADOS + PAGINACIÓN
  // ============================================

  /* El primer evento siempre es el hero (independiente de la página) */
  const eventoHero  = eventosFiltrados[0] || null;
  /* Los demás son los paginables */
  const eventosResto = eventosFiltrados.slice(1);

  const totalPaginas  = Math.ceil(eventosResto.length / EVENTOS_POR_PAGINA);
  const paginaActual  = Math.min(pagina, totalPaginas || 1);
  const inicio        = (paginaActual - 1) * EVENTOS_POR_PAGINA;
  const eventosPagina = eventosResto.slice(inicio, inicio + EVENTOS_POR_PAGINA);

  /* Sidebar: próximos 5 del total sin filtro */
  const eventosSidebar = eventos
    .filter((e) => esEventoProximo(e.fecha_evento))
    .sort((a, b) => new Date(a.fecha_evento) - new Date(b.fecha_evento))
    .slice(0, 5);

  const irAPagina = (num) => {
    setPagina(num);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // ============================================
  // RENDER
  // ============================================

  return (
    <main className="pagina-eventos">
      <div className="contenido-eventos">

        {/* CABECERA */}
        <div className="cabecera-eventos">
          <span><BsCalendarEvent /> Nuestra agenda comunal</span>
          <h1>Eventos de la Comunidad</h1>
          <p>
            Conoce las reuniones, actividades, jornadas y acontecimientos
            organizados para fortalecer la participación de los comuneros.
          </p>
        </div>

        {/* HERO: PRIMER EVENTO DESTACADO */}
        {eventoHero && (() => {
          const mediaPrincipal  = eventoHero.multimedia?.[0];
          const esProximo       = esEventoProximo(eventoHero.fecha_evento);
          const iconoCategoria  = obtenerIconoCategoria(eventoHero);
          const nombreCategoria = obtenerNombreCategoria(eventoHero);
          const descripcionCorta = eventoHero.descripcion
            ? eventoHero.descripcion.length > 220
              ? eventoHero.descripcion.substring(0, 220) + "..."
              : eventoHero.descripcion
            : "";

          return (
            <Link to={`/eventos/${eventoHero.id}`} className="evento-hero-destacado">
              <div className="hero-imagen-wrap">
                {mediaPrincipal?.tipo === "IMAGEN" ? (
                  <img src={mediaPrincipal.archivo_url} alt={eventoHero.titulo} loading="lazy" />
                ) : mediaPrincipal?.tipo === "VIDEO" ? (
                  <div className="hero-placeholder"><FaVideo /></div>
                ) : (
                  <div className="hero-placeholder">{iconoCategoria}</div>
                )}
              </div>
              <div className="hero-contenido">
                <span className="hero-categoria-badge">{nombreCategoria}</span>
                <h2 className="hero-titulo">{eventoHero.titulo}</h2>
                {descripcionCorta && <p className="hero-descripcion">{descripcionCorta}</p>}
                <div className="hero-meta">
                  <span className="hero-fecha">{formatearFechaCorta(eventoHero.fecha_evento)}</span>
                  <span className={`hero-etiqueta ${esProximo ? "proximo" : "pasado"}`}>
                    {esProximo ? <><BsCalendarCheck /> Próximo</> : <><BsCalendarX /> Pasado</>}
                  </span>
                </div>
              </div>
            </Link>
          );
        })()}

        {/* BARRA DE FILTROS */}
        <div className="panel-filtros">
          <div className="filtros-principales">
            <div className="buscador-eventos">
              <div className="buscador-eventos-inner">
                <FaSearch className="buscador-icon" />
                <input
                  type="text"
                  placeholder="Buscar..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                />
              </div>
            </div>
            <div className="filtro-select-wrap">
              <select value={filtroFecha} onChange={(e) => setFiltroFecha(e.target.value)}>
                <option value="todos">Ordenar por</option>
                <option value="proximos">Próximos primero</option>
                <option value="pasados">Pasados primero</option>
              </select>
            </div>
            <button className="filtro-filtrar"><FaSlidersH /> Filtrar</button>
          </div>
          <div className="filtros-secundarios">
            <div className="cambiar-vista">
              <button className={`boton-vista ${vista === "grid" ? "activo" : ""}`} onClick={() => setVista("grid")}>
                <FaThLarge /> Cuadrícula
              </button>
              <button className={`boton-vista ${vista === "lista" ? "activo" : ""}`} onClick={() => setVista("lista")}>
                <FaList /> Lista
              </button>
            </div>
            <div className="contador-resultados">
              <FaChartBar /> {eventosFiltrados.length}{" "}
              {eventosFiltrados.length === 1 ? "evento" : "eventos"} encontrados
            </div>
          </div>
        </div>

        {/* Mensaje error/vacío */}
        {mensaje && <p className="mensaje-info">{mensaje}</p>}
        {!mensaje && eventosFiltrados.length === 0 && (
          <p className="mensaje-info">No se encontraron eventos con esos filtros.</p>
        )}

        {/* LAYOUT: LISTA/GRID + SIDEBAR */}
        {eventosFiltrados.length > 0 && (
          <div className="layout-con-sidebar">

            {/* COLUMNA PRINCIPAL */}
            <div className="lista-eventos-columna">
              <div className={`contenedor-eventos ${vista === "lista" ? "vista-lista" : "vista-cuadricula"}`}>
                {eventosPagina.map((evento) => {
                  const mediaPrincipal  = evento.multimedia?.[0];
                  const esProximo       = esEventoProximo(evento.fecha_evento);
                  const iconoCategoria  = obtenerIconoCategoria(evento);
                  const nombreCategoria = obtenerNombreCategoria(evento);

                  return (
                    <Link to={`/eventos/${evento.id}`} className="tarjeta-evento" key={evento.id}>
                      <div className="media-evento">
                        {mediaPrincipal?.tipo === "IMAGEN" && (
                          <img src={mediaPrincipal.archivo_url} alt={evento.titulo} className="imagen-evento" loading="lazy" />
                        )}
                        {mediaPrincipal?.tipo === "VIDEO" && (
                          <div className="vista-previa-video">
                            <video className="miniatura-video" muted>
                              <source src={mediaPrincipal.archivo_url} type="video/mp4" />
                            </video>
                            <div className="superposicion-video"><FaVideo /></div>
                          </div>
                        )}
                        {!mediaPrincipal && (
                          <div className="placeholder-evento">{iconoCategoria}</div>
                        )}
                        <div className={`etiqueta-evento ${esProximo ? "proximo" : "pasado"}`}>
                          {esProximo ? <><BsCalendarCheck /> Próximo</> : <><BsCalendarX /> Pasado</>}
                        </div>
                      </div>
                      <div className="contenido-evento">
                        <span className="categoria-evento">{iconoCategoria} {nombreCategoria}</span>
                        <span className="fecha-evento">
                          <FaCalendarAlt /> {formatearFechaCorta(evento.fecha_evento)}
                        </span>
                        <h2 className="titulo-tarjeta">{evento.titulo}</h2>
                        <p>
                          {evento.descripcion?.length > 100
                            ? evento.descripcion.substring(0, 100) + "..."
                            : evento.descripcion}
                        </p>
                        {evento.ubicacion && (
                          <div className="ubicacion-evento"><MdLocationOn /> {evento.ubicacion}</div>
                        )}
                      </div>
                    </Link>
                  );
                })}
              </div>

              {/* ── PAGINACIÓN ── */}
              {totalPaginas > 1 && (
                <div className="paginacion">
                  {/* Botón Anterior */}
                  <button
                    className={`pag-btn pag-btn--nav ${paginaActual === 1 ? "pag-btn--disabled" : ""}`}
                    onClick={() => paginaActual > 1 && irAPagina(paginaActual - 1)}
                    disabled={paginaActual === 1}
                  >
                    <FaArrowLeft /> Anterior
                  </button>

                  {/* Números de página */}
                  {Array.from({ length: totalPaginas }, (_, i) => i + 1).map((num) => (
                    <button
                      key={num}
                      className={`pag-btn pag-btn--num ${num === paginaActual ? "pag-btn--active" : ""}`}
                      onClick={() => irAPagina(num)}
                    >
                      {num}
                    </button>
                  ))}

                  {/* Botón Siguiente */}
                  <button
                    className={`pag-btn pag-btn--nav ${paginaActual === totalPaginas ? "pag-btn--disabled" : ""}`}
                    onClick={() => paginaActual < totalPaginas && irAPagina(paginaActual + 1)}
                    disabled={paginaActual === totalPaginas}
                  >
                    Siguiente <FaArrowRight />
                  </button>
                </div>
              )}
            </div>

            {/* SIDEBAR */}
            <aside className="eventos-sidebar">
              <h2 className="sidebar-titulo">
                Apúntate a nuestros próximos eventos de la Comunidad
              </h2>
              <div className="sidebar-eventos-lista">
                {eventosSidebar.length > 0 ? (
                  eventosSidebar.map((ev) => {
                    const fechaBadge = extraerFechaBadge(ev.fecha_evento);
                    const lugarEv    = ev.ubicacion || ev.lugar || null;
                    return (
                      <Link key={ev.id} to={`/eventos/${ev.id}`} className="sidebar-evento-item">
                        <div className="sidebar-fecha-badge">
                          <span className="sidebar-fecha-label">{fechaBadge.label}</span>
                          <span className="sidebar-fecha-dia">{fechaBadge.dia}</span>
                          <span className="sidebar-fecha-mes">{fechaBadge.mes}</span>
                        </div>
                        <div className="sidebar-evento-info">
                          <p className="sidebar-evento-titulo">{ev.titulo}</p>
                          {lugarEv && (
                            <span className="sidebar-evento-lugar"><MdLocationOn /> {lugarEv}</span>
                          )}
                        </div>
                        <FaExternalLinkAlt className="sidebar-evento-externo" />
                      </Link>
                    );
                  })
                ) : (
                  <p className="sidebar-vacio">No hay eventos próximos programados.</p>
                )}
              </div>
            </aside>

          </div>
        )}
      </div>
    </main>
  );
}

export default Eventos;
