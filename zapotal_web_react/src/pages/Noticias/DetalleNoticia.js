import React, { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

import {
  FaThumbsUp,
  FaHeart,
  FaArrowLeft,
  FaMicrophoneAlt,
  FaPlay,
  FaPause,
  FaStop,
  FaVolumeUp,
  FaCalendarAlt,
  FaRegComments,
  FaPaperPlane,
  FaImage,
  FaVideo,
  FaInfoCircle,
} from "react-icons/fa";

import { BsEmojiAngryFill } from "react-icons/bs";

import "./DetalleNoticia.css";

function DetalleNoticia() {
  const { id } = useParams();

  const USUARIO_ID = 2;

  const [noticia, setNoticia] = useState(null);
  const [error, setError] = useState("");
  const [reacciones, setReacciones] = useState([]);
  const [comentarios, setComentarios] = useState([]);
  const [nuevoComentario, setNuevoComentario] = useState("");

  const [leyendo, setLeyendo] = useState(false);
  const [pausado, setPausado] = useState(false);
  const [progreso, setProgreso] = useState(0);

  const utteranceRef = useRef(null);

  const obtenerMejorVoz = () => {
    const voces = window.speechSynthesis.getVoices();

    const prioridad = [
      "Microsoft Jorge Online (Natural) - Spanish (Mexico)",
      "Microsoft Alvaro Online (Natural) - Spanish (Spain)",
      "Microsoft Alonso Online (Natural) - Spanish (Spain)",
      "Microsoft Dario Online (Natural) - Spanish (Mexico)",
      "Google español de Estados Unidos",
      "Google español",
      "Microsoft Sabina Desktop - Spanish (Mexico)",
      "Paulina",
      "Monica",
    ];

    for (const nombre of prioridad) {
      const encontrada = voces.find(
        (v) => v.name.toLowerCase() === nombre.toLowerCase()
      );

      if (encontrada) return encontrada;
    }

    return voces.find((v) => v.lang.startsWith("es")) || null;
  };

  const construirBloques = (contenido) => {
    const oraciones = contenido
      .split(/(?<=[.!?])\s+/)
      .filter((o) => o.trim().length > 0);

    const total = oraciones.length;

    return oraciones.map((oracion, i) => {
      if (i < 2) return { texto: oracion, rate: 0.82, pitch: 0.78 };
      if (i >= total - 2) return { texto: oracion, rate: 0.88, pitch: 1.0 };
      if (oracion.includes("!")) return { texto: oracion, rate: 0.95, pitch: 1.15 };
      if (oracion.includes("?")) return { texto: oracion, rate: 0.9, pitch: 1.1 };
      if (oracion.length > 120) return { texto: oracion, rate: 0.84, pitch: 0.9 };

      return { texto: oracion, rate: 0.88, pitch: 0.95 };
    });
  };

  const limpiarEstadoLector = () => {
    const lector = document.querySelector(".lector-voz");
    if (lector) lector.classList.remove("activo", "hablando");
  };

  const leerBloques = (bloques, indice, voz) => {
    if (indice >= bloques.length) {
      setLeyendo(false);
      setPausado(false);
      setProgreso(100);
      limpiarEstadoLector();
      return;
    }

    const bloque = bloques[indice];
    const utterance = new SpeechSynthesisUtterance(bloque.texto);

    if (voz) utterance.voice = voz;

    utterance.lang = "es-MX";
    utterance.rate = bloque.rate;
    utterance.pitch = bloque.pitch;
    utterance.volume = 1;

    utterance.onstart = () => {
      const lector = document.querySelector(".lector-voz");
      if (lector) lector.classList.add("activo", "hablando");

      const pct = Math.round((indice / bloques.length) * 100);
      setProgreso(pct);
    };

    utterance.onboundary = () => {
      const lector = document.querySelector(".lector-voz");
      if (!lector) return;

      lector.classList.add("hablando");

      clearTimeout(window.__areosVoiceTimer);
      window.__areosVoiceTimer = setTimeout(() => {
        lector.classList.remove("hablando");
      }, 130);
    };

    utterance.onend = () => {
      setTimeout(() => {
        leerBloques(bloques, indice + 1, voz);
      }, 180);
    };

    utterance.onerror = (e) => {
      if (e.error === "interrupted") return;

      console.log("ERROR VOZ:", e.error);
      setLeyendo(false);
      setPausado(false);
      limpiarEstadoLector();
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const iniciarLectura = () => {
    if (!noticia) return;

    window.speechSynthesis.cancel();
    setProgreso(0);

    const voz = obtenerMejorVoz();

    const tituloUtterance = new SpeechSynthesisUtterance(noticia.titulo);

    if (voz) tituloUtterance.voice = voz;

    tituloUtterance.lang = "es-MX";
    tituloUtterance.rate = 0.78;
    tituloUtterance.pitch = 0.72;
    tituloUtterance.volume = 1;

    tituloUtterance.onstart = () => {
      setLeyendo(true);
      setPausado(false);

      const lector = document.querySelector(".lector-voz");
      if (lector) lector.classList.add("activo");
    };

    const bloquesCuerpo = construirBloques(noticia.contenido);

    tituloUtterance.onend = () => {
      setTimeout(() => {
        leerBloques(bloquesCuerpo, 0, voz);
      }, 400);
    };

    tituloUtterance.onerror = (e) => {
      if (e.error === "interrupted") return;

      setLeyendo(false);
      setPausado(false);
      limpiarEstadoLector();
    };

    utteranceRef.current = tituloUtterance;
    window.speechSynthesis.speak(tituloUtterance);
  };

  const pausarReanudar = () => {
    if (!leyendo) return;

    if (pausado) {
      window.speechSynthesis.resume();
      setPausado(false);
    } else {
      window.speechSynthesis.pause();
      setPausado(true);
    }
  };

  const detenerLectura = () => {
    window.speechSynthesis.cancel();
    setLeyendo(false);
    setPausado(false);
    setProgreso(0);
    limpiarEstadoLector();
  };

  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  useEffect(() => {
    const cargarVoces = () => {
      window.speechSynthesis.getVoices();
    };

    cargarVoces();
    window.speechSynthesis.onvoiceschanged = cargarVoces;
  }, []);

  useEffect(() => {
    axios
      .get(`http://localhost:8000/api/noticias/${id}/`)
      .then((res) => setNoticia(res.data))
      .catch((err) => {
        console.log(err);
        setError("No se pudo cargar la noticia.");
      });
  }, [id]);

  const cargarReacciones = () => {
    axios
      .get("http://localhost:8000/api/reacciones/")
      .then((res) => {
        const filtradas = res.data.filter(
          (reaccion) => reaccion.noticia === Number(id)
        );
        setReacciones(filtradas);
      })
      .catch((err) => console.log(err));
  };

  const cargarComentarios = () => {
    axios
      .get("http://localhost:8000/api/comentarios/")
      .then((res) => {
        const filtrados = res.data.filter(
          (comentario) => comentario.noticia === Number(id)
        );
        setComentarios(filtrados);
      })
      .catch((err) => console.log(err));
  };

  useEffect(() => {
    cargarReacciones();
    cargarComentarios();
  }, [id]);

  const reaccionar = async (tipo) => {
    try {
      const reaccionExistente = reacciones.find(
        (reaccion) => reaccion.usuario === USUARIO_ID
      );

      if (reaccionExistente) {
        await axios.patch(
          `http://localhost:8000/api/reacciones/${reaccionExistente.id}/`,
          {
            tipo,
            usuario: USUARIO_ID,
            noticia: Number(id),
            evento: null,
          }
        );
      } else {
        await axios.post("http://localhost:8000/api/reacciones/", {
          tipo,
          usuario: USUARIO_ID,
          noticia: Number(id),
          evento: null,
        });
      }

      cargarReacciones();
    } catch (err) {
      console.log(err);
    }
  };

  const enviarComentario = async (e) => {
    e.preventDefault();

    const texto = nuevoComentario.trim();

    if (!texto) {
      alert("Debes escribir un comentario.");
      return;
    }

    if (texto.length < 3) {
      alert("El comentario es demasiado corto.");
      return;
    }

    if (texto.length > 500) {
      alert("El comentario es demasiado largo.");
      return;
    }

    const palabrasProhibidas = [
      "idiota",
      "estupido",
      "estúpido",
      "imbecil",
      "imbécil",
      "tonto",
      "baboso",
      "tarado",
      "inutil",
      "inútil",
      "burro",
      "ridiculo",
      "ridículo",
      "basura",
      "asco",
      "asqueroso",
      "asquerosa",
      "patetico",
      "patético",
      "fracasado",
      "fracasada",
      "ignorante",
      "maldito",
      "desgraciado",
      "desgraciada",
      "bruto",
      "bruta",
      "cojudo",
      "cojuda",
      "huevon",
      "huevón",
      "wevon",
      "webon",
      "gil",
      "gila",
      "mierda",
      "carajo",
      "ctm",
      "ptm",
      "hdp",
      "puta",
      "puto",
      "zorra",
      "perra",
      "callate",
      "cállate",
    ];

    const textoNormalizado = texto.toLowerCase();

    const contieneGroserias = palabrasProhibidas.some((palabra) =>
      textoNormalizado.includes(palabra.toLowerCase())
    );

    const estadoComentario = contieneGroserias ? "PENDIENTE" : "APROBADO";

    try {
      await axios.post("http://localhost:8000/api/comentarios/", {
        contenido: texto,
        usuario: USUARIO_ID,
        noticia: Number(id),
        evento: null,
        comentario_padre: null,
        estado: estadoComentario,
      });

      setNuevoComentario("");
      cargarComentarios();

      if (contieneGroserias) {
        alert("Tu comentario contiene palabras ofensivas y será revisado por el administrador.");
      } else {
        alert("Comentario publicado correctamente.");
      }
    } catch (error) {
      console.error("Error al enviar comentario:", error);

      if (error.response) {
        console.log(error.response.data);
        alert("El servidor no pudo procesar el comentario.");
      } else if (error.request) {
        alert("No se pudo conectar con el servidor.");
      } else {
        alert("Ocurrió un error inesperado.");
      }
    }
  };

  if (error) {
    return (
      <main className="detalle-page">
        <p className="detalle-mensaje">{error}</p>
      </main>
    );
  }

  if (!noticia) {
    return (
      <main className="detalle-page">
        <p className="detalle-mensaje">Cargando noticia...</p>
      </main>
    );
  }

  const multimediaOrdenada = noticia.multimedia
    ? [...noticia.multimedia].sort((a, b) => a.orden - b.orden)
    : [];

  const portada = multimediaOrdenada.find((media) => media.tipo === "IMAGEN");

  const multimediaExtra = multimediaOrdenada.filter(
    (media) => media.id !== portada?.id
  );

  const totalLike = reacciones.filter((r) => r.tipo === "LIKE").length;
  const totalLove = reacciones.filter((r) => r.tipo === "LOVE").length;
  const totalEnojo = reacciones.filter((r) => r.tipo === "ENOJO").length;

  const comentariosAprobados = comentarios.filter(
    (comentario) => comentario.estado === "APROBADO"
  );

  return (
    <main className="detalle-page">
      <Link to="/noticias" className="btn-volver">
        <FaArrowLeft className="btn-volver-icon" />
        <span>Volver a noticias</span>
      </Link>

      {portada ? (
        <section className="detalle-hero">
          <img
            src={portada.archivo_url}
            alt={noticia.titulo}
            className="hero-img"
          />

          <div className="hero-overlay">
            <div className="hero-content">
              <h1>{noticia.titulo}</h1>

              <p className="hero-fecha">
                <FaCalendarAlt className="hero-fecha-icon" />
                <span>
                  Publicado el{" "}
                  {new Date(noticia.fecha_publicacion).toLocaleDateString("es-PE", {
                    day: "2-digit",
                    month: "long",
                    year: "numeric",
                  })}
                </span>
              </p>
            </div>
          </div>
        </section>
      ) : (
        <section className="detalle-titulo-simple">
          <h1>{noticia.titulo}</h1>

          <p className="detalle-fecha">
            <FaCalendarAlt className="detalle-fecha-icon" />
            <span>
              Publicado el{" "}
              {new Date(noticia.fecha_publicacion).toLocaleDateString("es-PE", {
                day: "2-digit",
                month: "long",
                year: "numeric",
              })}
            </span>
          </p>
        </section>
      )}

      <section className="lector-voz">
        <div className="lector-header">
          <div className="lector-title">
            <FaMicrophoneAlt className="lector-icono" />
            <span className="lector-label">Escuchar noticia con AREOS</span>
          </div>

          {leyendo && (
            <div className="lector-ondas" aria-hidden="true">
              <span />
              <span />
              <span />
              <span />
              <span />
            </div>
          )}
        </div>

        <div className="lector-controles">
          {!leyendo ? (
            <button
              type="button"
              className="lector-btn lector-play"
              onClick={iniciarLectura}
              title="Reproducir"
            >
              <FaPlay className="lector-btn-icon" />
              <span>Reproducir</span>
            </button>
          ) : (
            <>
              <button
                type="button"
                className="lector-btn lector-pausa"
                onClick={pausarReanudar}
                title={pausado ? "Reanudar" : "Pausar"}
              >
                {pausado ? (
                  <>
                    <FaPlay className="lector-btn-icon" />
                    <span>Reanudar</span>
                  </>
                ) : (
                  <>
                    <FaPause className="lector-btn-icon" />
                    <span>Pausar</span>
                  </>
                )}
              </button>

              <button
                type="button"
                className="lector-btn lector-stop"
                onClick={detenerLectura}
                title="Detener"
              >
                <FaStop className="lector-btn-icon" />
                <span>Detener</span>
              </button>
            </>
          )}
        </div>

        {leyendo && (
          <div className="lector-progreso-wrap">
            <div
              className="lector-progreso-barra"
              style={{ width: `${progreso}%` }}
            />
          </div>
        )}

        {leyendo && (
          <div className="lector-estado">
            {pausado ? (
              <>
                <FaPause className="lector-estado-icon" />
                <span>Pausado</span>
              </>
            ) : (
              <>
                <FaVolumeUp className="lector-estado-icon" />
                <span>Leyendo noticia...</span>
              </>
            )}
          </div>
        )}
      </section>

      <section className="detalle-contenido-section">
        <p className="detalle-contenido">{noticia.contenido}</p>
      </section>

      <section className="reacciones-facebook">
        <button
          type="button"
          className="reaccion-btn like"
          onClick={() => reaccionar("LIKE")}
        >
          <FaThumbsUp className="icono-reaccion" />
          <span className="texto-reaccion">Me gusta</span>
          <strong>{totalLike}</strong>
        </button>

        <button
          type="button"
          className="reaccion-btn love"
          onClick={() => reaccionar("LOVE")}
        >
          <FaHeart className="icono-reaccion" />
          <span className="texto-reaccion">Me encanta</span>
          <strong>{totalLove}</strong>
        </button>

        <button
          type="button"
          className="reaccion-btn enojo"
          onClick={() => reaccionar("ENOJO")}
        >
          <BsEmojiAngryFill className="icono-reaccion" />
          <span className="texto-reaccion">Me enoja</span>
          <strong>{totalEnojo}</strong>
        </button>
      </section>

      <section className="comentarios-section">
        <div className="comentarios-header">
          <FaRegComments className="comentarios-header-icon" />
          <h2>Comentarios</h2>
        </div>

        <form className="comentario-form" onSubmit={enviarComentario}>
          <textarea
            value={nuevoComentario}
            onChange={(e) => setNuevoComentario(e.target.value)}
            placeholder="Escribe un comentario..."
          />

          <button type="submit">
            <FaPaperPlane className="comentario-btn-icon" />
            <span>Comentar</span>
          </button>
        </form>

        <div className="comentarios-lista">
          {comentariosAprobados.length === 0 ? (
            <p className="sin-comentarios">
              Aún no hay comentarios publicados.
            </p>
          ) : (
            comentariosAprobados.map((comentario) => (
              <article key={comentario.id} className="comentario-card">
                <p>{comentario.contenido}</p>
              </article>
            ))
          )}
        </div>
      </section>

      {multimediaExtra.length > 0 && (
        <section className="detalle-galeria">
          <div className="galeria-header">
            <FaImage className="galeria-header-icon" />
            <h2>Galería multimedia</h2>
          </div>

          {multimediaExtra.map((media) => (
            <div key={media.id} className="detalle-media">
              {media.tipo === "IMAGEN" && (
                <img
                  src={media.archivo_url}
                  alt={noticia.titulo}
                  className="detalle-img"
                />
              )}

              {media.tipo === "VIDEO" && (
                <div className="video-box">
                  <FaVideo className="video-icon" />
                  <video className="detalle-video" controls>
                    <source src={media.archivo_url} type="video/mp4" />
                    Tu navegador no soporta videos.
                  </video>
                </div>
              )}
            </div>
          ))}
        </section>
      )}

      <div className="detalle-estado">
        <FaInfoCircle className="detalle-estado-icon" />
        <strong>Estado:</strong>
        <span>{noticia.estado}</span>
      </div>
    </main>
  );
}

export default DetalleNoticia;