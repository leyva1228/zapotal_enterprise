import React, { useEffect, useState, useRef, useCallback, useMemo, memo } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import {
  FaArrowLeft, FaUserCircle, FaSignInAlt, FaUserPlus,
  FaTimes, FaReply, FaTrashAlt, FaUserCheck,
  FaTags, FaCalendarAlt, FaRegClock, FaEye, FaLock,
  FaBookmark, FaEllipsisH, FaEllipsisV, FaPencilAlt, FaCheck,
  FaFlag, FaPlay, FaMapMarkerAlt, FaUsers
} from "react-icons/fa";
import { BsShieldLockFill, BsFillPatchCheckFill } from "react-icons/bs";
import { MdAdminPanelSettings, MdVerified } from "react-icons/md";
import { AiOutlineLike, AiFillLike, AiOutlineDislike, AiFillDislike } from "react-icons/ai";
import { HiOutlineChatBubbleLeftRight } from "react-icons/hi2";
import { RiSendPlaneFill, RiShareForwardLine } from "react-icons/ri";
import "./DetalleEvento.css";

// ========== CONSTANTES Y FUNCIONES COMPARTIDAS ==========
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";
const MAX_COMMENT_LENGTH = 500;
const MIN_COMMENT_LENGTH = 3;
const RATE_LIMIT_COMMENTS = 10;

const PALABRAS_PROHIBIDAS = ["idiota","estupido","imbecil","tarado","basura","mierda"];

const formatFecha = (str) => {
  if (!str) return "Fecha reciente";
  try {
    const d = new Date(str);
    if (isNaN(d.getTime())) return "Fecha reciente";
    const meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
    return `${d.getDate()} ${meses[d.getMonth()]} ${d.getFullYear()}`;
  } catch { return "Fecha reciente"; }
};

const formatRelativeTime = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return "";
  const now = new Date();
  const diffMs = now - date;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  if (diffSecs < 60) return "hace un momento";
  if (diffMins < 60) return `hace ${diffMins} minuto${diffMins !== 1 ? "s" : ""}`;
  if (diffHours < 24) return `hace ${diffHours} hora${diffHours !== 1 ? "s" : ""}`;
  if (diffDays === 1) return "ayer";
  if (diffDays < 7) return `hace ${diffDays} días`;
  if (diffDays < 30) return `hace ${Math.floor(diffDays / 7)} semana${Math.floor(diffDays / 7) !== 1 ? "s" : ""}`;
  if (diffDays < 365) return `hace ${Math.floor(diffDays / 30)} mes${Math.floor(diffDays / 30) !== 1 ? "es" : ""}`;
  return `hace ${Math.floor(diffDays / 365)} año${Math.floor(diffDays / 365) !== 1 ? "s" : ""}`;
};

const validarComentario = (texto) => {
  const t = texto.toLowerCase();
  for (const p of PALABRAS_PROHIBIDAS)
    if (t.includes(p)) return { valido: false, mensaje: "El comentario contiene lenguaje ofensivo." };
  if (texto.length < MIN_COMMENT_LENGTH) return { valido: false, mensaje: `Mínimo ${MIN_COMMENT_LENGTH} caracteres.` };
  if (texto.length > MAX_COMMENT_LENGTH) return { valido: false, mensaje: `Máximo ${MAX_COMMENT_LENGTH} caracteres.` };
  if (/(.)\1{10,}/.test(texto)) return { valido: false, mensaje: "Demasiados caracteres repetidos." };
  return { valido: true };
};

// ========== COMPONENTES REUTILIZABLES (idénticos a DetalleNoticia) ==========
const Avatar = memo(({ foto, inicial, size = 40, bg = "#e0e0e0" }) => {
  if (foto) return <img src={foto} alt="" className="avatar-img" style={{ width: size, height: size }} />;
  return (
    <div className="avatar-inicial" style={{ width: size, height: size, fontSize: size * 0.38, backgroundColor: bg }}>
      {inicial}
    </div>
  );
});

const ComentarioReacciones = memo(({ comentarioId, reaccionesLista, estaAuth, onReaccionar, onAbrirModal, usuarioActualId }) => {
  const miReaccion   = reaccionesLista.find(r => r.usuario === usuarioActualId);
  const miTipo       = miReaccion?.tipo;
  const likeCount    = reaccionesLista.filter(r => r.tipo === "LIKE").length;
  const dislikeCount = reaccionesLista.filter(r => r.tipo === "DISLIKE").length;
  const handle = (tipo) => {
    if (!estaAuth) { onAbrirModal("like"); return; }
    onReaccionar(comentarioId, miTipo === tipo ? null : tipo);
  };
  return (
    <div className="comentario-reacciones-estaticas">
      <button className={`reaccion-estatica like-btn ${miTipo === "LIKE" ? "activa" : ""}`} onClick={() => handle("LIKE")} title="Me gusta">
        {miTipo === "LIKE" ? <AiFillLike /> : <AiOutlineLike />}
        {likeCount > 0 && <span>{likeCount}</span>}
      </button>
      <button className={`reaccion-estatica dislike-btn ${miTipo === "DISLIKE" ? "activa" : ""}`} onClick={() => handle("DISLIKE")} title="No me gusta">
        {miTipo === "DISLIKE" ? <AiFillDislike /> : <AiOutlineDislike />}
        {dislikeCount > 0 && <span>{dislikeCount}</span>}
      </button>
    </div>
  );
});

