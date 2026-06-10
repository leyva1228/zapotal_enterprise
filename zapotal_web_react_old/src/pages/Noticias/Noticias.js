
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./Noticias.css";

function Noticias() {

  const [noticias, setNoticias] = useState([]);
  const [paginaActual, setPaginaActual] = useState(1);

  /* =========================
     LOADING
  ========================= */

  const [loading, setLoading] = useState(true);

  const noticiasPorPagina = 10;

  useEffect(() => {

    setLoading(true);

    axios
      .get("http://localhost:8000/api/noticias/")
      .then((res) => {

        const datos = Array.isArray(res.data)
          ? res.data
          : res.data.results || [];

        /* PEQUEÑO RETARDO
           PARA QUE EL LOADER
           SE VEA ELEGANTE */

        setTimeout(() => {

          setNoticias(datos);
          setLoading(false);

        }, 900);

      })
      .catch((error) => {

        console.log(error);
        setLoading(false);

      });

  }, []);

  /* =========================
     LOADER PROFESIONAL
  ========================= */

  if (loading) {

    return (

      <div className="loader-container">

        <div className="loader-wrapper">

          <div className="loader-ring"></div>

          <div className="loader-ring ring-2"></div>

        </div>

        <h2 className="loader-title">
          Cargando publicaciones
        </h2>

        <p className="loader-subtitle">
          Espere un momento...
        </p>

      </div>

    );

  }

  if (noticias.length === 0) {
    return <p className="mensaje">No hay noticias disponibles.</p>;
  }

  /* =========================
     PAGINACIÓN
  ========================= */

  const ultimaNoticia =
    paginaActual * noticiasPorPagina;

  const primeraNoticia =
    ultimaNoticia - noticiasPorPagina;

  const noticiasActuales =
    noticias.slice(
      primeraNoticia,
      ultimaNoticia
    );

  const totalPaginas = Math.ceil(
    noticias.length / noticiasPorPagina
  );

  const cambiarPagina = (numero) => {

    if (
      numero < 1 ||
      numero > totalPaginas
    ) return;

    setPaginaActual(numero);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });

  };

  /* =========================
     HERO + GRID
  ========================= */

  const destacada = noticiasActuales[0];

  const resto = noticiasActuales.slice(1);

  return (

    <main className="noticias-page">

      {/* HERO */}

      <section className="noticia-hero">

        {destacada.multimedia?.length > 0 && (

          <img
            src={destacada.multimedia[0].archivo_url}
            alt={destacada.titulo}
            className="hero-img"
          />

        )}

        <div className="hero-overlay">

          <h1 className="hero-title">
            Publicaciones
          </h1>

          <h2>
            {destacada.titulo}
          </h2>

          <p className="noticia-fecha">

            {new Date(
              destacada.fecha_publicacion
            ).toLocaleDateString("es-PE", {
              day: "numeric",
              month: "long",
              year: "numeric",
            })}

          </p>

          <Link
            to={`/noticias/${destacada.id}`}
            className="hero-btn"
          >
            LEER MÁS →
          </Link>

        </div>

      </section>

      {/* GRID */}

      <div className="noticias-grid">

        {resto.map((noticia) => (

          <article
            className="noticia-item"
            key={noticia.id}
          >

            {noticia.multimedia?.length > 0 && (

              <img
                src={noticia.multimedia[0].archivo_url}
                alt={noticia.titulo}
                className="noticia-img"
                loading="lazy"
              />

            )}

            <h2 className="noticia-titulo">
              {noticia.titulo}
            </h2>

            <p className="noticia-fecha">

              {new Date(
                noticia.fecha_publicacion
              ).toLocaleDateString("es-PE", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}

            </p>

            <Link
              to={`/noticias/${noticia.id}`}
              className="leer-mas"
            >
              LEER MÁS →
            </Link>

          </article>

        ))}

      </div>

      {/* PAGINACIÓN */}

      {totalPaginas > 1 && (

        <div className="pagination">

          <button
            className={`page-btn ${
              paginaActual === 1
                ? "disabled"
                : ""
            }`}
            onClick={() =>
              cambiarPagina(
                paginaActual - 1
              )
            }
            disabled={paginaActual === 1}
          >
            ← Anterior
          </button>

          <div className="page-numbers">

            {[...Array(totalPaginas)].map(
              (_, index) => (

                <button
                  key={index}
                  className={`page-number ${
                    paginaActual === index + 1
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    cambiarPagina(index + 1)
                  }
                >
                  {index + 1}
                </button>

              )
            )}

          </div>

          <button
            className={`page-btn ${
              paginaActual === totalPaginas
                ? "disabled"
                : ""
            }`}
            onClick={() =>
              cambiarPagina(
                paginaActual + 1
              )
            }
            disabled={
              paginaActual === totalPaginas
            }
          >
            Siguiente →
          </button>

        </div>

      )}

    </main>

  );

}

export default Noticias;

