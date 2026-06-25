import React, { useEffect, useState, useCallback } from "react";
import {
  FaHistory, FaRedo, FaTrash, FaEdit, FaSearch, FaReply,
  FaCheck, FaExclamationCircle, FaPrint, FaSearchPlus, FaUserShield,
} from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

const ESTADOS = ["PENDIENTE", "EN_PROCESO", "RESUELTO"];
const PRIORIDADES = [
  { value: "BAJA",  label: "Baja",  color: "#6b7280" },
  { value: "MEDIA", label: "Media", color: "#d97706" },
  { value: "ALTA",  label: "Alta",  color: "#dc2626" },
];

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch { return "-"; }
}

function formatFechaCorta(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleDateString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
    });
  } catch { return "-"; }
}

function colorEstado(estado) {
  if (estado === "RESUELTO") return "admin-badge--success";
  if (estado === "EN_PROCESO") return "admin-badge--warning";
  return "admin-badge--danger";
}

export default function AdminReclamaciones() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [detalle, setDetalle] = useState(null);
  const [plantillas, setPlantillas] = useState([]);
  const [plantillaSeleccionada, setPlantillaSeleccionada] = useState("");
  const [textoRespuesta, setTextoRespuesta] = useState("");
  const [enviandoRespuesta, setEnviandoRespuesta] = useState(false);

  const cargar = useCallback(async () => {
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = {};
      if (filtroEstado) params.estado = filtroEstado;
      if (busqueda) params.search = busqueda;
      const { data } = await api.get("/libro-reclamaciones/", { params });
      setItems(extractList(data));
    } catch (e) {
      setError("No se pudieron cargar las reclamaciones.");
    } finally {
      setLoading(false);
    }
  }, [filtroEstado, busqueda]);

  useEffect(() => { cargar(); }, [cargar]);

  const cambiarEstado = async (item, nuevoEstado) => {
    setError(""); setOk("");
    try {
      await api.post(`/libro-reclamaciones/${item.id}/cambiar_estado/`, { estado: nuevoEstado });
      setOk(`Reclamo ${item.numero_reclamo} -> ${nuevoEstado}`);
      await cargar();
    } catch (e) {
      setError("No se pudo cambiar el estado.");
    }
  };

  const cambiarPrioridad = async (item, nuevaPrioridad) => {
    try {
      await api.patch(`/libro-reclamaciones/${item.id}/`, { prioridad: nuevaPrioridad });
      setOk(`Prioridad actualizada: ${item.numero_reclamo} -> ${nuevaPrioridad}`);
      await cargar();
    } catch (e) {
      setError("No se pudo cambiar la prioridad.");
    }
  };

  const eliminar = async (item) => {
    if (!window.confirm(`Eliminar reclamacion ${item.numero_reclamo} de "${item.nombre}"?`)) return;
    setError(""); setOk("");
    try {
      await api.delete(`/libro-reclamaciones/${item.id}/`);
      setOk("Reclamacion eliminada.");
      await cargar();
    } catch (e) {
      setError("No se pudo eliminar.");
    }
  };

  const abrirDetalle = async (item) => {
    setDetalle(item);
    setTextoRespuesta("");
    setPlantillaSeleccionada("");
    setPlantillas([]);
    // Cargar plantillas disponibles para este reclamo.
    try {
      const { data } = await api.get(`/libro-reclamaciones/${item.id}/plantillas-respuesta/`);
      setPlantillas(data.plantillas || []);
    } catch {
      // silencioso
    }
  };

  const aplicarPlantilla = (id) => {
    setPlantillaSeleccionada(id);
    const p = plantillas.find((x) => x.id === id);
    if (p) setTextoRespuesta(p.texto);
  };

  const enviarRespuesta = async () => {
    if (!textoRespuesta.trim()) {
      setError("La respuesta no puede estar vacia.");
      return;
    }
    if (!window.confirm(
      "Esta accion enviara un email al consumidor y marcara el reclamo como RESUELTO. Continuar?"
    )) return;
    setEnviandoRespuesta(true);
    setError(""); setOk("");
    try {
      await api.post(`/libro-reclamaciones/${detalle.id}/responder/`, {
        respuesta_texto: textoRespuesta,
        plantilla_usada: plantillaSeleccionada,
      });
      setOk(`Respuesta enviada a ${detalle.email}. Reclamo marcado como RESUELTO.`);
      setDetalle(null);
      await cargar();
    } catch (e) {
      setError("No se pudo enviar la respuesta.");
    } finally {
      setEnviandoRespuesta(false);
    }
  };

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaHistory className="mr-[6px]" />
            Libro de reclamaciones ({items.length})
          </h3>
          <div className="flex gap-2 flex-wrap">
            <div className="admin-input-with-icon">
              <FaSearch className="admin-input-with-icon__ico" />
              <input
                type="text"
                placeholder="Buscar por nombre, email, descripcion o numero..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") cargar(); }}
                className="admin-input"
              />
            </div>
            <select
              className="admin-select min-w-[160px]"
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
            >
              <option value="">Todos los estados</option>
              {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
            </select>
            <button className="admin-btn admin-btn-sm" onClick={cargar} disabled={loading}>
              <FaRedo /> Recargar
            </button>
          </div>
        </div>
        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">No hay reclamaciones.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Codigo</th>
                  <th>Nombre</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th>Fecha</th>
                  <th>Plazo</th>
                  <th>Estado</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => {
                  const diasRestantes = it.plazo_respuesta
                    ? Math.ceil((new Date(it.plazo_respuesta) - new Date()) / 86400000)
                    : null;
                  return (
                    <tr key={it.id} className={it.leido ? "" : "bg-gray-50"}>
                      <td>
                        <code style={{ background: '#f3f4f6', padding: '2px 6px', borderRadius: 4, fontSize: 12 }}>
                          {it.numero_reclamo || `#${it.id}`}
                        </code>
                        {it.leido === false && (
                          <span title="No leido" style={{ marginLeft: 6, color: '#d97706' }}>●</span>
                        )}
                      </td>
                      <td className="font-semibold">{it.nombre}</td>
                      <td className="text-xs">{it.email}</td>
                      <td>{it.tipo}</td>
                      <td className="text-mute">{formatFecha(it.fecha)}</td>
                      <td className="text-xs">
                        {it.plazo_respuesta ? (
                          <span style={{
                            color: diasRestantes < 5 ? '#dc2626' :
                                   diasRestantes < 10 ? '#d97706' : '#16a34a',
                            fontWeight: diasRestantes < 5 ? 700 : 400,
                          }}>
                            {formatFechaCorta(it.plazo_respuesta)}
                            <br />
                            <small>({diasRestantes}d)</small>
                          </span>
                        ) : '-'}
                      </td>
                      <td>
                        <span className={"admin-badge " + colorEstado(it.estado)}>
                          {it.estado}
                        </span>
                      </td>
                      <td className="actions justify-end" onClick={(e) => e.stopPropagation()}>
                        <button className="admin-btn admin-btn-sm" onClick={() => abrirDetalle(it)} title="Ver">
                          <FaEdit /> Ver
                        </button>
                        <select
                          className="admin-select min-w-[110px]"
                          value={it.estado}
                          onChange={(e) => cambiarEstado(it, e.target.value)}
                          title="Cambiar estado"
                        >
                          {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                        </select>
                        <select
                          className="admin-select min-w-[90px]"
                          value={it.prioridad}
                          onChange={(e) => cambiarPrioridad(it, e.target.value)}
                          title="Cambiar prioridad"
                        >
                          {PRIORIDADES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                        </select>
                        <button
                          className="admin-btn admin-btn-sm admin-btn-danger"
                          onClick={() => eliminar(it)}
                          title="Eliminar"
                        >
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <AdminModal
        open={!!detalle}
        title={detalle ? `Reclamo ${detalle.numero_reclamo || '#'+detalle.id}` : ''}
        onClose={() => setDetalle(null)}
        wide
        footer={
          detalle && (
            <>
              <button className="admin-btn" onClick={() => setDetalle(null)}>Cerrar</button>
              <a
                className="admin-btn admin-btn-secondary"
                href={`mailto:${detalle.email}?subject=Re: Reclamo ${detalle.numero_reclamo}`}
              >
                <FaReply /> Abrir cliente de correo
              </a>
              <button
                className="admin-btn admin-btn-primary"
                onClick={enviarRespuesta}
                disabled={enviandoRespuesta || !textoRespuesta.trim()}
              >
                <FaCheck /> Enviar respuesta y marcar como resuelto
              </button>
            </>
          )
        }
      >
        {detalle && (
          <div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label">Numero de reclamo</label>
                <code style={{ fontSize: 14, fontWeight: 700, color: '#0a3d1f' }}>
                  {detalle.numero_reclamo || `#${detalle.id}`}
                </code>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label">Fecha de recepcion</label>
                <p className="m-0">{formatFecha(detalle.fecha)}</p>
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Plazo legal (Ley 29571)</label>
              <p className="m-0">
                {formatFechaCorta(detalle.plazo_respuesta)}
                {detalle.plazo_respuesta && (
                  <small className="text-mute ml-2">
                    ({Math.ceil((new Date(detalle.plazo_respuesta) - new Date()) / 86400000)} dias restantes)
                  </small>
                )}
              </p>
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label">Nombre</label>
                <p className="m-0">{detalle.nombre}</p>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label">Tipo</label>
                <p className="m-0">{detalle.tipo}</p>
              </div>
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label">Email</label>
                <p className="m-0">
                  <a href={`mailto:${detalle.email}`}>{detalle.email}</a>
                </p>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label">Telefono</label>
                <p className="m-0">{detalle.telefono || "-"}</p>
              </div>
            </div>
            {detalle.direccion && (
              <div className="admin-form-group">
                <label className="admin-form-group__label">Direccion</label>
                <p className="m-0">{detalle.direccion}</p>
              </div>
            )}
            <div className="admin-form-group">
              <label className="admin-form-group__label">Descripcion del consumidor</label>
              <div className="rounded-8 whitespace-pre-wrap text-[13px]" style={{ background: '#f9fafb', padding: 12 }}>
                {detalle.descripcion}
              </div>
            </div>
            {detalle.respuesta_admin && (
              <div className="admin-form-group">
                <label className="admin-form-group__label">Respuesta enviada</label>
                <div className="rounded-8 whitespace-pre-wrap text-[13px]" style={{ background: '#f0fdf4', padding: 12, borderLeft: '4px solid #16a34a' }}>
                  {detalle.respuesta_admin}
                </div>
              </div>
            )}
            <hr style={{ margin: '20px 0', border: 0, borderTop: '1px solid #e5e7eb' }} />
            <h4 style={{ marginBottom: 8 }}>Responder al consumidor</h4>
            {plantillas.length > 0 && (
              <div className="admin-form-group">
                <label className="admin-form-group__label">Plantilla predefinida</label>
                <select
                  className="admin-select"
                  value={plantillaSeleccionada}
                  onChange={(e) => aplicarPlantilla(e.target.value)}
                >
                  <option value="">-- Selecciona una plantilla (editable) --</option>
                  {plantillas.map((p) => (
                    <option key={p.id} value={p.id}>{p.nombre}</option>
                  ))}
                </select>
                <small className="text-mute">
                  La plantilla rellena el textarea; puedes editarla antes de enviar.
                </small>
              </div>
            )}
            <div className="admin-form-group">
              <label className="admin-form-group__label">Respuesta (editable)</label>
              <textarea
                rows={8}
                className="admin-input"
                value={textoRespuesta}
                onChange={(e) => setTextoRespuesta(e.target.value)}
                placeholder="Escribe o selecciona una plantilla, luego personaliza..."
                style={{ minHeight: 160 }}
              />
            </div>
          </div>
        )}
      </AdminModal>
    </div>
  );
}
