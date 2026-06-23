import React, { useEffect, useState } from "react";
import { FaPlus, FaEdit, FaTrash, FaSearch } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

const EMPTY = {
  titulo: "", contenido: "", resumen: "",
  estado: "PUBLICADA", categoria: "",
  imagen: null,
};

export default function AdminNoticias() {
  const [items, setItems] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try {
      const [n, c] = await Promise.all([
        api.get("/noticias/?page_size=200"),
        api.get("/categorias/"),
      ]);
      setItems(extractList(n.data));
      setCategorias(extractList(c.data));
    } catch (e) {
      setError("No se pudieron cargar las noticias.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); }, []);

  const abrirNuevo = () => { setEditItem(null); setForm(EMPTY); setModalOpen(true); };
  const abrirEditar = (n) => {
    setEditItem(n);
    setForm({
      titulo: n.titulo || "",
      contenido: n.contenido || "",
      resumen: n.resumen || "",
      estado: n.estado || "PUBLICADA",
      categoria: n.categoria || "",
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
      data.append("contenido", form.contenido);
      data.append("resumen", form.resumen);
      data.append("estado", form.estado);
      if (form.categoria) data.append("categoria", form.categoria);
      if (form.imagen) data.append("imagen", form.imagen);
      const cfg = { headers: { "Content-Type": "multipart/form-data" } };
      if (editItem) {
        await api.patch(`/noticias/${editItem.id}/`, data, cfg);
        setOk("Noticia actualizada correctamente.");
      } else {
        await api.post("/noticias/", data, cfg);
        setOk("Noticia creada correctamente.");
      }
      cerrar();
      cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "Error al guardar la noticia.");
    } finally {
      setSaving(false);
    }
  };

  const eliminar = async (n) => {
    if (!window.confirm(`¿Eliminar la noticia "${n.titulo}"?`)) return;
    setError(""); setOk("");
    try {
      await api.delete(`/noticias/${n.id}/`);
      setOk("Noticia eliminada.");
      cargar();
    } catch (e) {
      setError("No se pudo eliminar la noticia.");
    }
  };

  const itemsFiltrados = items.filter(n => {
    const t = (n.titulo || "").toLowerCase();
    const okB = !busqueda || t.includes(busqueda.toLowerCase());
    const okE = !filtroEstado || n.estado === filtroEstado;
    return okB && okE;
  });

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">Noticias ({items.length})</h3>
          <div className="flex">
            <div className="relative">
              <FaSearch className="absolute" />
              <input
                className="admin-input pl-7 w-52"
                placeholder="Buscar..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
            </div>
            <select
              className="admin-select w-40"
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
            >
              <option value="">Todos los estados</option>
              <option value="PUBLICADA">Publicada</option>
              <option value="BORRADOR">Borrador</option>
              <option value="ARCHIVADA">Archivada</option>
            </select>
            <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
              <FaPlus /> Nueva noticia
            </button>
          </div>
        </div>

        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando noticias…</div>
          ) : itemsFiltrados.length === 0 ? (
            <div className="admin-empty">No hay noticias que coincidan.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Título</th>
                  <th>Categoría</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {itemsFiltrados.map(n => (
                  <tr key={n.id}>
                    <td>
                      <div className="font-semibold">{n.titulo}</div>
                      <div className="text-mute text-[12px]">
                        {(n.resumen || "").substring(0, 80)}
                      </div>
                    </td>
                    <td>{n.categoria_nombre || "—"}</td>
                    <td>
                      <span className={"admin-badge " + (
                        n.estado === "PUBLICADA" ? "admin-badge--success" :
                        n.estado === "BORRADOR"  ? "admin-badge--warning" :
                                                     "admin-badge--gray"
                      )}>
                        {n.estado}
                      </span>
                    </td>
                    <td className="text-mute">
                      {n.fecha_publicacion ? new Date(n.fecha_publicacion).toLocaleString("es-PE") : ""}
                    </td>
                    <td className="actions justify-end">
                      <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(n)}>
                        <FaEdit /> Editar
                      </button>
                      <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(n)}>
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
        title={editItem ? "Editar noticia" : "Nueva noticia"}
        onClose={cerrar}
        wide
        footer={
          <>
            <button className="admin-btn" onClick={cerrar} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              {saving ? "Guardando…" : (editItem ? "Guardar cambios" : "Crear noticia")}
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
            <label className="admin-form-group__label">Resumen</label>
            <input
              className="admin-input"
              value={form.resumen}
              onChange={(e) => setForm({ ...form, resumen: e.target.value })}
              maxLength={400}
            />
            <div className="admin-form-hint">Resumen corto que se muestra en las tarjetas del listado.</div>
          </div>
          <div className="admin-form-group">
            <label className="admin-form-group__label admin-form-group__label--required">Contenido</label>
            <textarea
              className="admin-textarea min-h-[180px]"
              value={form.contenido}
              onChange={(e) => setForm({ ...form, contenido: e.target.value })}
              required
            />
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label">Categoría</label>
              <select
                className="admin-select"
                value={form.categoria}
                onChange={(e) => setForm({ ...form, categoria: e.target.value })}
              >
                <option value="">— Sin categoría —</option>
                {categorias.map(c => (
                  <option key={c.id} value={c.id}>{c.nombre}</option>
                ))}
              </select>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Estado</label>
              <select
                className="admin-select"
                value={form.estado}
                onChange={(e) => setForm({ ...form, estado: e.target.value })}
              >
                <option value="PUBLICADA">PUBLICADA</option>
                <option value="BORRADOR">BORRADOR</option>
                <option value="ARCHIVADA">ARCHIVADA</option>
              </select>
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
