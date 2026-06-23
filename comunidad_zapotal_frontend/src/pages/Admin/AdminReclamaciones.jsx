import React, { useEffect, useState } from "react";
import { FaHistory, FaRedo, FaTrash, FaEdit } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

const ESTADOS = ["PENDIENTE", "EN_PROCESO", "RESUELTO"];

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
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
  const [detalle, setDetalle] = useState(null);

  const cargar = async () => {
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = filtroEstado ? { estado: filtroEstado } : {};
      const { data } = await api.get("/libro-reclamaciones/", { params });
      setItems(extractList(data));
    } catch (e) {
      setError("No se pudieron cargar las reclamaciones.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [filtroEstado]);

  const cambiarEstado = async (item, nuevoEstado) => {
    setError(""); setOk("");
    try {
      await api.post(`/libro-reclamaciones/${item.id}/cambiar_estado/`, { estado: nuevoEstado });
      setOk(`Reclamacion #${item.id} -> ${nuevoEstado}`);
      await cargar();
    } catch (e) {
      setError("No se pudo cambiar el estado.");
    }
  };

  const eliminar = async (item) => {
    if (!window.confirm(`Eliminar reclamacion #${item.id} de "${item.nombre}"?`)) return;
    setError(""); setOk("");
    try {
      await api.delete(`/libro-reclamaciones/${item.id}/`);
      setOk("Reclamacion eliminada.");
      await cargar();
    } catch (e) {
      setError("No se pudo eliminar.");
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
          <div className="flex">
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
                  <th>#</th>
                  <th>Nombre</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr key={it.id}>
                    <td>#{it.id}</td>
                    <td className="font-semibold">{it.nombre}</td>
                    <td className="text-xs">{it.email}</td>
                    <td>{it.tipo}</td>
                    <td className="text-mute">{formatFecha(it.fecha)}</td>
                    <td>
                      <span className={"admin-badge " + colorEstado(it.estado)}>
                        {it.estado}
                      </span>
                    </td>
                    <td className="actions justify-end">
                      <button className="admin-btn admin-btn-sm" onClick={() => setDetalle(it)}>
                        <FaEdit /> Ver
                      </button>
                      <select
                        className="admin-select min-w-[130px]"
                        value={it.estado}
                        onChange={(e) => cambiarEstado(it, e.target.value)}
                      >
                        {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
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
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <AdminModal
        open={!!detalle}
        title={`Reclamacion #${detalle?.id}`}
        onClose={() => setDetalle(null)}
        wide
        footer={
          <button className="admin-btn" onClick={() => setDetalle(null)}>Cerrar</button>
        }
      >
        {detalle && (
          <div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Nombre</label>
              <p className="m-0">{detalle.nombre}</p>
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label">Email</label>
                <p className="m-0">{detalle.email}</p>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label">Telefono</label>
                <p className="m-0">{detalle.telefono || "-"}</p>
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Direccion</label>
              <p className="m-0">{detalle.direccion || "-"}</p>
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label">Tipo</label>
                <p className="m-0">{detalle.tipo}</p>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label">Fecha</label>
                <p className="m-0">{formatFecha(detalle.fecha)}</p>
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Descripcion</label>
              <div className="rounded-8 whitespace-pre-wrap text-[13px]">
                {detalle.descripcion}
              </div>
            </div>
          </div>
        )}
      </AdminModal>
    </div>
  );
}
