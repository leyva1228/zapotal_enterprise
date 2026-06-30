import React, { useCallback, useEffect, useState } from "react";
import {
  FaHandHoldingHeart, FaSearch, FaEye, FaUndo, FaTimesCircle,
  FaCheckCircle, FaHourglassHalf, FaMoneyBillWave, FaUsers,
  FaCalendarAlt, FaIdCard, FaEnvelope, FaCreditCard, FaReceipt,
  FaDownload, FaFilter,
} from "react-icons/fa";
import api, { extractList } from "../../api";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import LiveChart from "../../components/Admin/LiveChart";
import { useUrlFilters, parseIntParam } from "../../hooks/useUrlFilters";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import { useTimeSeries } from "../../hooks/useTimeSeries";
import "./AdminDonaciones.css";

const ESTADOS = [
  { value: "",                  label: "Todos los estados" },
  { value: "APROBADO",          label: "Aprobadas" },
  { value: "EN_PROCESO",        label: "En proceso" },
  { value: "PENDIENTE",         label: "Pendientes" },
  { value: "RECHAZADO",         label: "Rechazadas" },
  { value: "CANCELADO",         label: "Canceladas" },
  { value: "REEMBOLSADO",       label: "Reembolsadas" },
];

const DESTINATARIOS_LABELS = {
  GENERAL:          "Comunidad general",
  INFRAESTRUCTURA:  "Obras e infraestructura",
  EVENTOS:          "Eventos y actividades",
  BECAS:            "Becas y capacitacion",
  EMERGENCIA:       "Fondo de emergencia",
};

const ESTADO_META = {
  APROBADO:    { label: "Aprobada",       color: "emerald", icon: <FaCheckCircle /> },
  EN_PROCESO:  { label: "En proceso",      color: "amber",   icon: <FaHourglassHalf /> },
  PENDIENTE:   { label: "Pendiente",      color: "amber",   icon: <FaHourglassHalf /> },
  RECHAZADO:   { label: "Rechazada",      color: "rose",    icon: <FaTimesCircle /> },
  CANCELADO:   { label: "Cancelada",      color: "gray",    icon: <FaTimesCircle /> },
  REEMBOLSADO: { label: "Reembolsada",    color: "sky",     icon: <FaUndo /> },
};

const METODO_LABELS = {
  visa: "Visa",
  master: "Mastercard",
  mastercard: "Mastercard",
  amex: "Amex",
  mercadopago: "Mercado Pago",
  account_money: "Saldo MP",
  debit_card: "Debito",
  credit_card: "Credito",
};

function formatPEN(n) {
  if (n === null || n === undefined || n === "") return "-";
  const num = Number(n);
  if (Number.isNaN(num)) return "-";
  return `S/ ${num.toFixed(2)}`;
}

