import React, { useEffect, useState, useCallback, useRef } from "react";
import { FaPlus, FaEdit, FaTrash, FaSearch } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import { useConfirm } from "../../components/Admin/AdminConfirmDialog";
import { useUrlFilters, parseIntParam } from "../../hooks/useUrlFilters";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import SubirMultimedia from "../../components/SubirMultimedia";
import "../../components/SubirMultimedia.css";

const EMPTY = {
  titulo: "", descripcion: "", lugar: "",
  fecha: "", imagen: null,
};

function toLocalDateTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function AdminEventos() {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const abortRef = useRef(null);
  const { confirm, ConfirmDialog } = useConfirm();

  const [filters, setFilters, clearFilters] = useUrlFilters({
    estadoEvento: { defaultValue: "" }, // "activos" | "finalizados" | ""
    search: { defaultValue: "" },
    page: { defaultValue: 1, parser: parseIntParam },
  });
  const debouncedSearch = useDebouncedValue(filters.search, 350);

  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const cargar = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = { page: filters.page };
      if (filters.estadoEvento === "activos") {
        const hoy = new Date().toISOString().slice(0, 10);
        params.fecha__gte = hoy;
      } else if (filters.estadoEvento === "finalizados") {
        const hoy = new Date().toISOString().slice(0, 10);
        params.fecha__lt = hoy;
      }
      if (debouncedSearch) params.search = debouncedSearch;
      const r = await api.get("/eventos/", { params, signal: controller.signal });
      const data = r.data;
      setItems(extractList(data));
      setTotalItems(data.count || 0);
    } catch (e) {
      if (e.name !== "CanceledError" && e.name !== "AbortError") {
        setError("No se pudieron cargar los eventos.");
      }
    } finally {
      setLoading(false);
    }
  }, [filters.page, filters.estadoEvento, debouncedSearch]);

  useEffect(() => { cargar(); }, [cargar]);
  useEffect(() => {
    if (filters.page !== 1) setFilters({ page: 1 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.estadoEvento, debouncedSearch]);

  const abrirNuevo = () => { setEditItem(null); setForm(EMPTY); setModalOpen(true); };
  const abrirEditar = (ev) => {
    setEditItem(ev);
    setForm({
      titulo: ev.titulo || "",
      descripcion: ev.descripcion || "",
      lugar: ev.lugar || "",
      fecha: toLocalDateTime(ev.fecha),
      imagen: null,
    });
    setModalOpen(true);
  };
  const cerrar = () => { setModalOpen(false); setEditItem(null); setForm(EMPTY); };

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true); setError(""); setOk("");
    try {
      const data = new FormData();
      data.append("titulo", form.titulo);
      data.append("descripcion", form.descripcion);
      data.append("lugar", form.lugar);
      if (form.fecha) data.append("fecha", new Date(form.fecha).toISOString());
      if (form.imagen) data.append("imagen", form.imagen);
      const cfg = { headers: { "Content-Type": "multipart/form-data" } };
      if (editItem) {
        await api.patch(`/eventos/${editItem.id}/`, data, cfg);
        setOk("Evento actualizado.");
      } else {
        await api.post("/eventos/", data, cfg);
        setOk("Evento creado.");
      }
      cerrar();
      cargar();
    } catch (err) {
      const data = err.response?.data;
      setError(typeof data === "string" ? data : (data?.detail || JSON.stringify(data) || "Error al guardar."));
    } finally {
      setSaving(false);
    }
  };

  const eliminar = async (ev) => {
    if (!await confirm({
      title: "Eliminar evento",
      message: `¿Eliminar el evento "${ev.titulo}"? Esta acción no se puede deshacer.`,
    })) return;
    setError(""); setOk("");
    try {
      await api.delete(`/eventos/${ev.id}/`);
      setOk("Evento eliminado.");
      cargar();
    } catch (e) {
      setError("No se pudo eliminar el evento.");
    }
  };

  const itemsFiltrados = items;

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">Eventos ({totalItems})</h3>
          <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
            <FaPlus /> Nuevo evento
          </button>
        </div>
        <div className="admin-card__body">
          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            chips={[
              { key: "estadoEvento", value: "", label: "Todos" },
              { key: "estadoEvento", value: "activos", label: "Activos" },
              { key: "estadoEvento", value: "finalizados", label: "Finalizados" },
            ]}
            searchKey="search"
            searchPlaceholder="Buscar por titulo..."
          />

          {loading ? (
            <div className="admin-loading">Cargando eventos...</div>
          ) : itemsFiltrados.length === 0 ? (
            <div className="admin-empty">
              {Object.values(filters).some((v) => v && v !== 1)
                ? "No hay eventos con los filtros aplicados."
                : "No hay eventos."}
            </div>
          ) : (
            <>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Titulo</th>
                    <th>Lugar</th>
                    <th>Fecha</th>
                    <th>Reacciones</th>
                    <th>Comentarios</th>
                    <th className="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {itemsFiltrados.map(ev => (
                  <tr key={ev.id}>
                    <td>
                      <div className="font-semibold">{ev.titulo}</div>
                      <div className="text-mute">
                        {(ev.descripcion || "").substring(0, 80)}
                      </div>
                    </td>
                    <td>{ev.lugar || "—"}</td>
                    <td className="text-mute">
                      {ev.fecha ? new Date(ev.fecha).toLocaleString("es-PE") : ""}
                    </td>
                    <td>
                      {Object.entries(ev.total_reacciones || {}).map(([k, v]) => (
                        <span key={k} className="admin-badge admin-badge--info mr-1">
                          {k} {v}
                        </span>
                      ))}
                    </td>
                    <td>{ev.total_comentarios || 0}</td>
                    <td className="actions justify-end">
                      <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(ev)}>
                        <FaEdit /> Editar
                      </button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(ev)}>
                        <FaTrash />
                      </button>
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
        open={modalOpen}
        title={editItem ? "Editar evento" : "Nuevo evento"}
        onClose={cerrar}
        footer={
          <>
            <button className="admin-btn" onClick={cerrar} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              {saving ? "Guardando…" : (editItem ? "Guardar cambios" : "Crear evento")}
            </button>
          </>
        }
      >
        <form onSubmit={guardar}>
          <div className="admin-form-group">
            <label className="admin-form-group__label admin-form-group__label--required">Título</label>
            <input
              className="admin-input"
              value={form.titulo}
              onChange={(e) => setForm({ ...form, titulo: e.target.value })}
              maxLength={200}
              required
            />
          </div>
          <div className="admin-form-group">
            <label className="admin-form-group__label">Descripción</label>
            <textarea
              className="admin-textarea"
              value={form.descripcion}
              onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
            />
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label admin-form-group__label--required">Fecha y hora</label>
              <input
                type="datetime-local"
                className="admin-input"
                value={form.fecha}
                onChange={(e) => setForm({ ...form, fecha: e.target.value })}
                required
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Lugar</label>
              <input
                className="admin-input"
                value={form.lugar}
                onChange={(e) => setForm({ ...form, lugar: e.target.value })}
                maxLength={200}
              />
            </div>
          </div>
          <div className="admin-form-group">
            <label className="admin-form-group__label">Imagen de portada</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setForm({ ...form, imagen: e.target.files?.[0] || null })}
            />
            {editItem?.imagen && !form.imagen && (
              <div className="admin-form-hint">Imagen actual: {editItem.imagen.split("/").pop()}</div>
            )}
          </div>
          <div className="admin-form-group">
            <SubirMultimedia
              itemId={editItem?.id}
              itemType="evento"
              initialFiles={editItem?.multimedia || []}
            />
          </div>
        </form>
      </AdminModal>
      {ConfirmDialog}
    </div>
  );
}