const MenuComentario = memo(({ puedeEditar, puedeEliminar, puedeReportar, onEditar, onEliminar, onReportar, estaAuth, onAbrirModal }) => {
  const [abierto, setAbierto] = useState(false);
  const menuRef = useRef(null);
  useEffect(() => {
    if (!abierto) return;
    const handler = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setAbierto(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [abierto]);
  const handleClick = () => {
    if (!estaAuth) { onAbrirModal("reporte"); return; }
    setAbierto(true);
  };
  return (
    <div className="menu-tres-puntos" ref={menuRef}>
      <button className="btn-tres-puntos" onClick={handleClick} title="Más opciones"><FaEllipsisV /></button>
      {abierto && estaAuth && (
        <div className="dropdown-menu-comentario">
          {puedeEditar && <button className="dropdown-item" onClick={() => { setAbierto(false); onEditar(); }}><FaPencilAlt /> Editar</button>}
          {puedeEliminar && <button className="dropdown-item dropdown-item--danger" onClick={() => { setAbierto(false); onEliminar(); }}><FaTrashAlt /> Eliminar</button>}
          {puedeReportar && <button className="dropdown-item" onClick={() => { setAbierto(false); onReportar(); }}><FaFlag /> Reportar</button>}
        </div>
      )}
    </div>
  );
});

const GaleriaMedia = memo(({ imagenes = [], videos = [], titulo = "" }) => {
  const [heroIdx, setHeroIdx] = useState(0);
  const [anim, setAnim]       = useState(null);
  useEffect(() => {
    if (imagenes.length > 0 && heroIdx >= imagenes.length) setHeroIdx(0);
  }, [imagenes, heroIdx]);
  if (imagenes.length === 0 && videos.length === 0) return null;
  const soloUna   = imagenes.length === 1;
  const hayThumbs = imagenes.length > 1;
  const heroImg   = imagenes[heroIdx];
  const swap = (idx) => {
    if (idx === heroIdx) return;
    const dir = idx > heroIdx ? "slide-left" : "slide-right";
    setAnim(dir);
    setTimeout(() => { setHeroIdx(idx); setAnim(null); }, 260);
  };
  return (
    <div className={`gm-wrapper${soloUna ? " gm-wrapper--solo" : ""}`}>
      {imagenes.length > 0 && (
        <div className="gm-hero">
          <img key={heroIdx} src={heroImg?.archivo_url} alt={titulo} className={`gm-hero__img${anim ? ` gm-hero__img--${anim}` : ""}`} loading="lazy" onError={e => { e.target.src = "/images/image-not-found.jpg"; }} />
          {hayThumbs && <div className="gm-hero__gradient" />}
          {hayThumbs && <div className="gm-hero__counter">{heroIdx + 1} / {imagenes.length}</div>}
          {hayThumbs && (
            <>
              <button className="gm-arrow gm-arrow--prev" onClick={() => swap((heroIdx - 1 + imagenes.length) % imagenes.length)} aria-label="Anterior">&#8249;</button>
              <button className="gm-arrow gm-arrow--next" onClick={() => swap((heroIdx + 1) % imagenes.length)} aria-label="Siguiente">&#8250;</button>
            </>
          )}
          {hayThumbs && (
            <div className="gm-thumbs-overlay">
              {imagenes.map((img, idx) => (
                <button key={img.id ?? idx} className={`gm-thumb${idx === heroIdx ? " gm-thumb--active" : ""}`} onClick={() => swap(idx)} title={`Imagen ${idx + 1}`}>
                  <img src={img.archivo_url} alt={`Miniatura ${idx + 1}`} loading="lazy" onError={e => { e.target.src = "/images/image-not-found.jpg"; }} />
                  {idx === heroIdx && <span className="gm-thumb__ring" />}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
      {videos.length > 0 && (
        <div className="gm-videos">
          {videos.map((v, i) => (
            <div key={v.id ?? i} className="gm-video">
              <video src={v.archivo_url} controls preload="metadata" className="gm-video__player" poster={v.thumbnail_url || imagenes[0]?.archivo_url} controlsList="nodownload" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
});

// ========== EVENTOS RELACIONADOS (similar a noticias relacionadas) ==========
const EventosRelacionados = memo(({ eventos }) => {
  if (!eventos.length) return null;

  const obtenerPreview = (evento) => {
    const video = evento.multimedia?.find(m => m.tipo === "VIDEO");
    const imagen = evento.multimedia?.find(m => m.tipo === "IMAGEN");
    if (video) {
      return <video src={video.archivo_url} muted preload="metadata" className="preview-video-relacionada" />;
    }
    return <img src={imagen?.archivo_url || evento.miniatura || "/images/placeholder-event.jpg"} alt={evento.titulo} />;
  };

  const tieneVideo = (evento) => evento.multimedia?.some(m => m.tipo === "VIDEO") || false;

  return (
    <aside className="eventos-relacionados">
      <h4><FaCalendarAlt /> Eventos relacionados</h4>
      <div className="relacionadas-lista">
        {eventos.map(evento => (
          <Link to={`/eventos/${evento.id}`} key={evento.id} className="relacionada-card-horizontal">
            <div className="relacionada-miniatura">
              {obtenerPreview(evento)}
              {tieneVideo(evento) && <span className="video-badge-horizontal"><FaPlay /></span>}
            </div>
            <div className="relacionada-contenido">
              <h5 className="relacionada-titulo-horizontal">{evento.titulo}</h5>
              <div className="relacionada-meta">
                <span className="relacionada-canal-horizontal">{evento.usuario_nombre?.split(" ")[0] || "Organizador"}</span>
                <span className="relacionada-puntos">•</span>
                {evento.vistas && <span className="relacionada-views-horizontal">{evento.vistas} vistas</span>}
                <span className="relacionada-puntos">•</span>
                <span className="relacionada-fecha-horizontal">{formatFecha(evento.fecha_evento)}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </aside>
  );
});

// ========================= COMPONENTE PRINCIPAL =========================
function DetalleEvento() {
  const { id }   = useParams();
  const navigate = useNavigate();

  const eventoId = useMemo(() => {
    const parsed = Number(id);
    if (isNaN(parsed) || parsed <= 0) { navigate("/eventos"); return null; }
    return parsed;
  }, [id, navigate]);

  const [userActual] = useState(() => {
    try { return JSON.parse(localStorage.getItem("usuario")); } catch { return null; }
  });
  const estaAuth  = !!userActual?.id;
  const esAdmin   = userActual?.tipo_usuario === "ADMIN";
  const usuarioId = userActual?.id;

  const [evento,              setEvento]            = useState(null);
  const [error,               setError]             = useState("");
  const [loading,             setLoading]           = useState(true);
  const [reacciones,          setReacciones]        = useState([]);
  const [reaccsComent,        setReaccsComent]      = useState({});
  const [comentarios,         setComentarios]       = useState([]);
  const [nuevoComentario,     setNuevo]             = useState("");
  const [respondiendoA,       setRespondiendoA]     = useState(null);
  const [textoRespuesta,      setTextoResp]         = useState("");
  const [respuestasVis,       setRespuestasVis]     = useState({});
  const [modal,               setModal]             = useState({ show: false, accion: null });
  const [rateLimit,           setRateLimit]         = useState({ count: 0, lastReset: Date.now() });
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [isSubmittingReply,   setIsSubmittingReply]   = useState(false);
  const [relacionados,        setRelacionados]      = useState([]);
  const [compartido,          setCompartido]        = useState(false);
  const [descExpanded,        setDescExpanded]      = useState(false);
  const [editando,            setEditando]          = useState({});
  const [ordenComentarios,    setOrdenComentarios]  = useState("recientes");
  const [mostrarMenuOrden,    setMostrarMenuOrden]  = useState(false);

  const menuOrdenRef         = useRef(null);
  const timeoutRef           = useRef(null);
  const comentariosScrollRef = useRef(null);

  useEffect(() => () => { if (timeoutRef.current) clearTimeout(timeoutRef.current); }, []);

  // Cargar evento
  useEffect(() => {
    if (!eventoId) return;
    (async () => {
      try {
        const { data } = await axios.get(`${API_BASE_URL}/eventos/${eventoId}/`);
        setEvento(data);
      } catch (err) {
        setError(err.response?.status === 404 ? "El evento no existe o fue eliminado." : "No se pudo cargar el evento.");
      } finally { setLoading(false); }
    })();
  }, [eventoId]);

  // Contador de vistas
  useEffect(() => {
    if (!eventoId || !evento) return;
    const claveLocal = estaAuth && usuarioId
      ? `visto_evento_${eventoId}_user_${usuarioId}`
      : `visto_evento_${eventoId}_session`;
    const storage = estaAuth && usuarioId ? localStorage : sessionStorage;
    if (!storage?.getItem(claveLocal)) {
      const nuevasVistas = (evento.vistas || 0) + 1;
      axios.patch(`${API_BASE_URL}/eventos/${eventoId}/`, { vistas: nuevasVistas })
        .then(() => {
          setEvento(prev => ({ ...prev, vistas: nuevasVistas }));
          storage.setItem(claveLocal, "true");
        })
        .catch(err => console.warn("Error al incrementar vistas:", err));
    }
  }, [eventoId, evento, estaAuth, usuarioId]);

  // Cargar eventos relacionados
  useEffect(() => {
    if (!eventoId) return;
    axios.get(`${API_BASE_URL}/eventos/${eventoId}/relacionados/`)
      .then(res => setRelacionados(res.data))
      .catch(() => setRelacionados([]));
  }, [eventoId]);

  const cargarReacciones = useCallback(() => {
    if (!eventoId) return Promise.resolve();
    return axios.get(`${API_BASE_URL}/reacciones/?evento=${eventoId}`)
      .then(({ data }) => setReacciones(data)).catch(() => {});
  }, [eventoId]);

  const cargarReaccionesComentarios = useCallback(async (lista) => {
    if (!lista.length) return;
    const resultados = await Promise.all(
      lista.map(com =>
        axios.get(`${API_BASE_URL}/reacciones/?comentario=${com.id}`)
          .then(res => ({ id: com.id, data: res.data }))
          .catch(() => ({ id: com.id, data: [] }))
      )
    );
    const nuevoMap = {};
    resultados.forEach(({ id, data }) => { nuevoMap[id] = data; });
    setReaccsComent(prev => ({ ...prev, ...nuevoMap }));
  }, []);

  const cargarComentarios = useCallback(() => {
    if (!eventoId) return Promise.resolve();
    return axios.get(`${API_BASE_URL}/comentarios/?evento=${eventoId}`)
      .then(async ({ data }) => {
        const visibles = data.filter(c => c.estado !== "ELIMINADO");
        setComentarios(visibles);
        await cargarReaccionesComentarios(visibles);
      }).catch(() => {});
  }, [eventoId, cargarReaccionesComentarios]);

  useEffect(() => {
    if (eventoId) { cargarReacciones(); cargarComentarios(); }
  }, [eventoId, cargarReacciones, cargarComentarios]);

  const hasPermission = useCallback((p) => {
    if (!userActual) return false;
    if (userActual.tipo_usuario === "INVITADO" && (p === "comentar" || p === "reaccionar")) return false;
    return true;
  }, [userActual]);

  const checkRate = useCallback(() => {
    const now = Date.now();
    if (now - rateLimit.lastReset > 60000) { setRateLimit({ count: 0, lastReset: now }); return true; }
    return rateLimit.count < RATE_LIMIT_COMMENTS;
  }, [rateLimit]);

  const openModal  = (accion) => setModal({ show: true, accion });
  const closeModal = () => setModal({ show: false, accion: null });

  const enviarReaccion = async (tipo) => {
    if (!hasPermission("reaccionar") || !estaAuth) { openModal("reaccion"); return; }
    try {
      if (tipo === null) {
        const existente = reacciones.find(r => r.usuario === usuarioId);
        if (existente) await axios.delete(`${API_BASE_URL}/reacciones/${existente.id}/`);
      } else {
        const anterior = reacciones.find(r => r.usuario === usuarioId);
        if (anterior && anterior.tipo !== tipo) await axios.delete(`${API_BASE_URL}/reacciones/${anterior.id}/`);
        if (!anterior || anterior.tipo !== tipo)
          await axios.post(`${API_BASE_URL}/reacciones/`, { tipo, usuario: usuarioId, evento: eventoId, noticia: null, comentario: null });
      }
      cargarReacciones();
    } catch {}
  };

  const enviarReaccionComentario = async (comentarioId, tipo) => {
    if (!hasPermission("reaccionar") || !estaAuth) { openModal("like"); return; }
    try {
      if (tipo === null) {
        const existente = (reaccsComent[comentarioId] || []).find(r => r.usuario === usuarioId);
        if (existente) await axios.delete(`${API_BASE_URL}/reacciones/${existente.id}/`);
      } else {
        const anterior = (reaccsComent[comentarioId] || []).find(r => r.usuario === usuarioId);
        if (anterior && anterior.tipo !== tipo) await axios.delete(`${API_BASE_URL}/reacciones/${anterior.id}/`);
        await axios.post(`${API_BASE_URL}/reacciones/`, { tipo, usuario: usuarioId, evento: null, noticia: null, comentario: comentarioId });
      }
      const { data } = await axios.get(`${API_BASE_URL}/reacciones/?comentario=${comentarioId}`);
      setReaccsComent(prev => ({ ...prev, [comentarioId]: data }));
    } catch {}
  };

  const enviarComentario = async (e) => {
    e.preventDefault();
    if (!hasPermission("comentar") || !estaAuth) { openModal("comentario"); return; }
    if (!checkRate()) { alert("Límite de comentarios alcanzado. Espera un momento."); return; }
    const texto = nuevoComentario.trim();
    const v = validarComentario(texto);
    if (!v.valido) { alert(v.mensaje); return; }
    if (isSubmittingComment) return;
    setIsSubmittingComment(true);
    setRateLimit(p => ({ ...p, count: p.count + 1 }));
    try {
      await axios.post(`${API_BASE_URL}/comentarios/`, { contenido: texto, usuario: usuarioId, evento: eventoId, noticia: null, comentario_padre: null, estado: "APROBADO" });
      setNuevo("");
      await cargarComentarios();
      if (comentariosScrollRef.current) comentariosScrollRef.current.scrollTop = comentariosScrollRef.current.scrollHeight;
    } catch { alert("Error al enviar el comentario."); }
    finally { setIsSubmittingComment(false); }
  };

  const enviarRespuesta = async (padreId) => {
    if (!hasPermission("comentar") || !estaAuth) { openModal("respuesta"); return; }
    if (!checkRate()) { alert("Límite de respuestas alcanzado."); return; }
    const texto = textoRespuesta.trim();
    const v = validarComentario(texto);
    if (!v.valido) { alert(v.mensaje); return; }
    if (isSubmittingReply) return;
    setIsSubmittingReply(true);
    setRateLimit(p => ({ ...p, count: p.count + 1 }));
    try {
      await axios.post(`${API_BASE_URL}/comentarios/`, { contenido: texto, usuario: usuarioId, evento: eventoId, noticia: null, comentario_padre: padreId, estado: "APROBADO" });
      setTextoResp(""); setRespondiendoA(null);
      await cargarComentarios();
    } catch { alert("Error al enviar la respuesta."); }
    finally { setIsSubmittingReply(false); }
  };

  const eliminarComentario = async (cId, autorId) => {
    if (usuarioId !== autorId && !esAdmin) { alert("Solo el autor o un administrador pueden eliminar."); return; }
    if (!window.confirm("¿Eliminar este comentario?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/comentarios/${cId}/`);
      await cargarComentarios();
    } catch { alert("Error al eliminar el comentario."); }
  };

  const reportarComentario = (comentarioId, autorNombre) => {
    if (!estaAuth) { openModal("reporte"); return; }
    alert(`Has reportado el comentario de "${autorNombre}". Gracias por tu ayuda.`);
  };

  const iniciarEdicion  = (cId, textoActual) => setEditando(prev => ({ ...prev, [cId]: { activo: true, texto: textoActual } }));
  const cancelarEdicion = (cId) => setEditando(prev => { const n = { ...prev }; delete n[cId]; return n; });

  const guardarEdicion = async (cId) => {
    const texto = editando[cId]?.texto?.trim();
    if (!texto) return;
    const v = validarComentario(texto);
    if (!v.valido) { alert(v.mensaje); return; }
    try {
      await axios.patch(`${API_BASE_URL}/comentarios/${cId}/`, { contenido: texto });
      cancelarEdicion(cId);
      await cargarComentarios();
    } catch { alert("Error al editar el comentario."); }
  };

  const compartirEvento = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) await navigator.share({ title: evento?.titulo || "Evento", url });
      else {
        await navigator.clipboard.writeText(url);
        setCompartido(true);
        setTimeout(() => setCompartido(false), 2500);
      }
    } catch {}
  };

  const obtenerComentariosOrdenados = useMemo(() => {
    if (!comentarios.length) return [];
    const raices = comentarios.filter(c => !c.comentario_padre);
    const ordenados = [...raices];
    if (ordenComentarios === "recientes")
      ordenados.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
    else
      ordenados.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
    return ordenados;
  }, [comentarios, ordenComentarios]);

  const { imagenes, videos, principales, totalLikes, totalDislikes, userReaccion } = useMemo(() => {
    if (!evento) return { imagenes: [], videos: [], principales: [], totalLikes: 0, totalDislikes: 0, userReaccion: null };
    const multi  = evento.multimedia ? [...evento.multimedia].sort((a, b) => a.orden - b.orden) : [];
    const imgs   = multi.filter(m => m.tipo === "IMAGEN");
    const vids   = multi.filter(m => m.tipo === "VIDEO");
    const princ  = obtenerComentariosOrdenados;
    const likes  = reacciones.filter(r => r.tipo === "LIKE").length;
    const dislikes = reacciones.filter(r => r.tipo === "DISLIKE").length;
    const userReact = reacciones.find(r => r.usuario === usuarioId);
    return { imagenes: imgs, videos: vids, principales: princ, totalLikes: likes, totalDislikes: dislikes, userReaccion: userReact?.tipo || null };
  }, [evento, reacciones, comentarios, usuarioId, obtenerComentariosOrdenados]);

  const getRespuestas = useCallback((cId) => comentarios.filter(c => c.comentario_padre === cId), [comentarios]);

  const organizadorNombre = evento?.usuario?.nombre_completo || evento?.usuario_nombre || "Comunidad Campesina";
  const organizadorFoto   = evento?.usuario?.foto_perfil_url || evento?.usuario_foto || null;
  const organizadorEsAdmin = evento?.usuario?.tipo_usuario === "ADMIN";
  const organizadorInicial = organizadorNombre.charAt(0).toUpperCase();

  const accionLabel = { reaccion: "reaccionar", comentario: "comentar", respuesta: "responder", like: "interactuar", reporte: "reportar" };

  if (loading) return (
    <main className="detalle-page">
      <div className="loading-container"><div className="loading-spinner" /><p>Cargando evento…</p></div>
    </main>
  );

  if (error) return (
    <main className="detalle-page">
      <div className="error-container">
        <BsShieldLockFill className="error-icon" />
        <p>{error}</p>
        <Link to="/eventos" className="btn-volver"><FaArrowLeft /> Volver a eventos</Link>
      </div>
    </main>
  );

  if (!evento) return null;

  const tieneRelacionados = relacionados.length > 0;
  const fechaEvento = evento.fecha_evento ? new Date(evento.fecha_evento) : null;
  const ubicacion = evento.ubicacion || evento.lugar || "Lugar por confirmar";
  const capacidad = evento.cupo_maximo || evento.capacidad || null;

  const renderComentario = (c, esRespuesta = false) => {
    const nombre         = c.usuario_nombre || c.usuario_data?.nombre_completo || "Usuario";
    const foto           = c.usuario_foto   || c.usuario_data?.foto_perfil_url  || null;
    const inicial        = (c.usuario_iniciales || nombre.charAt(0)).toUpperCase();
    const esAutorC       = usuarioId === c.usuario;
    const esAutorEvento  = c.usuario === evento?.usuario?.id;
    const rcComent       = reaccsComent[c.id] || [];
    const enEdicion      = editando[c.id]?.activo;
    const puedeEditar    = esAutorC && !esRespuesta;
    const puedeEliminar  = esAutorC || esAdmin;
    const puedeReportar  = estaAuth && !esAutorC;
    const tiempoRelativo = formatRelativeTime(c.fecha);

    return (
      <div key={c.id} className={`comentario-item${esRespuesta ? " es-respuesta" : ""}`}>
        <div className="comentario-avatar">
          <Avatar foto={foto} inicial={inicial} size={esRespuesta ? 32 : 40} />
        </div>
        <div className="comentario-contenido">
          <div className="comentario-header-meta">
            <div className="comentario-nombre-fila">
              <span className="comentario-nombre">{nombre}</span>
              {esAutorEvento && <span className="autor-badge"><BsFillPatchCheckFill /> Organizador</span>}
              {esAdmin && c.usuario === usuarioId && !esAutorEvento && (
                <span className="admin-badge"><MdAdminPanelSettings /> Admin</span>
              )}
              <span className="comentario-fecha">{tiempoRelativo}</span>
            </div>
            <MenuComentario
              puedeEditar={puedeEditar}
              puedeEliminar={puedeEliminar}
              puedeReportar={puedeReportar}
              onEditar={() => iniciarEdicion(c.id, c.contenido)}
              onEliminar={() => eliminarComentario(c.id, c.usuario)}
              onReportar={() => reportarComentario(c.id, nombre)}
              estaAuth={estaAuth}
              onAbrirModal={openModal}
            />
          </div>
          {enEdicion ? (
            <div className="edicion-inline">
              <textarea className="edicion-textarea" value={editando[c.id].texto} onChange={e => setEditando(prev => ({ ...prev, [c.id]: { ...prev[c.id], texto: e.target.value } }))} maxLength={MAX_COMMENT_LENGTH} autoFocus rows={3} />
              <div className="edicion-botones">
                <button className="btn-cancelar" onClick={() => cancelarEdicion(c.id)}><FaTimes /> Cancelar</button>
                <button className="btn-guardar"  onClick={() => guardarEdicion(c.id)} disabled={!editando[c.id]?.texto?.trim()}><FaCheck /> Guardar</button>
              </div>
            </div>
          ) : (
            <div className="comentario-texto">{c.contenido}</div>
          )}
          {!enEdicion && (
            <div className="comentario-acciones">
              <ComentarioReacciones
                comentarioId={c.id}
                reaccionesLista={rcComent}
                estaAuth={estaAuth}
                onReaccionar={enviarReaccionComentario}
                onAbrirModal={openModal}
                usuarioActualId={usuarioId}
              />
              {estaAuth && !esRespuesta && (
                <button className="comentario-responder-btn" onClick={() => setRespondiendoA(respondiendoA === c.id ? null : c.id)}>
                  <FaReply /> Responder
                </button>
              )}
            </div>
          )}
          {respondiendoA === c.id && estaAuth && !esRespuesta && (
            <div className="respuesta-input-wrapper">
              <div className="comentario-avatar small"><Avatar foto={userActual?.foto_perfil} inicial={(userActual?.nombres || "U").charAt(0).toUpperCase()} size={32} /></div>
              <div className="respuesta-form">
                <input type="text" value={textoRespuesta} onChange={e => setTextoResp(e.target.value)} placeholder={`Responder a ${nombre}…`} maxLength={MAX_COMMENT_LENGTH} autoFocus />
                <div className="respuesta-buttons">
                  <button className="btn-cancelar" onClick={() => { setRespondiendoA(null); setTextoResp(""); }}><FaTimes /> Cancelar</button>
                  <button className="btn-responder" onClick={() => enviarRespuesta(c.id)} disabled={!textoRespuesta.trim() || isSubmittingReply}><RiSendPlaneFill /> Responder</button>
                </div>
              </div>
            </div>
          )}
          {!esRespuesta && (() => {
            const respuestas = getRespuestas(c.id);
            if (!respuestas.length) return null;
            return (
              <div className="respuestas-seccion">
                <button className="ver-respuestas-btn" onClick={() => setRespuestasVis(p => ({ ...p, [c.id]: !p[c.id] }))}>
                  <FaReply />
                  {respuestasVis[c.id] ? `Ocultar respuestas (${respuestas.length})` : `Ver ${respuestas.length} respuesta${respuestas.length !== 1 ? "s" : ""}`}
                </button>
                {respuestasVis[c.id] && (
                  <div className="respuestas-lista">
                    {respuestas.map(r => renderComentario(r, true))}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      </div>
    );
  };

  return (
    <main className="detalle-page">
      {modal.show && (
        <div className="modal-auth" onClick={closeModal}>
          <div className="modal-auth-content" onClick={e => e.stopPropagation()}>
            <button className="modal-auth-close" onClick={closeModal}><FaTimes /></button>
            <div className="modal-auth-icon"><FaLock /></div>
            <h3>Acceso Restringido</h3>
            <p>Para <strong>{accionLabel[modal.accion] || "interactuar"}</strong> necesitas iniciar sesión.</p>
            <div className="modal-auth-buttons">
              <button className="modal-btn-login"    onClick={() => navigate("/login")}    ><FaSignInAlt /> Iniciar Sesión</button>
              <button className="modal-btn-register" onClick={() => navigate("/registro")} ><FaUserPlus /> Registrarme</button>
            </div>
          </div>
        </div>
      )}

      <div className="detalle-header">
        <Link to="/eventos" className="btn-volver"><FaArrowLeft /> Volver</Link>
        <div className={`usuario-indicador ${estaAuth ? "autenticado" : "invitado"}`}>
          {estaAuth ? <FaUserCheck /> : <FaUserCircle />}
          <span>
            {userActual
              ? <>Conectado como: <strong>{userActual.nombres || userActual.email || "Usuario"}</strong></>
              : <>Modo invitado — <Link to="/login">Inicia sesión</Link></>}
          </span>
        </div>
      </div>

      <div className={`detalle-layout-full${tieneRelacionados ? " two-columns" : ""}`}>
        <div className="detalle-contenido-principal">
          <div className="noticia-card">
            <GaleriaMedia imagenes={imagenes} videos={videos} titulo={evento.titulo} />
            <h1 className="yt-titulo">{evento.titulo}</h1>

            {/* Información adicional del evento */}
            <div className="evento-info-adicional">
              {fechaEvento && (
                <div className="evento-info-item">
                  <FaCalendarAlt /> <strong>Fecha:</strong> {formatFecha(evento.fecha_evento)} {evento.hora_evento && `a las ${evento.hora_evento}`}
                </div>
              )}
              {ubicacion && (
                <div className="evento-info-item">
                  <FaMapMarkerAlt /> <strong>Ubicación:</strong> {ubicacion}
                </div>
              )}
              {capacidad && (
                <div className="evento-info-item">
                  <FaUsers /> <strong>Cupo:</strong> {capacidad} personas
                </div>
              )}
            </div>

            <div className="yt-acciones-bar">
              <div className="yt-canal-info">
                <div className="yt-canal-avatar">
                  <Avatar foto={organizadorFoto} inicial={organizadorInicial} size={40} bg="#e0e0e0" />
                  {organizadorEsAdmin && <span className="yt-canal-badge"><MdAdminPanelSettings /></span>}
                </div>
                <div className="yt-canal-texto">
                  <div className="yt-canal-nombre">
                    {organizadorNombre}
                    {organizadorEsAdmin && <MdVerified className="yt-verificado" />}
                  </div>
                  <div className="yt-canal-sub">
                    {evento.categoria_nombre && <span className="yt-categoria-chip">{evento.categoria_nombre}</span>}
                    <span className="yt-canal-fecha"><FaRegClock /> {formatFecha(evento.fecha_creacion)}</span>
                  </div>
                </div>
              </div>

              <div className="yt-acciones-botones">
                <div className="yt-like-group">
                  <button
                    className={`yt-like-btn ${userReaccion === "LIKE" ? "activo" : ""}`}
                    onClick={() => enviarReaccion(userReaccion === "LIKE" ? null : "LIKE")}
                    title="Me gusta"
                  >
                    {userReaccion === "LIKE" ? <AiFillLike /> : <AiOutlineLike />}
                    <span>{totalLikes > 0 ? totalLikes : "Me gusta"}</span>
                  </button>
                  <div className="yt-divider-v" />
                  <button
                    className={`yt-dislike-btn ${userReaccion === "DISLIKE" ? "activo" : ""}`}
                    onClick={() => { if (!estaAuth) { openModal("reaccion"); return; } enviarReaccion(userReaccion === "DISLIKE" ? null : "DISLIKE"); }}
                    title="No me gusta"
                  >
                    {userReaccion === "DISLIKE" ? <AiFillDislike /> : <AiOutlineDislike />}
                    {totalDislikes > 0 && <span>{totalDislikes}</span>}
                  </button>
                </div>

                <button className={`yt-btn yt-share-btn ${compartido ? "copiado" : ""}`} onClick={compartirEvento} title="Compartir">
                  <RiShareForwardLine /><span>{compartido ? "¡Copiado!" : "Compartir"}</span>
                </button>
                <button className="yt-btn" title="Guardar"><FaBookmark /><span>Guardar</span></button>
                <button className="yt-btn yt-mas-btn" title="Más opciones"><FaEllipsisH /></button>
              </div>
            </div>

            <div className={`yt-desc-box ${descExpanded ? "expandida" : ""}`}>
              <div className="yt-desc-meta-row">
                {evento.vistas && <span className="yt-desc-views"><FaEye /> {evento.vistas} visualizaciones</span>}
                <span className="yt-desc-fecha">Publicado: {formatFecha(evento.fecha_creacion)}</span>
              </div>
              <div className="yt-desc-contenido">
                <p>{evento.descripcion || evento.contenido}</p>
              </div>
              <button className="yt-desc-toggle" onClick={() => setDescExpanded(!descExpanded)}>
                {descExpanded ? "mostrar menos" : "mostrar más"}
              </button>
            </div>
          </div>

          <div className="comentarios-facebook">
            <div className="comentarios-header">
              <h3>{principales.length} comentarios</h3>
              <div className="orden-comentarios-container" ref={menuOrdenRef}>
                <button className="yt-ordenar-btn" onClick={() => setMostrarMenuOrden(!mostrarMenuOrden)}>
                  <HiOutlineChatBubbleLeftRight /> Ordenar por
                </button>
                {mostrarMenuOrden && (
                  <div className="dropdown-menu-orden">
                    <button className={ordenComentarios === "recientes" ? "active" : ""} onClick={() => { setOrdenComentarios("recientes"); setMostrarMenuOrden(false); }}>Más recientes</button>
                    <button className={ordenComentarios === "antiguos" ? "active" : ""} onClick={() => { setOrdenComentarios("antiguos"); setMostrarMenuOrden(false); }}>Más antiguos</button>
                  </div>
                )}
              </div>
            </div>

            <div className="comentario-input-wrapper">
              <div className="comentario-avatar">
                {estaAuth
                  ? <Avatar foto={userActual.foto_perfil} inicial={(userActual.nombres || userActual.email || "U").charAt(0).toUpperCase()} />
                  : <FaUserCircle className="avatar-icon-default" />}
              </div>
              <form className="comentario-form" onSubmit={enviarComentario}>
                <input type="text" value={nuevoComentario} onChange={e => setNuevo(e.target.value)} placeholder={estaAuth ? "Añade un comentario…" : "Inicia sesión para comentar…"} disabled={!estaAuth} maxLength={MAX_COMMENT_LENGTH} />
                <button type="submit" disabled={!estaAuth || !nuevoComentario.trim() || isSubmittingComment} title="Enviar"><RiSendPlaneFill /></button>
              </form>
            </div>

            <div className="comentarios-tiktok-scroll" ref={comentariosScrollRef}>
              <div className="comentarios-lista">
                {principales.length === 0
                  ? <div className="sin-comentarios"><HiOutlineChatBubbleLeftRight className="sin-comentarios-icon" /><p>No hay comentarios. ¡Sé el primero!</p></div>
                  : principales.map(c => renderComentario(c, false))
                }
              </div>
            </div>
          </div>
        </div>

        {tieneRelacionados && (
          <div className="detalle-sidebar">
            <EventosRelacionados eventos={relacionados} />
          </div>
        )}
      </div>
    </main>
  );
}

export default DetalleEvento;