function formatFecha(str) {
  if (!str) return "-";
  try {
    return new Date(str).toLocaleString("es-PE", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch { return "-"; }
}

export default function AdminDonaciones() {
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  const [filters, setFilters, clearFilters] = useUrlFilters({
    estado: { defaultValue: "" },
    destinatario: { defaultValue: "" },
    search: { defaultValue: "" },
    page: { defaultValue: 1, parser: parseIntParam },
  });
  const debouncedSearch = useDebouncedValue(filters.search, 350);
  const PAGE_SIZE = 20;

  const [detalle, setDetalle] = useState(null);
  const [confirmAccion, setConfirmAccion] = useState(null);
  const [donacionesChart, setDonacionesChart] = useState([]);
  const [chartLoading, setChartLoading] = useState(true);

  const cargarChart = useCallback(async () => {
    setChartLoading(true);
    try {
      const hace24h = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
      const { data } = await api.get("/donaciones/admin/lista/", {
        params: { fecha_donacion__gte: hace24h, estado: "APROBADO", page_size: 500 }
      });
      const lista = extractList(data);
      // Mapear a {timestamp, value} donde value = monto
      setDonacionesChart(
        lista.map((d) => ({
          timestamp: d.fecha_donacion || d.fecha_creacion || d.created_at,
          value: Number(d.monto) || 0,
        }))
      );
    } catch {
      setDonacionesChart([]);
    } finally {
      setChartLoading(false);
    }
  }, []);

  const seriesChart = useTimeSeries(donacionesChart, {
    dateKey: "timestamp",
    valueKey: "value",
    bucketMs: 60 * 60 * 1000, // 1h
    windowSecs: 86400, // 24h
  });

  const cargarStats = useCallback(async () => {
    try {
      const { data } = await api.get("/donaciones/estadisticas/");
      setStats(data);
    } catch {
      setStats(null);
    }
  }, []);

  const cargar = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = { page: filters.page };
      if (filters.estado) params.estado = filters.estado;
      if (filters.destinatario) params.destinatario = filters.destinatario;
      if (debouncedSearch.trim()) params.search = debouncedSearch.trim();
      const { data } = await api.get("/donaciones/admin/lista/", { params });
      setItems(extractList(data));
      setCount(typeof data === "object" && data?.count !== undefined ? data.count : (Array.isArray(data) ? data.length : 0));
    } catch (e) {
      setError("No se pudieron cargar las donaciones.");
      setItems([]);
      setCount(0);
    } finally {
      setLoading(false);
    }
  }, [filters.page, filters.estado, filters.destinatario, debouncedSearch]);

  useEffect(() => { cargarStats(); }, [cargarStats]);
  useEffect(() => { cargar(); }, [cargar]);
  useEffect(() => { cargarChart(); }, [cargarChart]);

  const ejecutarAccion = async () => {
    if (!confirmAccion) return;
    setActionLoading(true);
    setError(""); setOk("");
    try {
      const { donacion, accion } = confirmAccion;
      const endpoint = accion === "reembolsar"
        ? `/donaciones/admin/${donacion.id}/reembolsar/`
        : `/donaciones/admin/${donacion.id}/cancelar/`;
      const { data } = await api.post(endpoint, {});
      setOk(data.detail || `Donacion #${donacion.id} ${accion === "reembolsar" ? "reembolsada" : "cancelada"}.`);
      setConfirmAccion(null);
      await Promise.all([cargar(), cargarStats()]);
    } catch (e) {
      setError(e.response?.data?.detail || `No se pudo ${confirmAccion.accion} la donacion.`);
    } finally {
      setActionLoading(false);
    }
  };

  const totalPaginas = Math.max(1, Math.ceil(count / PAGE_SIZE));

  return (
    <div className="adn-wrap">
      <header className="adn-header">
        <h1 className="adn-title">
          <FaHandHoldingHeart /> Donaciones
        </h1>
        <p className="adn-sub">
          Gestion de donaciones recibidas via Mercado Pago (sandbox/produccion).
        </p>
      </header>

      {error && <div className="adn-alert adn-alert--err" role="alert">{error}</div>}
      {ok && <div className="adn-alert adn-alert--ok" role="status">{ok}</div>}

      {stats && (
        <section className="adn-stats">
          <div className="adn-stat adn-stat--emerald">
            <span className="adn-stat__icon"><FaMoneyBillWave /></span>
            <div>
              <p className="adn-stat__num">{formatPEN(stats.total_recaudado)}</p>
              <p className="adn-stat__lbl">Total recaudado</p>
            </div>
          </div>
          <div className="adn-stat adn-stat--emerald">
            <span className="adn-stat__icon"><FaCheckCircle /></span>
            <div>
              <p className="adn-stat__num">{stats.cantidad_donaciones ?? 0}</p>
              <p className="adn-stat__lbl">Aprobadas</p>
            </div>
          </div>
          <div className="adn-stat adn-stat--amber">
            <span className="adn-stat__icon"><FaUsers /></span>
            <div>
              <p className="adn-stat__num">{stats.donantes_unicos ?? 0}</p>
              <p className="adn-stat__lbl">Donantes unicos</p>
            </div>
          </div>
          <div className="adn-stat adn-stat--sky">
            <span className="adn-stat__icon"><FaHandHoldingHeart /></span>
            <div>
              <p className="adn-stat__num">{formatPEN(stats.promedio_donacion)}</p>
              <p className="adn-stat__lbl">Promedio</p>
            </div>
          </div>
        </section>
      )}

        <section className="adn-filters">
          <FaFilter className="adn-filters__icon" />
          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            chips={[
              { key: "estado", value: "", label: "Todos" },
              { key: "estado", value: "APROBADO", label: "Aprobadas" },
              { key: "estado", value: "PENDIENTE", label: "Pendientes" },
              { key: "estado", value: "RECHAZADO", label: "Rechazadas" },
              { key: "estado", value: "CANCELADO", label: "Canceladas" },
              { key: "estado", value: "REEMBOLSADO", label: "Reembolsadas" },
            ]}
            searchKey="search"
            searchPlaceholder="Buscar por email, nombre o MP payment id..."
            extra={
              <select
                className="adn-select"
                value={filters.destinatario || ""}
                onChange={(e) => setFilters({ destinatario: e.target.value, page: 1 })}
                aria-label="Filtrar por destinatario"
              >
                <option value="">Todos los destinos</option>
                {Object.entries(DESTINATARIOS_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            }
          />
          <div className="adn-search">
            <FaSearch />
            <input
              type="search"
              placeholder="Buscar por email, nombre o MP payment id..."
              value={filters.search || ""}
              onChange={(e) => setFilters({ search: e.target.value, page: 1 })}
            />
          </div>
        </section>

        <section style={{ marginBottom: 24 }}>
          <LiveChart
            data={seriesChart}
            windowSecs={86400}
            windows={[
              { label: "1h", secs: 3600 },
              { label: "6h", secs: 21600 },
              { label: "24h", secs: 86400 },
            ]}
            title="Monto recaudado (ultimas 24h)"
            color="#16a34a"
            valueFormatter={(v) => `S/ ${v.toFixed(2)}`}
            badge={seriesChart.length > 0 ? seriesChart[seriesChart.length - 1].value : 0}
            height={180}
          />
        </section>

      <section className="adn-table-card">
        <div className="adn-table-meta">
          <span>{count} donacion{count === 1 ? "" : "es"} en total</span>
          {totalPaginas > 1 && (
            <span>Pagina {filters.page} de {totalPaginas}</span>
          )}
        </div>
        {loading ? (
          <p className="adn-empty">Cargando donaciones...</p>
        ) : items.length === 0 ? (
          <p className="adn-empty">No hay donaciones que coincidan con los filtros.</p>
        ) : (
          <div className="adn-table-scroll">
            <table className="adn-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Donante</th>
                  <th>Monto</th>
                  <th>Destino</th>
                  <th>Estado</th>
                  <th>MP ref</th>
                  <th>Fecha</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((d) => {
                  const meta = ESTADO_META[d.estado] || ESTADO_META.PENDIENTE;
                  const metodo = d.mp_payment_method ? (METODO_LABELS[d.mp_payment_method] || d.mp_payment_method) : "-";
                  return (
                    <tr key={d.id}>
                      <td className="adn-cell-id">#{d.id}</td>
                      <td>
                        <div className="adn-donor">
                          <strong>{d.nombre_display || "Anonimo"}</strong>
                          {d.email_display && (
                            <span className="adn-donor__email">{d.email_display}</span>
                          )}
                        </div>
                      </td>
                      <td className="adn-cell-monto">{formatPEN(d.monto)}</td>
                      <td>{DESTINATARIOS_LABELS[d.destinatario] || d.destinatario || "-"}</td>
                      <td>
                        <span className={`adn-badge adn-badge--${meta.color}`}>
                          {meta.icon} {meta.label}
                        </span>
                        <div className="adn-cell-metodo">{metodo}</div>
                      </td>
                      <td className="adn-cell-ref">
                        {d.mp_payment_id ? `#${String(d.mp_payment_id)}` : "-"}
                      </td>
                      <td className="adn-cell-fecha">{formatFecha(d.created_at)}</td>
                      <td className="adn-cell-actions">
                        <button
                          type="button"
                          className="adn-btn adn-btn-ghost"
                          onClick={() => setDetalle(d)}
                          title="Ver detalle"
                        >
                          <FaEye />
                        </button>
                        {d.estado === "APROBADO" && (
                          <button
                            type="button"
                            className="adn-btn adn-btn-warn"
                            onClick={() => setConfirmAccion({ donacion: d, accion: "reembolsar" })}
                            title="Reembolsar"
                          >
                            <FaUndo />
                          </button>
                        )}
                        {d.estado === "PENDIENTE" && (
                          <button
                            type="button"
                            className="adn-btn adn-btn-danger"
                            onClick={() => setConfirmAccion({ donacion: d, accion: "cancelar" })}
                            title="Cancelar"
                          >
                            <FaTimesCircle />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

          {totalPaginas > 1 && (
            <div className="adn-pager">
              <Pagination
                page={filters.page}
                totalPages={totalPaginas}
                totalItems={count}
                pageSize={PAGE_SIZE}
                onPageChange={(p) => setFilters({ page: p })}
              />
            </div>
          )}
        </section>

      {detalle && (
        <DonacionDetalleModal donacion={detalle} onClose={() => setDetalle(null)} />
      )}

      {confirmAccion && (
        <ConfirmModal
          donacion={confirmAccion.donacion}
          accion={confirmAccion.accion}
          loading={actionLoading}
          onConfirm={ejecutarAccion}
          onClose={() => setConfirmAccion(null)}
        />
      )}
    </div>
  );
}

function DonacionDetalleModal({ donacion, onClose }) {
  const meta = ESTADO_META[donacion.estado] || ESTADO_META.PENDIENTE;
  const metodo = donacion.mp_payment_method
    ? (METODO_LABELS[donacion.mp_payment_method] || donacion.mp_payment_method)
    : "-";
  const rawResponse = (() => {
    try { return donacion.mp_raw_response ? JSON.stringify(JSON.parse(donacion.mp_raw_response), null, 2) : null; }
    catch { return donacion.mp_raw_response; }
  })();

  const descargarJson = () => {
    const blob = new Blob([rawResponse || JSON.stringify(donacion, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `donacion-${donacion.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="adn-modal-backdrop" onClick={onClose}>
      <div className="adn-modal adn-modal--lg" onClick={(e) => e.stopPropagation()}>
        <header className="adn-modal__head">
          <h2>
            <FaReceipt /> Donacion #{donacion.id}
          </h2>
          <button type="button" className="adn-modal__close" onClick={onClose} aria-label="Cerrar">
            <FaTimesCircle />
          </button>
        </header>
        <div className="adn-modal__body">
          <div className="adn-modal__grid">
            <section>
              <h3 className="adn-section-title"><FaIdCard /> Donante</h3>
              <dl className="adn-dl">
                <dt>Usuario</dt>
                <dd>{donacion.usuario ? `ID ${donacion.usuario}` : "Visitante"}</dd>
                <dt>Nombre</dt>
                <dd>{donacion.nombre_display || "Anonimo"}</dd>
                <dt>Email</dt>
                <dd>{donacion.email_display || "-"}</dd>
                <dt>Documento</dt>
                <dd>{donacion.documento_donante || "-"}</dd>
                <dt>Anonima</dt>
                <dd>{donacion.anonima ? "Si" : "No"}</dd>
              </dl>
            </section>
            <section>
              <h3 className="adn-section-title"><FaHandHoldingHeart /> Donacion</h3>
              <dl className="adn-dl">
                <dt>Monto</dt>
                <dd className="adn-strong">{formatPEN(donacion.monto)} {donacion.moneda}</dd>
                <dt>Destino</dt>
                <dd>{DESTINATARIOS_LABELS[donacion.destinatario] || donacion.destinatario || "-"}</dd>
                <dt>Mensaje</dt>
                <dd>{donacion.mensaje ? `"${donacion.mensaje}"` : <em className="adn-muted">sin mensaje</em>}</dd>
                <dt>Estado</dt>
                <dd><span className={`adn-badge adn-badge--${meta.color}`}>{meta.icon} {meta.label}</span></dd>
                <dt>Aprobado en</dt>
                <dd>{formatFecha(donacion.aprobado_at)}</dd>
                <dt>Reembolsado en</dt>
                <dd>{formatFecha(donacion.reembolsado_at)}</dd>
              </dl>
            </section>
            <section>
              <h3 className="adn-section-title"><FaCreditCard /> Mercado Pago</h3>
              <dl className="adn-dl">
                <dt>MP payment id</dt>
                <dd>{donacion.mp_payment_id || "-"}</dd>
                <dt>Status</dt>
                <dd>{donacion.mp_status || "-"}</dd>
                <dt>Status detail</dt>
                <dd>{donacion.mp_status_detail || "-"}</dd>
                <dt>Metodo</dt>
                <dd>{metodo}</dd>
                <dt>Tipo</dt>
                <dd>{donacion.mp_payment_type || "-"}</dd>
                <dt>Cuotas</dt>
                <dd>{donacion.mp_installments ?? "-"}</dd>
              </dl>
            </section>
            <section>
              <h3 className="adn-section-title"><FaCalendarAlt /> Auditoria</h3>
              <dl className="adn-dl">
                <dt>Creado</dt>
                <dd>{formatFecha(donacion.created_at)}</dd>
                <dt>Actualizado</dt>
                <dd>{formatFecha(donacion.updated_at)}</dd>
                <dt>IP origen</dt>
                <dd>{donacion.ip_origen || "-"}</dd>
                <dt>User agent</dt>
                <dd className="adn-ua">{donacion.user_agent || "-"}</dd>
              </dl>
            </section>
          </div>

          {rawResponse && (
            <details className="adn-raw">
              <summary>Respuesta cruda de Mercado Pago</summary>
              <div className="adn-raw__bar">
                <button type="button" className="adn-btn adn-btn-ghost" onClick={descargarJson}>
                  <FaDownload /> Descargar JSON
                </button>
              </div>
              <pre>{rawResponse}</pre>
            </details>
          )}
        </div>
        <footer className="adn-modal__foot">
          <button type="button" className="adn-btn adn-btn-ghost" onClick={onClose}>Cerrar</button>
        </footer>
      </div>
    </div>
  );
}

function ConfirmModal({ donacion, accion, loading, onConfirm, onClose }) {
  const isReembolso = accion === "reembolsar";
  return (
    <div className="adn-modal-backdrop" onClick={onClose}>
      <div className="adn-modal adn-modal--sm" onClick={(e) => e.stopPropagation()}>
        <header className="adn-modal__head">
          <h2>
            {isReembolso ? <><FaUndo /> Confirmar reembolso</> : <><FaTimesCircle /> Confirmar cancelacion</>}
          </h2>
          <button type="button" className="adn-modal__close" onClick={onClose} aria-label="Cerrar">
            <FaTimesCircle />
          </button>
        </header>
        <div className="adn-modal__body">
          <p>
            {isReembolso ? (
              <>
                Vas a <strong>reembolsar</strong> la donacion <strong>#{donacion.id}</strong> de{" "}
                <strong>{formatPEN(donacion.monto)}</strong> a <strong>{donacion.nombre_display}</strong>.
                Esta accion devuelve el dinero al donante en Mercado Pago y no se puede deshacer.
              </>
            ) : (
              <>
                Vas a <strong>cancelar</strong> la donacion <strong>#{donacion.id}</strong> de{" "}
                <strong>{formatPEN(donacion.monto)}</strong> a <strong>{donacion.nombre_display}</strong>.
                Solo es posible si la donacion aun no fue procesada por Mercado Pago.
              </>
            )}
          </p>
        </div>
        <footer className="adn-modal__foot adn-modal__foot--end">
          <button type="button" className="adn-btn adn-btn-ghost" onClick={onClose} disabled={loading}>
            Cancelar
          </button>
          <button
            type="button"
            className={`adn-btn ${isReembolso ? "adn-btn-warn" : "adn-btn-danger"}`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Procesando..." : (isReembolso ? "Si, reembolsar" : "Si, cancelar")}
          </button>
        </footer>
      </div>
    </div>
  );
}
