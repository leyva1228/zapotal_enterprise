import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./Eventos.css";

function Eventos() {
  const [eventos, setEventos] = useState([]);
  const [mensaje, setMensaje] = useState("Cargando eventos...");

  const [busqueda, setBusqueda] = useState("");
  const [filtroFecha, setFiltroFecha] = useState("todos");

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/eventos/")
      .then((res) => {
        const datos = Array.isArray(res.data)
          ? res.data
          : res.data.results || [];

        setEventos(datos);
        setMensaje("");
      })
      .catch((error) => {
        console.log("ERROR API:", error);
        setMensaje("Error al cargar eventos.");
      });
  }, []);

  const eventosFiltrados = useMemo(() => {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    let resultado = eventos.filter((evento) => {
      const texto = `${evento.titulo || ""} ${evento.descripcion || ""}`.toLowerCase();

      const coincideBusqueda =
        busqueda.trim() === "" ||
        texto.includes(busqueda.toLowerCase());

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

  return (
    <main className="eventos-page">
      <section className="eventos-contenido">

        <div className="eventos-header">
          <span>Nuestra agenda comunal</span>

          <h1>Eventos de la Comunidad</h1>

          <p>
            Conoce las reuniones, actividades, jornadas y acontecimientos
            organizados para fortalecer la participación de los comuneros.
          </p>
        </div>

        <div className="eventos-panel-filtros">
          <div className="eventos-buscador">
            <label>Buscar evento</label>
            <input
              type="text"
              placeholder="Escribe el nombre del evento..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>

          <div className="filtro-grupo">
            <label>Estado</label>
            <select
              value={filtroFecha}
              onChange={(e) => setFiltroFecha(e.target.value)}
            >
              <option value="todos">Todos los eventos</option>
              <option value="proximos">Próximos eventos</option>
              <option value="pasados">Eventos pasados</option>
            </select>
          </div>
        </div>

        {mensaje && <p className="mensaje">{mensaje}</p>}

        {!mensaje && eventosFiltrados.length === 0 && (
          <p className="mensaje">
            No se encontraron eventos disponibles.
          </p>
        )}

        <div className="eventos-grid">
          {eventosFiltrados.map((evento) => {
            const mediaPrincipal = evento.multimedia?.[0];

            return (
              <article className="evento-card" key={evento.id}>
                <div className="evento-media">
                  {mediaPrincipal?.tipo === "IMAGEN" && (
                    <img
                      src={mediaPrincipal.archivo_url}
                      alt={evento.titulo}
                      className="evento-img"
                    />
                  )}

                  {mediaPrincipal?.tipo === "VIDEO" && (
                    <video className="evento-video" controls>
                      <source
                        src={mediaPrincipal.archivo_url}
                        type="video/mp4"
                      />
                      Tu navegador no soporta video.
                    </video>
                  )}
                </div>

                <div className="evento-content">
                  <span className="evento-fecha">
                    {new Date(evento.fecha_evento).toLocaleDateString(
                      "es-PE",
                      {
                        day: "2-digit",
                        month: "long",
                        year: "numeric",
                      }
                    )}
                  </span>

                  <h2>{evento.titulo}</h2>

                  <p>
                    {evento.descripcion?.length > 125
                      ? evento.descripcion.substring(0, 125) + "..."
                      : evento.descripcion}
                  </p>

                  <Link to={`/eventos/${evento.id}`} className="btn-evento">
                    Ver detalles →
                  </Link>
                </div>
              </article>
            );
          })}
        </div>

      </section>
    </main>
  );
}

export default Eventos;