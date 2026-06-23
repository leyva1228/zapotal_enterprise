import React, { useEffect, useState } from "react";
import { FaEnvelope, FaRedo, FaTrash, FaEye } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch { return "-"; }
}

export default function AdminContacto() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [detalle, setDetalle] = useState(null);

  const cargar = async () => {
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = busqueda ? { search: busqueda } : {};
      const { data } = await api.get("/contacto-mensajes/", { params });
      setItems(extractList(data));
    } catch (e) {
      setError("No se pudieron cargar los mensajes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  const eliminar = async (item) => {
    if (!window.confirm(`Eliminar mensaje de "${item.nombre}"?`)) return;
    setError(""); setOk("");
    try {
      await api.delete(`/contacto-mensajes/${item.id}/`);
      setOk("Mensaje eliminado.");
      if (detalle?.id === item.id) setDetalle(null);
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
            <FaEnvelope className="mr-[6px]" />
            Mensajes de contacto ({items.length})
          </h3>
          <div className="flex">
            <input
              className="admin-input min-w-[240px]"
              placeholder="Buscar por nombre, email o asunto..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") cargar(); }}
            />
            <button className="admin-btn admin-btn-sm" onClick={cargar} disabled={loading}>
              <FaRedo /> Recargar
            </button>
          </div>
        </div>
        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">No hay mensajes de contacto.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Email</th>
                  <th>Asunto</th>
                  <th>Fecha</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr key={it.id}>
                    <td className="font-semibold">{it.nombre}</td>
                    <td className="text-xs">{it.email}</td>
                    <td>{it.asunto}</td>
                    <td className="text-mute">{formatFecha(it.fecha)}</td>
                    <td className="actions justify-end">
                      <button className="admin-btn admin-btn-sm" onClick={() => setDetalle(it)}>
                        <FaEye /> Ver
                      </button>
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
        title={`Mensaje de ${detalle?.nombre || ""}`}
        onClose={() => setDetalle(null)}
        wide
        footer={
          <button className="admin-btn" onClick={() => setDetalle(null)}>Cerrar</button>
        }
      >
        {detalle && (
          <div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label">Nombre</label>
                <p className="m-0">{detalle.nombre}</p>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label">Email</label>
                <p className="m-0">{detalle.email}</p>
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Asunto</label>
              <p className="m-0">{detalle.asunto}</p>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Fecha</label>
              <p className="m-0">{formatFecha(detalle.fecha)}</p>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Mensaje</label>
              <div className="rounded-8 whitespace-pre-wrap text-[13px]">
                {detalle.mensaje}
              </div>
            </div>
          </div>
        )}
      </AdminModal>
    </div>
  );
}
