/**
 * AdminGaleria - Gestion de la galeria de imagenes.
 *
 * CRUD completo de GaleriaImagen con filtros por categoria, busqueda
 * y paginacion. Diseno pulido con Tailwind para grilla de imagenes.
 *
 * Endpoints:
 * - GET    /api/v1/galeria/                  (lista paginada con filtros)
 * - POST   /api/v1/galeria/                  (crear con FormData/imagen)
 * - PATCH  /api/v1/galeria/{id}/             (actualizar)
 * - DELETE /api/v1/galeria/{id}/             (eliminar)
 */
import React, { useEffect, useState, useCallback, useRef } from "react";
import {
  FaPlus, FaEdit, FaTrash, FaImages, FaCheck, FaTimes, FaSave,
  FaCalendarAlt, FaSortNumericDown, FaTag, FaToggleOn, FaToggleOff,
  FaSearch,
} from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import { useConfirm } from "../../components/Admin/AdminConfirmDialog";
import { useUrlFilters, parseIntParam } from "../../hooks/useUrlFilters";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import useAdminRefresh from "../../hooks/useAdminRefresh";

const CATEGORIAS = [
  { value: "",                label: "Todas las categorias" },
  { value: "COMUNIDAD",       label: "Comunidad" },
  { value: "AUTORIDADES",     label: "Autoridades" },
  { value: "FESTIVIDADES",    label: "Festividades" },
  { value: "INFRAESTRUCTURA", label: "Infraestructura" },
  { value: "NATURALEZA",      label: "Naturaleza" },
  { value: "PATRIMONIO",      label: "Patrimonio Cultural" },
  { value: "OTRO",            label: "Otro" },
];

const CATEGORIA_COLORS = {
  COMUNIDAD:       "bg-emerald-100 text-emerald-800",
  AUTORIDADES:     "bg-amber-100 text-amber-800",
  FESTIVIDADES:    "bg-rose-100 text-rose-800",
  INFRAESTRUCTURA: "bg-sky-100 text-sky-800",
  NATURALEZA:      "bg-lime-100 text-lime-800",
  PATRIMONIO:      "bg-violet-100 text-violet-800",
  OTRO:            "bg-slate-100 text-slate-700",
};

const EMPTY = {
  titulo: "",
  descripcion: "",
  categoria: "COMUNIDAD",
  fecha: "",
  orden: 0,
  activo: true,
  imagen: null,
  imagen_url_externa: "",
  noticia: "",
  evento: "",
};

