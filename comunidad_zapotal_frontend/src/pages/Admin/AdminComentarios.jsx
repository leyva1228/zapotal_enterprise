import React, { useEffect, useState } from "react";
import { FaTrash, FaEye, FaEyeSlash, FaSearch } from "react-icons/fa";
import api, { extractList } from "../../api";

const ESTADOS = ["", "PUBLICADO", "OCULTO", "ELIMINADO", "PENDIENTE"];

export default function AdminComentarios() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");

  const cargar = async () => {
    setLoading(true);
    try {
      const r = await api.get(`/comentarios/?page_size=200${filtroEstado ? `&estado=${filtroEstado}` : ""}`);
      setItems(extractList(r.data));
    } catch (e) { setError("No se pudieron cargar los comentarios."); }
    finally { setLoading(false); }
  };
  useEffect(() => { cargar(); }, [filtroEstado]);

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

  const itemsFiltrados = items.filter(c => {
    const txt = ((c.autor_email || "") + " " + (c.contenido || "")).toLowerCase();
    return (!busqueda || txt.includes(busqueda.toLowerCase()));
  });

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card" style={{ marginTop: 16 }}>
        <div className="admin-card__header">
          <h3 className="admin-card__title">Comentarios ({items.length})</h3>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div style={{ position: "relative" }}>
              <FaSearch style={{ position: "absolute", left: 10, top: 11, color: "#9ca3af" }} />
              <input
                className="admin-input"
                style={{ paddingLeft: 30, width: 220 }}
                placeholder="Buscar texto o autor..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
            </div>
            <select
              className="admin-select" style={{ width: 160 }}
              value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}
            >
              <option value="">Todos los estados</option>
              <option value="PUBLICADO">PUBLICADO</option>
              <option value="OCULTO">OCULTO</option>
              <option value="ELIMINADO">ELIMINADO</option>
              <option value="PENDIENTE">PENDIENTE</option>
            </select>
          </div>
        </div>

        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando…</div>
          ) : itemsFiltrados.length === 0 ? (
            <div className="admin-empty">No hay comentarios.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Contenido</th>
                  <th>Autor</th>
                  <th>Noticia/Evento</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th style={{ textAlign: "right" }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {itemsFiltrados.map(c => (
                  <tr key={c.id}>
                    <td>{c.id}</td>
                    <td style={{ maxWidth: 340 }}>
                      <div style={{ fontSize: 13 }}>{(c.contenido || "").substring(0, 140)}{(c.contenido || "").length > 140 ? "…" : ""}</div>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: 12 }}>{c.autor_nombre || c.autor_email || `Usuario #${c.autor || "?"}`}</div>
                      <div style={{ color: "#6b7280", fontSize: 11 }}>{c.autor_email}</div>
                    </td>
                    <td style={{ fontSize: 12, color: "#374151" }}>
                      {c.noticia  ? <span title="Noticia #{c.noticia}">📰 #{c.noticia}</span> : null}
                      {c.evento   ? <span title="Evento #{c.evento}">📅 #{c.evento}</span>  : null}
                      {c.respuesta_a ? <div style={{ color: "#6b7280" }}>↳ Respuesta a #{c.respuesta_a}</div> : null}
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
                    <td style={{ color: "#6b7280", fontSize: 12 }}>
                      {c.fecha ? new Date(c.fecha).toLocaleString("es-PE") : ""}
                    </td>
                    <td className="actions" style={{ justifyContent: "flex-end", flexWrap: "wrap" }}>
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
          )}
        </div>
      </div>
    </div>
  );
}
