import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  FaChevronDown, FaSignOutAlt, FaUser, FaCog,
  FaSearch, FaShieldAlt,
  FaHome, FaNewspaper, FaCalendarAlt, FaUsers,
  FaPhoneAlt, FaHandHoldingHeart, FaTimes,
} from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';
import './Navbar.css';

const PUBLIC_LINKS = [
  { to: '/',            label: 'Inicio',      icon: <FaHome /> },
  { to: '/noticias',    label: 'Noticias',    icon: <FaNewspaper /> },
  { to: '/eventos',     label: 'Eventos',     icon: <FaCalendarAlt /> },
  { to: '/autoridades', label: 'Autoridades', icon: <FaUsers /> },
  { to: '/contactanos', label: 'Contacto',    icon: <FaPhoneAlt /> },
  { to: '/donaciones',  label: 'Donaciones',  icon: <FaHandHoldingHeart /> },
];

const ADMIN_LINK = { to: '/admin', label: 'Admin', icon: <FaShieldAlt /> };

function Navbar() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const navbarRef = useRef(null);

  const { user, isAuthenticated, clearAuth, isAdmin: isAdminCtx } = useAuth();
  const isAdmin = !!isAdminCtx;

  const [perfilAbierto,   setPerfilAbierto]   = useState(false);
  const [menuAbierto,     setMenuAbierto]     = useState(false);
  const [nosotrosAbierto, setNosotrosAbierto] = useState(false);
  const [scrolled,        setScrolled]        = useState(false);
  const [buscadorAbierto, setBuscadorAbierto] = useState(false);
  const [terminoBusqueda, setTerminoBusqueda] = useState('');

  const enlaces = useMemo(
    () => (isAdmin ? [...PUBLIC_LINKS, ADMIN_LINK] : PUBLIC_LINKS),
    [isAdmin]
  );

  const cerrarMenu = useCallback(() => {
    setMenuAbierto(false);
    setNosotrosAbierto(false);
  }, []);

  /* ── Scroll ── */
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  /* ── Bloquear scroll del body cuando menú móvil abierto ── */
  useEffect(() => {
    document.body.style.overflow = menuAbierto ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [menuAbierto]);

  /* ── Cerrar dropdowns al clic fuera ── */
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

  /* ── Escape key cierra todo ── */
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        cerrarMenu();
        setPerfilAbierto(false);
        setBuscadorAbierto(false);
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [cerrarMenu]);

  const handleLogout = useCallback(async () => {
    try { await clearAuth(); }
    finally { setPerfilAbierto(false); navigate('/login'); }
  }, [clearAuth, navigate]);

  const handleBuscar = useCallback((e) => {
    e.preventDefault();
    if (terminoBusqueda.trim()) {
      navigate(`/buscar?q=${encodeURIComponent(terminoBusqueda.trim())}`);
      setBuscadorAbierto(false);
      cerrarMenu();
      setTerminoBusqueda('');
    }
  }, [terminoBusqueda, navigate, cerrarMenu]);

  const enlaceActivo = useCallback(
    (path) => path === '/' ? location.pathname === '/' : location.pathname.startsWith(path),
    [location.pathname]
  );

  const userInitial = useMemo(() => {
    if (!user) return 'U';
    return (user.nombres?.charAt(0) || user.email?.charAt(0) || 'U').toUpperCase();
  }, [user]);

  return (
    <>
      <header ref={navbarRef} className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>

        {/* ══ FRANJA SUPERIOR ══ */}
        <div className="navbar-top">

          {/* Brand */}
          <Link to="/" className="navbar-brand" onClick={cerrarMenu}>
            <img
              src="/img/Logo-comunidad/Logo-principal.png"
              alt="Logo Comunidad Campesina Zapotal"
              className="navbar-logo-img"
            />
            <div className="navbar-brand-text">
              <strong>Comunidad Zapotal</strong>
            </div>
          </Link>

          {/* Acciones */}
          <div className="navbar-actions">

            {/* Buscador — solo desktop */}
            <div className="buscador-box">
              <button
                className="circle-btn"
                onClick={() => setBuscadorAbierto(prev => !prev)}
                aria-label="Buscar"
                title="Buscar"
              >
                <FaSearch />
              </button>
              {buscadorAbierto && (
                <form className="buscador-dropdown" onSubmit={handleBuscar}>
                  <input
                    type="text"
                    placeholder="Buscar noticias..."
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
                  onClick={() => setPerfilAbierto(prev => !prev)}
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
                      <div className="profile-info-name">{user.nombres} {user.apellidos}</div>
                      <div className="profile-info-email">{user.email}</div>
                    </div>
                    <div className="profile-options">
                      <Link to="/perfil" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                        <FaUser /> Ver perfil
                      </Link>
                      <Link to="/perfil" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                        <FaCog /> Configuración
                      </Link>
                      {isAdmin && (
                        <Link to="/admin" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                          <FaShieldAlt /> Panel admin
                        </Link>
                      )}
                      <button className="profile-option logout-btn" onClick={handleLogout}>
                        <FaSignOutAlt /> Cerrar sesión
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="auth-buttons">
                <Link to="/login"    className="btn-ingresar">Ingresar</Link>
                <Link to="/registro" className="btn-registrarse">Registrarse</Link>
              </div>
            )}

            {/* Hamburguesa — solo móvil/tablet */}
            <button
              className={`burger-btn ${menuAbierto ? 'burger-open' : ''}`}
              onClick={() => setMenuAbierto(prev => !prev)}
              aria-label={menuAbierto ? 'Cerrar menú' : 'Abrir menú'}
            >
              <span className="burger-bar" />
              <span className="burger-bar" />
              <span className="burger-bar" />
            </button>
          </div>
        </div>

        {/* ══ FRANJA NAV — solo desktop ══ */}
        <div className="navbar-nav-wrapper">
          <nav className="nav-links nav-desktop">
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

            <div className={`dropdown ${nosotrosAbierto ? 'dropdown-open' : ''}`}>
              <button
                className={`nav-link dropdown-title ${enlaceActivo('/nosotros') ? 'activo' : ''}`}
                onClick={() => setNosotrosAbierto(prev => !prev)}
              >
                <span className="nav-icon"><FaUsers /></span>
                Nosotros <FaChevronDown className="dropdown-arrow" />
              </button>
              <div className="dropdown-menu">
                <Link to="/nosotros/historia">Nuestra historia</Link>
                <Link to="/nosotros/conocenos">Conócenos</Link>
              </div>
            </div>
          </nav>
        </div>
      </header>

      {/* ══ OVERLAY ══ */}
      {menuAbierto && (
        <div className="nav-overlay" onClick={cerrarMenu} aria-hidden="true" />
      )}

      {/* ══ PANEL LATERAL MÓVIL ══ */}
      <nav className={`nav-drawer ${menuAbierto ? 'nav-drawer-open' : ''}`} aria-label="Menú principal">

        {/* Cabecera */}
        <div className="drawer-header">
          <img src="/img/Logo-comunidad/Logo-principal.png" alt="Logo" className="drawer-logo" />
          <div className="drawer-brand">
            <p className="drawer-title">Comunidad Zapotal</p>
            <p className="drawer-sub">Portal Oficial</p>
          </div>
          <button className="drawer-close" onClick={cerrarMenu} aria-label="Cerrar menú">
            <FaTimes />
          </button>
        </div>

        {/* Buscador */}
        <div className="drawer-search">
          <form onSubmit={handleBuscar}>
            <FaSearch className="drawer-search-icon" />
            <input
              type="text"
              placeholder="Buscar noticias..."
              value={terminoBusqueda}
              onChange={(e) => setTerminoBusqueda(e.target.value)}
              maxLength={100}
            />
            {terminoBusqueda && (
              <button type="submit" className="drawer-search-btn">Ir</button>
            )}
          </form>
        </div>

        {/* Usuario logueado — mini card */}
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
              <p className="drawer-user-name">{user.nombres} {user.apellidos}</p>
              <p className="drawer-user-email">{user.email}</p>
            </div>
          </div>
        )}

        {/* Sección: Navegación */}
        <div className="drawer-section-label">Navegación</div>
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
              onClick={() => setNosotrosAbierto(prev => !prev)}
            >
              <span className="drawer-icon"><FaUsers /></span>
              Nosotros
              <FaChevronDown className="drawer-accordion-arrow" />
            </button>
            <div className="drawer-accordion-body">
              <Link to="/nosotros/historia" className="drawer-sub-link" onClick={cerrarMenu}>
                Nuestra historia
              </Link>
              <Link to="/nosotros/conocenos" className="drawer-sub-link" onClick={cerrarMenu}>
                Conócenos
              </Link>
            </div>
          </div>
        </div>

        {/* Sección: Cuenta */}
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
                Configuración
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
                <FaSignOutAlt /> Cerrar sesión
              </button>
            </div>
          </>
        ) : (
          <div className="drawer-auth">
            <Link to="/login"    className="drawer-btn-ingresar"    onClick={cerrarMenu}>Ingresar</Link>
            <Link to="/registro" className="drawer-btn-registrarse" onClick={cerrarMenu}>Registrarse</Link>
          </div>
        )}
      </nav>
    </>
  );
}

export default Navbar;