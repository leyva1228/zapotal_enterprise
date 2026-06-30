import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  FaChevronDown, FaSignOutAlt, FaUser, FaCog, FaTimes,
  FaSearch, FaShieldAlt,
  FaHome, FaNewspaper, FaCalendarAlt, FaUsers,
  FaPhoneAlt, FaHandHoldingHeart,
} from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';
import './Navbar.css';

// ── Links publicos con icono (estilo del companero) ──
const PUBLIC_LINKS = [
  { to: '/',             label: 'Inicio',      icon: <FaHome /> },
  { to: '/noticias',     label: 'Noticias',    icon: <FaNewspaper /> },
  { to: '/eventos',      label: 'Eventos',     icon: <FaCalendarAlt /> },
  { to: '/autoridades',  label: 'Autoridades', icon: <FaUsers /> },
  { to: '/contactanos',  label: 'Contacto',    icon: <FaPhoneAlt /> },
  { to: '/donaciones',   label: 'Donaciones',  icon: <FaHandHoldingHeart /> },
];

// ── Link admin (solo visible si el usuario es admin) ──
const ADMIN_LINK = { to: '/admin', label: 'Admin', icon: <FaShieldAlt /> };

function Navbar() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const navbarRef = useRef(null);

  const { user, isAuthenticated, clearAuth } = useAuth();
  const { isAdmin: isAdminCtx } = useAuth();
  const isAdmin = !!isAdminCtx;

  const [perfilAbierto,   setPerfilAbierto]   = useState(false);
  const [menuAbierto,     setMenuAbierto]     = useState(false);
  const [nosotrosAbierto, setNosotrosAbierto] = useState(false);
  const [scrolled,        setScrolled]        = useState(false);
  const [buscadorAbierto, setBuscadorAbierto] = useState(false);
  const [terminoBusqueda, setTerminoBusqueda] = useState('');

  const enlaces = isAdmin ? [...PUBLIC_LINKS, ADMIN_LINK] : PUBLIC_LINKS;

  /* ── Scroll: agrega sombra al navbar cuando hay scroll ── */
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  /* ── Bloquear scroll del body cuando el drawer esta abierto ── */
  useEffect(() => {
    document.body.style.overflow = menuAbierto ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [menuAbierto]);

  /* ── Cerrar dropdowns al hacer clic fuera ── */
  useEffect(() => {
    const onClickOutside = (e) => {
      if (navbarRef.current && !navbarRef.current.contains(e.target)) {
        setPerfilAbierto(false);
        setNosotrosAbierto(false);
        setBuscadorAbierto(false);
      }
    };
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  /* ── Tecla Escape cierra todo ── */
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setMenuAbierto(false);
        setPerfilAbierto(false);
        setBuscadorAbierto(false);
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  /* ── Logout (misma logica que ya tenias) ── */
  const handleLogout = async () => {
    try {
      await clearAuth();
    } finally {
      setPerfilAbierto(false);
      setMenuAbierto(false);
      navigate('/login');
    }
  };

  /* ── Busqueda (misma logica que ya tenias) ── */
  const handleBuscar = (e) => {
    e.preventDefault();
    if (terminoBusqueda.trim()) {
      navigate(`/buscar?q=${encodeURIComponent(terminoBusqueda.trim())}`);
      setBuscadorAbierto(false);
      setMenuAbierto(false);
      setTerminoBusqueda('');
    }
  };

  const cerrarMenu = () => {
    setMenuAbierto(false);
    setNosotrosAbierto(false);
  };

  /* ── Detectar link activo ── */
  const enlaceActivo = (path) => {
    if (path === '/') return location.pathname === '/';
    if (path === '/nosotros/historia' || path === '/nosotros/conocenos')
      return location.pathname.startsWith('/nosotros');
    return location.pathname.startsWith(path);
  };

  /* ── Inicial del usuario para el avatar ── */
  const userInitial = (user?.nombres?.charAt(0) || user?.email?.charAt(0) || 'U').toUpperCase();

  return (
    <>
      {/* ═══════════════════════════════════════════
          NAVBAR FIJO (2 franjas en desktop)
          ═══════════════════════════════════════════ */}
      <header ref={navbarRef} className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>

        {/* ─── FRANJA SUPERIOR (52px) ─── */}
        <div className="navbar-top">

          {/* Brand */}
          <Link to="/" className="navbar-brand" onClick={cerrarMenu}>
            <img
              src="/img/Logo-comunidad/Logo-principal.png"
              alt="Logo Comunidad Campesina Niño Dios de Zapotal"
            />
            <div>
              <strong>Comunidad Campesina <br/> Niño Dios de Zapotal</strong>
            </div>
          </Link>

          {/* Acciones (buscador, notif, perfil, auth, burger) */}
          <div className="navbar-user navbar-actions">

            {/* Buscador — solo desktop (en mobile va dentro del drawer) */}
            <div className="buscador-box">
              <button
                className="circle-btn"
                onClick={() => setBuscadorAbierto((prev) => !prev)}
                aria-label="Buscar"
                title="Buscar"
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

            {/* Notificaciones */}
            <div className="notification-container">
              <NotificationBell />
            </div>

            {/* Perfil / Auth */}
            {isAuthenticated && user ? (
              <div className="profile-box">
                <button
                  className="profile-trigger"
                  onClick={() => setPerfilAbierto((prev) => !prev)}
                  aria-label="Perfil"
                >
                  {user.foto_perfil || user.foto_perfil_url ? (
                    <img
                      src={user.foto_perfil || user.foto_perfil_url}
                      alt="Perfil"
                      className="profile-img"
                    />
                  ) : (
                    <div className="profile-letter">{userInitial}</div>
                  )}
                </button>
                {perfilAbierto && (
                  <div className="profile-dropdown">
                    <div className="profile-info-header">
                      <div className="profile-avatar-sm">{userInitial}</div>
                      <div className="profile-info-name">
                        {user.nombres} {user.apellidos}
                      </div>
                      <div className="profile-info-email">{user.email}</div>
                    </div>
                    <div className="profile-options">
                      <Link
                        to="/perfil"
                        className="profile-option"
                        onClick={() => setPerfilAbierto(false)}
                      >
                        <FaUser /> Ver perfil
                      </Link>
                      <Link
                        to="/perfil"
                        className="profile-option"
                        onClick={() => setPerfilAbierto(false)}
                      >
                        <FaCog /> Configuracion
                      </Link>
                      {isAdmin && (
                        <Link
                          to="/admin"
                          className="profile-option"
                          onClick={() => setPerfilAbierto(false)}
                        >
                          <FaShieldAlt /> Panel admin
                        </Link>
                      )}
                      <button
                        className="profile-option logout-btn"
                        onClick={handleLogout}
                      >
                        <FaSignOutAlt /> Cerrar sesion
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="auth-buttons">
                <Link to="/login"    className="login-btn btn-ingresar">Ingresar</Link>
                <Link to="/registro" className="register-btn btn-registrarse">Registrarse</Link>
              </div>
            )}

            {/* Hamburguesa — solo mobile/tablet */}
            <button
              className={`burger-btn ${menuAbierto ? 'burger-open' : ''}`}
              onClick={() => setMenuAbierto((prev) => !prev)}
              aria-label={menuAbierto ? 'Cerrar menu' : 'Abrir menu'}
            >
              <span className="burger-bar" />
              <span className="burger-bar" />
              <span className="burger-bar" />
            </button>
          </div>
        </div>

        {/* ─── FRANJA NAV VERDE (44px) — solo desktop ─── */}
        <div className="navbar-nav-wrapper">
          <nav className="nav-desktop nav-links">
            {enlaces.map(({ to, label, icon }) => (
              <Link
                key={to}
                to={to}
                className={`nav-link ${enlaceActivo(to) ? 'activo' : ''}`}
              >
                <span className="nav-icon">{icon}</span>
                {label}
              </Link>
            ))}

            {/* Dropdown Nosotros (desktop) */}
            <div className={`dropdown ${nosotrosAbierto ? 'dropdown-open' : ''}`}>
              <button
                className={`nav-link dropdown-title ${enlaceActivo('/nosotros') ? 'activo' : ''}`}
                onClick={() => setNosotrosAbierto((prev) => !prev)}
              >
                <span className="nav-icon"><FaUsers /></span>
                Nosotros <FaChevronDown className="dropdown-arrow" />
              </button>
              <div className="dropdown-menu">
                <Link to="/nosotros/historia" onClick={cerrarMenu}>Nuestra historia</Link>
                <Link to="/nosotros/conocenos" onClick={cerrarMenu}>Conocenos</Link>
              </div>
            </div>
          </nav>
        </div>
      </header>

      {/* ═══════════════════════════════════════════
          DRAWER MOBILE
          ═══════════════════════════════════════════ */}
      {menuAbierto && (
        <div className="nav-overlay" onClick={cerrarMenu} aria-hidden="true" />
      )}

      <nav
        className={`nav-drawer ${menuAbierto ? 'nav-drawer-open' : ''}`}
        aria-label="Menu principal"
      >
        {/* Cabecera del drawer */}
        <div className="drawer-header">
          <img
            src="/img/Logo-comunidad/Logo-principal.png"
            alt="Logo"
            className="drawer-logo"
          />
          <div className="drawer-brand">
            <p className="drawer-title">Comunidad Campesina <br/>Niño Dios de Zapotal</p>
            <p className="drawer-sub">Portal Oficial</p>
          </div>
          <button
            className="drawer-close"
            onClick={cerrarMenu}
            aria-label="Cerrar menu"
          >
            <FaTimes />
          </button>
        </div>

        {/* Buscador del drawer */}
        <div className="drawer-search">
          <form onSubmit={handleBuscar}>
            <FaSearch className="drawer-search-icon" />
            <input
              type="text"
              placeholder="Buscar noticias, eventos..."
              value={terminoBusqueda}
              onChange={(e) => setTerminoBusqueda(e.target.value)}
              maxLength={100}
            />
            {terminoBusqueda && (
              <button type="submit" className="drawer-search-btn">Ir</button>
            )}
          </form>
        </div>

        {/* Usuario logueado (mini card) */}
        {isAuthenticated && user && (
          <div className="drawer-user">
            <div className="drawer-user-avatar">
              {user.foto_perfil || user.foto_perfil_url ? (
                <img src={user.foto_perfil || user.foto_perfil_url} alt="Perfil" />
              ) : (
                <span>{userInitial}</span>
              )}
            </div>
            <div className="drawer-user-info">
              <p className="drawer-user-name">
                {user.nombres} {user.apellidos}
              </p>
              <p className="drawer-user-email">{user.email}</p>
            </div>
          </div>
        )}

        {/* Links principales */}
        <div className="drawer-section-label">Navegacion</div>
        <div className="drawer-links">
          {enlaces.map(({ to, label, icon }) => (
            <Link
              key={to}
              to={to}
              className={`drawer-link ${enlaceActivo(to) ? 'drawer-link-activo' : ''}`}
              onClick={cerrarMenu}
            >
              <span className="drawer-icon">{icon}</span>
              {label}
              {enlaceActivo(to) && <span className="drawer-active-dot" />}
            </Link>
          ))}

          {/* Nosotros accordion */}
          <div className={`drawer-accordion ${nosotrosAbierto ? 'drawer-accordion-open' : ''}`}>
            <button
              className={`drawer-link drawer-accordion-btn ${enlaceActivo('/nosotros') ? 'drawer-link-activo' : ''}`}
              onClick={() => setNosotrosAbierto((prev) => !prev)}
            >
              <span className="drawer-icon"><FaUsers /></span>
              Nosotros
              <FaChevronDown className="drawer-accordion-arrow" />
            </button>
            <div className="drawer-accordion-body">
              <Link
                to="/nosotros/historia"
                className="drawer-sub-link"
                onClick={cerrarMenu}
              >
                Nuestra historia
              </Link>
              <Link
                to="/nosotros/conocenos"
                className="drawer-sub-link"
                onClick={cerrarMenu}
              >
                Conocenos
              </Link>
            </div>
          </div>
        </div>

        {/* Seccion cuenta */}
        {isAuthenticated && user ? (
          <>
            <div className="drawer-section-label">Mi cuenta</div>
            <div className="drawer-links">
              <Link to="/perfil" className="drawer-link" onClick={cerrarMenu}>
                <span className="drawer-icon"><FaUser /></span>
                Ver perfil
              </Link>
              <Link to="/perfil" className="drawer-link" onClick={cerrarMenu}>
                <span className="drawer-icon"><FaCog /></span>
                Configuracion
              </Link>
              {isAdmin && (
                <Link to="/admin" className="drawer-link" onClick={cerrarMenu}>
                  <span className="drawer-icon"><FaShieldAlt /></span>
                  Panel admin
                </Link>
              )}
            </div>
            <div className="drawer-footer">
              <button className="drawer-logout" onClick={handleLogout}>
                <FaSignOutAlt /> Cerrar sesion
              </button>
            </div>
          </>
        ) : (
          <div className="drawer-auth">
            <Link
              to="/login"
              className="drawer-btn-ingresar"
              onClick={cerrarMenu}
            >
              Ingresar
            </Link>
            <Link
              to="/registro"
              className="drawer-btn-registrarse"
              onClick={cerrarMenu}
            >
              Registrarse
            </Link>
          </div>
        )}
      </nav>
    </>
  );
}

export default Navbar;
