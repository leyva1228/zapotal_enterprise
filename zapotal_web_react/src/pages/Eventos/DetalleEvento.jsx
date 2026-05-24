import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

import { FaThumbsUp, FaHeart } from "react-icons/fa";
import { BsEmojiAngryFill } from "react-icons/bs";

import "./DetalleEvento.css";

function DetalleEvento() {
  const { id } = useParams();

  const [evento, setEvento] = useState(null);
  const [error, setError] = useState("");
  const [reacciones, setReacciones] = useState([]);

  useEffect(() => {
    axios
      .get(`http://localhost:8000/api/eventos/${id}/`)
      .then((res) => setEvento(res.data))
      .catch((err) => {
        console.log(err);
        setError("No se pudo cargar el evento.");
      });
  }, [id]);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/reacciones/")
      .then((res) => {
        const filtradas = res.data.filter(
          (reaccion) => reaccion.evento === Number(id)
        );

        setReacciones(filtradas);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [id]);

  const reaccionar = async (tipo) => {
    try {
      await axios.post("http://localhost:8000/api/reacciones/", {
        tipo: tipo,
        usuario: 2,
        noticia: null,
        evento: Number(id),
      });

      const res = await axios.get("http://localhost:8000/api/reacciones/");

      const filtradas = res.data.filter(
        (reaccion) => reaccion.evento === Number(id)
      );

      setReacciones(filtradas);
    } catch (err) {
      console.log(err);
    }
  };

  if (error) return <p className="mensaje">{error}</p>;
  if (!evento) return <p className="mensaje">Cargando evento...</p>;

  const multimedia = evento.multimedia
    ? [...evento.multimedia].sort((a, b) => a.orden - b.orden)
    : [];

  const portada = multimedia.find((m) => m.tipo === "IMAGEN");

  const multimediaExtra = multimedia.filter((m) => m.id !== portada?.id);

  const fechaEvento = evento.fecha_evento
    ? new Date(evento.fecha_evento).toLocaleDateString("es-PE", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      })
    : "Fecha no disponible";

  const horaEvento = evento.fecha_evento
    ? new Date(evento.fecha_evento).toLocaleTimeString("es-PE", {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "Hora no disponible";

  const totalLike = reacciones.filter((r) => r.tipo === "LIKE").length;
  const totalLove = reacciones.filter((r) => r.tipo === "LOVE").length;
  const totalEnojo = reacciones.filter((r) => r.tipo === "ENOJO").length;

  return (
    <main className="detalle-evento">
      <Link to="/eventos" className="btn-volver">
        ← Volver a eventos
      </Link>

      {portada && (
        <section className="evento-hero">
          <img
            src={portada.archivo_url}
            alt={evento.titulo}
            className="hero-img"
          />

          <div className="hero-overlay">
            <h1>{evento.titulo}</h1>

            <p className="hero-fecha">
              {fechaEvento} | {horaEvento}
            </p>
          </div>
        </section>
      )}

      <section className="evento-info">
        <h2>Detalles del evento</h2>

        <p>
          <strong>Fecha:</strong> {fechaEvento}
        </p>

        <p>
          <strong>Hora:</strong> {horaEvento}
        </p>
      </section>

      <p className="evento-descripcion">{evento.descripcion}</p>

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

      {multimediaExtra.length > 0 && (
        <section className="detalle-galeria">
          {multimediaExtra.map((media) => (
            <div key={media.id} className="detalle-media">
              {media.tipo === "IMAGEN" && (
                <img
                  src={media.archivo_url}
                  alt={evento.titulo}
                  className="detalle-img"
                />
              )}

              {media.tipo === "VIDEO" && (
                <video className="detalle-video" controls>
                  <source src={media.archivo_url} type="video/mp4" />
                  Tu navegador no soporta videos.
                </video>
              )}
            </div>
          ))}
        </section>
      )}
    </main>
  );
}

export default DetalleEvento;