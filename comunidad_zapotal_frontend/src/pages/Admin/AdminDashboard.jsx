import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaNewspaper, FaCalendarAlt, FaTags, FaUsers, FaUserShield,
  FaCommentDots, FaThumbsUp, FaThumbsDown, FaChartLine,
  FaUserClock, FaHistory, FaEnvelope, FaBell, FaExclamationCircle,
  FaBook, FaClipboardList, FaHandHoldingHeart, FaMoneyBillWave,
} from "react-icons/fa";
import api, { extractList } from "../../api";
import { useAuth } from "../../context/AuthContext";

function StatCard({ icon, label, value, color, to }) {
  const Card = to ? Link : "div";
  const cardProps = to ? { to } : {};
  return (
    <Card {...cardProps} className={"dash-stat" + (to ? " dash-stat--link" : "")}>
      <div className={"dash-stat__icon " + color}>{icon}</div>
      <div>
        <div className="dash-stat__label">{label}</div>
        <div className="dash-stat__value">{value}</div>
      </div>
    </Card>
  );
}

function colorAccion(accion) {
  if (!accion) return "admin-badge--gray";
  if (accion.startsWith("LOGIN")) return "admin-badge--info";
  if (accion.startsWith("OTP")) return "admin-badge--warning";
  if (accion === "APPROVE" || accion === "UNBLOCK") return "admin-badge--success";
  if (accion === "REJECT" || accion === "BLOCK" || accion === "DELETE") return "admin-badge--danger";
  if (accion === "CREATE") return "admin-badge--info";
  if (accion === "UPDATE") return "admin-badge--warning";
  return "admin-badge--gray";
}

