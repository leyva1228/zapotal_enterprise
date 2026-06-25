import React, { useEffect, useState, useCallback, useRef } from "react";
import { FaTrashAlt, FaCheck, FaTimes, FaRedo, FaUserShield } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import { useUrlFilters, parseIntParam } from "../../hooks/useUrlFilters";

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch { return "-"; }
}

function colorEstado(estado) {
  if (estado === "PENDIENTE") return "admin-badge--warning";
  if (estado === "APROBADA") return "admin-badge--danger";
  if (estado === "RECHAZADA") return "admin-badge--info";
  return "admin-badge--gray";
}

export default function AdminBajas() {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [modal, setModal] = useState({ open: false, item: null, accion: null });
  const [notas, setNotas] = useState("");
  const [saving, setSaving] = useState(false);
  const abortRef = useRef(null);

  const [filters, setFilters, clearFilters] = useUrlFilters({
    estado: { defaultValue: "PENDIENTE" },
    page: { defaultValue: 1, parser: parseIntParam },
  });

  const cargar = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = { page: filters.page };
      if (filters.estado) params.estado = filters.estado;
      const { data } = await api.get("/solicitudes-baja/", { params, signal: controller.signal });
      setItems(extractList(data));
      setTotalItems(data.count || 0);
    } catch (e) {
      if (e.name !== "CanceledError" && e.name !== "AbortError") {
        setError("No se pudieron cargar las solicitudes.");
      }
    } finally {
      setLoading(false);
    }
  }, [filters.page, filters.estado]);

  useEffect(() => { cargar(); }, [cargar]);
  useEffect(() => {
    if (filters.page !== 1) setFilters({ page: 1 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.estado]);

  const ejecutar = async () => {
    if (!modal.item) return;
    setSaving(true);
    setError(""); setOk("");
    try {
      const endpoint = modal.accion === "aprobar"
        ? `/solicitudes-baja/${modal.item.id}/aprobar/`
        : `/solicitudes-baja/${modal.item.id}/rechazar/`;
      await api.post(endpoint, { notas_admin: notas });
      setOk(`Solicitud ${modal.accion === "aprobar" ? "aprobada" : "rechazada"}.`);
      setModal({ open: false, item: null, accion: null });
      setNotas("");
      await cargar();
    } catch (e) {
      const d = e.response?.data;
      setError(typeof d === "string" ? d : (d?.detail || "No se pudo procesar."));
    } finally { setSaving(false); }
  };

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaUserShield className="mr-[6px]" />
            Solicitudes de baja de cuenta ({totalItems})
          </h3>
        </div>
        <div className="admin-card__body">
          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            chips={[
              { key: "estado", value: "PENDIENTE", label: "Pendientes" },
              { key: "estado", value: "APROBADA", label: "Aprobadas" },
              { key: "estado", value: "RECHAZADA", label: "Rechazadas" },
              { key: "estado", value: "CANCELADA", label: "Canceladas" },
              { key: "estado", value: "", label: "Todas" },
            ]}
            searchKey="search"
            searchPlaceholder="Buscar por email o nombre..."
          />
            {loading ? (
              <div className="admin-loading">Cargando...</div>
            ) : items.length === 0 ? (
              <div className="admin-empty">No hay solicitudes con ese filtro.</div>
            ) : (
              <>
              <table className="admin-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Motivo</th>
                  <th>Fecha solicitud</th>
                  <th>Estado</th>
                  <th>Revisado por</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((s) => (
                  <tr key={s.id}>
                    <td>
                      <div className="font-semibold">{s.usuario_email}</div>
                      <div className="text-[12px]">{s.usuario_nombre}</div>
                    </td>
                    <td className="max-w-sm">
                      <div className="text-[13px]">{s.motivo}</div>
                      {s.notas_admin && (
                        <div className="text-[11px] text-soft">
                          <strong>Notas admin:</strong> {s.notas_admin}
                        </div>
                      )}
                    </td>
                    <td className="text-[12px]">{formatFecha(s.fecha_solicitud)}</td>
                    <td><span className={`admin-badge ${colorEstado(s.estado)}`}>{s.estado}</span></td>
                    <td className="text-[12px]">{s.fecha_revision ? formatFecha(s.fecha_revision) : "-"}</td>
                    <td className="actions justify-end">
                      {s.estado === "PENDIENTE" && (
                        <>
                          <button
                            className="admin-btn admin-btn-sm admin-btn-danger"
                            onClick={() => setModal({ open: true, item: s, accion: "aprobar" })}
                          >
                            <FaTrashAlt /> Aprobar
                          </button>
                          <button
                            className="admin-btn admin-btn-sm"
                            onClick={() => setModal({ open: true, item: s, accion: "rechazar" })}
                          >
                            <FaTimes /> Rechazar
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
                </tbody>
              </table>
              <Pagination
                page={filters.page}
                totalPages={Math.max(1, Math.ceil(totalItems / 20))}
                totalItems={totalItems}
                onPageChange={(p) => setFilters({ page: p })}
              />
              </>
            )}
          </div>
      </div>

      <AdminModal
        open={modal.open}
        title={modal.accion === "aprobar" ? `Aprobar baja de ${modal.item?.usuario_email}` : `Rechazar baja de ${modal.item?.usuario_email}`}
        onClose={() => !saving && setModal({ open: false, item: null, accion: null })}
        footer={
          <>
            <button className="admin-btn" onClick={() => setModal({ open: false, item: null, accion: null })} disabled={saving}>
              Cancelar
            </button>
            <button
              className={`admin-btn ${modal.accion === "aprobar" ? "admin-btn-danger" : "admin-btn-primary"}`}
              onClick={ejecutar}
              disabled={saving}
            >
              {saving ? "Procesando..." : (modal.accion === "aprobar" ? "Confirmar baja" : "Confirmar rechazo")}
            </button>
          </>
        }
      >
        <p className="text-mute">
          {modal.accion === "aprobar"
            ? "El usuario sera desactivado y no podra iniciar sesion. Sus datos se conservaran por 30 dias."
            : "El rechazo sera notificado al usuario."}
        </p>
        <div className="admin-form-group">
          <label className="admin-form-group__label">Notas (opcional)</label>
          <textarea
            className="admin-textarea"
            value={notas}
            onChange={(e) => setNotas(e.target.value)}
            rows={3}
            placeholder="Comentarios para el usuario..."
          />
        </div>
      </AdminModal>
    </div>
  );
}
