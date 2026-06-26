import React, { useEffect, useState, useRef, useCallback, useMemo, memo } from "react";
import { useConfirm } from "../../components/Admin/AdminConfirmDialog";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  FaArrowLeft, FaUserCircle, FaSignInAlt, FaUserPlus,
  FaTimes, FaReply, FaTrashAlt, FaUserCheck,
  FaTags, FaNewspaper, FaRegClock, FaEye, FaLock,
  FaEllipsisV, FaPencilAlt, FaCheck,
  FaFlag, FaPlay, FaImage, FaVideo, FaChevronLeft, FaChevronRight,
} from "react-icons/fa";
import { BsShieldLockFill, BsFillPatchCheckFill } from "react-icons/bs";
import { MdAdminPanelSettings, MdVerified } from "react-icons/md";
import { AiOutlineLike, AiFillLike, AiOutlineDislike, AiFillDislike } from "react-icons/ai";
import { HiOutlineChatBubbleLeftRight } from "react-icons/hi2";
import { RiSendPlaneFill, RiShareForwardLine } from "react-icons/ri";
import api, { extractList } from "../../api";
import { useAuth } from "../../context/AuthContext";
import BotonFavorito from "../../components/BotonFavorito";
import "./DetalleNoticia.css";

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

const Avatar = memo(({ foto, inicial, size = 40, bg = "#e0e0e0" }) => {
  const varStyle = { '--avatar-size': `${size}px` };
  if (foto) return <img src={foto} alt="" className="avatar-img" style={{ ...varStyle, width: size, height: size }} />;
  return (
    <div className="avatar-inicial" style={varStyle}>
      {inicial}
    </div>
  );
});

