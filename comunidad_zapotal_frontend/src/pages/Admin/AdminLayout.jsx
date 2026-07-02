/**
 * AdminLayout - Shell del panel administrador.
 *
 * LOOP 1 (rediseño):
 * - Sidebar con header "COMUNIDAD / ZAPOTAL" (2 lineas).
 * - Items planos (sin subcategorias; los filtros viven en cada pagina).
 * - Cajita de perfil sticky al fondo con foto, nombre, cargo, estado, logout.
 * - Ancho FIJO (no arrastrable, no redimensionable).
 *
 * LOOP 2 (header):
 * - Header blanco minimalista: titulo al centro + 3 iconos a la derecha.
 * - Sin pill de usuario (vive en el sidebar).
 */
import React, { useEffect, useState, useMemo, useRef } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import {
  FaTachometerAlt, FaUsers, FaNewspaper, FaCalendarAlt, FaCommentDots,
  FaEnvelope, FaLandmark, FaHandHoldingHeart, FaListAlt, FaCog, FaUserCircle,
  FaSignOutAlt, FaHome, FaSync, FaBell, FaBars,
} from 'react-icons/fa';
import { useAuth } from '../../context/AuthContext';
import api from '../../api';
import './AdminLayout.css';

// Items del sidebar en el orden pedido por el usuario.
// Galeria se administra desde Institucional (tab Galeria).
// Perfil como item independiente al final.
const MENU_ITEMS = [
  { to: '/admin',                label: 'Dashboard',     icon: <FaTachometerAlt /> },
  { to: '/admin/usuarios',       label: 'Usuarios',      icon: <FaUsers /> },
  { to: '/admin/noticias',       label: 'Noticias',      icon: <FaNewspaper /> },
  { to: '/admin/eventos',        label: 'Eventos',       icon: <FaCalendarAlt /> },
  { to: '/admin/notificaciones', label: 'Mensajeria',    icon: <FaEnvelope /> },
  { to: '/admin/comentarios',    label: 'Comentarios',   icon: <FaCommentDots /> },
  { to: '/admin/autoridades',    label: 'Autoridades',   icon: <FaLandmark /> },
  { to: '/admin/donaciones',     label: 'Donaciones',    icon: <FaHandHoldingHeart /> },
  { to: '/admin/institucional',  label: 'Contenido',     icon: <FaListAlt /> },
  { to: '/admin/auditoria',      label: 'Sistema',       icon: <FaCog /> },
  { to: '/admin/perfil',         label: 'Perfil',        icon: <FaUserCircle /> },
];

// Mapeo: pathname -> query param que define la subseccion + label default.
const SUBSECTION_MAP = {
  '/admin/usuarios':       { param: 'estado',        default: 'Todos' },
  '/admin/comentarios':    { param: 'estado',        default: 'Todos' },
  '/admin/noticias':       { param: 'estadoNoticia', default: 'Publicadas' },
  '/admin/eventos':        { param: 'estadoEvento',  default: 'Activos' },
  '/admin/donaciones':     { param: 'estado',        default: 'Todas' },
  '/admin/autoridades':    { param: 'nivel',         default: 'Directiva Comunal' },
  '/admin/bajas':          { param: 'estado',        default: 'Pendientes' },
  '/admin/notificaciones': { param: 'leido',         default: 'Todas' },
  '/admin/auditoria':      { param: null,            default: '' },
  '/admin/reclamaciones':  { param: 'estado',        default: 'Pendientes' },
  '/admin/contacto':       { param: null,            default: '' },
  '/admin/perfil':         { param: null,            default: '' },
  '/admin/institucional':  { param: null,            default: '' },
};

