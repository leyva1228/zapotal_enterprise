import React, { useEffect, useState, useCallback, useRef, useMemo } from "react";
import {
  FaBell, FaRedo, FaCheck, FaCheckDouble, FaTrash, FaUndo,
  FaNewspaper, FaCalendarAlt, FaUserCheck, FaUserTimes, FaUserSlash,
  FaUserShield, FaCheckCircle, FaTimesCircle, FaUser, FaExternalLinkAlt,
  FaInbox, FaInfoCircle, FaUserMinus, FaCommentDots, FaSpinner,
  FaEnvelope, FaGavel, FaBook, FaTimes,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import { useUrlFilters, parseBoolParam, parseIntParam } from "../../hooks/useUrlFilters";

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch { return "-"; }
}

function formatGrupoFecha(fechaStr) {
  const fecha = new Date(fechaStr);
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  const ayer = new Date(hoy);
  ayer.setDate(ayer.getDate() - 1);
  if (fecha >= hoy) return "Hoy";
  if (fecha >= ayer) return "Ayer";
  const diff = (hoy - fecha) / 86400000;
  if (diff < 7) return "Esta semana";
  return "Mas antiguas";
}

const ICONO_POR_TIPO = {
  info: <FaInfoCircle />,
  aprobacion_cuenta: <FaUserCheck />,
  rechazo_cuenta: <FaUserTimes />,
  cuenta_bloqueada: <FaUserSlash />,
  cuenta_desbloqueada: <FaUserShield />,
  nueva_noticia: <FaNewspaper />,
  nuevo_evento: <FaCalendarAlt />,
  nueva_solicitud_baja: <FaUserMinus />,
  solicitud_baja_aprobada: <FaCheck />,
  solicitud_baja_rechazada: <FaTimesCircle />,
  solicitud_baja_cancelada: <FaTimesCircle />,
  comentario_moderado: <FaCommentDots />,
  // Nuevos (Loop 3.4)
  nuevo_mensaje_contacto: <FaEnvelope />,
  nuevo_reclamo: <FaGavel />,
  reclamo_estado_cambiado: <FaBook />,
  mensaje: <FaEnvelope />,
};

const TIPOS_DISPONIBLES = [
  { value: '',                          label: 'Todos los tipos' },
  { value: 'info',                      label: 'Informacion' },
  { value: 'nuevo_mensaje_contacto',    label: 'Mensaje de contacto' },
  { value: 'nuevo_reclamo',             label: 'Nuevo reclamo' },
  { value: 'reclamo_estado_cambiado',   label: 'Reclamo - estado cambiado' },
  { value: 'aprobacion_cuenta',         label: 'Aprobacion de cuenta' },
  { value: 'rechazo_cuenta',            label: 'Rechazo de cuenta' },
  { value: 'cuenta_bloqueada',          label: 'Cuenta bloqueada' },
  { value: 'cuenta_desbloqueada',       label: 'Cuenta reactivada' },
  { value: 'nueva_noticia',             label: 'Nueva noticia' },
  { value: 'nuevo_evento',              label: 'Nuevo evento' },
  { value: 'nueva_solicitud_baja',      label: 'Solicitud de baja' },
  { value: 'comentario_moderado',       label: 'Comentario moderado' },
];