const ComentarioReacciones = memo(({ comentarioId, reaccionesLista, estaAuth, onReaccionar, onAbrirModal, usuarioActualId }) => {
  const miReaccion   = reaccionesLista.find(r => r.autor === usuarioActualId);
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
      <button className="btn-tres-puntos" onClick={handleClick} title="Mas opciones"><FaEllipsisV /></button>
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

// ============== GALERIA MULTIMEDIA COMPLETA ==============
// Muestra: imagen principal + video principal (si hay) + galeria con todos los items multimedia.
const GaleriaMedia = memo(({ imagenPrincipal, multimedia, titulo }) => {
  const multi = multimedia || [];
  const [indice, setIndice] = useState(0);

  // Construir la lista visible: primero imagen principal (si existe), luego items multimedia.
  const items = useMemo(() => {
    const base = [];
    if (imagenPrincipal) {
      base.push({ id: "principal", kind: "IMAGEN", url: imagenPrincipal, principal: true });
    }
    const extra = multi
      .slice()
      .sort((a, b) => (a.orden || 0) - (b.orden || 0))
      .map((m, i) => ({
        id: m.id ?? `mm-${i}`,
        kind: m.tipo === "VIDEO" ? "VIDEO" : "IMAGEN",
        url: m.archivo_url || m.url,
        principal: false,
      }));
    return [...base, ...extra];
  }, [imagenPrincipal, multi]);

  if (!items.length) {
    return (
      <div className="gm-wrapper gm-wrapper--empty">
        <div className="gm-empty">
          <FaNewspaper />
          <p>Esta publicacion no tiene contenido multimedia disponible.</p>
        </div>
      </div>
    );
  }

  const actual = items[Math.min(indice, items.length - 1)];

  const irAtras = () => setIndice((i) => (i - 1 + items.length) % items.length);
  const irAdelante = () => setIndice((i) => (i + 1) % items.length);

  return (
    <div className="gm-wrapper">
      <div className="gm-hero">
        {actual.kind === "VIDEO" ? (
          <video
            key={actual.id}
            src={actual.url}
            autoPlay
            muted
            loop
            playsInline
            controls
            preload="metadata"
            className="gm-hero__video"
            poster={imagenPrincipal || ""}
            controlsList="nodownload"
          />
        ) : (
          <img
            key={actual.id}
            src={actual.url}
            alt={titulo}
            className="gm-hero__imagen"
            loading="lazy"
          />
        )}
        {actual.principal && <span className="gm-badge gm-badge--principal">Principal</span>}
        <span className="gm-badge gm-badge--kind">
          {actual.kind === "VIDEO" ? <FaVideo /> : <FaImage />}
        </span>
        {items.length > 1 && (
          <>
            <button className="gm-nav gm-nav--prev" onClick={irAtras} aria-label="Anterior"><FaChevronLeft /></button>
            <button className="gm-nav gm-nav--next" onClick={irAdelante} aria-label="Siguiente"><FaChevronRight /></button>
            <div className="gm-counter">{indice + 1} / {items.length}</div>
          </>
        )}
      </div>

      {items.length > 1 && (
        <div className="gm-thumbs">
          {items.map((it, i) => (
            <button
              key={it.id}
              className={`gm-thumb ${i === indice ? "gm-thumb--active" : ""}`}
              onClick={() => setIndice(i)}
              aria-label={`Item ${i + 1}`}
            >
              {it.kind === "VIDEO" ? (
                <span className="gm-thumb__video"><FaPlay /></span>
              ) : (
                <img src={it.url} alt="" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
});

const NoticiasRelacionadas = memo(({ noticias }) => {
  if (!noticias.length) return null;

  const obtenerPreview = (noticia) => {
    const imagen = noticia.multimedia?.find(m => m.tipo === "IMAGEN");
    const src = imagen?.archivo_url || noticia.imagen_url || noticia.miniatura;
    if (src) {
      return <img src={src} alt={noticia.titulo} onError={(e) => { e.currentTarget.src = "/images/placeholder-news.jpg"; }} />;
    }
    return (
      <div className="gm-thumb__placeholder">
        <FaNewspaper />
      </div>
    );
  };

  const tieneVideo = (noticia) => noticia.multimedia?.some(m => m.tipo === "VIDEO") || false;

  return (
    <aside className="noticias-relacionadas">
      <h4><FaNewspaper /> Noticias relacionadas</h4>
      <div className="relacionadas-lista">
        {noticias.map(noticia => (
          <Link to={`/noticias/${noticia.id}`} key={noticia.id} className="relacionada-card-horizontal">
            <div className="relacionada-miniatura">
              {obtenerPreview(noticia)}
              {tieneVideo(noticia) && (
                <span className="video-badge-horizontal"><FaPlay /></span>
              )}
            </div>
            <div className="relacionada-contenido">
              <h5 className="relacionada-titulo-horizontal">{noticia.titulo}</h5>
              <div className="relacionada-meta">
                <span className="relacionada-canal-horizontal">{noticia.categoria_nombre || "Comunidad"}</span>
                <span className="relacionada-puntos">•</span>
                {noticia.vistas != null && <span className="relacionada-views-horizontal">{noticia.vistas} vistas</span>}
                <span className="relacionada-puntos">•</span>
                <span className="relacionada-fecha-horizontal">{formatFecha(noticia.fecha_publicacion)}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </aside>
  );
});

function DetalleNoticia() {
  const { id }   = useParams();
  const navigate = useNavigate();
  const { confirm, ConfirmDialog } = useConfirm();

  const noticiaId = useMemo(() => {
    const parsed = Number(id);
    if (isNaN(parsed) || parsed <= 0) { navigate("/noticias"); return null; }
    return parsed;
  }, [id, navigate]);

  const { user: userActual, isAuthenticated: estaAuth, isAdmin: esAdminCtx } = useAuth();
  const esAdmin   = !!esAdminCtx || userActual?.tipo_usuario === "ADMIN" || userActual?.is_superuser === true;
  const usuarioId = userActual?.id;

  const [noticia,             setNoticia]            = useState(null);
  const [error,               setError]              = useState("");
  const [loading,             setLoading]            = useState(true);
  const [reacciones,          setReacciones]         = useState([]);
  const [reaccsComent,        setReaccsComent]       = useState({});
  const [comentarios,         setComentarios]        = useState([]);
  const [nuevoComentario,     setNuevo]              = useState("");
  const [respondiendoA,       setRespondiendoA]      = useState(null);
  const [textoRespuesta,      setTextoResp]          = useState("");
  const [respuestasVis,       setRespuestasVis]      = useState({});
  const [modal,               setModal]              = useState({ show: false, accion: null });
  const [rateLimit,           setRateLimit]          = useState({ count: 0, lastReset: Date.now() });
  const [isSubmittingComment, setIsSubmittingComment]= useState(false);
  const [isSubmittingReply,   setIsSubmittingReply]  = useState(false);
  const [relacionadas,        setRelacionadas]       = useState([]);
  const [compartido,          setCompartido]         = useState(false);
  const [descExpanded,        setDescExpanded]       = useState(false);
  const [editando,            setEditando]           = useState({});
  const [ordenComentarios,    setOrdenComentarios]   = useState("recientes");
  const [mostrarMenuOrden,    setMostrarMenuOrden]   = useState(false);

  const menuOrdenRef         = useRef(null);
  const timeoutRef           = useRef(null);
  const comentariosScrollRef = useRef(null);

  useEffect(() => () => { if (timeoutRef.current) clearTimeout(timeoutRef.current); }, []);

  // Cargar noticia
  useEffect(() => {
    if (!noticiaId) return;
    (async () => {
      try {
        const { data } = await api.get(`/noticias/${noticiaId}/`);
        setNoticia(data);
      } catch (err) {
        setError(err.response?.status === 404 ? "La noticia no existe o fue eliminada." : "No se pudo cargar la noticia.");
      } finally { setLoading(false); }
    })();
  }, [noticiaId]);

  // Contador de vistas (endpoint dedicado, una vez por usuario/sesion)
  useEffect(() => {
    if (!noticiaId || !noticia) return;
    const claveLocal = estaAuth && usuarioId
      ? `visto_noticia_${noticiaId}_user_${usuarioId}`
      : `visto_noticia_${noticiaId}_session`;
    const storage = (typeof window !== "undefined")
      ? (estaAuth && usuarioId ? window.localStorage : window.sessionStorage)
      : null;
    if (storage && !storage.getItem(claveLocal)) {
      api.post(`/noticias/${noticiaId}/incrementar_vistas/`)
        .then(({ data }) => {
          setNoticia((prev) => prev ? { ...prev, vistas: data.vistas } : prev);
          try { storage.setItem(claveLocal, new Date().toISOString()); } catch (e) { /* noop */ }
        })
        .catch(err => console.warn("Error al incrementar vistas:", err));
    }
  }, [noticiaId, noticia, estaAuth, usuarioId]);

  // Cargar relacionadas
  useEffect(() => {
    if (!noticiaId) return;
    api.get(`/noticias/${noticiaId}/relacionadas/`)
      .then(res => setRelacionadas(res.data))
      .catch(() => setRelacionadas([]));
  }, [noticiaId]);

  const cargarReacciones = useCallback(() => {
    if (!noticiaId) return Promise.resolve();
    return api.get(`/reacciones/?noticia=${noticiaId}`)
      .then(({ data }) => setReacciones(extractList(data))).catch(() => {});
  }, [noticiaId]);

  const cargarReaccionesComentarios = useCallback(async (lista) => {
    if (!lista.length) return;
    const resultados = await Promise.all(
      lista.map(com =>
        api.get(`/reacciones/?comentario=${com.id}`)
          .then(res => ({ id: com.id, data: extractList(res.data) }))
          .catch(() => ({ id: com.id, data: [] }))
      )
    );
    const nuevoMap = {};
    resultados.forEach(({ id, data }) => { nuevoMap[id] = data; });
    setReaccsComent(prev => ({ ...prev, ...nuevoMap }));
  }, []);

  const cargarComentarios = useCallback(() => {
    if (!noticiaId) return Promise.resolve();
    return api.get(`/comentarios/?noticia=${noticiaId}`)
      .then(async ({ data }) => {
        const visibles = extractList(data).filter(c => c.estado !== "ELIMINADO");
        setComentarios(visibles);
        await cargarReaccionesComentarios(visibles);
      }).catch(() => {});
  }, [noticiaId, cargarReaccionesComentarios]);

  useEffect(() => {
    if (noticiaId) { cargarReacciones(); cargarComentarios(); }
  }, [noticiaId, cargarReacciones, cargarComentarios]);

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
        const existente = reacciones.find(r => r.autor === usuarioId);
        if (existente) await api.delete(`/reacciones/${existente.id}/`);
      } else {
        const anterior = reacciones.find(r => r.autor === usuarioId);
        if (anterior && anterior.tipo !== tipo) {
          await api.delete(`/reacciones/${anterior.id}/`);
        }
        if (!anterior || anterior.tipo !== tipo) {
          await api.post(`/reacciones/`, { tipo, noticia: noticiaId });
        }
      }
      cargarReacciones();
    } catch {}
  };

  const enviarReaccionComentario = async (comentarioId, tipo) => {
    if (!hasPermission("reaccionar") || !estaAuth) { openModal("like"); return; }
    try {
      if (tipo === null) {
        const existente = (reaccsComent[comentarioId] || []).find(r => r.autor === usuarioId);
        if (existente) await api.delete(`/reacciones/${existente.id}/`);
      } else {
        const anterior = (reaccsComent[comentarioId] || []).find(r => r.autor === usuarioId);
        if (anterior && anterior.tipo !== tipo) {
          await api.delete(`/reacciones/${anterior.id}/`);
        }
        if (!anterior || anterior.tipo !== tipo) {
          await api.post(`/reacciones/`, { tipo, comentario: comentarioId });
        }
      }
      const { data } = await api.get(`/reacciones/?comentario=${comentarioId}`);
      setReaccsComent(prev => ({ ...prev, [comentarioId]: extractList(data) }));
    } catch {}
  };

  const enviarComentario = async (e) => {
    e.preventDefault();
    if (!hasPermission("comentar") || !estaAuth) { openModal("comentario"); return; }
    if (!checkRate()) { alert("Limite de comentarios alcanzado. Espera un momento."); return; }
    const texto = nuevoComentario.trim();
    const v = validarComentario(texto);
    if (!v.valido) { alert(v.mensaje); return; }
    if (isSubmittingComment) return;
    setIsSubmittingComment(true);
    setRateLimit(p => ({ ...p, count: p.count + 1 }));
    try {
      await api.post(`/comentarios/`, {
        contenido: texto,
        noticia: noticiaId,
        evento: null,
        respuesta_a: null,
        estado: "PUBLICADO",
      });
      setNuevo("");
      await cargarComentarios();
      if (comentariosScrollRef.current) comentariosScrollRef.current.scrollTop = comentariosScrollRef.current.scrollHeight;
    } catch (err) {
      const d = err.response?.data;
      const msg = (d && (d.detail || d.mensaje)) || "Error al enviar el comentario.";
      alert(typeof msg === "string" ? msg : "Error al enviar el comentario.");
    }
    finally { setIsSubmittingComment(false); }
  };

  const enviarRespuesta = async (padreId) => {
    if (!hasPermission("comentar") || !estaAuth) { openModal("respuesta"); return; }
    if (!checkRate()) { alert("Limite de respuestas alcanzado."); return; }
    const texto = textoRespuesta.trim();
    const v = validarComentario(texto);
    if (!v.valido) { alert(v.mensaje); return; }
    if (isSubmittingReply) return;
    setIsSubmittingReply(true);
    setRateLimit(p => ({ ...p, count: p.count + 1 }));
    try {
      await api.post(`/comentarios/`, {
        contenido: texto,
        noticia: noticiaId,
        evento: null,
        respuesta_a: padreId,
        estado: "PUBLICADO",
      });
      setTextoResp(""); setRespondiendoA(null);
      await cargarComentarios();
    } catch { alert("Error al enviar la respuesta."); }
    finally { setIsSubmittingReply(false); }
  };

  const eliminarComentario = async (cId, autorId) => {
    if (usuarioId !== autorId && !esAdmin) { alert("Solo el autor o un administrador pueden eliminar."); return; }
    if (!await confirm({
      title: "Eliminar comentario",
      message: "¿Eliminar este comentario? Esta acción no se puede deshacer.",
    })) return;
    try {
      await api.delete(`/comentarios/${cId}/`);
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
      await api.patch(`/comentarios/${cId}/`, { contenido: texto });
      cancelarEdicion(cId);
      await cargarComentarios();
    } catch { alert("Error al editar el comentario."); }
  };

  const compartirNoticia = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) await navigator.share({ title: noticia?.titulo || "Noticia", url });
      else {
        await navigator.clipboard.writeText(url);
        setCompartido(true);
        setTimeout(() => setCompartido(false), 2500);
      }
    } catch {}
  };

  const obtenerComentariosOrdenados = useMemo(() => {
    if (!comentarios.length) return [];
    const raices = comentarios.filter(c => !c.respuesta_a);
    const ordenados = [...raices];
    if (ordenComentarios === "recientes")
      ordenados.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
    else
      ordenados.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
    return ordenados;
  }, [comentarios, ordenComentarios]);

  const { multimedia, principales, totalLikes, totalDislikes, userReaccion, imagenPrincipal } = useMemo(() => {
    if (!noticia) return { multimedia: [], principales: [], totalLikes: 0, totalDislikes: 0, userReaccion: null, imagenPrincipal: null };
    const multi  = (noticia.multimedia || []).slice();
    const princ  = obtenerComentariosOrdenados;
    const likes  = reacciones.filter(r => r.tipo === "LIKE").length;
    const dislikes = reacciones.filter(r => r.tipo === "DISLIKE").length;
    const userReact = reacciones.find(r => r.autor === usuarioId);
    return {
      multimedia: multi,
      principales: princ,
      totalLikes: likes,
      totalDislikes: dislikes,
      userReaccion: userReact?.tipo || null,
      imagenPrincipal: noticia.imagen_url || null,
    };
  }, [noticia, reacciones, comentarios, usuarioId, obtenerComentariosOrdenados]);

  const getRespuestas = useCallback((cId) => comentarios.filter(c => c.respuesta_a === cId), [comentarios]);

  const autorNombre  = noticia?.usuario?.nombre_completo || noticia?.usuario_nombre || "Comunidad Campesina";
  const autorFoto    = noticia?.usuario?.foto_perfil_url || noticia?.usuario_foto || null;
  const autorEsAdmin = noticia?.usuario?.tipo_usuario === "ADMIN";
  const autorInicial = autorNombre.charAt(0).toUpperCase();

  const accionLabel = { reaccion: "reaccionar", comentario: "comentar", respuesta: "responder", like: "interactuar", reporte: "reportar" };

  if (loading) return (
    <main className="detalle-page">
      <div className="loading-container"><div className="loading-spinner" /><p>Cargando noticia…</p></div>
    </main>
  );

  if (error) return (
    <main className="detalle-page">
      <div className="error-container">
        <BsShieldLockFill className="error-icon" />
        <p>{error}</p>
        <Link to="/noticias" className="btn-volver"><FaArrowLeft /> Volver a noticias</Link>
      </div>
    </main>
  );

  if (!noticia) return null;

  const tieneRelacionadas = relacionadas.length > 0;

  const renderComentario = (c, esRespuesta = false) => {
    const nombre         = c.autor_nombre || c.autor?.email || c.usuario_nombre || c.usuario_data?.nombre_completo || "Usuario";
    const foto           = c.autor_foto   || c.usuario_foto  || c.usuario_data?.foto_perfil_url || null;
    const inicial        = (c.usuario_iniciales || nombre.charAt(0)).toUpperCase();
    const esAutorC       = usuarioId === c.autor;
    const esAutorNoticia = c.autor === noticia?.usuario?.id;
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
              {esAutorNoticia && <span className="autor-badge"><BsFillPatchCheckFill /> Autor</span>}
              {esAdmin && c.autor === usuarioId && !esAutorNoticia && (
                <span className="admin-badge"><MdAdminPanelSettings /> Admin</span>
              )}
              <span className="comentario-fecha">{tiempoRelativo}</span>
            </div>
            <MenuComentario
              puedeEditar={puedeEditar}
              puedeEliminar={puedeEliminar}
              puedeReportar={puedeReportar}
              onEditar={() => iniciarEdicion(c.id, c.contenido)}
              onEliminar={() => eliminarComentario(c.id, c.autor)}
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
            <p>Para <strong>{accionLabel[modal.accion] || "interactuar"}</strong> necesitas iniciar sesion.</p>
            <div className="modal-auth-buttons">
              <button className="modal-btn-login"    onClick={() => navigate("/login")}    ><FaSignInAlt /> Iniciar Sesion</button>
              <button className="modal-btn-register" onClick={() => navigate("/registro")} ><FaUserPlus /> Registrarme</button>
            </div>
          </div>
        </div>
      )}

      <div className="detalle-header">
        <Link to="/noticias" className="btn-volver"><FaArrowLeft /> Volver</Link>
        <div className={`usuario-indicador ${estaAuth ? "autenticado" : "invitado"}`}>
          {estaAuth ? <FaUserCheck /> : <FaUserCircle />}
          <span>
            {userActual
              ? <>Conectado como: <strong>{userActual.nombres || userActual.email || "Usuario"}</strong></>
              : <>Modo invitado — <Link to="/login">Inicia sesion</Link></>}
          </span>
        </div>
      </div>

      <div className={`detalle-layout-full${tieneRelacionadas ? " two-columns" : ""}`}>
        <div className="detalle-contenido-principal">
          <div className="noticia-card">
            <GaleriaMedia
              imagenPrincipal={imagenPrincipal}
              multimedia={multimedia}
              titulo={noticia.titulo}
            />
            <h1 className="yt-titulo">{noticia.titulo}</h1>

            <div className="yt-acciones-bar">
              <div className="yt-canal-info">
                <div className="yt-canal-avatar">
                  <Avatar foto={autorFoto} inicial={autorInicial} size={40} bg="#e0e0e0" />
                  {autorEsAdmin && <span className="yt-canal-badge"><MdAdminPanelSettings /></span>}
                </div>
                <div className="yt-canal-texto">
                  <div className="yt-canal-nombre">
                    {autorNombre}
                    {autorEsAdmin && <MdVerified className="yt-verificado" />}
                  </div>
                  <div className="yt-canal-sub">
                    {noticia.categoria_nombre && <span className="yt-categoria-chip">{noticia.categoria_nombre}</span>}
                    <span className="yt-canal-fecha"><FaRegClock /> {formatFecha(noticia.fecha_publicacion)}</span>
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

                <button className={`yt-btn yt-share-btn ${compartido ? "copiado" : ""}`} onClick={compartirNoticia} title="Compartir">
                  <RiShareForwardLine /><span>{compartido ? "¡Copiado!" : "Compartir"}</span>
                </button>

                <BotonFavorito tipo="NOTICIA" itemId={noticiaId} />
              </div>
            </div>

            <div className={`yt-desc-box ${descExpanded ? "expandida" : ""}`}>
              <div className="yt-desc-meta-row">
                {noticia.vistas != null && <span className="yt-desc-views"><FaEye /> {noticia.vistas} visualizaciones</span>}
                <span className="yt-desc-fecha">{formatFecha(noticia.fecha_publicacion)}</span>
              </div>
              <div className="yt-desc-contenido">
                <p>{noticia.contenido}</p>
              </div>
              <button className="yt-desc-toggle" onClick={() => setDescExpanded(!descExpanded)}>
                {descExpanded ? "mostrar menos" : "mostrar mas"}
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
                    <button className={ordenComentarios === "recientes" ? "active" : ""} onClick={() => { setOrdenComentarios("recientes"); setMostrarMenuOrden(false); }}>Mas recientes</button>
                    <button className={ordenComentarios === "antiguos" ? "active" : ""} onClick={() => { setOrdenComentarios("antiguos"); setMostrarMenuOrden(false); }}>Mas antiguos</button>
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
                <input type="text" value={nuevoComentario} onChange={e => setNuevo(e.target.value)} placeholder={estaAuth ? "Añade un comentario…" : "Inicia sesion para comentar…"} disabled={!estaAuth} maxLength={MAX_COMMENT_LENGTH} />
                <button type="submit" disabled={!estaAuth || !nuevoComentario.trim() || isSubmittingComment} title="Enviar"><RiSendPlaneFill /></button>
              </form>
            </div>

            <div className="comentarios-tiktok-scroll" ref={comentariosScrollRef}>
              <div className="comentarios-lista">
                {principales.length === 0
                  ? <div className="sin-comentarios"><HiOutlineChatBubbleLeftRight className="sin-comentarios-icon" /><p>No hay comentarios. ¡Se el primero!</p></div>
                  : principales.map(c => renderComentario(c, false))
                }
              </div>
            </div>
          </div>
        </div>

        {tieneRelacionadas && (
          <div className="detalle-sidebar">
            <NoticiasRelacionadas noticias={relacionadas} />
          </div>
        )}
      </div>
    {ConfirmDialog}
    </main>
  );
}

export default DetalleNoticia;
