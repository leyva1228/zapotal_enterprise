import React, { useEffect, useState } from "react";
import { FaBell, FaRedo, FaCheck, FaCheckDouble, FaTrash } from "react-icons/fa";
import api, { extractList } from "../../api";

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch { return "-"; }
}

export default function AdminNotificaciones() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [filtroLeido, setFiltroLeido] = useState("");

  const cargar = async () => {
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = {};
      if (filtroLeido === "leidas") params.leido = true;
      if (filtroLeido === "no_leidas") params.leido = false;
      const { data } = await api.get("/notificaciones/", { params });
      setItems(extractList(data));
    } catch (e) {
      setError("No se pudieron cargar las notificaciones.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [filtroLeido]);

  const marcarLeida = async (n) => {
    if (n.leido) return;
    setError(""); setOk("");
    try {
      await api.patch(`/notificaciones/${n.id}/`, { leido: true });
      setOk("Notificacion marcada como leida.");
      await cargar();
    } catch (e) {
      setError("No se pudo marcar como leida.");
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
      await cargar();
    } catch (e) {
      setError("No se pudo eliminar.");
    }
  };

  const noLeidas = items.filter((i) => !i.leido).length;

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaBell className="mr-[6px]" />
            Notificaciones ({items.length}) {noLeidas > 0 && <span className="admin-badge admin-badge--warning">{noLeidas} sin leer</span>}
          </h3>
          <div className="flex">
            <select
              className="admin-select min-w-[160px]"
              value={filtroLeido}
              onChange={(e) => setFiltroLeido(e.target.value)}
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
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">No hay notificaciones.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Estado</th>
                  <th>Titulo</th>
                  <th>Mensaje</th>
                  <th>Tipo</th>
                  <th>Fecha</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr key={it.id} className={it.leido ? '' : 'bg-gray-50'}>
                    <td>
                      {it.leido
                        ? <span className="admin-badge admin-badge--gray">Leida</span>
                        : <span className="admin-badge admin-badge--info">Nueva</span>}
                    </td>
                    <td className="font-semibold">{it.titulo}</td>
                    <td className="overflow-hidden text-ellipsis">
                      {it.mensaje}
                    </td>
                    <td><span className="admin-badge admin-badge--gray">{it.tipo || "info"}</span></td>
                    <td className="text-mute">{formatFecha(it.fecha)}</td>
                    <td className="actions justify-end">
                      {!it.leido && (
                        <button
                          className="admin-btn admin-btn-sm admin-btn-success"
                          onClick={() => marcarLeida(it)}
                          title="Marcar como leida"
                        >
                          <FaCheck />
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
          )}
        </div>
      </div>
    </div>
  );
}