export default function AdminNotificaciones() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [filtroLeido, setFiltroLeido] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");
  // V2.3: modal de detalle con mensaje completo.
  const [detalle, setDetalle] = useState(null);

  // LOOP 6: sincronizar filtros con URL.
  const [filters, setFilters, clearFilters] = useUrlFilters({
    leido: { defaultValue: null, parser: parseBoolParam },
    tipo: { defaultValue: "" },
    page: { defaultValue: 1, parser: parseIntParam },
  });

  // Sincronizar URL con state local al montar.
  useEffect(() => {
    if (filters.leido === true) setFiltroLeido("leidas");
    else if (filters.leido === false) setFiltroLeido("no_leidas");
    else setFiltroLeido("");
    if (filters.tipo) setFiltroTipo(filters.tipo);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const intervalRef = useRef(null);
  const abortRef = useRef(null);

  const cargar = useCallback(async () => {
    // Loop 3.6: AbortController para evitar overlap de requests
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setError(""); setOk("");
    try {
      const params = {};
      if (filtroLeido === "leidas") params.leido = true;
      if (filtroLeido === "no_leidas") params.leido = false;
      if (filtroTipo) params.tipo = filtroTipo;
      const { data } = await api.get("/notificaciones/", { params, signal: controller.signal });
      setItems(extractList(data));
    } catch (e) {
      if (e.name !== 'CanceledError' && e.code !== 'ERR_CANCELED') {
        setError("No se pudieron cargar las notificaciones.");
      }
    } finally {
      setLoading(false);
    }
  }, [filtroLeido, filtroTipo]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  // Auto-refresh cada 60s con AbortController
  useEffect(() => {
    intervalRef.current = setInterval(async () => {
      const controller = new AbortController();
      try {
        const params = {};
        if (filtroLeido === "leidas") params.leido = true;
        if (filtroLeido === "no_leidas") params.leido = false;
        if (filtroTipo) params.tipo = filtroTipo;
        const { data } = await api.get("/notificaciones/", { params, signal: controller.signal });
        setItems(extractList(data));
      } catch {
        /* silencioso */
      }
    }, 60000);
    return () => {
      clearInterval(intervalRef.current);
      abortRef.current?.abort();
    };
  }, [filtroLeido, filtroTipo]);

  // Loop 3.6: sync badge del sidebar
  const dispatchNotifActualizadas = () => {
    try {
      window.dispatchEvent(new CustomEvent('notificaciones:actualizadas'));
    } catch { /* silencioso */ }
  };

  const marcarLeida = async (n) => {
    if (n.leido) return;
    setError(""); setOk("");
    try {
      await api.patch(`/notificaciones/${n.id}/`, { leido: true });
      setOk("Notificacion marcada como leida.");
      dispatchNotifActualizadas();
      await cargar();
    } catch (e) {
      setError("No se pudo marcar como leida.");
    }
  };

  const marcarNoLeida = async (n) => {
    if (!n.leido) return;
    setError(""); setOk("");
    try {
      await api.patch(`/notificaciones/${n.id}/`, { leido: false });
      setOk("Notificacion marcada como no leida.");
      dispatchNotifActualizadas();
      await cargar();
    } catch (e) {
      setError("No se pudo des-marcar.");
    }
  };

  const marcarTodasLeidas = async () => {
    const noLeidas = items.filter((i) => !i.leido);
    if (noLeidas.length === 0) return;
    setError(""); setOk("");
    try {
      await Promise.all(
        noLeidas.map((n) => api.patch(`/notificaciones/${n.id}/`, { leido: true })),
      );
      setOk(`${noLeidas.length} notificaciones marcadas como leidas.`);
      dispatchNotifActualizadas();
      await cargar();
    } catch (e) {
      setError("No se pudieron marcar todas como leidas.");
    }
  };

  const eliminar = async (n) => {
    if (!window.confirm("Eliminar esta notificacion?")) return;
    setError(""); setOk("");
    try {
      await api.delete(`/notificaciones/${n.id}/`);
      setOk("Notificacion eliminada.");
      dispatchNotifActualizadas();
      await cargar();
    } catch (e) {
      setError("No se pudo eliminar.");
    }
  };

  const onClickFila = async (n) => {
    if (!n.leido) {
      try {
        await api.patch(`/notificaciones/${n.id}/`, { leido: true });
        dispatchNotifActualizadas();
      } catch { /* continuar */ }
    }
    // V2.3: abrir modal con el mensaje completo primero;
    // el admin puede decidir ir a la URL desde el modal.
    setDetalle(n);
  };

  const irADestino = () => {
    if (detalle?.url_destino) navigate(detalle.url_destino);
  };

  // Loop 3.6: agrupar por fecha
  const itemsAgrupados = useMemo(() => {
    const grupos = { Hoy: [], Ayer: [], 'Esta semana': [], 'Mas antiguas': [] };
    items.forEach((it) => {
      const grupo = formatGrupoFecha(it.fecha);
      grupos[grupo].push(it);
    });
    return grupos;
  }, [items]);

  const noLeidas = items.filter((i) => !i.leido).length;

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaBell className="mr-[6px]" />
            Centro de notificaciones ({items.length})
            {noLeidas > 0 && <span className="admin-badge admin-badge--warning">{noLeidas} sin leer</span>}
            <span style={{ fontSize: 11, color: '#6b7280', marginLeft: 8 }}>
              <FaSpinner className="fa-spin" /> auto-refresh 60s
            </span>
          </h3>
          <div className="flex gap-2 flex-wrap">
            <select
              className="admin-select min-w-[160px]"
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              title="Filtrar por tipo"
            >
              {TIPOS_DISPONIBLES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <select
              className="admin-select min-w-[140px]"
              value={filtroLeido}
              onChange={(e) => setFiltroLeido(e.target.value)}
              title="Filtrar por estado de lectura"
            >
              <option value="">Todas</option>
              <option value="no_leidas">Sin leer</option>
              <option value="leidas">Leidas</option>
            </select>
            <button className="admin-btn admin-btn-sm" onClick={cargar} disabled={loading}>
              <FaRedo /> Recargar
            </button>
            <button
              className="admin-btn admin-btn-sm admin-btn-primary"
              onClick={marcarTodasLeidas}
              disabled={noLeidas === 0}
            >
              <FaCheckDouble /> Marcar todas
            </button>
          </div>
        </div>
        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">
              <FaSpinner className="fa-spin" /> Cargando...
            </div>
          ) : items.length === 0 ? (
            <div className="admin-empty">
              <FaInbox style={{ fontSize: 48, opacity: 0.4 }} />
              <p>No hay notificaciones{filtroLeido || filtroTipo ? ' con estos filtros' : ''}.</p>
            </div>
          ) : (
            <>
              {Object.entries(itemsAgrupados).map(([grupo, itemsGrupo]) =>
                itemsGrupo.length > 0 ? (
                  <div key={grupo} className="admin-notif-grupo">
                    <h4 className="admin-notif-grupo__titulo">{grupo} ({itemsGrupo.length})</h4>
                    <table className="admin-table">
                      <thead>
                        <tr>
                          <th>Tipo</th>
                          <th>Titulo</th>
                          <th>Mensaje</th>
                          <th>Fecha</th>
                          <th className="text-right">Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {itemsGrupo.map((it) => (
                          <tr
                            key={it.id}
                            onClick={() => onClickFila(it)}
                            className={it.leido ? '' : 'bg-gray-50'}
                            style={{ cursor: it.url_destino ? 'pointer' : 'default' }}
                            title={it.url_destino ? `Ir a ${it.url_destino}` : 'Sin URL de destino'}
                          >
                            <td>
                              <span
                                className="admin-badge admin-badge--info"
                                style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}
                              >
                                {ICONO_POR_TIPO[it.tipo] || <FaInfoCircle />}
                                {it.leido ? 'Leida' : 'Nueva'}
                              </span>
                            </td>
                            <td className="font-semibold">
                              {it.titulo}
                              {it.url_destino && (
                                <FaExternalLinkAlt style={{ fontSize: 10, marginLeft: 6, color: '#6b7280' }} />
                              )}
                            </td>
                            <td className="overflow-hidden text-ellipsis" style={{ maxWidth: 320 }}>
                              {it.mensaje}
                            </td>
                            <td className="text-mute">{formatFecha(it.fecha)}</td>
                            <td className="actions justify-end" onClick={(e) => e.stopPropagation()}>
                              {!it.leido ? (
                                <button
                                  className="admin-btn admin-btn-sm admin-btn-success"
                                  onClick={() => marcarLeida(it)}
                                  title="Marcar como leida"
                                >
                                  <FaCheck />
                                </button>
                              ) : (
                                <button
                                  className="admin-btn admin-btn-sm admin-btn-secondary"
                                  onClick={() => marcarNoLeida(it)}
                                  title="Marcar como no leida"
                                >
                                  <FaUndo />
                                </button>
                              )}
                              <button
                                className="admin-btn admin-btn-sm admin-btn-danger"
                                onClick={() => eliminar(it)}
                                title="Eliminar"
                              >
                                <FaTrash />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : null
              )}
            </>
          )}
        </div>
      </div>

      {/* V2.3: modal de mensaje completo */}
      <AdminModal
        open={!!detalle}
        title={detalle?.titulo || "Detalle de notificacion"}
        onClose={() => setDetalle(null)}
        size="md"
        footer={
          detalle && (
            <>
              {detalle.url_destino && (
                <button className="admin-btn" onClick={irADestino}>
                  <FaExternalLinkAlt /> Ir al destino
                </button>
              )}
              <button className="admin-btn admin-btn-secondary" onClick={() => setDetalle(null)}>
                <FaTimes /> Cerrar
              </button>
            </>
          )
        }
      >
        {detalle && (
          <div className="admin-notif-detalle">
            <div className="admin-notif-detalle__fila">
              <strong>Tipo:</strong>
              <span>{detalle.tipo || "info"}</span>
            </div>
            <div className="admin-notif-detalle__fila">
              <strong>Fecha:</strong>
              <span>{formatFecha(detalle.fecha)}</span>
            </div>
            <div className="admin-notif-detalle__fila">
              <strong>Estado:</strong>
              <span>{detalle.leido ? "Leida" : "No leida"}</span>
            </div>
            {detalle.url_destino && (
              <div className="admin-notif-detalle__fila">
                <strong>URL:</strong>
                <span className="admin-notif-detalle__url">{detalle.url_destino}</span>
              </div>
            )}
            <hr className="admin-notif-detalle__sep" />
            <h4 className="admin-notif-detalle__subtitulo">Mensaje completo</h4>
            <p className="admin-notif-detalle__cuerpo">{detalle.mensaje}</p>
          </div>
        )}
      </AdminModal>
    </div>
  );
}
