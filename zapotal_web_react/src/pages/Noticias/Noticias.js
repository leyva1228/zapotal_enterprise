import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./Noticias.css";

function Noticias() {
  const [noticias, setNoticias] = useState([]);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/noticias/")
      .then((res) => {
        const datos = Array.isArray(res.data)
          ? res.data
          : res.data.results || [];

        setNoticias(datos);
      })
      .catch((error) => console.log(error));
  }, []);

  if (noticias.length === 0) {
    return <p className="mensaje">Cargando noticias...</p>;
  }

  const destacada = noticias[0];
  const resto = noticias.slice(1);

  return (
    <main className="noticias-page">
      <section className="noticia-hero">
        {destacada.multimedia?.length > 0 && (
          <img
            src={destacada.multimedia[0].archivo_url}
            alt={destacada.titulo}
            className="hero-img"
          />
        )}

        <div className="hero-overlay">
          <h1 className="hero-title">Publicaciones</h1>

          <h2>{destacada.titulo}</h2>

          <p className="noticia-fecha">
            {new Date(destacada.fecha_publicacion).toLocaleDateString("es-PE", {
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </p>

          <Link to={`/noticias/${destacada.id}`} className="hero-btn">
            LEER MÁS →
          </Link>
        </div>
      </section>

      <div className="noticias-grid">
        {resto.map((noticia) => (
          <article className="noticia-item" key={noticia.id}>
            {noticia.multimedia?.length > 0 && (
              <img
                src={noticia.multimedia[0].archivo_url}
                alt={noticia.titulo}
                className="noticia-img"
              />
            )}

            <h2 className="noticia-titulo">{noticia.titulo}</h2>

            <p className="noticia-fecha">
              {new Date(noticia.fecha_publicacion).toLocaleDateString("es-PE", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </p>

            <Link to={`/noticias/${noticia.id}`} className="leer-mas">
              LEER MÁS →
            </Link>
          </article>
        ))}
      </div>
    </main>
  );
}

export default Noticias;