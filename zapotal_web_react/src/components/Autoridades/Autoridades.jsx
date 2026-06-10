import React, { useEffect, useState } from "react";
import axios from "axios";
import { FaLeaf, FaUsers } from "react-icons/fa";
import { Link } from "react-router-dom";
import "./Autoridades.css";

function Autoridades() {
  const [autoridades, setAutoridades] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/autoridades/")
      .then((res) => {
        setAutoridades(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <section className="autoridades-section">

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
          Autoridades comprometidas con el desarrollo, organización
          y bienestar de nuestra comunidad.
        </p>
      </div>

      <div className="autoridades-grid">
        {autoridades.map((autoridad) => (
          <div className="autoridad-card" key={autoridad.id}>

            <div className="autoridad-imagen">
              <img
                src={autoridad.foto_url}
                alt={autoridad.nombres}
              />
            </div>

            <div className="autoridad-info">
              <span className="autoridad-cargo">
                {autoridad.cargo}
              </span>

              <h3>
                {autoridad.nombres} <br />
                {autoridad.apellidos}
              </h3>

              <div className="autoridad-linea"></div>

              <p>
                {autoridad.descripcion}
              </p>
            </div>

          </div>
        ))}
      </div>

      <div className="autoridades-banner">
        <div className="banner-icon">
          <FaUsers />
        </div>

        <div className="banner-text">
          <h4>
            Trabajamos unidos por el bienestar y desarrollo de nuestra comunidad.
          </h4>
        </div>

        <div className="banner-divider"></div>

        <p>
          La participación de todos los comuneros es clave para construir
          un futuro mejor.
        </p>

        <Link
          to="/nosotros/conocenos"
          className="banner-btn"
        >
          <FaLeaf />
          Conoce más sobre nuestra comunidad
        </Link>
      </div>

    </section>
  );
}

export default Autoridades;