// Labels legibles para los valores de subseccion.
const SUBSECTION_LABELS = {
  estado: {
    '':                       'Todos',
    'PENDIENTE':              'Pendientes',
    'PENDIENTE_OTP':          'Pendientes',
    'PENDIENTE_APROBACION':   'Pendientes',
    'ACTIVO':                 'Activos',
    'BLOQUEADO':              'Bloqueados',
    'INACTIVO':               'Inactivos',
    'RECHAZADO':              'Rechazados',
    'RECHAZADA':              'Rechazadas',
    'CANCELADA':              'Canceladas',
    'PUBLICADA':              'Publicadas',
    'OCULTO':                 'Censurados',
    'EN_PROCESO':             'En proceso',
    'RESUELTO':               'Resueltos',
    'VENCIDO':                'Vencidos',
    'APROBADO':               'Aprobadas',
  },
  estadoNoticia: {
    '':           'Todos',
    'PUBLICADA':  'Publicadas',
    'BORRADOR':   'Borradores',
    'ARCHIVADA':  'Archivadas',
  },
  estadoEvento: {
    '':            'Todos',
    'activos':     'Activos',
    'finalizados': 'Finalizados',
  },
  nivel: {
    'COMUNAL':   'Directiva Comunal',
    'MUNICIPAL': 'Municipalidad',
    'POLITICO':  'Autoridad Politica',
    '__STATS__': 'Estadisticas',
  },
  leido: {
    '':      'Todas',
    'true':  'Leidas',
    'false': 'No leidas',
  },
};

function getTituloYSubseccion(pathname, searchParams) {
  const item = MENU_ITEMS.find((i) => i.to === pathname);
  const titulo = item ? item.label : 'Administracion';
  const config = SUBSECTION_MAP[pathname];
  if (!config || !config.param) {
    return { titulo, subseccion: '' };
  }
  const value = searchParams.get(config.param) || '';
  const subseccion = SUBSECTION_LABELS[config.param]?.[value] || value;
  return { titulo, subseccion };
}

function getRoleLabel(user) {
  if (!user) return '';
  if (user.tipo_usuario === 'ADMIN') return 'Administrador';
  if (user.tipo_usuario === 'COMUNERO') return 'Comunero';
  return 'Comunero';
}