function timeAgo(str) {
  if (!str) return "";
  const d = new Date(str);
  if (isNaN(d.getTime())) return "";
  const diff = Date.now() - d.getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "hace un momento";
  if (min < 60) return `hace ${min} min`;
  const h = Math.floor(min / 60);
  if (h < 24) return `hace ${h} h`;
  const dd = Math.floor(h / 24);
  return `hace ${dd} d`;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    noticias: 0, eventos: 0, categorias: 0, autoridades: 0,
    usuarios: 0, comentarios: 0, likes: 0, dislikes: 0,
    pendientes: 0, audit24h: 0, reclamacionesPendientes: 0, mensajesContacto: 0,
    donacionesTotal: 0, donacionesAprobadas: 0, donacionesRecaudado: '0.00',
  });
  const [ultimasNoticias, setUltimasNoticias] = useState([]);
  const [proximosEventos, setProximosEventos] = useState([]);
  const [ultimaAuditoria, setUltimaAuditoria] = useState([]);
  const [ultimosReclamos, setUltimosReclamos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      try {
        const hace24h = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        const [n, e, c, a, u, co, re, pe, au, lr, cm, don] = await Promise.all([
          api.get("/noticias/?page_size=5").catch(() => ({ data: { data: [] } })),
          api.get("/eventos/?page_size=5").catch(() => ({ data: { data: [] } })),
          api.get("/categorias/").catch(() => ({ data: { data: [] } })),
          api.get("/autoridades/").catch(() => ({ data: { data: [] } })),
          api.get("/usuarios/?page_size=200").catch(() => ({ data: { data: [] } })),
          api.get("/comentarios/").catch(() => ({ data: { data: [] } })),
          api.get("/reacciones/").catch(() => ({ data: { data: [] } })),
          api.get("/usuarios/pendientes/").catch(() => ({ data: { count: 0, results: [] } })),
          api.get("/audit-log/?timestamp__gte=" + hace24h).catch(() => ({ data: { results: [] } })),
          api.get("/libro-reclamaciones/?estado=PENDIENTE").catch(() => ({ data: { results: [] } })),
          api.get("/contacto-mensajes/").catch(() => ({ data: { results: [] } })),
          api.get("/donaciones/estadisticas/").catch(() => ({ data: { cantidad_donaciones: 0, total_recaudado: '0.00' } })),
        ]);
        const nl = extractList(n.data);
        const el = extractList(e.data);
        const cl = extractList(c.data);
        const al = extractList(a.data);
        const ul = extractList(u.data);
        const col = extractList(co.data);
        const rl = extractList(re.data);
        const peCount = pe.data?.count ?? 0;
        const auList = extractList(au.data);
        const lrList = extractList(lr.data);
        const cmList = extractList(cm.data);
        const donData = don.data || {};
        setStats({
          noticias: nl.length,
          eventos: el.length,
          categorias: cl.length,
          autoridades: al.length,
          usuarios: ul.length,
          comentarios: col.length,
          likes: rl.filter(r => r.tipo === "LIKE").length,
          dislikes: rl.filter(r => r.tipo === "DISLIKE").length,
          pendientes: peCount,
          audit24h: auList.length,
          reclamacionesPendientes: lrList.length,
          mensajesContacto: cmList.length,
          donacionesAprobadas: donData.cantidad_donaciones || 0,
          donacionesTotal: (donData.donantes_unicos || 0),
          donacionesRecaudado: donData.total_recaudado || '0.00',
        });
        setUltimasNoticias(nl.slice(0, 5));
        setProximosEventos(el.slice(0, 5));
        setUltimaAuditoria(auList.slice(0, 6));
        setUltimosReclamos(lrList.slice(0, 5));
      } catch (e) {
        console.error("Dashboard load error", e);
      } finally {
        setLoading(false);
      }
    };
    cargar();
  }, []);

  return (
    <>
      <div className="dash-stats">
        <StatCard icon={<FaNewspaper />}     label="Noticias"             value={stats.noticias}    color="dash-stat__icon--blue"   to="/admin/noticias" />
        <StatCard icon={<FaCalendarAlt />}   label="Eventos"              value={stats.eventos}     color="dash-stat__icon--green"  to="/admin/eventos" />
        <StatCard icon={<FaTags />}          label="Categorias"           value={stats.categorias}  color="dash-stat__icon--yellow" to="/admin/categorias" />
        <StatCard icon={<FaUsers />}         label="Autoridades"          value={stats.autoridades} color="dash-stat__icon--purple" to="/admin/autoridades" />
        <StatCard icon={<FaUserShield />}    label="Usuarios"             value={stats.usuarios}    color="dash-stat__icon--cyan"   to="/admin/usuarios" />
        <StatCard icon={<FaUserClock />}     label="Pendientes"           value={stats.pendientes}  color="dash-stat__icon--yellow" to="/admin/usuarios/pendientes" />
        <StatCard icon={<FaCommentDots />}   label="Comentarios"          value={stats.comentarios} color="dash-stat__icon--blue"   to="/admin/comentarios" />
        <StatCard icon={<FaThumbsUp />}      label="Likes"                value={stats.likes}       color="dash-stat__icon--green" />
        <StatCard icon={<FaThumbsDown />}    label="Dislikes"             value={stats.dislikes}    color="dash-stat__icon--red" />
        <StatCard icon={<FaExclamationCircle />} label="Reclamos"          value={stats.reclamacionesPendientes} color="dash-stat__icon--red" to="/admin/reclamaciones" />
        <StatCard icon={<FaEnvelope />}      label="Mensajes contacto"    value={stats.mensajesContacto} color="dash-stat__icon--purple" to="/admin/contacto" />
        <StatCard icon={<FaHistory />}       label="Auditoria 24h"        value={stats.audit24h}    color="dash-stat__icon--cyan"   to="/admin/auditoria" />
        <StatCard icon={<FaHandHoldingHeart />} label="Donaciones aprobadas" value={stats.donacionesAprobadas} color="dash-stat__icon--green" to="/admin/donaciones" />
        <StatCard icon={<FaMoneyBillWave />}  label="Recaudado total"      value={`S/ ${stats.donacionesRecaudado}`} color="dash-stat__icon--emerald" to="/admin/donaciones" />
      </div>

      <div className="dash-grid">
        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaUserClock className="mr-[6px]" /> Pendientes de aprobacion
          </h3>
          {stats.pendientes === 0 ? (
            <p className="text-mute">No hay usuarios pendientes.</p>
          ) : (
            <div className="dash-action">
              <p className="text-[13px]">
                Hay <strong>{stats.pendientes}</strong> usuario(s) esperando aprobacion.
              </p>
              <Link to="/admin/usuarios/pendientes" className="admin-btn admin-btn-primary admin-btn-sm">
                <FaClipboardList /> Revisar pendientes
              </Link>
            </div>
          )}
        </div>

        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaChartLine className="mr-[6px]" /> Ultimas noticias
          </h3>
          {ultimasNoticias.length === 0 ? (
            <p className="text-mute">No hay noticias aun.</p>
          ) : (
            <ul className="dash-list">
              {ultimasNoticias.map(n => (
                <li key={n.id} className="dash-list__item">
                  <span className="dash-list__item__title">{n.titulo}</span>
                  <span className={"admin-badge " + (
                    n.estado === "PUBLICADA" ? "admin-badge--success" :
                    n.estado === "BORRADOR"  ? "admin-badge--warning" :
                                                 "admin-badge--gray"
                  )}>
                    {n.estado}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3">
            <Link to="/admin/noticias" className="admin-btn admin-btn-ghost admin-btn-sm">Ver todas</Link>
          </div>
        </div>

        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaCalendarAlt className="mr-[6px]" /> Proximos eventos
          </h3>
          {proximosEventos.length === 0 ? (
            <p className="text-mute">No hay eventos aun.</p>
          ) : (
            <ul className="dash-list">
              {proximosEventos.map(ev => (
                <li key={ev.id} className="dash-list__item">
                  <span className="dash-list__item__title">{ev.titulo}</span>
                  <span className="dash-list__item__meta">
                    {ev.fecha ? new Date(ev.fecha).toLocaleDateString("es-PE") : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3">
            <Link to="/admin/eventos" className="admin-btn admin-btn-ghost admin-btn-sm">Ver todos</Link>
          </div>
        </div>

        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaHistory className="mr-[6px]" /> Auditoria reciente
          </h3>
          {ultimaAuditoria.length === 0 ? (
            <p className="text-mute">Sin actividad en las ultimas 24h.</p>
          ) : (
            <ul className="dash-list">
              {ultimaAuditoria.map((it) => (
                <li key={it.id} className="dash-list__item">
                  <span className="dash-list__item__title">
                    <span className={"admin-badge mr-[6px] " + colorAccion(it.accion)}>
                      {it.accion}
                    </span>
                    {it.descripcion || it.modelo_afectado}
                  </span>
                  <span className="dash-list__item__meta">{timeAgo(it.timestamp)}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3">
            <Link to="/admin/auditoria" className="admin-btn admin-btn-ghost admin-btn-sm">
              Ver todo el registro
            </Link>
          </div>
        </div>

        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaBook className="mr-[6px]" /> Reclamaciones pendientes
          </h3>
          {ultimosReclamos.length === 0 ? (
            <p className="text-mute">Sin reclamaciones pendientes.</p>
          ) : (
            <ul className="dash-list">
              {ultimosReclamos.map((r) => (
                <li key={r.id} className="dash-list__item">
                  <span className="dash-list__item__title">
                    <strong>#{r.id}</strong> {r.nombre} - {r.tipo}
                  </span>
                  <span className="dash-list__item__meta">{timeAgo(r.fecha)}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3">
            <Link to="/admin/reclamaciones" className="admin-btn admin-btn-ghost admin-btn-sm">
              Gestionar reclamaciones
            </Link>
          </div>
        </div>

        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaBell className="mr-[6px]" /> Accesos rapidos
          </h3>
          <div className="flex flex-col">
            <Link to="/admin/notificaciones" className="admin-btn admin-btn-ghost admin-btn-sm">
              <FaBell /> Ver notificaciones
            </Link>
            <Link to="/admin/auditoria" className="admin-btn admin-btn-ghost admin-btn-sm">
              <FaHistory /> Registro de auditoria
            </Link>
            <Link to="/admin/contacto" className="admin-btn admin-btn-ghost admin-btn-sm">
              <FaEnvelope /> Mensajes de contacto
            </Link>
            <Link to="/admin/usuarios/pendientes" className="admin-btn admin-btn-ghost admin-btn-sm">
              <FaUserClock /> Usuarios pendientes
            </Link>
          </div>
          <div className="text-[12px]">
            Sesion activa: <strong>{user?.email || "admin"}</strong>
          </div>
        </div>
      </div>

      {loading && (
        <div className="admin-loading mt-4">
          Actualizando datos...
        </div>
      )}
    </>
  );
}
