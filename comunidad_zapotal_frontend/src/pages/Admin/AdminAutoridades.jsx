import React, { useEffect, useState } from "react";
import { FaPlus, FaEdit, FaTrash } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

const EMPTY = {
  cargo: "", periodo: "",
  fecha_inicio: "", fecha_fin: "",
  comunero: "", usuario: "",
};

export default function AdminAutoridades() {
  const [items, setItems] = useState([]);
  const [comuneros, setComuneros] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try {
      const [a, c, u] = await Promise.all([
        api.get("/autoridades/?page_size=200"),
        api.get("/comuneros/").catch(() => ({ data: { data: [] } })),
        api.get("/usuarios/?page_size=200").catch(() => ({ data: { data: [] } })),
      ]);
      setItems(extractList(a.data));
      setComuneros(extractList(c.data));
      setUsuarios(extractList(u.data));
    } catch (e) { setError("No se pudieron cargar las autoridades."); }
    finally { setLoading(false); }
  };
  useEffect(() => { cargar(); }, []);

  const abrirNuevo = () => { setEditItem(null); setForm(EMPTY); setModalOpen(true); };
  const abrirEditar = (a) => {
    setEditItem(a);
    setForm({
      cargo: a.cargo, periodo: a.periodo,
      fecha_inicio: a.fecha_inicio || "",
      fecha_fin: a.fecha_fin || "",
      comunero: a.comunero || "",
      usuario: a.usuario || "",
    });
    setModalOpen(true);
  };
  const cerrar = () => { setModalOpen(false); setEditItem(null); setForm(EMPTY); };

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true); setError(""); setOk("");
    try {
      const payload = { ...form };
      if (!payload.fecha_fin) delete payload.fecha_fin;
      if (editItem) await api.patch(`/autoridades/${editItem.id}/`, payload);
      else await api.post("/autoridades/", payload);
      setOk("Autoridad guardada.");
      cerrar(); cargar();
    } catch (err) { setError(err.response?.data?.detail || JSON.stringify(err.response?.data) || "Error al guardar."); }
    finally { setSaving(false); }
  };
  const eliminar = async (a) => {
    if (!window.confirm(`¿Eliminar a "${a.cargo}"?`)) return;
    setError(""); setOk("");
    try { await api.delete(`/autoridades/${a.id}/`); setOk("Eliminado."); cargar(); }
    catch (e) { setError("No se pudo eliminar."); }
  };

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card" style={{ marginTop: 16 }}>
        <div className="admin-card__header">
          <h3 className="admin-card__title">Autoridades ({items.length})</h3>
          <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
            <FaPlus /> Nueva autoridad
          </button>
        </div>
        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando…</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">No hay autoridades.</div>
          ) : (
            <table className="admin-table">
              <thead><tr><th>Cargo</th><th>Persona</th><th>Período</th><th>Desde</th><th>Hasta</th><th style={{ textAlign: "right" }}>Acciones</th></tr></thead>
              <tbody>
                {items.map(a => (
                  <tr key={a.id}>
                    <td style={{ fontWeight: 600 }}>{a.cargo}</td>
                    <td>{[a.nombres, a.apellidos].filter(Boolean).join(" ") || "—"}</td>
                    <td>{a.periodo || "—"}</td>
                    <td style={{ color: "#6b7280", fontSize: 12 }}>{a.fecha_inicio || "—"}</td>
                    <td style={{ color: "#6b7280", fontSize: 12 }}>{a.fecha_fin || "En curso"}</td>
                    <td className="actions" style={{ justifyContent: "flex-end" }}>
                      <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(a)}><FaEdit /> Editar</button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(a)}><FaTrash /></button>
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
        title={editItem ? "Editar autoridad" : "Nueva autoridad"}
        onClose={cerrar}
        footer={
          <>
            <button className="admin-btn" onClick={cerrar} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              {saving ? "Guardando…" : "Guardar"}
            </button>
          </>
        }
      >
        <form onSubmit={guardar}>
          <div className="admin-form-group">
            <label className="admin-form-group__label admin-form-group__label--required">Cargo</label>
            <input className="admin-input" value={form.cargo}
              onChange={(e) => setForm({ ...form, cargo: e.target.value })} maxLength={100} required />
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label">Período (texto)</label>
              <input className="admin-input" value={form.periodo}
                onChange={(e) => setForm({ ...form, periodo: e.target.value })} maxLength={50} placeholder="2025-2027" />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label admin-form-group__label--required">Comunero</label>
              <select className="admin-select" value={form.comunero}
                onChange={(e) => setForm({ ...form, comunero: e.target.value })} required>
                <option value="">— Seleccionar —</option>
                {comuneros.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.nombre_completo || `${c.nombres} ${c.apellidos}`} (DNI {c.dni})
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="admin-form-group">
            <label className="admin-form-group__label admin-form-group__label--required">Usuario asociado</label>
            <select className="admin-select" value={form.usuario}
              onChange={(e) => setForm({ ...form, usuario: e.target.value })} required>
              <option value="">— Seleccionar —</option>
              {usuarios.map(u => (
                <option key={u.id} value={u.id}>
                  {u.nombre_completo || u.email} ({u.tipo_usuario})
                </option>
              ))}
            </select>
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label admin-form-group__label--required">Fecha de inicio</label>
              <input type="date" className="admin-input" value={form.fecha_inicio}
                onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })} required />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Fecha de fin (opcional)</label>
              <input type="date" className="admin-input" value={form.fecha_fin}
                onChange={(e) => setForm({ ...form, fecha_fin: e.target.value })} />
            </div>
          </div>
        </form>
      </AdminModal>
    </div>
  );
}
