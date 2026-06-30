import React, { useEffect, useState, useCallback } from "react";
import { FaEdit, FaSave, FaTimes, FaFileAlt, FaRedo, FaExclamationTriangle } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

export default function AdminCms() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState({ titulo: "", contenido: "" });
  const [saving, setSaving] = useState(false);

  const cargar = async () => {
    setLoading(true);
    setError(""); setOk("");
    try {
      const { data } = await api.get("/cms/contenido/");
      setItems(extractList(data));
    } catch (e) {
      setError("No se pudo cargar el contenido.");
    } finally { setLoading(false); }
  };

  useEffect(() => { cargar(); }, []);

  const iniciarEdicion = (item) => {
    setEditando(item);
    setForm({ titulo: item.titulo, contenido: item.contenido });
  };
  const cancelar = () => {
    setEditando(null);
    setForm({ titulo: "", contenido: "" });
  };

  const guardar = async () => {
    setSaving(true);
    try {
      await api.patch(`/cms/contenido/${editando.id}/`, {
        titulo: form.titulo,
        contenido: form.contenido,
      });
      setOk(`Se actualizo "${editando.titulo}".`);
      cancelar();
      cargar();
    } catch (e) {
      setError("No se pudo guardar.");
    } finally { setSaving(false); }
  };

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-banner admin-banner--warn mt-4">
        <FaExclamationTriangle />
        <div>
          <strong>Esta seccion esta deprecada.</strong>{' '}
          El contenido aqui (<code>ContenidoEstatico</code> de <code>apps.cms</code>) ya no se muestra en
          la UI publica. Usa{' '}
          <a href="/admin/institucional" style={{ textDecoration: 'underline', fontWeight: 600 }}>
            <code>/admin/institucional</code>
          </a>{' '}
          en su lugar: ahi encontraras Configuracion, Textos Internos, Marco Legal, Paginas Legales,
          Hitos Historicos, Galeria y Categorias. Este panel se conserva solo como respaldo historico
          y se eliminara en una version futura.
        </div>
      </div>

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaFileAlt className="mr-[6px]" />
            Contenido estatico ({items.length})
          </h3>
          <button className="admin-btn admin-btn-sm" onClick={cargar} disabled={loading}>
            <FaRedo /> Recargar
          </button>
        </div>
        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">No hay contenido. Ejecute <code>python manage.py seed_contenido_estatico</code>.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Seccion</th>
                  <th>Titulo</th>
                  <th>Contenido</th>
                  <th>Activo</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr key={it.id}>
                    <td>
                      <span className="admin-badge admin-badge--info">{it.seccion}</span>
                    </td>
                    <td className="font-semibold">{it.titulo}</td>
                    <td className="text-[12px] text-mute">
                      {it.contenido.substring(0, 140) + (it.contenido.length > 140 ? "..." : "")}
                    </td>
                    <td>
                      <span className={`admin-badge ${it.activo ? "admin-badge--success" : "admin-badge--gray"}`}>
                        {it.activo ? "SI" : "NO"}
                      </span>
                    </td>
                    <td className="actions justify-end">
                      <button
                        className="admin-btn admin-btn-sm"
                        onClick={() => iniciarEdicion(it)}
                      >
                        <FaEdit /> Editar
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
        open={!!editando}
        title={`Editar: ${editando?.titulo || ''}`}
        onClose={cancelar}
        wide
        footer={
          <>
            <button className="admin-btn" onClick={cancelar} disabled={saving}>
              <FaTimes /> Cancelar
            </button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              <FaSave /> {saving ? "Guardando..." : "Guardar"}
            </button>
          </>
        }
      >
        <div className="admin-form-group">
          <label className="admin-form-group__label">Titulo</label>
          <input
            className="admin-input"
            value={form.titulo}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
            maxLength={200}
          />
        </div>
        <div className="admin-form-group">
          <label className="admin-form-group__label">Contenido</label>
          <textarea
            className="admin-textarea"
            value={form.contenido}
            onChange={(e) => setForm({ ...form, contenido: e.target.value })}
            rows={10}
          />
          <div className="admin-form-hint">Texto plano. Se muestra tal cual en la pagina publica.</div>
        </div>
      </AdminModal>
    </div>
  );
}
