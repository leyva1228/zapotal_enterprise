import React, { useEffect, useState, useRef, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaBell } from "react-icons/fa";
import api from "../api";
import { useAuth } from "../context/AuthContext";
import { extractList } from "../api";
import "./NotificationBell.css";

const INTERVAL = 60_000; // 60s polling

function timeAgo(str) {
  if (!str) return "";
  const d = new Date(str);
  if (isNaN(d.getTime())) return "";
  const diff = Date.now() - d.getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "ahora";
  if (min < 60) return `hace ${min} min`;
  const h = Math.floor(min / 60);
  if (h < 24) return `hace ${h} h`;
  return `hace ${Math.floor(h / 24)} d`;
}

function destinoInterno(url) {
  if (!url) return null;
  // Solo enlaces relativos al frontend.
  if (url.startsWith("http://") || url.startsWith("https://")) return null;
  return url;
}

export default function NotificationBell() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const cargar = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const [contador, list] = await Promise.all([
        api.get('/notificaciones/contador-no-leidas/'),
        api.get('/notificaciones/?leido=false&page_size=5'),
      ]);
      setUnread(contador.data?.count || 0);
      const raw = list.data;
      const arr = Array.isArray(raw) ? raw : (raw?.results || []);
      setItems(arr);
    } catch (e) {
      // ignore
    }
  }, [isAuthenticated]);

  useEffect(() => {
    cargar();
    const id = setInterval(cargar, INTERVAL);
    const onVis = () => { if (!document.hidden) cargar(); };
    document.addEventListener('visibilitychange', onVis);
    return () => { clearInterval(id); document.removeEventListener('visibilitychange', onVis); };
  }, [cargar]);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  const marcarLeida = async (n) => {
    try {
      await api.patch(`/notificaciones/${n.id}/`, { leido: true });
      setItems((prev) => prev.filter((x) => x.id !== n.id));
      setUnread((u) => Math.max(0, u - 1));
      const destino = destinoInterno(n.url_destino);
      if (destino) {
        setOpen(false);
        navigate(destino);
      }
    } catch (e) {
      // ignore
    }
  };

  const marcarTodas = async () => {
    try {
      await api.post('/notificaciones/marcar-todas-leidas/');
      setItems([]);
      setUnread(0);
    } catch (e) {
      // ignore
    }
  };

  const irAPerfil = () => {
    setOpen(false);
    navigate('/perfil?tab=notificaciones');
  };

  if (!isAuthenticated) return null;

  return (
    <div className="notif-bell" ref={ref}>
      <button
        type="button"
        className="notif-bell__btn"
        onClick={() => setOpen((o) => !o)}
        aria-label={`Notificaciones${unread > 0 ? ` (${unread} sin leer)` : ''}`}
        title="Notificaciones"
      >
        <FaBell />
        {unread > 0 && (
          <span className="notif-bell__badge" aria-hidden="true">
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="notif-bell__dropdown" role="menu">
          <header className="notif-bell__head">
            <h4>Notificaciones</h4>
            {unread > 0 && (
              <button className="notif-bell__link" type="button" onClick={marcarTodas}>
                Marcar todas leidas
              </button>
            )}
          </header>

          <div className="notif-bell__list">
            {items.length === 0 ? (
              <div className="notif-bell__empty">No tienes notificaciones nuevas.</div>
            ) : (
              items.map((n) => {
                const interno = destinoInterno(n.url_destino);
                const contenido = (
                  <>
                    <div className="notif-bell__item-title">{n.titulo}</div>
                    <div className="notif-bell__item-msg">{n.mensaje}</div>
                    <div className="notif-bell__item-time">{timeAgo(n.fecha)}</div>
                  </>
                );
                if (interno) {
                  return (
                    <Link
                      key={n.id}
                      to={interno}
                      className="notif-bell__item"
                      onClick={() => marcarLeida(n)}
                      role="menuitem"
                    >
                      {contenido}
                    </Link>
                  );
                }
                return (
                  <div
                    key={n.id}
                    className="notif-bell__item"
                    onClick={() => marcarLeida(n)}
                    role="menuitem"
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter') marcarLeida(n); }}
                  >
                    {contenido}
                  </div>
                );
              })
            )}
          </div>

          <footer className="notif-bell__foot">
            <button type="button" onClick={irAPerfil} className="notif-bell__ver-todas">
              Ver todas las notificaciones
            </button>
          </footer>
        </div>
      )}
    </div>
  );
}
