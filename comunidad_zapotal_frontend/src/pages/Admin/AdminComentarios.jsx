import React, { useEffect, useState, useCallback, useRef } from "react";
import { FaTrash, FaEye, FaEyeSlash, FaSearch } from "react-icons/fa";
import api, { extractList } from "../../api";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import { useUrlFilters, parseIntParam } from "../../hooks/useUrlFilters";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";

const ESTADOS = ["", "PUBLICADO", "OCULTO", "ELIMINADO", "PENDIENTE"];

export default function AdminComentarios() {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const abortRef = useRef(null);

  const [filters, setFilters, clearFilters] = useUrlFilters({
    estado: { defaultValue: "" },
    search: { defaultValue: "" },
    page: { defaultValue: 1, parser: parseIntParam },
  });
  const debouncedSearch = useDebouncedValue(filters.search, 350);

  const cargar = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = { page: filters.page };
      if (filters.estado) params.estado = filters.estado;
      if (debouncedSearch) params.search = debouncedSearch;
      const r = await api.get("/comentarios/", { params, signal: controller.signal });
      const data = r.data;
      setItems(extractList(data));
      setTotalItems(data.count || 0);
    } catch (e) {
      if (e.name !== "CanceledError" && e.name !== "AbortError") {
        setError("No se pudieron cargar los comentarios.");
      }
    } finally {
      setLoading(false);
    }
  }, [filters.page, filters.estado, debouncedSearch]);

  useEffect(() => { cargar(); }, [cargar]);
  useEffect(() => {
    if (filters.page !== 1) setFilters({ page: 1 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.estado, debouncedSearch]);

  const cambiarEstado = async (c, estado) => {
    setError(""); setOk("");
    try {
      await api.post(`/comentarios/${c.id}/cambiar_estado/`, { estado });
      setOk(`Comentario #${c.id} ahora está ${estado}.`);
      cargar();
    } catch (e) { setError("No se pudo cambiar el estado."); }
  };

  const eliminar = async (c) => {
    if (!window.confirm(`¿Eliminar definitivamente el comentario #${c.id}?`)) return;
    setError(""); setOk("");
    try { await api.delete(`/comentarios/${c.id}/`); setOk("Comentario eliminado."); cargar(); }
    catch (e) { setError("No se pudo eliminar."); }
  };

  const chips = [
    { key: "estado", value: "", label: "Todos" },
    { key: "estado", value: "PENDIENTE", label: "Moderacion" },
    { key: "estado", value: "PUBLICADO", label: "Publicados" },
    { key: "estado", value: "OCULTO", label: "Censurados" },
    { key: "estado", value: "ELIMINADO", label: "Eliminados" },
  ];

  const totalPages = Math.max(1, Math.ceil(totalItems / 20));

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">Comentarios ({totalItems})</h3>
        </div>
        <div className="admin-card__body">
          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            chips={chips}
            searchKey="search"
            searchPlaceholder="Buscar texto o autor..."
          />

          {loading ? (
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">
              {Object.values(filters).some((v) => v && v !== 1)
                ? "No hay comentarios con los filtros aplicados."
                : "No hay comentarios."}
            </div>
          ) : (
            <>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Contenido</th>
                    <th>Autor</th>
                    <th>Noticia/Evento</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                    <th className="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map(c => (
                    <tr key={c.id}>
                      <td>{c.id}</td>
                      <td className="max-w-md">
                        <div className="text-[13px]">{(c.contenido || "").substring(0, 140)}{(c.contenido || "").length > 140 ? "..." : ""}</div>
                      </td>
                      <td>
                        <div className="font-[600]">{c.autor_nombre || c.autor_email || `Usuario #${c.autor || "?"}`}</div>
                        <div className="text-mute">{c.autor_email}</div>
                      </td>
                      <td className="text-[12px]">
                        {c.noticia  ? <span title="Noticia #{c.noticia}">Noticia #{c.noticia}</span> : null}
                        {c.evento   ? <span title="Evento #{c.evento}">Evento #{c.evento}</span>  : null}
                        {c.respuesta_a ? <div className="text-mute">↳ Respuesta a #{c.respuesta_a}</div> : null}
                      </td>
                      <td>
                        <span className={"admin-badge " + (
                          c.estado === "PUBLICADO" ? "admin-badge--success" :
                          c.estado === "OCULTO"    ? "admin-badge--warning" :
                          c.estado === "ELIMINADO" ? "admin-badge--danger" :
                                                      "admin-badge--info"
                        )}>
                          {c.estado}
                        </span>
                      </td>
                      <td className="text-mute">
                        {c.fecha ? new Date(c.fecha).toLocaleString("es-PE") : ""}
                      </td>
                      <td className="actions justify-end">
                        {c.estado !== "PUBLICADO" && (
                          <button className="admin-btn admin-btn-sm admin-btn-success" onClick={() => cambiarEstado(c, "PUBLICADO")}>
                            <FaEye /> Publicar
                          </button>
                        )}
                        {c.estado !== "OCULTO" && (
                          <button className="admin-btn admin-btn-sm" onClick={() => cambiarEstado(c, "OCULTO")}>
                            <FaEyeSlash /> Ocultar
                          </button>
                        )}
                        <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(c)}>
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <Pagination
                page={filters.page}
                totalPages={totalPages}
                totalItems={totalItems}
                onPageChange={(p) => setFilters({ page: p })}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
