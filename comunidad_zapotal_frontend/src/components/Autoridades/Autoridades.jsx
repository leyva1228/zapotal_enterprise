import React, { useEffect, useState } from "react";
import { FaLeaf } from "react-icons/fa";
import { Link } from "react-router-dom";
import api, { extractList } from "../../api";
import PageLoader from "../common/PageLoader/PageLoader";
import { useTaskLifecycle } from "../../context/LoaderContext";
import "./Autoridades.css";

function Autoridades() {
  const [autoridades, setAutoridades] = useState([]);
  const [loading, setLoading] = useState(true);

  useTaskLifecycle("autoridades:list", loading);
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
        <PageLoader variant="section" mensaje="Cargando autoridades" />
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
          Líderes de la Comunidad Campesina Niño Dios de Zapotal
        </h2>

        <p>
          Autoridades comprometidas con el desarrollo,
          la organización y el bienestar de todos los
          comuneros de nuestra comunidad.
        </p>

      </div>

      {/* TARJETAS DE AUTORIDADES */}
      <div className="autoridades-grid">

        {autoridades.map((autoridad) => {
          const nombreCompleto = `${autoridad.nombres || ''} ${autoridad.apellidos || ''}`.trim();
          const iniciales = (autoridad.nombres?.[0] || '') + (autoridad.apellidos?.[0] || '');
          return (
            <article className="autoridad-card" key={autoridad.id}>
              <div className="autoridad-imagen">
                {autoridad.foto_url ? (
                  <img
                    src={autoridad.foto_url}
                    alt={nombreCompleto || 'Autoridad'}
                    loading="lazy"
                    onError={(e) => {
                      // Si la URL falla, mostramos un placeholder con iniciales
                      e.target.style.display = 'none';
                      e.target.nextElementSibling?.classList.remove('hidden');
                    }}
                  />
                ) : null}
                <div
                  className={`autoridad-placeholder ${autoridad.foto_url ? 'hidden' : ''}`}
                  aria-hidden="true"
                >
                  <span className="autoridad-placeholder-iniciales">
                    {iniciales || '?'}
                  </span>
                </div>
              </div>

              <div className="autoridad-info">
                <span className="autoridad-cargo">{autoridad.cargo}</span>
                <h3>{nombreCompleto || 'Sin nombre'}</h3>
                <div className="autoridad-linea"></div>
                {autoridad.periodo && (
                  <p className="autoridad-periodo">Periodo: {autoridad.periodo}</p>
                )}
              </div>
            </article>
          );
        })}

      </div>

    </section>
  );
}

export default Autoridades;
