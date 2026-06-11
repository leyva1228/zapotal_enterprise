import React, { useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  FaTachometerAlt, FaNewspaper, FaCalendarAlt, FaTags, FaUsers,
  FaUserShield, FaCommentDots, FaSignOutAlt, FaUser, FaChevronLeft, FaHome,
} from "react-icons/fa";
import "./AdminLayout.css";

const MENU = [
  { to: "/admin", icon: <FaTachometerAlt />,  label: "Dashboard",  end: true },
  { to: "/admin/noticias",   icon: <FaNewspaper />,  label: "Noticias" },
  { to: "/admin/eventos",    icon: <FaCalendarAlt />, label: "Eventos" },
  { to: "/admin/categorias", icon: <FaTags />,        label: "Categorías" },
  { to: "/admin/autoridades",icon: <FaUsers />,       label: "Autoridades" },
  { to: "/admin/usuarios",   icon: <FaUserShield />,  label: "Usuarios" },
  { to: "/admin/comentarios",icon: <FaCommentDots />, label: "Comentarios" },
];

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const usuario = (() => {
    try { return JSON.parse(localStorage.getItem("usuario") || "null"); }
    catch { return null; }
  })();

  if (!usuario || usuario.tipo_usuario !== "ADMIN") {
    return (
      <main className="admin-denied">
        <div className="admin-denied-card">
          <h1>Acceso restringido</h1>
          <p>Solo los administradores pueden acceder al panel.</p>
          <Link to="/login" className="admin-btn admin-btn-primary">Iniciar sesión</Link>
        </div>
      </main>
    );
  }

  const handleLogout = () => {
    localStorage.removeItem("usuario");
    localStorage.removeItem("token");
    localStorage.removeItem("refresh");
    navigate("/login");
  };

  return (
    <div className={`admin-shell${collapsed ? " admin-shell--collapsed" : ""}`}>
      <aside className="admin-sidebar">
        <div className="admin-sidebar__brand">
          <span className="admin-sidebar__logo">Z</span>
          {!collapsed && <span className="admin-sidebar__title">Zapotal Admin</span>}
        </div>
        <nav className="admin-sidebar__nav">
          {MENU.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                "admin-sidebar__link" + (isActive ? " admin-sidebar__link--active" : "")
              }
            >
              <span className="admin-sidebar__icon">{item.icon}</span>
              {!collapsed && <span className="admin-sidebar__label">{item.label}</span>}
            </NavLink>
          ))}
        </nav>
        <button
          type="button"
          className="admin-sidebar__collapse"
          onClick={() => setCollapsed(c => !c)}
          title={collapsed ? "Expandir" : "Colapsar"}
        >
          <FaChevronLeft style={{ transform: collapsed ? "rotate(180deg)" : "none" }} />
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
            <div className="admin-topbar__user" title={usuario.email}>
              <FaUser />
              <span>{usuario.nombre_completo || usuario.email}</span>
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
  if (path === "/admin") return "Dashboard";
  const item = MENU.find(m => m.to !== "/admin" && path.startsWith(m.to));
  return item ? item.label : "Administración";
}