export default function AdminGaleria() {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const { confirm, ConfirmDialog } = useConfirm();

  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const [preview, setPreview] = useState(null);
  const [noticias, setNoticias] = useState([]);
  const [eventos, setEventos] = useState([]);

  const abortRef = useRef(null);

  const [filters, setFilters, clearFilters] = useUrlFilters({
    categoria: { defaultValue: "" },
    search:    { defaultValue: "" },
    page:      { defaultValue: 1, parser: parseIntParam },
  });

  const debouncedSearch = useDebouncedValue(filters.search, 350);

  const cargar = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError("");
    setOk("");
    try {
      const params = { page: filters.page, page_size: 20 };
      if (filters.categoria) params.categoria = filters.categoria;
      if (debouncedSearch) params.search = debouncedSearch;
      const { data } = await api.get("/galeria/", { params, signal: controller.signal });
      setItems(extractList(data));
      setTotalItems(data.count || 0);
    } catch (e) {
      if (e.name !== "CanceledError" && e.code !== "ERR_CANCELED") {
        setError("No se pudieron cargar las imagenes.");
      }
    } finally {
      if (abortRef.current === controller) setLoading(false);
    }
  }, [filters.page, filters.categoria, debouncedSearch]);

  useEffect(() => { cargar(); }, [cargar]);
  useAdminRefresh(cargar);
  useEffect(() => {
    if (filters.page !== 1) setFilters({ page: 1 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.categoria, debouncedSearch]);

  // Cargar listas de noticias y eventos para los selectores del modal
  // de alta/edicion de GaleriaImagen.
  useEffect(() => {
    Promise.all([
      api.get('/noticias/', { params: { page_size: 100, estado: 'PUBLICADA' } })
        .then(r => setNoticias(extractList(r.data)))
        .catch(() => setNoticias([])),
      api.get('/eventos/', { params: { page_size: 100 } })
        .then(r => setEventos(extractList(r.data)))
        .catch(() => setEventos([])),
    ]);
  }, []);

  const abrirNuevo = () => {
    setEditItem(null);
    setForm(EMPTY);
    setPreview(null);
    setModalOpen(true);
  };

  const abrirEditar = (it) => {
    setEditItem(it);
    setForm({
      titulo: it.titulo || "",
      descripcion: it.descripcion || "",
      categoria: it.categoria || "COMUNIDAD",
      fecha: it.fecha || "",
      orden: it.orden || 0,
      activo: it.activo !== false,
      imagen: null,
      imagen_url_externa: it.imagen_url_externa || "",
      noticia: it.noticia || "",
      evento: it.evento || "",
    });
    setPreview(it.imagen_url || null);
    setModalOpen(true);
  };

  const cerrar = () => {
    setModalOpen(false);
    setEditItem(null);
    setForm(EMPTY);
    setPreview(null);
  };

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true);
    setError("");
    setOk("");
    try {
      const data = new FormData();
      data.append("titulo", form.titulo);
      data.append("descripcion", form.descripcion);
      data.append("categoria", form.categoria);
      data.append("orden", String(form.orden || 0));
      data.append("activo", form.activo ? "true" : "false");
      if (form.fecha) data.append("fecha", form.fecha);
      if (form.imagen) data.append("imagen", form.imagen);
      if (form.imagen_url_externa) data.append("imagen_url_externa", form.imagen_url_externa);
      if (form.noticia) data.append("noticia", form.noticia);
      if (form.evento) data.append("evento", form.evento);
      const cfg = { headers: { "Content-Type": "multipart/form-data" } };
      if (editItem) {
        await api.patch(`/galeria/${editItem.id}/`, data, cfg);
        setOk("Imagen actualizada.");
      } else {
        await api.post("/galeria/", data, cfg);
        setOk("Imagen agregada a la galeria.");
      }
      cerrar();
      cargar();
    } catch (err) {
      const d = err.response?.data;
      setError(typeof d === "string" ? d : (d?.detail || JSON.stringify(d) || "Error al guardar."));
    } finally {
      setSaving(false);
    }
  };

  const eliminar = async (it) => {
    if (!await confirm({
      title: "Eliminar imagen",
      message: `¿Eliminar la imagen "${it.titulo}"? Esta accion no se puede deshacer.`,
    })) return;
    setError("");
    setOk("");
    try {
      await api.delete(`/galeria/${it.id}/`);
      setOk("Imagen eliminada.");
      cargar();
    } catch (e) {
      setError("No se pudo eliminar.");
    }
  };

  const onFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setForm({ ...form, imagen: f });
      setPreview(URL.createObjectURL(f));
    }
  };

  const getCategoriaColor = (cat) => CATEGORIA_COLORS[cat] || "bg-slate-100 text-slate-700";

  return (
    <div className="space-y-4">
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaImages className="text-emerald-700" />
            Galeria de imagenes
            <span className="text-xs text-gray-500 font-normal ml-2">({totalItems})</span>
          </h3>
          <button
            className="admin-btn admin-btn-primary"
            onClick={abrirNuevo}
            title="Agregar nueva imagen"
          >
            <FaPlus /> Agregar nueva imagen
          </button>
        </div>
        <div className="admin-card__body space-y-4">
          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            chips={CATEGORIAS.map((c) => ({
              key: "categoria", value: c.value, label: c.label,
            }))}
            searchKey="search"
            searchPlaceholder="Buscar por titulo..."
          />

          {loading ? (
            <div className="admin-loading">
              <FaSearch className="fa-spin mr-2" /> Cargando imagenes...
            </div>
          ) : items.length === 0 ? (
            <div className="admin-empty">
              <FaImages className="text-5xl text-gray-300" />
              <p className="mt-2">
                {filters.categoria || debouncedSearch
                  ? "No hay imagenes con los filtros aplicados."
                  : "Aun no hay imagenes. Agrega la primera con el boton superior."}
              </p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {items.map((it) => (
                  <div
                    key={it.id}
                    className="group bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div className="aspect-square bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center relative overflow-hidden">
                      {it.imagen_url ? (
                        <img
                          src={it.imagen_url}
                          alt={it.titulo}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      ) : (
                        <FaImages className="text-4xl text-gray-300" />
                      )}
                      {!it.activo && (
                        <span className="absolute top-2 right-2 admin-badge admin-badge--gray text-[10px]">
                          <FaToggleOff /> Oculto
                        </span>
                      )}
                      {it.activo && (
                        <span className="absolute top-2 right-2 admin-badge admin-badge--success text-[10px]">
                          <FaToggleOn /> Visible
                        </span>
                      )}
                    </div>
                    <div className="p-3 space-y-1">
                      <div className="text-sm font-semibold text-gray-900 truncate" title={it.titulo}>
                        {it.titulo}
                      </div>
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${getCategoriaColor(it.categoria)}`}>
                          {it.categoria_display || it.categoria}
                        </span>
                        {it.fecha && (
                          <span className="text-[10px] text-gray-500 flex items-center gap-0.5">
                            <FaCalendarAlt /> {new Date(it.fecha).toLocaleDateString("es-PE", { year: "numeric", month: "short" })}
                          </span>
                        )}
                      </div>
                      {(it.noticia || it.evento) && (
                      <div className="text-[10px] text-gray-500">
                        {it.noticia && <span>Noticia #{it.noticia}</span>}
                        {it.noticia && it.evento && ' · '}
                        {it.evento && <span>Evento #{it.evento}</span>}
                      </div>
                    )}
                    <div className="flex items-center justify-end gap-1 pt-1.5 border-t border-gray-100">
                        <button
                          className="admin-btn-icon admin-btn-icon--neutral"
                          onClick={() => abrirEditar(it)}
                          title="Editar"
                          aria-label="Editar"
                        >
                          <FaEdit />
                        </button>
                        <button
                          className="admin-btn-icon admin-btn-icon--danger"
                          onClick={() => eliminar(it)}
                          title="Eliminar"
                          aria-label="Eliminar"
                        >
                          <FaTrash />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
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
        title={
          <span className="flex items-center gap-2">
            <FaImages className="text-emerald-700" />
            {editItem ? "Editar imagen" : "Agregar nueva imagen"}
          </span>
        }
        onClose={cerrar}
        wide
        footer={
          <>
            <button className="admin-btn" onClick={cerrar} disabled={saving}>
              <FaTimes /> Cancelar
            </button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              <FaSave /> {saving ? "Guardando..." : "Guardar"}
            </button>
          </>
        }
      >
        <form onSubmit={guardar} className="space-y-3">
          <div className="admin-form-group">
            <label className="admin-form-group__label admin-form-group__label--required">
              Titulo
            </label>
            <input
              className="admin-input"
              value={form.titulo}
              onChange={(e) => setForm({ ...form, titulo: e.target.value })}
              maxLength={200}
              required
            />
          </div>

          <div className="admin-form-group">
            <label className="admin-form-group__label">Descripcion</label>
            <textarea
              className="admin-textarea"
              value={form.descripcion}
              onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
              rows={2}
            />
          </div>

          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label">
                <FaTag className="inline mr-1" /> Categoria
              </label>
              <select
                className="admin-select"
                value={form.categoria}
                onChange={(e) => setForm({ ...form, categoria: e.target.value })}
              >
                {CATEGORIAS.filter((c) => c.value).map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">
                <FaCalendarAlt className="inline mr-1" /> Fecha
              </label>
              <input
                className="admin-input"
                type="date"
                value={form.fecha || ""}
                onChange={(e) => setForm({ ...form, fecha: e.target.value })}
              />
            </div>
          </div>

          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label">
                <FaSortNumericDown className="inline mr-1" /> Orden
              </label>
              <input
                className="admin-input"
                type="number"
                value={form.orden}
                onChange={(e) => setForm({ ...form, orden: parseInt(e.target.value, 10) || 0 })}
              />
              <div className="admin-form-hint">Menor numero aparece primero.</div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Visibilidad</label>
              <label className="flex items-center gap-2 h-9 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.activo}
                  onChange={(e) => setForm({ ...form, activo: e.target.checked })}
                  className="w-4 h-4 accent-emerald-600"
                />
                <span className="text-sm text-gray-700">Visible en la galeria publica</span>
              </label>
            </div>
          </div>

          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label">Noticia asociada (opcional)</label>
              <select
                className="admin-select"
                value={form.noticia || ""}
                onChange={(e) => setForm({ ...form, noticia: e.target.value })}
              >
                <option value="">(Sin noticia)</option>
                {noticias.map(n => (
                  <option key={n.id} value={n.id}>#{n.id} - {n.titulo}</option>
                ))}
              </select>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Evento asociado (opcional)</label>
              <select
                className="admin-select"
                value={form.evento || ""}
                onChange={(e) => setForm({ ...form, evento: e.target.value })}
              >
                <option value="">(Sin evento)</option>
                {eventos.map(ev => (
                  <option key={ev.id} value={ev.id}>#{ev.id} - {ev.titulo}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="admin-form-group">
            <label className="admin-form-group__label">Imagen</label>
            <input
              type="file"
              accept="image/*"
              onChange={onFileChange}
              className="block w-full text-sm text-gray-700 file:mr-3 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer"
            />
            {preview && (
              <div className="mt-2 flex items-center gap-3">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-24 h-24 object-cover rounded-lg border border-gray-200"
                />
                <span className="text-xs text-gray-500">Vista previa</span>
              </div>
            )}
            {editItem && !preview && (
              <div className="admin-form-hint">Sube una imagen solo si quieres reemplazarla.</div>
            )}
          </div>
        </form>
      </AdminModal>
      {ConfirmDialog}
    </div>
  );
}