function getStatusLabel(user) {
  if (!user) return '';
  const e = user.estado;
  if (e === 'ACTIVO') return 'Vigente';
  if (e === 'INACTIVO') return 'Inactivo';
  if (e === 'BLOQUEADO') return 'Bloqueado';
  if (e === 'RECHAZADO') return 'Rechazado';
  if (e === 'PENDIENTE_APROBACION') return 'Pendiente aprobacion';
  if (e === 'PENDIENTE_OTP') return 'Pendiente verificacion';
  return e;
}

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { user, clearAuth } = useAuth();

  const SIDEBAR_WIDTH = 260;
  const SIDEBAR_COLLAPSED_WIDTH = 92;

  const [notifNoLeidas, setNotifNoLeidas] = useState(0);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [profileFloatOpen, setProfileFloatOpen] = useState(false);

  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth > 900) {
        setMobileNavOpen(false);
      }
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    let cancelado = false;
    const cargar = async () => {
      try {
        const { data } = await api.get('/notificaciones/no-leidas/count/');
        if (!cancelado) setNotifNoLeidas(data.count || 0);
      } catch {
        /* silencioso */
      }
    };
    cargar();
    const id = setInterval(cargar, 30000);
    const handler = () => cargar();
    window.addEventListener('notificaciones:actualizadas', handler);
    return () => {
      cancelado = true;
      clearInterval(id);
      window.removeEventListener('notificaciones:actualizadas', handler);
    };
  }, []);

  const handleLogout = async () => {
    try {
      await clearAuth();
    } finally {
      navigate('/login');
    }
  };

  const handleRefresh = () => {
    window.dispatchEvent(new CustomEvent('admin:refresh'));
  };

  const toggleSidebar = () => {
    if (typeof window !== 'undefined' && window.innerWidth <= 900) {
      setMobileNavOpen((prev) => !prev);
      return;
    }
    setSidebarCollapsed((prev) => !prev);
  };

  const closeMobileNav = () => {
    setMobileNavOpen(false);
  };

  const profileFloatRef = useRef(null);
  const profileTriggerRef = useRef(null);

  useEffect(() => {
    if (!profileFloatOpen) return;
    const handleClick = (e) => {
      if (
        profileFloatRef.current && !profileFloatRef.current.contains(e.target) &&
        profileTriggerRef.current && !profileTriggerRef.current.contains(e.target)
      ) {
        setProfileFloatOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [profileFloatOpen]);

  const { titulo, subseccion } = useMemo(
    () => getTituloYSubseccion(location.pathname, searchParams),
    [location.pathname, searchParams],
  );

  return (
    <div
      className={[
        'admin-shell',
        sidebarCollapsed ? 'admin-shell--collapsed' : '',
        mobileNavOpen ? 'admin-shell--nav-open' : '',
      ].filter(Boolean).join(' ')}
      style={{
        '--sidebar-width': `${SIDEBAR_WIDTH}px`,
        '--sidebar-collapsed-width': `${SIDEBAR_COLLAPSED_WIDTH}px`,
      }}
    >
      <button
        type="button"
        className={mobileNavOpen ? 'admin-sidebar__backdrop admin-sidebar__backdrop--visible' : 'admin-sidebar__backdrop'}
        aria-label="Cerrar menu lateral"
        onClick={closeMobileNav}
      />

      {/* ===== SIDEBAR FIJO (no arrastrable) ===== */}
      <aside
        className="admin-sidebar"
        style={{
          width: sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
          flexShrink: 0,
        }}
      >
        <div className="admin-sidebar__ambient" aria-hidden="true" />
        {/* Header del sidebar */}
        <div className="admin-sidebar__header">
          <button
            type="button"
            className="admin-sidebar__logo-btn"
            onClick={toggleSidebar}
            aria-label={sidebarCollapsed || mobileNavOpen ? 'Expandir menu lateral' : 'Contraer menu lateral'}
            title={sidebarCollapsed || mobileNavOpen ? 'Expandir menu lateral' : 'Contraer menu lateral'}
          >
            <img
              className="admin-sidebar__logo-img"
              src="/img/Logo-comunidad/Logo-principal.png"
              alt="Logo Comunidad Zapotal"
            />
          </button>
          <div className="admin-sidebar__header-text">
            <div className="admin-sidebar__eyebrow">Panel administrativo</div>
            <div className="admin-sidebar__title-line1">COMUNIDAD</div>
            <div className="admin-sidebar__title-line2">ZAPOTAL</div>
          </div>
        </div>

        {/* Lista plana de items */}
        <nav className="admin-sidebar__nav">
          {MENU_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/admin'}
              onClick={closeMobileNav}
              className={({ isActive }) =>
                'admin-sidebar__item' + (isActive ? ' admin-sidebar__item--active' : '')
              }
            >
              <span className="admin-sidebar__icon">{item.icon}</span>
              <span className="admin-sidebar__label">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Cajita de perfil STICKY al fondo del sidebar */}
        <div className="admin-profile-card">
          <button
            type="button"
            className="admin-profile-card__logout"
            onClick={handleLogout}
            title="Cerrar sesion"
            aria-label="Cerrar sesion"
          >
            <FaSignOutAlt />
          </button>
          <div className="admin-profile-card__photo">
            {user?.foto_perfil_url ? (
              <img src={user.foto_perfil_url} alt="Foto de perfil" />
            ) : (
              <FaUserCircle />
            )}
          </div>
          <div className="admin-profile-card__name">
            {user?.nombre_completo || user?.email || 'Usuario'}
          </div>
          <div className="admin-profile-card__role">
            {getRoleLabel(user)}
          </div>
          <div className="admin-profile-card__status">
            <span
              className={
                'admin-profile-card__status-dot'
                + (user?.estado === 'ACTIVO' ? ' admin-profile-card__status-dot--ok' : '')
              }
            />
            {getStatusLabel(user)}
          </div>
        </div>

        {/* Trigger circulo del perfil cuando sidebar esta colapsado */}
        <button
          type="button"
          ref={profileTriggerRef}
          className={'admin-profile-card__trigger' + (profileFloatOpen ? ' admin-profile-card__trigger--open' : '')}
          onClick={() => setProfileFloatOpen(v => !v)}
          aria-label="Abrir perfil"
          title="Abrir perfil"
        >
          {user?.foto_perfil_url ? (
            <img src={user.foto_perfil_url} alt="Foto de perfil" />
          ) : (
            <FaUserCircle />
          )}
        </button>

        {/* Card flotante de perfil al hacer click en trigger */}
        {profileFloatOpen && (
          <div className="admin-profile-card__float" ref={profileFloatRef}>
            <button
              type="button"
              className="admin-profile-card__float-close"
              onClick={() => setProfileFloatOpen(false)}
              aria-label="Cerrar perfil"
            >
              &times;
            </button>
            <button
              type="button"
              className="admin-profile-card__float-logout"
              onClick={handleLogout}
              title="Cerrar sesion"
              aria-label="Cerrar sesion"
            >
              <FaSignOutAlt />
            </button>
            <div className="admin-profile-card__float-photo">
              {user?.foto_perfil_url ? (
                <img src={user.foto_perfil_url} alt="Foto de perfil" />
              ) : (
                <FaUserCircle />
              )}
            </div>
            <div className="admin-profile-card__float-name">
              {user?.nombre_completo || user?.email || 'Usuario'}
            </div>
            <div className="admin-profile-card__float-role">
              {getRoleLabel(user)}
            </div>
            <div className="admin-profile-card__float-status">
              <span
                className={
                  'admin-profile-card__float-status-dot'
                  + (user?.estado === 'ACTIVO' ? ' admin-profile-card__float-status-dot--ok' : '')
                }
              />
              {getStatusLabel(user)}
            </div>
          </div>
        )}
      </aside>

      {/* ===== MAIN ===== */}
      <div className="admin-main">
        {/* Header blanco */}
        <header className="admin-topbar">
          <div className="admin-topbar__center">
            <button
              type="button"
              className="admin-topbar__logo-toggle"
              onClick={toggleSidebar}
              aria-label="Mostrar u ocultar menu lateral"
              title="Mostrar u ocultar menu lateral"
            >
              <FaBars className="admin-topbar__hamburger" />
              <img
                className="admin-topbar__logo-toggle-img"
                src="/img/Logo-comunidad/Logo-principal.png"
                alt="Logo Comunidad Zapotal"
              />
            </button>
            <div className="admin-topbar__heading">
              <span className="admin-topbar__eyebrow">Centro de control</span>
              <h1 className="admin-topbar__title">{titulo}</h1>
              {subseccion && (
                <span className="admin-topbar__subtitle">{subseccion}</span>
              )}
            </div>
          </div>
          <div className="admin-topbar__right">
            <Link
              to="/"
              className="admin-topbar__icon-btn"
              title="Ir al sitio publico"
              aria-label="Ir al sitio publico"
            >
              <FaHome />
            </Link>
            <button
              type="button"
              className="admin-topbar__icon-btn"
              onClick={handleRefresh}
              title="Recargar data"
              aria-label="Recargar data"
            >
              <FaSync />
            </button>
            <button
              type="button"
              className="admin-topbar__icon-btn admin-topbar__icon-btn--notif"
              onClick={() => navigate('/admin/notificaciones')}
              title="Notificaciones"
              aria-label="Notificaciones"
            >
              <FaBell />
              {notifNoLeidas > 0 && (
                <span className="admin-topbar__badge">{notifNoLeidas > 99 ? '99+' : notifNoLeidas}</span>
              )}
            </button>
          </div>
        </header>

        {/* Contenido */}
        <main className="admin-content">
          <div className="admin-content__inner">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
