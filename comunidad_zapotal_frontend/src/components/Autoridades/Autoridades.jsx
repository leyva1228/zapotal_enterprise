import React, { useEffect, useState } from "react";
import { FaLeaf } from "react-icons/fa";
import { Link } from "react-router-dom";
import api, { extractList } from "../../api";
import "./Autoridades.css";

function Autoridades() {
  const [autoridades, setAutoridades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/autoridades/")
      .then((response) => {
        setAutoridades(extractList(response.data));
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error al obtener autoridades:", error);
        setError("No se pudieron cargar las autoridades");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <section className="autoridades-section">
        <div className="loading-spinner"></div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="autoridades-section">
        <div className="error-message">{error}</div>
      </section>
    );
  }

  return (
    <section className="autoridades-section">

      {/* CABECERA */}
      <div className="autoridades-header">

        <div className="autoridades-decor">
          <span></span>
          <FaLeaf />
          <span></span>
        </div>

        <h5>Nuestras Autoridades</h5>

        <h2>
          Líderes de la Comunidad Campesina Zapotal
        </h2>

        <p>
          Autoridades comprometidas con el desarrollo,
          la organización y el bienestar de todos los
          comuneros de nuestra comunidad.
        </p>

      </div>

      {/* TARJETAS DE AUTORIDADES */}
      <div className="autoridades-grid">

        {autoridades.map((autoridad) => (
          <article
            className="autoridad-card"
            key={autoridad.id}
          >
            <div className="autoridad-imagen">
              <img
                src={autoridad.foto_url}
                alt={`${autoridad.nombres} ${autoridad.apellidos}`}
                onError={(e) => {
                  e.target.src = '/images/default-avatar.jpg';
                }}
              />
            </div>

            <div className="autoridad-info">

              <span className="autoridad-cargo">
                {autoridad.cargo}
              </span>

              <h3>
                {autoridad.nombres} {autoridad.apellidos}
              </h3>

              <div className="autoridad-linea"></div>

              <p className="autoridad-periodo">
                Periodo: {autoridad.periodo}
              </p>

            </div>
          </article>
        ))}

      </div>

    </section>
  );
}

export default Autoridades;
