import React, { useState, useEffect } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  FaTachometerAlt, FaNewspaper, FaCalendarAlt, FaTags, FaUsers,
  FaUserShield, FaCommentDots, FaSignOutAlt, FaUser, FaChevronLeft, FaHome,
  FaHistory, FaEnvelope, FaBell, FaChevronDown, FaChevronRight,
  FaInbox, FaFlag, FaCog, FaListAlt, FaArchive, FaCheckCircle, FaUserCheck,
  FaHandHoldingHeart, FaMoneyBillWave, FaLandmark, FaBuilding, FaUserTie,
  FaChartPie, FaGavel,
} from 'react-icons/fa';
import { useAuth } from '../../context/AuthContext';
import api from '../../api';
import './AdminLayout.css';

const MENU_GROUPS = [
  {
    id: 'usuarios',
    title: 'Usuarios',
    icon: <FaUserShield />,
    items: [
      { to: '/admin/usuarios', label: 'Todos', icon: <FaUsers /> },
      { to: '/admin/usuarios', label: 'Pendientes', icon: <FaUserCheck />, state: 'PENDIENTE' },
      { to: '/admin/usuarios', label: 'Bloqueados', icon: <FaFlag />, state: 'BLOQUEADO' },
    ],
  },
  {
    id: 'comentarios',
    title: 'Comentarios',
    icon: <FaCommentDots />,
    items: [
      { to: '/admin/comentarios', label: 'Todos', icon: <FaListAlt /> },
      { to: '/admin/comentarios', label: 'Moderacion', icon: <FaCommentDots />, estado: 'PENDIENTE' },
      { to: '/admin/comentarios', label: 'Censurados', icon: <FaFlag />, estado: 'OCULTO' },
    ],
  },
  {
    id: 'noticias',
    title: 'Noticias',
    icon: <FaNewspaper />,
    items: [
      { to: '/admin/noticias', label: 'Publicadas', icon: <FaCheckCircle />, estadoNoticia: 'PUBLICADA' },
      { to: '/admin/noticias', label: 'Borradores', icon: <FaArchive />, estadoNoticia: 'BORRADOR' },
      { to: '/admin/categorias', label: 'Categorias', icon: <FaTags /> },
    ],
  },
  {
    id: 'eventos',
    title: 'Eventos',
    icon: <FaCalendarAlt />,
    items: [
      { to: '/admin/eventos', label: 'Activos', icon: <FaCheckCircle /> },
      { to: '/admin/eventos', label: 'Finalizados', icon: <FaArchive /> },
    ],
  },
  {
    id: 'contenido',
    title: 'Contenido',
    icon: <FaListAlt />,
    items: [
      { to: '/admin/bajas', label: 'Solicitudes de baja', icon: <FaUserShield /> },
      { to: '/admin/cms', label: 'CMS', icon: <FaCog /> },
      { to: '/admin/institucional', label: 'Institucional', icon: <FaCog /> },
    ],
  },
  {
    id: 'autoridades',
    title: 'Autoridades',
    icon: <FaLandmark />,
    items: [
      { to: '/admin/autoridades', label: 'Directiva Comunal',  icon: <FaUsers />,    nivel: 'COMUNAL' },
      { to: '/admin/autoridades', label: 'Municipalidad C.P.', icon: <FaBuilding />, nivel: 'MUNICIPAL' },
      { to: '/admin/autoridades', label: 'Autoridad Politica', icon: <FaUserTie />,  nivel: 'POLITICO' },
      { to: '/admin/comites-comunales', label: 'Comites Comunales', icon: <FaGavel /> },
      { to: '/admin/autoridades', label: 'Estadisticas',       icon: <FaChartPie />, nivel: '__STATS__' },
    ],
  },
  {
    id: 'mensajeria',
    title: 'Mensajeria',
    icon: <FaEnvelope />,
    items: [
      { to: '/admin/notificaciones', label: 'Notificaciones', icon: <FaBell />, badgeKey: 'notif' },
      { to: '/admin/contacto', label: 'Contacto', icon: <FaEnvelope /> },
      { to: '/admin/reclamaciones', label: 'Reclamaciones', icon: <FaInbox /> },
    ],
  },
  {
    id: 'donaciones',
    title: 'Donaciones',
    icon: <FaHandHoldingHeart />,
    items: [
      { to: '/admin/donaciones', label: 'Todas', icon: <FaListAlt /> },
      { to: '/admin/donaciones', label: 'Aprobadas', icon: <FaCheckCircle />, estado: 'APROBADO' },
      { to: '/admin/donaciones', label: 'Pendientes', icon: <FaArchive />, estado: 'PENDIENTE' },
      { to: '/admin/donaciones', label: 'Rechazadas', icon: <FaFlag />, estado: 'RECHAZADO' },
    ],
  },
  {
    id: 'sistema',
    title: 'Sistema',
    icon: <FaCog />,
    items: [
      { to: '/admin/auditoria', label: 'Auditoria', icon: <FaHistory /> },
    ],
  },
];

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [abiertos, setAbiertos] = useState(() => {
    const inicial = {};
    MENU_GROUPS.forEach((g) => { inicial[g.id] = true; });
    return inicial;
  });
  const { user, clearAuth } = useAuth();
  const [notifNoLeidas, setNotifNoLeidas] = useState(0);

  useEffect(() => {
    let cancelado = false;
    const cargar = async () => {
      try {
        const { data } = await api.get('/notificaciones/no-leidas/count/');
        if (!cancelado) setNotifNoLeidas(data.count || 0);
      } catch {
        /* silencioso: badge no aparece */
      }
    };
    cargar();
    const id = setInterval(cargar, 30000);
    // Loop 3.6: decrementar inmediatamente cuando se marca leida en otra pagina.
    const handler = () => cargar();
    window.addEventListener('notificaciones:actualizadas', handler);
    return () => {
      cancelado = true;
      clearInterval(id);
      window.removeEventListener('notificaciones:actualizadas', handler);
    };
  }, []);

  const toggleGrupo = (id) => setAbiertos((prev) => ({ ...prev, [id]: !prev[id] }));

  const handleLogout = async () => {
    try {
      await clearAuth();
    } finally {
      navigate('/login');
    }
  };

  const renderItem = (item) => {
    const params = new URLSearchParams();
    if (item.estado)      params.set('estado', item.estado);
    if (item.estadoNoticia) params.set('estadoNoticia', item.estadoNoticia);
    if (item.state)       params.set('state', item.state);
    if (item.nivel)       params.set('nivel', item.nivel);
    const search = params.toString();
    const to = search ? `${item.to}?${search}` : item.to;
    const badge = item.badgeKey === 'notif' && notifNoLeidas > 0 ? notifNoLeidas : null;

    return (
      <NavLink
        key={`${item.to}-${item.label}`}
        to={to}
        end={item.to === '/admin'}
        className={({ isActive }) =>
          'admin-sidebar__sublink' + (isActive && location.search === (search ? `?${search}` : '') ? ' admin-sidebar__sublink--active' : '')
        }
      >
        <span className="admin-sidebar__subicon">{item.icon}</span>
        {!collapsed && <span>{item.label}</span>}
        {!collapsed && badge !== null && (
          <span className="admin-sidebar__badge admin-sidebar__badge--warn">{badge}</span>
        )}
      </NavLink>
    );
  };

  return (
    <div className={`admin-shell${collapsed ? ' admin-shell--collapsed' : ''}`}>
      <aside className="admin-sidebar">
        <div className="admin-sidebar__brand">
          <span className="admin-sidebar__logo">Z</span>
          {!collapsed && <span className="admin-sidebar__title">Zapotal Admin</span>}
        </div>
        <nav className="admin-sidebar__nav">
          <NavLink
            to="/admin"
            end
            className={({ isActive }) =>
              'admin-sidebar__link' + (isActive ? ' admin-sidebar__link--active' : '')
            }
          >
            <span className="admin-sidebar__icon"><FaTachometerAlt /></span>
            {!collapsed && <span className="admin-sidebar__label">Dashboard</span>}
          </NavLink>

          {MENU_GROUPS.map((grupo) => (
            <div key={grupo.id} className="admin-sidebar__group">
              {!collapsed && (
                <button
                  type="button"
                  className={`admin-sidebar__group-title ${abiertos[grupo.id] ? 'is-open' : ''}`}
                  onClick={() => toggleGrupo(grupo.id)}
                >
                  <span className="admin-sidebar__icon">{grupo.icon}</span>
                  <span className="admin-sidebar__group-label">{grupo.title}</span>
                  <span className="admin-sidebar__group-chevron">
                    {abiertos[grupo.id] ? <FaChevronDown /> : <FaChevronRight />}
                  </span>
                </button>
              )}
              {collapsed && (
                <div className="admin-sidebar__group-title admin-sidebar__group-title--collapsed" title={grupo.title}>
                  {grupo.icon}
                </div>
              )}
              {abiertos[grupo.id] && (
                <div className="admin-sidebar__sublinks">
                  {grupo.items.map(renderItem)}
                </div>
              )}
            </div>
          ))}
        </nav>
        <button
          type="button"
          className="admin-sidebar__collapse"
          onClick={() => setCollapsed((c) => !c)}
          title={collapsed ? 'Expandir' : 'Colapsar'}
        >
          <FaChevronLeft className={collapsed ? 'rotate-180' : ''} />
          {!collapsed && <span>Colapsar</span>}
        </button>
      </aside>

      <div className="admin-main">
        <header className="admin-topbar">
          <div className="admin-topbar__left">
            <Link to="/" className="admin-topbar__back">
              <FaHome /> {!collapsed && <span>Ver sitio</span>}
            </Link>
            <h1 className="admin-topbar__title">{tituloRuta(location.pathname)}</h1>
          </div>
          <div className="admin-topbar__right">
            <div className="admin-topbar__user" title={user?.email}>
              <FaUser />
              <span>{user?.nombre_completo || user?.email}</span>
            </div>
            <button className="admin-btn admin-btn-ghost" onClick={handleLogout}>
              <FaSignOutAlt /> Salir
            </button>
          </div>
        </header>
        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function tituloRuta(path) {
  if (path === '/admin') return 'Dashboard';
  for (const g of MENU_GROUPS) {
    for (const it of g.items) {
      if (it.to === path) return `${g.title} - ${it.label}`;
    }
  }
  return 'Administracion';
}
