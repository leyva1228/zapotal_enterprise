import React, { useEffect, useState } from "react";
import { FaSearch, FaHistory, FaRedo } from "react-icons/fa";
import api, { extractList } from "../../api";

const ACCIONES = [
  "", "CREATE", "UPDATE", "DELETE",
  "LOGIN", "LOGIN_FAILED", "LOGOUT",
  "APPROVE", "REJECT", "BLOCK", "UNBLOCK",
  "PASSWORD_RESET", "TWO_FA_ENABLE", "TWO_FA_DISABLE",
  "OTP_SENT", "OTP_VERIFIED", "OTP_FAILED", "OTP_EXPIRED",
];

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  } catch { return "-"; }
}

function colorAccion(accion) {
  if (!accion) return "admin-badge--gray";
  if (accion.startsWith("LOGIN")) return "admin-badge--info";
  if (accion.startsWith("OTP")) return "admin-badge--warning";
  if (accion === "APPROVE" || accion === "UNBLOCK") return "admin-badge--success";
  if (accion === "REJECT" || accion === "BLOCK" || accion === "DELETE") return "admin-badge--danger";
  if (accion === "CREATE") return "admin-badge--info";
  if (accion === "UPDATE") return "admin-badge--warning";
  return "admin-badge--gray";
}

export default function AdminAuditoria() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [filtros, setFiltros] = useState({
    accion: "",
    usuario: "",
    modelo_afectado: "",
    desde: "",
    hasta: "",
  });

  const PAGE_SIZE = 30;

  const cargar = async () => {
    setLoading(true);
    setError("");
    try {
      const params = { page, page_size: PAGE_SIZE };
      if (filtros.accion) params.accion = filtros.accion;
      if (filtros.usuario) params.usuario = filtros.usuario;
      if (filtros.modelo_afectado) params.modelo_afectado = filtros.modelo_afectado;
      if (filtros.desde) params.timestamp__gte = filtros.desde;
      if (filtros.hasta) params.timestamp__lte = filtros.hasta;

      const { data } = await api.get("/audit-log/", { params });
      const list = extractList(data);
      setItems(list);
      if (data && typeof data === "object" && !Array.isArray(data)) {
        setCount(data.count ?? list.length);
      } else {
        setCount(list.length);
      }
    } catch (e) {
      setError("No se pudo cargar el registro de auditoria.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [page]);

  const aplicarFiltros = (e) => {
    e?.preventDefault?.();
    setPage(1);
    cargar();
  };

  const limpiarFiltros = () => {
    setFiltros({ accion: "", usuario: "", modelo_afectado: "", desde: "", hasta: "" });
    setPage(1);
    setTimeout(cargar, 0);
  };

  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE));

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaHistory className="mr-[6px]" />
            Registro de auditoria ({count})
          </h3>
          <button className="admin-btn admin-btn-sm" onClick={cargar} disabled={loading}>
            <FaRedo /> Recargar
          </button>
        </div>
        <div className="admin-card__body p-4">
          <form
            onSubmit={aplicarFiltros}
            className="grid"
          >
            <div>
              <label className="admin-form-group__label">Accion</label>
              <select
                className="admin-select"
                value={filtros.accion}
                onChange={(e) => setFiltros({ ...filtros, accion: e.target.value })}
              >
                {ACCIONES.map((a) => (
                  <option key={a} value={a}>{a || "Todas"}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="admin-form-group__label">Usuario (ID)</label>
              <input
                className="admin-input"
                type="number"
                value={filtros.usuario}
                onChange={(e) => setFiltros({ ...filtros, usuario: e.target.value })}
                placeholder="ID usuario"
              />
            </div>
            <div>
              <label className="admin-form-group__label">Modelo</label>
              <input
                className="admin-input"
                value={filtros.modelo_afectado}
                onChange={(e) => setFiltros({ ...filtros, modelo_afectado: e.target.value })}
                placeholder="Usuario, Noticia, ..."
              />
            </div>
            <div>
              <label className="admin-form-group__label">Desde</label>
              <input
                className="admin-input"
                type="datetime-local"
                value={filtros.desde}
                onChange={(e) => setFiltros({ ...filtros, desde: e.target.value })}
              />
            </div>
            <div>
              <label className="admin-form-group__label">Hasta</label>
              <input
                className="admin-input"
                type="datetime-local"
                value={filtros.hasta}
                onChange={(e) => setFiltros({ ...filtros, hasta: e.target.value })}
              />
            </div>
            <div className="flex">
              <button className="admin-btn admin-btn-primary" type="submit">
                <FaSearch /> Buscar
              </button>
              <button className="admin-btn admin-btn-ghost" type="button" onClick={limpiarFiltros}>
                Limpiar
              </button>
            </div>
          </form>

          {loading ? (
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">Sin resultados.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Accion</th>
                  <th>Usuario</th>
                  <th>Modelo</th>
                  <th>Objeto</th>
                  <th>IP</th>
                  <th>Descripcion</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr key={it.id}>
                    <td className="text-mute text-[12px]">{formatFecha(it.timestamp)}</td>
                    <td>
                      <span className={"admin-badge " + colorAccion(it.accion)}>
                        {it.accion}
                      </span>
                    </td>
                    <td>{it.usuario_email || (it.usuario ? `#${it.usuario}` : "-")}</td>
                    <td>{it.modelo_afectado || "-"}</td>
                    <td className="text-[12px]">{it.objeto_id || "-"}</td>
                    <td className="text-[12px]">{it.ip_address || "-"}</td>
                    <td className="overflow-hidden">
                      {it.descripcion || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {totalPages > 1 && (
            <div className="flex justify-center">
              <button
                className="admin-btn admin-btn-sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Anterior
              </button>
              <span className="text-[13px]">
                Pagina {page} de {totalPages}
              </span>
              <button
                className="admin-btn admin-btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Siguiente
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
