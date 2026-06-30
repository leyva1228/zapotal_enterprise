import React from "react";
import { Link } from "react-router-dom";
import { FaCookieBite } from "react-icons/fa";
import useBannerCookies from "../hooks/useBannerCookies";
import "./Footer.css";

function Footer() {
  const { open } = useBannerCookies();

  return (
    <footer className="footer">
      <div className="footer-glow" />

      <div className="footer-container">

        <div className="footer-brand">
            <h2>Comunidad Campesina Niño Dios de Zapotal</h2>
          <p>
            Plataforma digital institucional para informar y conectar
            a nuestra comunidad.
          </p>
          <div className="libro-reclamaciones-item">
            <Link to="/libro-reclamaciones" className="libro-reclamaciones-link">
              <img
                src="img/Libro _de_reclamaciones/libro_de_recalmaciones.png"
                alt="Libro de reclamaciones"
                className="libro-reclamaciones-img"
              />
            </Link>
          </div>
        </div>

        <div className="footer-section">
          <h3>Navegación</h3>
          <ul>
            <li><Link to="/">Inicio</Link></li>
            <li><Link to="/noticias">Noticias</Link></li>
            <li><Link to="/eventos">Eventos</Link></li>
            <li><Link to="/autoridades">Autoridades</Link></li>
            <li><Link to="/contactanos">Contáctanos</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h3>Institucional</h3>
          <ul>
            <li><Link to="/nosotros/historia">Nuestra historia</Link></li>
            <li><Link to="/nosotros/conocenos">Conocenos</Link></li>
            <li><Link to="/nosotros/marco-legal">Marco legal</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h3>Legal</h3>
          <ul>
            <li><Link to="/terminos">Terminos y Condiciones</Link></li>
            <li><Link to="/privacidad">Politica de Privacidad</Link></li>
            <li><Link to="/cookies">Politica de Cookies</Link></li>
            <li>
              <button
                type="button"
                className="footer-admin-cookies"
                onClick={() => open('footer')}
                aria-label="Abrir preferencias de cookies"
              >
                <FaCookieBite className="footer-icon" /> Administrar cookies
              </button>
            </li>
          </ul>
        </div>

      </div>

      <div className="footer-bottom">
        <p>© 2026 Comunidad Campesina Niño Dios de Zapotal. Todos los derechos reservados.</p>
      </div>

    </footer>
  );
}

export default Footer;
