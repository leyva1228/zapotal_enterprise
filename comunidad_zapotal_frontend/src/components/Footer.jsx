import React from "react";
import { Link } from "react-router-dom";
import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-glow" />

      <div className="footer-container">

        <div className="footer-brand">
          <h2>Comunidad Campesina Zapotal</h2>
          <p>
            Plataforma digital institucional creada para informar,
            conectar y fortalecer la identidad de nuestra comunidad
            mediante noticias, eventos y contenido relevante.
          </p>
          <div className="footer-badge">
            <span>Portal institucional comunitario</span>
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
          <h3>Legal</h3>
          <ul>
            <li><Link to="/terminos">Terminos y Condiciones</Link></li>
            <li><Link to="/privacidad">Politica de Privacidad</Link></li>
            <li><Link to="/cookies">Politica de Cookies</Link></li>
          </ul>
        </div>

      </div>

      <div className="footer-bottom">
        <p>© 2026 Comunidad Campesina Zapotal. Todos los derechos reservados.</p>
      </div>

    </footer>
  );
}

export default Footer;