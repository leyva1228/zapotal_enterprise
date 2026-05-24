import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

import { FaThumbsUp, FaHeart } from "react-icons/fa";
import { BsEmojiAngryFill } from "react-icons/bs";

import "./DetalleNoticia.css";

function DetalleNoticia() {

  const { id } = useParams();

  const USUARIO_ID = 2;

  const [noticia, setNoticia] = useState(null);

  const [error, setError] = useState("");

  const [reacciones, setReacciones] = useState([]);

  const [comentarios, setComentarios] = useState([]);

  const [nuevoComentario, setNuevoComentario] =
    useState("");

  /* =========================
     CARGAR NOTICIA
  ========================= */

  useEffect(() => {

    axios
      .get(
        `http://localhost:8000/api/noticias/${id}/`
      )

      .then((res) => {

        setNoticia(res.data);

      })

      .catch((err) => {

        console.log(err);

        setError(
          "No se pudo cargar la noticia."
        );

      });

  }, [id]);

  /* =========================
     CARGAR REACCIONES
  ========================= */

  const cargarReacciones = () => {

    axios
      .get(
        "http://localhost:8000/api/reacciones/"
      )

      .then((res) => {

        const filtradas =
          res.data.filter(
            (reaccion) =>
              reaccion.noticia === Number(id)
          );

        setReacciones(filtradas);

      })

      .catch((err) => {

        console.log(err);

      });
  };

  /* =========================
     CARGAR COMENTARIOS
  ========================= */

  const cargarComentarios = () => {

    axios
      .get(
        "http://localhost:8000/api/comentarios/"
      )

      .then((res) => {

        const filtrados =
          res.data.filter(
            (comentario) =>
              comentario.noticia === Number(id)
          );

        setComentarios(filtrados);

      })

      .catch((err) => {

        console.log(err);

      });
  };

  useEffect(() => {

    cargarReacciones();

    cargarComentarios();

  }, [id]);

  /* =========================
     REACCIONAR
  ========================= */

  const reaccionar = async (tipo) => {

    try {

      const reaccionExistente =
        reacciones.find(
          (reaccion) =>
            reaccion.usuario === USUARIO_ID
        );

      if (reaccionExistente) {

        await axios.patch(
          `http://localhost:8000/api/reacciones/${reaccionExistente.id}/`,
          {
            tipo: tipo,
            usuario: USUARIO_ID,
            noticia: Number(id),
            evento: null,
          }
        );

      } else {

        await axios.post(
          "http://localhost:8000/api/reacciones/",
          {
            tipo: tipo,
            usuario: USUARIO_ID,
            noticia: Number(id),
            evento: null,
          }
        );
      }

      cargarReacciones();

    } catch (err) {

      console.log(err);

    }
  };

  /* =========================
     ENVIAR COMENTARIO
  ========================= */

  const enviarComentario = async (e) => {

    e.preventDefault();

    const texto =
      nuevoComentario.trim();

    /* VALIDAR VACÍO */

    if (!texto) {

      alert(
        "Debes escribir un comentario."
      );

      return;
    }

    /* VALIDAR LONGITUD */

    if (texto.length < 3) {

      alert(
        "El comentario es demasiado corto."
      );

      return;
    }

    if (texto.length > 500) {

      alert(
        "El comentario es demasiado largo."
      );

      return;
    }

    /* PALABRAS PROHIBIDAS */

    const palabrasProhibidas = [
      "gey",

      "idiota",
      "estupido",
      "idiota",
      "estupido",
      "estúpido",
      "imbecil",
      "imbécil",
      "tonto",
      "baboso",
      "tarado",
      "idiotez",
      "animal",
      "burro",
      "mongol",
      "payaso",
      "inutil",
      "inútil",
      "sonso",
      "sonsazo",
      "loco",
      "enfermo",
      "menso",
      "torpe",
      "asno",
      "bestia",
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
      "maleducado",
      "malcriado",
      "maldito",
      "malparido",
      "desgraciado",
      "desgraciada",
      "infeliz",
      "payasin",
      "babosada",
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
      "cabron",
      "cabrón",
      "cabrona",
      "mierda",
      "mierdoso",
      "mierdosa",
      "carajo",
      "caradura",
      "conchudo",
      "conchuda",
      "concha",
      "ctm",
      "ptm",
      "hdp",
      "joder",
      "jodete",
      "jódete",
      "puta",
      "puto",
      "put4",
      "putita",
      "zorra",
      "perra",
      "malnacido",
      "malnacida",
      "maldito seas",
      "maldita sea",
      "pedo",
      "apestoso",
      "apestosa",
      "sapo",
      "soplón",
      "soplon",
      "rata",
      "lacra",
      "parásito",
      "parasito",
      "estorbo",
      "feo",
      "fea",
      "horrible",
      "malogrado",
      "malogrado",
      "deficiente",
      "cretino",
      "cretina",
      "pelotudo",
      "pelotuda",
      "cagon",
      "cagón",
      "cagona",
      "cagada",
      "mocoso",
      "mocosa",
      "tarúpido",
      "tarupido",
      "idiotazo",
      "imbecilon",
      "webada",
      "huevada",
      "porqueria",
      "porquería",
      "maldito perro",
      "maldita perra",
      "idiota de mierda",
      "estupido de mierda",
      "animal de mierda",
      "gilazo",
      "mongolito",
      "mongólica",
      "mongolico",
      "babosón",
      "baboson",
      "pendejo",
      "pendeja",
      "maricon",
      "maricón",
      "marica",
      "idiota inutil",
      "bestia humana",
      "muérete",
      "muerete",
      "ojala te mueras",
      "ojalá te mueras",
      "te odio",
      "callate",
      "cállate",
      "calla",
      "maldito idiota",
      "maldita idiota",
      "idiota estupido",
      "malnacido de mierda",
      "cara de rata",
      "cara de perro",
      "baboso de mierda",
      "hijo de puta",
      "hija de puta",
      "hijo de perra",
      "hija de perra",
      "hijo del demonio",
      "demonio",
      "diablo",
      "maldito seas",
      "idiota total",
      "retardado",
      "retardada",
      "retrasado",
      "retrasada",
      "subnormal",
      "subnormalito",
      "enano idiota",
      "gordo estupido",
      "flaco estupido",
      "cara fea",
      "feo de mierda",
      "asqueroso animal",
      "porquería humana",
      "payaso estupido",
      "inservible",
      "idiota inútil",
      "idiota inutil",
      "perdedor",
      "perdedora",
      "mugroso",
      "mugrosa",
      "apestas",
      "cerebro de pollo",
      "mono",
      "simio",
      "bestia inútil",
      "estorbo humano",
      "escoria",
      "escoria humana",
      "rata humana",
      "desadaptado",
      "maldito tarado",
      "sarnoso",
      "ridícula",
      "ridiculo humano",
      "patético ser",
      "cochinada",
      "cochino",
      "cochina",
      "vago",
      "vaga",
      "flojo",
      "floja",
      "parásito humano",
      "ignorante estupido",
      "ignorante idiota"

  

    ];
      // AGREGA MÁS AQUÍ

    

    /* NORMALIZAR */

    const textoNormalizado =
      texto.toLowerCase();

    /* DETECTAR */

    const contieneGroserias =
      palabrasProhibidas.some(
        (palabra) =>
          textoNormalizado.includes(
            palabra.toLowerCase()
          )
      );

    /* ESTADO */

    const estadoComentario =
      contieneGroserias
        ? "PENDIENTE"
        : "APROBADO";

    try {

      await axios.post(
        "http://localhost:8000/api/comentarios/",
        {

          contenido: texto,

          usuario: USUARIO_ID,

          noticia: Number(id),

          evento: null,

          comentario_padre: null,

          estado: estadoComentario,

        }
      );

      /* LIMPIAR */

      setNuevoComentario("");

      /* RECARGAR */

      cargarComentarios();

      /* MENSAJES */

      if (contieneGroserias) {

        alert(
          "Tu comentario contiene palabras ofensivas y será revisado por el administrador."
        );

      } else {

        alert(
          "Comentario publicado correctamente."
        );
      }

    } catch (error) {

      console.error(
        "Error al enviar comentario:",
        error
      );

      /* ERROR SERVIDOR */

      if (error.response) {

        console.log(
          error.response.data
        );

        alert(
          "El servidor no pudo procesar el comentario."
        );

      }

      /* ERROR CONEXIÓN */

      else if (error.request) {

        alert(
          "No se pudo conectar con el servidor."
        );

      }

      /* ERROR GENERAL */

      else {

        alert(
          "Ocurrió un error inesperado."
        );
      }
    }
  };

  /* =========================
     ERRORES
  ========================= */

  if (error) {

    return (
      <p className="detalle-mensaje">
        {error}
      </p>
    );
  }

  if (!noticia) {

    return (
      <p className="detalle-mensaje">
        Cargando noticia...
      </p>
    );
  }

  /* =========================
     MULTIMEDIA
  ========================= */

  const multimediaOrdenada =
    noticia.multimedia
      ? [...noticia.multimedia].sort(
          (a, b) => a.orden - b.orden
        )
      : [];

  const portada =
    multimediaOrdenada.find(
      (media) =>
        media.tipo === "IMAGEN"
    );

  const multimediaExtra =
    multimediaOrdenada.filter(
      (media) =>
        media.id !== portada?.id
    );

  /* =========================
     CONTADORES
  ========================= */

  const totalLike =
    reacciones.filter(
      (r) => r.tipo === "LIKE"
    ).length;

  const totalLove =
    reacciones.filter(
      (r) => r.tipo === "LOVE"
    ).length;

  const totalEnojo =
    reacciones.filter(
      (r) => r.tipo === "ENOJO"
    ).length;

  /* =========================
     SOLO APROBADOS
  ========================= */

  const comentariosAprobados =
    comentarios.filter(
      (comentario) =>
        comentario.estado ===
        "APROBADO"
    );

  return (

    <main className="detalle-page">

      {/* VOLVER */}

      <Link
        to="/noticias"
        className="btn-volver"
      >
        ← Volver a noticias
      </Link>

      {/* HERO */}

      {portada ? (

        <section className="detalle-hero">

          <img
            src={portada.archivo_url}
            alt={noticia.titulo}
            className="hero-img"
          />

          <div className="hero-overlay">

            <h1>{noticia.titulo}</h1>

            <p className="hero-fecha">

              Publicado el:{" "}

              {new Date(
                noticia.fecha_publicacion
              ).toLocaleDateString(
                "es-PE",
                {
                  day: "2-digit",
                  month: "long",
                  year: "numeric",
                }
              )}

            </p>

          </div>

        </section>

      ) : (

        <>
          <h1>{noticia.titulo}</h1>

          <p className="detalle-fecha">

            Publicado el:{" "}

            {new Date(
              noticia.fecha_publicacion
            ).toLocaleDateString(
              "es-PE",
              {
                day: "2-digit",
                month: "long",
                year: "numeric",
              }
            )}

          </p>
        </>
      )}

      {/* CONTENIDO */}

      <p className="detalle-contenido">
        {noticia.contenido}
      </p>

      {/* REACCIONES */}

      <section className="reacciones-facebook">

        <button
          type="button"
          className="reaccion-btn like"
          onClick={() =>
            reaccionar("LIKE")
          }
        >

          <FaThumbsUp className="icono-reaccion" />

          <span className="texto-reaccion">
            Me gusta
          </span>

          <strong>
            {totalLike}
          </strong>

        </button>

        <button
          type="button"
          className="reaccion-btn love"
          onClick={() =>
            reaccionar("LOVE")
          }
        >

          <FaHeart className="icono-reaccion" />

          <span className="texto-reaccion">
            Me encanta
          </span>

          <strong>
            {totalLove}
          </strong>

        </button>

        <button
          type="button"
          className="reaccion-btn enojo"
          onClick={() =>
            reaccionar("ENOJO")
          }
        >

          <BsEmojiAngryFill className="icono-reaccion" />

          <span className="texto-reaccion">
            Me enoja
          </span>

          <strong>
            {totalEnojo}
          </strong>

        </button>

      </section>

      {/* COMENTARIOS */}

      <section className="comentarios-section">

        <h2>
          Comentarios
        </h2>

        <form
          className="comentario-form"
          onSubmit={enviarComentario}
        >

          <textarea
            value={nuevoComentario}

            onChange={(e) =>
              setNuevoComentario(
                e.target.value
              )
            }

            placeholder="Escribe un comentario..."
          />

          <button type="submit">
            Comentar
          </button>

        </form>

        <div className="comentarios-lista">

          {comentariosAprobados.length === 0 ? (

            <p className="sin-comentarios">
              Aún no hay comentarios.
            </p>

          ) : (

            comentariosAprobados.map(
              (comentario) => (

                <div
                  key={comentario.id}
                  className="comentario-card"
                >

                  <p>
                    {comentario.contenido}
                  </p>

                </div>

              )
            )
          )}

        </div>

      </section>

      {/* GALERÍA */}

      {multimediaExtra.length > 0 && (

        <section className="detalle-galeria">

          {multimediaExtra.map(
            (media) => (

              <div
                key={media.id}
                className="detalle-media"
              >

                {media.tipo ===
                  "IMAGEN" && (

                  <img
                    src={media.archivo_url}
                    alt={noticia.titulo}
                    className="detalle-img"
                  />
                )}

                {media.tipo ===
                  "VIDEO" && (

                  <video
                    className="detalle-video"
                    controls
                  >

                    <source
                      src={media.archivo_url}
                      type="video/mp4"
                    />

                    Tu navegador no soporta videos.

                  </video>
                )}

              </div>

            )
          )}

        </section>

      )}

      {/* ESTADO */}

      <strong className="detalle-estado">
        Estado: {noticia.estado}
      </strong>

    </main>
  );
}

export default DetalleNoticia;