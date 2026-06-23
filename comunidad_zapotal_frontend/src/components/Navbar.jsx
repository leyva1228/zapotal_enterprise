import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  FaChevronDown, FaSignOutAlt, FaUser, FaCog,
  FaBars, FaTimes, FaSearch, FaShieldAlt,
} from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';
import './Navbar.css';

const PUBLIC_LINKS = [
  { to: '/', label: 'Inicio' },
  { to: '/noticias', label: 'Noticias' },
  { to: '/eventos', label: 'Eventos' },
  { to: '/autoridades', label: 'Autoridades' },
  { to: '/contactanos', label: 'Contacto' },
  { to: '/donaciones', label: 'Donaciones' },
];

const ADMIN_LINK = { to: '/admin', label: 'Admin' };

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const navbarRef = useRef(null);
  const buscadorRef = useRef(null);

  const { user, isAuthenticated, clearAuth } = useAuth();
  const [perfilAbierto, setPerfilAbierto] = useState(false);
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [nosotrosAbierto, setNosotrosAbierto] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [buscadorAbierto, setBuscadorAbierto] = useState(false);
  const [terminoBusqueda, setTerminoBusqueda] = useState('');

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

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

  const handleLogout = async () => {
    try {
      await clearAuth();
    } finally {
      navigate('/login');
    }
  };

  const handleBuscar = (e) => {
    e.preventDefault();
    if (terminoBusqueda.trim()) {
      navigate(`/buscar?q=${encodeURIComponent(terminoBusqueda)}`);
      setBuscadorAbierto(false);
      setTerminoBusqueda('');
    }
  };

  const cerrarMenu = () => setMenuAbierto(false);

  const enlaceActivo = (path) => {
    if (path === '/') return location.pathname === '/';
    if (path === '/nosotros/historia' || path === '/nosotros/conocenos')
      return location.pathname.startsWith('/nosotros');
    return location.pathname.startsWith(path);
  };

  // Lee isAdmin del AuthContext. Si no existe, intenta del usuario.
  const { isAdmin: isAdminCtx } = useAuth();
  const isAdmin = !!isAdminCtx;

  const enlaces = isAdmin ? [...PUBLIC_LINKS, ADMIN_LINK] : PUBLIC_LINKS;

  return (
    <header ref={navbarRef} className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
      <Link to="/" className="navbar-brand" onClick={cerrarMenu}>
        <img src="/img/Logo-comunidad/Logo-principal.png" alt="Logo" />
        <div>
          <strong>Comunidad Campesina</strong>
          <span>Zapotal</span>
        </div>
      </Link>

      <button className="burger-btn" onClick={() => setMenuAbierto(!menuAbierto)} aria-label="Menu">
        {menuAbierto ? <FaTimes /> : <FaBars />}
      </button>

      {menuAbierto && <div className="nav-overlay" onClick={cerrarMenu} />}

      <nav className={`nav-links ${menuAbierto ? 'active' : ''}`}>
        {enlaces.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={enlaceActivo(to) ? 'activo' : ''}
            onClick={cerrarMenu}
          >
            {label}
          </Link>
        ))}

        <div className={`dropdown ${nosotrosAbierto ? 'dropdown-open' : ''}`}>
          <button
            className={`dropdown-title ${enlaceActivo('/nosotros') ? 'activo' : ''}`}
            onClick={() => setNosotrosAbierto(!nosotrosAbierto)}
          >
            Nosotros <FaChevronDown />
          </button>
          <div className="dropdown-menu">
            <Link to="/nosotros/historia" onClick={cerrarMenu}>Nuestra historia</Link>
            <Link to="/nosotros/conocenos" onClick={cerrarMenu}>Conocenos</Link>
          </div>
        </div>
      </nav>

      <div className="navbar-user">
        <div className="buscador-box" ref={buscadorRef}>
          <button
            className="circle-btn"
            onClick={() => setBuscadorAbierto(!buscadorAbierto)}
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

        <NotificationBell />

        {isAuthenticated && user ? (
          <div className="profile-box">
            <button
              className="profile-trigger"
              onClick={() => setPerfilAbierto(!perfilAbierto)}
              aria-label="Perfil"
            >
              {user.foto_perfil || user.foto_perfil_url ? (
                <img src={user.foto_perfil || user.foto_perfil_url} alt="Perfil" className="profile-img" />
              ) : (
                <div className="profile-letter">
                  {(user.nombres?.charAt(0) || user.email?.charAt(0) || 'U').toUpperCase()}
                </div>
              )}
            </button>
            {perfilAbierto && (
              <div className="profile-dropdown">
                <div className="profile-info-header">
                  <div className="profile-avatar-sm">
                    {(user.nombres?.charAt(0) || user.email?.charAt(0) || 'U').toUpperCase()}
                  </div>
                  <div className="profile-info-name">{user.nombres} {user.apellidos}</div>
                  <div className="profile-info-email">{user.email}</div>
                </div>
                <div className="profile-options">
                  <Link to="/perfil" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                    <FaUser /> Ver perfil
                  </Link>
                  <Link to="/perfil" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                    <FaCog /> Configuracion
                  </Link>
                  {isAdmin && (
                    <Link to="/admin" className="profile-option" onClick={() => setPerfilAbierto(false)}>
                      <FaShieldAlt /> Panel admin
                    </Link>
                  )}
                  <button className="profile-option logout-btn" onClick={handleLogout}>
                    <FaSignOutAlt /> Cerrar sesion
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
