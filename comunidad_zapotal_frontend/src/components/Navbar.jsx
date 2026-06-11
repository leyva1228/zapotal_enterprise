import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import {
  FaChevronDown, FaSignOutAlt, FaUser, FaCog,
  FaBars, FaTimes, FaBell, FaSearch, FaInbox,
  FaNewspaper, FaCalendarAlt,
} from "react-icons/fa";
import api, { extractList } from "../api";
import "./Navbar.css";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const navbarRef = useRef(null);
  const buscadorRef = useRef(null);

  const [usuario, setUsuario] = useState(null);
  const [perfilAbierto, setPerfilAbierto] = useState(false);
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [nosotrosAbierto, setNosotrosAbierto] = useState(false);
  const [mostrarNotificaciones, setMostrarNotificaciones] = useState(false);
  const [mostrarBuzon, setMostrarBuzon] = useState(false);
  const [notificaciones, setNotificaciones] = useState([]);
  const [novedades, setNovedades] = useState([]);
  const [scrolled, setScrolled] = useState(false);
  const [buscadorAbierto, setBuscadorAbierto] = useState(false);
  const [terminoBusqueda, setTerminoBusqueda] = useState("");

  useEffect(() => {
    const raw = localStorage.getItem("usuario");
    if (raw) {
      try { setUsuario(JSON.parse(raw)); }
      catch { localStorage.removeItem("usuario"); }
    }
  }, []);

  const enlaceActivo = (path) => {
    if (path === "/") return location.pathname === "/";
    if (path === "/nosotros/historia" || path === "/nosotros/conocenos")
      return location.pathname.startsWith("/nosotros");
    return location.pathname.startsWith(path);
  };

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const onClickOutside = (e) => {
      if (navbarRef.current && !navbarRef.current.contains(e.target)) {
        setPerfilAbierto(false);
        setMostrarNotificaciones(false);
        setMostrarBuzon(false);
        setNosotrosAbierto(false);
        setBuscadorAbierto(false);
      }
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  useEffect(() => {
    if (!usuario) return;
    api.get(`/notificaciones/?usuario_id=${usuario.id}`)
      .then((r) => setNotificaciones(extractList(r.data)))
      .catch(() => {});
  }, [usuario]);

  useEffect(() => {
    const cargar = async () => {
      try {
        const [nR, eR] = await Promise.all([
          api.get(`/noticias/`),
          api.get(`/eventos/`),
        ]);
        const noticias = extractList(nR.data);
        const eventos  = extractList(eR.data);
        const corte = new Date();
        corte.setDate(corte.getDate() - 3);

        const todo = [
          ...noticias.filter(n => new Date(n.fecha_publicacion) >= corte)
            .map(n => ({ ...n, tipo: "NOTICIA", fecha: n.fecha_publicacion })),
          ...eventos.filter(e => new Date(e.fecha_evento) >= corte)
            .map(e => ({ ...e, tipo: "EVENTO", fecha: e.fecha_evento })),
        ].sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

        setNovedades(todo);
      } catch {}
    };
    cargar();
  }, []);

  const cerrarSesion = () => {
    ["usuario", "token", "accionPendiente"].forEach(k => localStorage.removeItem(k));
    setUsuario(null);
    navigate("/login");
  };

  const handleBuscar = (e) => {
    e.preventDefault();
    if (terminoBusqueda.trim()) {
      navigate(`/buscar?q=${encodeURIComponent(terminoBusqueda)}`);
      setBuscadorAbierto(false);
      setTerminoBusqueda("");
    }
  };

  const cerrarMenu = () => setMenuAbierto(false);

  return (
    <header ref={navbarRef} className={`navbar ${scrolled ? "navbar-scrolled" : ""}`}>

      <Link to="/" className="navbar-brand" onClick={cerrarMenu}>
        <img src="/img/Logo-comunidad/Logo-principal.png" alt="Logo" />
        <div>
          <strong>Comunidad Campesina</strong>
          <span>Zapotal</span>
        </div>
      </Link>

      <button className="burger-btn" onClick={() => setMenuAbierto(!menuAbierto)} aria-label="Menú">
        {menuAbierto ? <FaTimes /> : <FaBars />}
      </button>

      {menuAbierto && <div className="nav-overlay" onClick={cerrarMenu} />}

      <nav className={`nav-links ${menuAbierto ? "active" : ""}`}>
        {[
          { to: "/", label: "Inicio" },
          { to: "/noticias", label: "Noticias" },
          { to: "/eventos", label: "Eventos" },
          { to: "/autoridades", label: "Autoridades" },
          { to: "/contactanos", label: "Contacto" },
          { to: "/donaciones", label: "Donaciones" },
        ].map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={enlaceActivo(to) ? "activo" : ""}
            onClick={cerrarMenu}
          >
            {label}
          </Link>
        ))}

        <div className={`dropdown ${nosotrosAbierto ? "dropdown-open" : ""}`}>
          <button
            className={`dropdown-title ${enlaceActivo("/nosotros") ? "activo" : ""}`}
            onClick={() => setNosotrosAbierto(!nosotrosAbierto)}
          >
            Nosotros <FaChevronDown />
          </button>
          <div className="dropdown-menu">
            <Link to="/nosotros/historia" onClick={cerrarMenu}>Nuestra historia</Link>
            <Link to="/nosotros/conocenos" onClick={cerrarMenu}>Conócenos</Link>
          </div>
        </div>
      </nav>

      <div className="navbar-user">

        <div className="buscador-box" ref={buscadorRef}>
          <button
            className="circle-btn"
            onClick={() => setBuscadorAbierto(!buscadorAbierto)}
            aria-label="Buscar"
          >
            <FaSearch />
          </button>
          {buscadorAbierto && (
            <form className="buscador-dropdown" onSubmit={handleBuscar}>
              <input
                type="text"
                placeholder="Buscar noticias, eventos..."
                value={terminoBusqueda}
                onChange={(e) => setTerminoBusqueda(e.target.value)}
                autoFocus
                maxLength={100}
              />
              <button type="submit">Buscar</button>
            </form>
          )}
        </div>

        {usuario && (
          <div className="notificacion-box">
            <button
              className="circle-btn"
              onClick={() => { setMostrarNotificaciones(!mostrarNotificaciones); setMostrarBuzon(false); setPerfilAbierto(false); }}
              aria-label="Notificaciones"
            >
              <FaBell />
              {notificaciones.length > 0 && (
                <span className="notification-count">{notificaciones.length}</span>
              )}
            </button>
            {mostrarNotificaciones && (
              <div className="notification-dropdown">
                <h3>Notificaciones</h3>
                {notificaciones.length === 0 ? (
                  <p className="notification-empty">No hay notificaciones</p>
                ) : (
                  notificaciones.map((n) => (
                    <div key={n.id} className="notification-item">
                      <strong>{n.titulo}</strong>
                      <span>{n.mensaje}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        <div className="buzon-box">
          <button
            className="circle-btn"
            onClick={() => { setMostrarBuzon(!mostrarBuzon); setMostrarNotificaciones(false); setPerfilAbierto(false); }}
            aria-label="Novedades"
          >
            <FaInbox />
            {novedades.length > 0 && (
              <span className="notification-count">{novedades.length}</span>
            )}
          </button>
          {mostrarBuzon && (
            <div className="notification-dropdown">
              <h3>Novedades recientes</h3>
              {novedades.length === 0 ? (
                <p className="notification-empty">No hay novedades recientes</p>
              ) : (
                novedades.map((item) => (
                  <Link
                    key={`${item.tipo}-${item.id}`}
                    to={item.tipo === "EVENTO" ? `/eventos/${item.id}` : `/noticias/${item.id}`}
                    className="notification-item"
                    onClick={() => setMostrarBuzon(false)}
                  >
                    <strong className="buzon-title">
                      {item.tipo === "EVENTO"
                        ? <FaCalendarAlt className="buzon-icon evento" />
                        : <FaNewspaper className="buzon-icon noticia" />}
                      {item.titulo}
                    </strong>
                    <span>
                      {(item.descripcion || item.contenido || "").slice(0, 70)}...
                    </span>
                  </Link>
                ))
              )}
            </div>
          )}
        </div>

        {usuario ? (
          <div className="profile-box">
            <button
              className="profile-trigger"
              onClick={() => { setPerfilAbierto(!perfilAbierto); setMostrarNotificaciones(false); setMostrarBuzon(false); }}
              aria-label="Perfil"
            >
              {usuario.foto_perfil ? (
                <img src={usuario.foto_perfil} alt="Perfil" className="profile-img" />
              ) : (
                <div className="profile-letter">
                  {usuario.nombres?.charAt(0) || usuario.email?.charAt(0) || "U"}
                </div>
              )}
            </button>
            {perfilAbierto && (
              <div className="profile-dropdown">
                <div className="profile-info-header">
                  <div className="profile-avatar-sm">
                    {usuario.foto_perfil
                      ? <img src={usuario.foto_perfil} alt="" />
                      : <span>{usuario.nombres?.charAt(0) || "U"}</span>}
                  </div>
                  <div className="profile-info-name">{usuario.nombres} {usuario.apellidos}</div>
                  <div className="profile-info-email">{usuario.email}</div>
                </div>
                <div className="profile-options">
                  <Link to="/perfil" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                    <FaUser /> Ver perfil
                  </Link>
                  <Link to="/configuracion" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                    <FaCog /> Configuración
                  </Link>
                  <button className="profile-option logout-btn" onClick={cerrarSesion}>
                    <FaSignOutAlt /> Cerrar sesión
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="auth-buttons">
            <Link to="/login" className="login-btn">Ingresar</Link>
            <Link to="/registro" className="register-btn">Registrarse</Link>
          </div>
        )}

      </div>
    </header>
  );
}

export default Navbar;
