import React, { useEffect, useState } from "react";
import { FaPlus, FaEdit, FaTrash } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import { useConfirm } from "../../components/Admin/AdminConfirmDialog";

const EMPTY = { nombre: "", descripcion: "" };

export default function AdminCategorias() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const { confirm, ConfirmDialog } = useConfirm();

  const cargar = async () => {
    setLoading(true);
    try {
      const r = await api.get("/categorias/?page_size=200");
      setItems(extractList(r.data));
    } catch (e) { setError("No se pudieron cargar las categorías."); }
    finally { setLoading(false); }
  };
  useEffect(() => { cargar(); }, []);

  const abrirNuevo = () => { setEditItem(null); setForm(EMPTY); setModalOpen(true); };
  const abrirEditar = (c) => { setEditItem(c); setForm({ nombre: c.nombre, descripcion: c.descripcion || "" }); setModalOpen(true); };
  const cerrar = () => { setModalOpen(false); setEditItem(null); setForm(EMPTY); };

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true); setError(""); setOk("");
    try {
      if (editItem) await api.patch(`/categorias/${editItem.id}/`, form);
      else await api.post("/categorias/", form);
      setOk("Categoría guardada.");
      cerrar(); cargar();
    } catch (err) { setError(err.response?.data?.nombre?.[0] || err.response?.data?.detail || "Error al guardar."); }
    finally { setSaving(false); }
  };
  const eliminar = async (c) => {
    if (!await confirm({
      title: "Eliminar categoría",
      message: `¿Eliminar la categoría "${c.nombre}"? Esta acción no se puede deshacer.`,
    })) return;
    setError(""); setOk("");
    try { await api.delete(`/categorias/${c.id}/`); setOk("Categoría eliminada."); cargar(); }
    catch (e) { setError("No se pudo eliminar. Verifica que no tenga noticias asociadas."); }
  };

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">Categorías ({items.length})</h3>
          <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
            <FaPlus /> Nueva categoría
          </button>
        </div>
        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando…</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">No hay categorías.</div>
          ) : (
            <table className="admin-table">
              <thead><tr><th>Nombre</th><th>Descripción</th><th>Noticias</th><th className="text-right">Acciones</th></tr></thead>
              <tbody>
                {items.map(c => (
                  <tr key={c.id}>
                    <td className="font-semibold">{c.nombre}</td>
                    <td className="text-mute">{c.descripcion || "—"}</td>
                    <td>{c.total_noticias ?? 0}</td>
                    <td className="actions justify-end">
                      <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(c)}><FaEdit /> Editar</button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(c)}><FaTrash /></button>
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
        title={editItem ? "Editar categoría" : "Nueva categoría"}
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
            <label className="admin-form-group__label admin-form-group__label--required">Nombre</label>
            <input className="admin-input" value={form.nombre}
              onChange={(e) => setForm({ ...form, nombre: e.target.value })} maxLength={100} required />
          </div>
          <div className="admin-form-group">
            <label className="admin-form-group__label">Descripción</label>
            <textarea className="admin-textarea" value={form.descripcion}
              onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          </div>
        </form>
      </AdminModal>
      {ConfirmDialog}
    </div>
  );
}
