import React, { useEffect, useState } from "react";
import { FaPlus, FaEdit, FaTrash, FaSearch } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try {
      const r = await api.get("/eventos/?page_size=200");
      setItems(extractList(r.data));
    } catch (e) {
      setError("No se pudieron cargar los eventos.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); }, []);

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
    if (!window.confirm(`¿Eliminar el evento "${ev.titulo}"?`)) return;
    setError(""); setOk("");
    try {
      await api.delete(`/eventos/${ev.id}/`);
      setOk("Evento eliminado.");
      cargar();
    } catch (e) {
      setError("No se pudo eliminar el evento.");
    }
  };

  const itemsFiltrados = items.filter(ev =>
    !busqueda || (ev.titulo || "").toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card" style={{ marginTop: 16 }}>
        <div className="admin-card__header">
          <h3 className="admin-card__title">Eventos ({items.length})</h3>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div style={{ position: "relative" }}>
              <FaSearch style={{ position: "absolute", left: 10, top: 11, color: "#9ca3af" }} />
              <input
                className="admin-input"
                style={{ paddingLeft: 30, width: 200 }}
                placeholder="Buscar..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
            </div>
            <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
              <FaPlus /> Nuevo evento
            </button>
          </div>
        </div>

        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando eventos…</div>
          ) : itemsFiltrados.length === 0 ? (
            <div className="admin-empty">No hay eventos.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Título</th>
                  <th>Lugar</th>
                  <th>Fecha</th>
                  <th>Reacciones</th>
                  <th>Comentarios</th>
                  <th style={{ textAlign: "right" }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {itemsFiltrados.map(ev => (
                  <tr key={ev.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{ev.titulo}</div>
                      <div style={{ color: "#6b7280", fontSize: 12 }}>
                        {(ev.descripcion || "").substring(0, 80)}
                      </div>
                    </td>
                    <td>{ev.lugar || "—"}</td>
                    <td style={{ color: "#6b7280", fontSize: 12 }}>
                      {ev.fecha ? new Date(ev.fecha).toLocaleString("es-PE") : ""}
                    </td>
                    <td>
                      {Object.entries(ev.total_reacciones || {}).map(([k, v]) => (
                        <span key={k} className="admin-badge admin-badge--info" style={{ marginRight: 4 }}>
                          {k} {v}
                        </span>
                      ))}
                    </td>
                    <td>{ev.total_comentarios || 0}</td>
                    <td className="actions" style={{ justifyContent: "flex-end" }}>
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
        </form>
      </AdminModal>
    </div>
  );
}
