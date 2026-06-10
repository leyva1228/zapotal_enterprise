import React from "react";
import { Link } from "react-router-dom";
import {
  FaHome,
  FaRegNewspaper,
  FaRegCalendarAlt,
  FaUserTie,
  FaRegEnvelope,
  FaBookOpen,
  FaUniversity,
  FaShieldAlt,
} from "react-icons/fa";

import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-glow"></div>

      <div className="footer-container">

        {/* LOGO / INFORMACIÓN */}
        <div className="footer-brand">

          <h2>Comunidad Campesina Zapotal</h2>

          <p>
            Plataforma digital institucional creada para informar,
            conectar y fortalecer la identidad de nuestra comunidad
            mediante noticias, eventos y contenido relevante.
          </p>

          <div className="footer-badge">
            <FaShieldAlt />
            <span>Portal institucional comunitario</span>
          </div>

        </div>

        {/* NAVEGACIÓN */}
        <div className="footer-section">

          <h3>Navegación</h3>

          <ul>

            <li>
              <Link to="/">
                <FaHome className="footer-icon" />
                <span>Inicio</span>
              </Link>
            </li>

            <li>
              <Link to="/noticias">
                <FaRegNewspaper className="footer-icon" />
                <span>Noticias</span>
              </Link>
            </li>

            <li>
              <Link to="/eventos">
                <FaRegCalendarAlt className="footer-icon" />
                <span>Eventos</span>
              </Link>
            </li>

            <li>
              <Link to="/autoridades">
                <FaUserTie className="footer-icon" />
                <span>Autoridades</span>
              </Link>
            </li>

            <li>
              <Link to="/contactanos">
                <FaRegEnvelope className="footer-icon" />
                <span>Contáctanos</span>
              </Link>
            </li>

          </ul>

        </div>

        {/* INSTITUCIONAL */}
        <div className="footer-section">

          <h3>Institucional</h3>

          <ul>

            <li>
              <Link to="/nosotros/historia">
                <FaBookOpen className="footer-icon" />
                <span>Nuestra historia</span>
              </Link>
            </li>

            <li>
              <Link to="/nosotros/conocenos">
                <FaUniversity className="footer-icon" />
                <span>Conócenos</span>
              </Link>
            </li>

          </ul>

          {/* IMAGEN LIBRO */}
          <div className="libro-reclamaciones-item">

            <Link
              to="/libro-reclamaciones"
              className="libro-reclamaciones-link"
            >

              <img
                src="img/Libro _de_reclamaciones/libro_de_recalmaciones.png"
                alt="Libro de reclamaciones"
                className="libro-reclamaciones-img"
              />

            </Link>

          </div>

        </div>

      </div>

      {/* FOOTER BOTTOM */}
      <div className="footer-bottom">

        <p>
          © 2026 Comunidad Campesina Zapotal.
          Todos los derechos reservados.
        </p>

      </div>

    </footer>
  );
}

export default Footer;