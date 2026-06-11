import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaNewspaper, FaCalendarAlt, FaTags, FaUsers, FaUserShield,
  FaCommentDots, FaThumbsUp, FaThumbsDown, FaChartLine,
} from "react-icons/fa";
import api, { extractList } from "../../api";

function StatCard({ icon, label, value, color }) {
  return (
    <div className="dash-stat">
      <div className={"dash-stat__icon " + color}>{icon}</div>
      <div>
        <div className="dash-stat__label">{label}</div>
        <div className="dash-stat__value">{value}</div>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    noticias: 0, eventos: 0, categorias: 0, autoridades: 0,
    usuarios: 0, comentarios: 0, likes: 0, dislikes: 0,
  });
  const [ultimasNoticias, setUltimasNoticias] = useState([]);
  const [proximosEventos, setProximosEventos] = useState([]);

  useEffect(() => {
    const cargar = async () => {
      try {
        const [n, e, c, a, u, co, re] = await Promise.all([
          api.get("/noticias/?page_size=5").catch(() => ({ data: { data: [] } })),
          api.get("/eventos/?page_size=5").catch(() => ({ data: { data: [] } })),
          api.get("/categorias/").catch(() => ({ data: { data: [] } })),
          api.get("/autoridades/").catch(() => ({ data: { data: [] } })),
          api.get("/usuarios/").catch(() => ({ data: { data: [] } })),
          api.get("/comentarios/").catch(() => ({ data: { data: [] } })),
          api.get("/reacciones/").catch(() => ({ data: { data: [] } })),
        ]);
        const nl = extractList(n.data);
        const el = extractList(e.data);
        const cl = extractList(c.data);
        const al = extractList(a.data);
        const ul = extractList(u.data);
        const col = extractList(co.data);
        const rl = extractList(re.data);
        setStats({
          noticias: nl.length,
          eventos: el.length,
          categorias: cl.length,
          autoridades: al.length,
          usuarios: ul.length,
          comentarios: col.length,
          likes: rl.filter(r => r.tipo === "LIKE").length,
          dislikes: rl.filter(r => r.tipo === "DISLIKE").length,
        });
        setUltimasNoticias(nl.slice(0, 5));
        setProximosEventos(el.slice(0, 5));
      } catch (e) {
        console.error("Dashboard load error", e);
      }
    };
    cargar();
  }, []);

  return (
    <>
      <div className="dash-stats">
        <StatCard icon={<FaNewspaper />}  label="Noticias"     value={stats.noticias}    color="dash-stat__icon--blue" />
        <StatCard icon={<FaCalendarAlt />} label="Eventos"      value={stats.eventos}     color="dash-stat__icon--green" />
        <StatCard icon={<FaTags />}        label="Categorías"   value={stats.categorias}  color="dash-stat__icon--yellow" />
        <StatCard icon={<FaUsers />}       label="Autoridades"  value={stats.autoridades} color="dash-stat__icon--purple" />
        <StatCard icon={<FaUserShield />}  label="Usuarios"     value={stats.usuarios}    color="dash-stat__icon--cyan" />
        <StatCard icon={<FaCommentDots />} label="Comentarios"   value={stats.comentarios}  color="dash-stat__icon--blue" />
        <StatCard icon={<FaThumbsUp />}    label="Likes"        value={stats.likes}        color="dash-stat__icon--green" />
        <StatCard icon={<FaThumbsDown />}  label="Dislikes"     value={stats.dislikes}     color="dash-stat__icon--red" />
      </div>

      <div className="dash-grid">
        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaChartLine style={{ marginRight: 6 }} /> Últimas noticias
          </h3>
          {ultimasNoticias.length === 0 ? (
            <p style={{ color: "#6b7280", fontSize: 13 }}>No hay noticias aún.</p>
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
          <div style={{ marginTop: 12 }}>
            <Link to="/admin/noticias" className="admin-btn admin-btn-ghost admin-btn-sm">Ver todas →</Link>
          </div>
        </div>

        <div className="dash-card">
          <h3 className="dash-card__title">
            <FaCalendarAlt style={{ marginRight: 6 }} /> Próximos eventos
          </h3>
          {proximosEventos.length === 0 ? (
            <p style={{ color: "#6b7280", fontSize: 13 }}>No hay eventos aún.</p>
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
          <div style={{ marginTop: 12 }}>
            <Link to="/admin/eventos" className="admin-btn admin-btn-ghost admin-btn-sm">Ver todos →</Link>
          </div>
        </div>
      </div>
    </>
  );
}
