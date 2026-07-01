import React, { useEffect, useState, useCallback, useRef } from "react";
import { FaPlus, FaEdit, FaTrash, FaSearch } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import { useConfirm } from "../../components/Admin/AdminConfirmDialog";
import { useUrlFilters, parseIntParam } from "../../hooks/useUrlFilters";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import SubirMultimedia from "../../components/media/SubirMultimedia/SubirMultimedia";
import "../../components/media/SubirMultimedia/SubirMultimedia.css";

const EMPTY = {
  titulo: "", contenido: "", resumen: "",
  estado: "PUBLICADA", categoria: "",
  imagen: null,
};

export default function AdminNoticias() {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const abortRef = useRef(null);

  const [filters, setFilters, clearFilters] = useUrlFilters({
    estadoNoticia: { defaultValue: "" },
    search: { defaultValue: "" },
    page: { defaultValue: 1, parser: parseIntParam },
  });
  const debouncedSearch = useDebouncedValue(filters.search, 350);
  const { confirm, ConfirmDialog } = useConfirm();

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
      const params = { page: filters.page, page_size: 15 };
      if (filters.estadoNoticia) params.estado = filters.estadoNoticia;
      if (debouncedSearch) params.search = debouncedSearch;
      const [n, c] = await Promise.all([
        api.get("/noticias/", { params, signal: controller.signal }),
        api.get("/categorias/", { signal: controller.signal }),
      ]);
      const data = n.data;
      setItems(extractList(data));
      setTotalItems(data.count || 0);
      setCategorias(extractList(c.data));
    } catch (e) {
      if (e.name !== "CanceledError" && e.name !== "AbortError") {
        setError("No se pudieron cargar las noticias.");
      }
    } finally {
      setLoading(false);
    }
  }, [filters.page, filters.estadoNoticia, debouncedSearch]);

  useEffect(() => { cargar(); }, [cargar]);
  useEffect(() => {
    if (filters.page !== 1) setFilters({ page: 1 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.estadoNoticia, debouncedSearch]);

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
      const cfg = {};
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
    if (!await confirm({
      title: "Eliminar noticia",
      message: `¿Eliminar la noticia "${n.titulo}"? Esta acción no se puede deshacer.`,
    })) return;
    setError(""); setOk("");
    try {
      await api.delete(`/noticias/${n.id}/`);
      setOk("Noticia eliminada.");
      cargar();
    } catch (e) {
      setError("No se pudo eliminar la noticia.");
    }
  };

  const itemsFiltrados = items;

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">Noticias ({totalItems})</h3>
          <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
            <FaPlus /> Nueva noticia
          </button>
        </div>
        <div className="admin-card__body">
          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            chips={[
              { key: "estadoNoticia", value: "", label: "Todos" },
              { key: "estadoNoticia", value: "PUBLICADA", label: "Publicadas" },
              { key: "estadoNoticia", value: "BORRADOR", label: "Borradores" },
              { key: "estadoNoticia", value: "ARCHIVADA", label: "Archivadas" },
            ]}
            searchKey="search"
            searchPlaceholder="Buscar por titulo..."
          />

          {loading ? (
            <div className="admin-loading">Cargando noticias...</div>
          ) : itemsFiltrados.length === 0 ? (
            <div className="admin-empty">
              {Object.values(filters).some((v) => v && v !== 1)
                ? "No hay noticias con los filtros aplicados."
                : "No hay noticias."}
            </div>
          ) : (
            <>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Titulo</th>
                    <th>Categoria</th>
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
                      <td>{n.categoria_nombre || "-"}</td>
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
              <Pagination
                page={filters.page}
                totalPages={Math.max(1, Math.ceil(totalItems / 15))}
                totalItems={totalItems}
                onPageChange={(p) => setFilters({ page: p })}
              />
            </>
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
          <div className="admin-form-group">
            <SubirMultimedia
              itemId={editItem?.id}
              itemType="noticia"
              initialFiles={editItem?.multimedia || []}
            />
          </div>
        </form>
      </AdminModal>
      {ConfirmDialog}
    </div>
  );
}
