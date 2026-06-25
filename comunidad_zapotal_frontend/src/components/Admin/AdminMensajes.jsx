import React, { useState } from 'react';
import {
  FaInbox, FaEnvelope, FaEnvelopeOpen, FaClock, FaCheck,
  FaSearch, FaFilter, FaTimes, FaReply, FaTrash, FaEye, FaSpinner,
  FaFlag, FaCircle, FaExclamationCircle, FaInfoCircle,
} from 'react-icons/fa';
import api from '../../api';
import AdminModal from '../Admin/AdminModal';

/**
 * Inbox reutilizable de MensajeContacto.
 * Usado en /admin/contacto. La antigua tab "Mensajes" de AdminInstitucional
 * fue removida para evitar duplicacion.
 */
export default function AdminMensajes() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState('todos');
  const [busqueda, setBusqueda] = useState('');
  const [detalle, setDetalle] = useState(null);

  const cargar = () => {
    setLoading(true);
    api.get('/mensajes-contacto/').then((r) => {
      setItems(r.data.results || r.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  React.useEffect(cargar, []);

  const marcarLeido = async (m, e) => {
    e && e.stopPropagation();
    await api.post(`/mensajes-contacto/${m.id}/marcar_leido/`);
    cargar();
  };
  const marcarRespondido = async (m, e) => {
    e && e.stopPropagation();
    await api.post(`/mensajes-contacto/${m.id}/marcar_respondido/`);
    cargar();
    if (detalle && detalle.id === m.id) {
      setDetalle({ ...detalle, respondido: true });
    }
  };
  const eliminar = async (m, e) => {
    e && e.stopPropagation();
    if (!window.confirm(`Eliminar mensaje de "${m.nombre}"?`)) return;
    await api.delete(`/mensajes-contacto/${m.id}/`);
    cargar();
    if (detalle && detalle.id === m.id) setDetalle(null);
  };
  const verDetalle = async (m) => {
    setDetalle(m);
    if (!m.leido) {
      await api.post(`/mensajes-contacto/${m.id}/marcar_leido/`).catch(() => {});
      cargar();
    }
  };
  const responderMailto = (m) => {
    const subject = encodeURIComponent(`Re: ${m.asunto}`);
    const body = encodeURIComponent(
      `Hola ${m.nombre},\n\nGracias por contactarnos.\n\n-- \nMensaje original:\n> ${m.mensaje}\n`
    );
    return `mailto:${m.email}?subject=${subject}&body=${body}`;
  };

  const total = items.length;
  const noLeidos = items.filter((m) => !m.leido).length;
  const respond = items.filter((m) => m.respondido).length;
  const pendientes = items.filter((m) => m.leido && !m.respondido).length;

  const itemsFiltrados = items
    .filter((m) => {
      if (filtro === 'no_leidos') return !m.leido;
      if (filtro === 'leidos') return m.leido && !m.respondido;
      if (filtro === 'respondidos') return m.respondido;
      return true;
    })
    .filter((m) => {
      if (!busqueda) return true;
      const q = busqueda.toLowerCase();
      return (
        m.nombre.toLowerCase().includes(q) ||
        m.email.toLowerCase().includes(q) ||
        m.asunto.toLowerCase().includes(q) ||
        m.mensaje.toLowerCase().includes(q)
      );
    });

  if (loading) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando mensajes...</div>;

  return (
    <div className="admin-mensajes">
      <div className="admin-mensajes__stats">
        <div className="admin-stat-card">
          <FaInbox className="admin-stat-card__icono" />
          <div>
            <div className="admin-stat-card__valor">{total}</div>
            <div className="admin-stat-card__label">Total</div>
          </div>
        </div>
        <div className="admin-stat-card admin-stat-card--warning">
          <FaEnvelope className="admin-stat-card__icono" />
          <div>
            <div className="admin-stat-card__valor">{noLeidos}</div>
            <div className="admin-stat-card__label">No leidos</div>
          </div>
        </div>
        <div className="admin-stat-card admin-stat-card--info">
          <FaClock className="admin-stat-card__icono" />
          <div>
            <div className="admin-stat-card__valor">{pendientes}</div>
            <div className="admin-stat-card__label">Pendientes</div>
          </div>
        </div>
        <div className="admin-stat-card admin-stat-card--success">
          <FaCheck className="admin-stat-card__icono" />
          <div>
            <div className="admin-stat-card__valor">{respond}</div>
            <div className="admin-stat-card__label">Respondidos</div>
          </div>
        </div>
      </div>

      <div className="admin-mensajes__herramientas">
        <div className="admin-mensajes__busqueda">
          <FaSearch />
          <input
            type="text"
            placeholder="Buscar por nombre, email, asunto o contenido..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="admin-input"
          />
          {busqueda && (
            <button className="admin-btn admin-btn-sm" onClick={() => setBusqueda('')}>
              <FaTimes />
            </button>
          )}
        </div>
        <div className="admin-mensajes__filtros">
          <FaFilter />
          {[
            { id: 'todos', label: 'Todos' },
            { id: 'no_leidos', label: 'No leidos' },
            { id: 'leidos', label: 'Pendientes' },
            { id: 'respondidos', label: 'Respondidos' },
          ].map((f) => (
            <button
              key={f.id}
              type="button"
              onClick={() => setFiltro(f.id)}
              className={`admin-btn admin-btn-sm ${filtro === f.id ? 'admin-btn-primary' : 'admin-btn-secondary'}`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {itemsFiltrados.length === 0 ? (
        <div className="admin-mensajes__vacio">
          <FaInbox />
          <p>No hay mensajes {filtro !== 'todos' ? 'con este filtro' : 'aun'}.</p>
        </div>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th style={{ width: 36 }}></th>
              <th>Fecha</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Asunto</th>
              <th>Estado</th>
              <th className="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {itemsFiltrados.map(m => (
              <tr
                key={m.id}
                onClick={() => verDetalle(m)}
                style={{
                  background: m.leido ? '#fff' : '#fef9e7',
                  cursor: 'pointer',
                }}
                title="Click para ver el mensaje completo"
              >
                <td>
                  {m.leido ? (
                    <FaEnvelopeOpen style={{ color: '#9ca3af' }} />
                  ) : (
                    <FaEnvelope style={{ color: '#d4a72c' }} />
                  )}
                </td>
                <td className="text-mute">
                  {new Date(m.fecha).toLocaleString('es-PE', { dateStyle: 'short', timeStyle: 'short' })}
                </td>
                <td className="font-semibold">{m.nombre}</td>
                <td><a href={`mailto:${m.email}`} onClick={(e) => e.stopPropagation()}>{m.email}</a></td>
                <td>
                  <span
                    className={`admin-prioridad-dot admin-prioridad-dot--${(m.prioridad || 'MEDIA').toLowerCase()}`}
                    title={`Prioridad: ${m.prioridad || 'MEDIA'}`}
                    aria-label={`Prioridad ${m.prioridad || 'MEDIA'}`}
                  />
                  {m.asunto}
                </td>
                <td>
                  {m.respondido ? (
                    <span className="admin-badge admin-badge--ok"><FaCheck /> Respondido</span>
                  ) : m.leido ? (
                    <span className="admin-badge admin-badge--info">Leido</span>
                  ) : (
                    <span className="admin-badge admin-badge--warn">No leido</span>
                  )}
                </td>
                <td className="actions justify-end" onClick={(e) => e.stopPropagation()}>
                  <a
                    className="admin-btn admin-btn-sm admin-btn-secondary"
                    href={responderMailto(m)}
                    title="Responder por correo"
                  >
                    <FaReply /> Responder
                  </a>
                  {!m.respondido && (
                    <button
                      className="admin-btn admin-btn-sm"
                      onClick={(e) => marcarRespondido(m, e)}
                      title="Marcar como respondido"
                    >
                      <FaCheck />
                    </button>
                  )}
                  <button
                    className="admin-btn admin-btn-sm admin-btn-danger"
                    onClick={(e) => eliminar(m, e)}
                    title="Eliminar"
                  >
                    <FaTrash />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <AdminModal
        open={!!detalle}
        title={detalle ? `Mensaje de ${detalle.nombre}` : ''}
        onClose={() => setDetalle(null)}
        size="lg"
        footer={
          detalle && (
            <>
              <a
                className="admin-btn admin-btn-secondary"
                href={`mailto:${detalle.email}`}
                onClick={() => setDetalle(null)}
              >
                <FaReply /> Abrir en cliente de correo
              </a>
              <a
                className="admin-btn admin-btn-primary"
                href={responderMailto(detalle)}
                onClick={() => {
                  marcarRespondido(detalle);
                }}
              >
                <FaReply /> Responder y marcar como respondido
              </a>
            </>
          )
        }
      >
        {detalle && (
          <div className="admin-mensaje-detalle">
            <div className="admin-mensaje-detalle__fila">
              <strong>De:</strong>
              <span>{detalle.nombre} &lt;<a href={`mailto:${detalle.email}`}>{detalle.email}</a>&gt;</span>
            </div>
            {detalle.telefono && (
              <div className="admin-mensaje-detalle__fila">
                <strong>Telefono:</strong>
                <a href={`tel:${detalle.telefono}`}>{detalle.telefono}</a>
              </div>
            )}
            <div className="admin-mensaje-detalle__fila">
              <strong>Fecha:</strong>
              <span>{new Date(detalle.fecha).toLocaleString('es-PE')}</span>
            </div>
            <div className="admin-mensaje-detalle__fila">
              <strong>Asunto:</strong>
              <span>{detalle.asunto}</span>
            </div>
            {detalle.ip_origen && (
              <div className="admin-mensaje-detalle__fila">
                <strong>IP de origen:</strong>
                <code style={{ background: '#f3f4f6', padding: '2px 6px', borderRadius: 4 }}>{detalle.ip_origen}</code>
              </div>
            )}
            <hr style={{ margin: '16px 0', border: 0, borderTop: '1px solid #e5e7eb' }} />
            <div className="admin-mensaje-detalle__cuerpo">
              {detalle.mensaje}
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 16, alignItems: 'center', flexWrap: 'wrap' }}>
              {detalle.leido ? (
                <span className="admin-badge admin-badge--ok"><FaEye /> Leido</span>
              ) : (
                <span className="admin-badge admin-badge--warn">No leido</span>
              )}
              {detalle.respondido ? (
                <span className="admin-badge admin-badge--ok"><FaCheck /> Respondido</span>
              ) : (
                <button
                  className="admin-btn admin-btn-sm"
                  onClick={() => marcarRespondido(detalle)}
                >
                  <FaCheck /> Marcar como respondido
                </button>
              )}
            </div>
          </div>
        )}
      </AdminModal>
    </div>
  );
}
