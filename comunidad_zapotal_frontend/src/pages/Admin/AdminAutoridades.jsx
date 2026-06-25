import React, { useEffect, useRef, useState, useMemo } from "react";
import {
  FaPlus, FaEdit, FaTrash, FaCloudUploadAlt, FaChartPie,
  FaUsers, FaBuilding, FaUserTie, FaExclamationTriangle, FaCheckCircle,
  FaVenusMars,
} from "react-icons/fa";
import { useSearchParams } from "react-router-dom";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

const NIVELES = {
  COMUNAL:   { label: "Directiva Comunal",     icon: <FaUsers />,    duracion: 2, cargos: ["PRESIDENTE", "VICEPRESIDENTE", "SECRETARIO", "TESORERO", "FISCAL", "VOCAL"] },
  MUNICIPAL: { label: "Municipalidad C.P.",    icon: <FaBuilding />, duracion: 4, cargos: ["PRESIDENTE", "VICEPRESIDENTE", "REGIDOR", "VOCAL"] },
  POLITICO:  { label: "Autoridad Politica",    icon: <FaUserTie />,  duracion: 4, cargos: ["OTRO", "PRESIDENTE", "VOCAL"] },
};

const EMPTY = {
  cargo: "", cargo_tipo: "OTRO",
  nivel_gobierno: "COMUNAL", orden: 1,
  periodo: "",
  periodo_inicio: "", periodo_fin: "",
  duracion_mandato_anos: 2,
  descripcion: "",
  sexo: "M", dni: "",
  telefono: "", email_institucional: "",
  nro_partida_sunarp: "",
  sede_inscripcion: "", resolucion_inscripcion: "",
  fecha_inscripcion: "", fecha_vencimiento_inscripcion: "",
  estado_inscripcion: "",
  es_cargo_tradicional: false, nombre_tradicional: "",
  reelegido: false, autoridad_anterior: "",
  lengua_materna: "",
  es_admin: false, activo: true,
  comunero: "", usuario: "",
  foto: null,
};

export default function AdminAutoridades() {
  const [searchParams, setSearchParams] = useSearchParams();
  const nivelParam = searchParams.get("nivel") || "COMUNAL";
  const isStats = nivelParam === "__STATS__";

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
  const [fotoPreview, setFotoPreview] = useState(null);
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const inputFotoRef = useRef(null);

  const cargar = async () => {
    setLoading(true);
    setError("");
    try {
      const cfg = { params: { page_size: 200 } };
      if (!isStats && nivelParam !== "__ALL__") {
        cfg.params.nivel_gobierno = nivelParam;
      }
      const [a, c, u] = await Promise.all([
        api.get("/autoridades/", cfg),
        api.get("/comuneros/").catch(() => ({ data: { data: [] } })),
        api.get("/usuarios/?page_size=200").catch(() => ({ data: { data: [] } })),
      ]);
      setItems(extractList(a.data));
      setComuneros(extractList(c.data));
      setUsuarios(extractList(u.data));
    } catch (e) {
      setError("No se pudieron cargar las autoridades.");
    } finally {
      setLoading(false);
    }
  };

  const cargarStats = async () => {
    setStatsLoading(true);
    try {
      const r = await api.get("/autoridades/estadisticas/");
      setStats(r.data);
    } catch (e) {
      setError("No se pudieron cargar las estadisticas.");
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => { cargar(); }, [nivelParam, isStats]);
  useEffect(() => { if (isStats) cargarStats(); }, [isStats]);

  const vencenPronto = useMemo(() => {
    return items.filter(i => i.tiempo_restante != null && i.tiempo_restante > 0 && i.tiempo_restante <= 90);
  }, [items]);

  const cuotaMujeres = useMemo(() => {
    if (!items.length) return { count: 0, total: 0, pct: 0, cumple: null };
    const total = items.filter(i => i.activo).length;
    if (total < 3) return { count: items.filter(i => i.activo && i.sexo === "F").length, total, pct: 0, cumple: null };
    const mujeres = items.filter(i => i.activo && i.sexo === "F").length;
    const pct = Math.round((mujeres / total) * 100);
    return { count: mujeres, total, pct, cumple: pct >= 30 };
  }, [items]);

  const limpiarFoto = () => {
    if (fotoPreview && fotoPreview.startsWith('blob:')) URL.revokeObjectURL(fotoPreview);
    setFotoPreview(null);
    setForm((f) => ({ ...f, foto: null }));
  };

  const handleNivelChange = (nuevo) => {
    setSearchParams({ nivel: nuevo }, { replace: true });
  };

  const abrirNuevo = () => {
    setEditItem(null);
    const defaults = NIVELES[nivelParam] || NIVELES.COMUNAL;
    setForm({ ...EMPTY, nivel_gobierno: nivelParam, duracion_mandato_anos: defaults.duracion });
    setFotoPreview(null);
    setModalOpen(true);
  };

  const abrirEditar = (a) => {
    setEditItem(a);
    setForm({
      cargo: a.cargo || "", cargo_tipo: a.cargo_tipo || "OTRO",
      nivel_gobierno: a.nivel_gobierno || "COMUNAL",
      orden: a.orden || 1,
      periodo: a.periodo || "",
      periodo_inicio: a.periodo_inicio || "",
      periodo_fin: a.periodo_fin || "",
      duracion_mandato_anos: a.duracion_mandato_anos || 2,
      descripcion: a.descripcion || "",
      sexo: a.sexo || "M",
      dni: a.dni || "",
      telefono: a.telefono || "",
      email_institucional: a.email_institucional || "",
      nro_partida_sunarp: a.nro_partida_sunarp || "",
      sede_inscripcion: a.sede_inscripcion || "",
      resolucion_inscripcion: a.resolucion_inscripcion || "",
      fecha_inscripcion: a.fecha_inscripcion || "",
      fecha_vencimiento_inscripcion: a.fecha_vencimiento_inscripcion || "",
      estado_inscripcion: a.estado_inscripcion || "",
      es_cargo_tradicional: !!a.es_cargo_tradicional,
      nombre_tradicional: a.nombre_tradicional || "",
      reelegido: !!a.reelegido,
      autoridad_anterior: a.autoridad_anterior || "",
      lengua_materna: a.lengua_materna || "",
      es_admin: !!a.es_admin,
      activo: a.activo !== false,
      comunero: a.comunero || "",
      usuario: a.usuario || "",
      foto: null,
    });
    setFotoPreview(a.foto_url || null);
    setModalOpen(true);
  };

  // FASE 4E: Duplicar autoridad para nuevo periodo electoral
  const abrirDuplicar = (a) => {
    setEditItem(null);
    const cfg = NIVELES[a.nivel_gobierno] || NIVELES.COMUNAL;
    const hoy = new Date();
    const fin = new Date(hoy);
    fin.setFullYear(hoy.getFullYear() + cfg.duracion);
    setForm({
      ...EMPTY,
      // Mantener cargo, nivel, tipo, orden
      cargo: a.cargo || "",
      cargo_tipo: a.cargo_tipo || "OTRO",
      nivel_gobierno: a.nivel_gobierno || "COMUNAL",
      orden: a.orden || 1,
      descripcion: a.descripcion || "",
      // Avanzar fechas al nuevo periodo
      periodo: `${hoy.getFullYear()}-${fin.getFullYear()}`,
      periodo_inicio: hoy.toISOString().slice(0, 10),
      periodo_fin: fin.toISOString().slice(0, 10),
      duracion_mandato_anos: cfg.duracion,
      // Reusar datos de contacto y marco legal
      sede_inscripcion: a.sede_inscripcion || "",
      nro_partida_sunarp: a.nro_partida_sunarp || "",
      resolucion_inscripcion: a.resolucion_inscripcion || "",
      estado_inscripcion: a.estado_inscripcion || "",
      fecha_inscripcion: a.fecha_inscripcion || "",
      fecha_vencimiento_inscripcion: a.fecha_vencimiento_inscripcion || "",
      // Limpiar datos personales (no se heredan)
      comunero: "",
      usuario: "",
      dni: "",
      foto: null,
    });
    setFotoPreview(a.foto_url || null);
    setModalOpen(true);
  };

  const cerrar = () => {
    limpiarFoto();
    setModalOpen(false);
    setEditItem(null);
    setForm(EMPTY);
  };

  const handleFile = (e) => {
    const archivo = e.target.files && e.target.files[0];
    if (!archivo) return;
    if (!archivo.type || !archivo.type.startsWith('image/')) {
      setError("El archivo no es una imagen valida.");
      return;
    }
    if (archivo.size > 10 * 1024 * 1024) {
      setError("La imagen es demasiado grande (max 10 MB).");
      return;
    }
    if (fotoPreview && fotoPreview.startsWith('blob:')) URL.revokeObjectURL(fotoPreview);
    setForm((f) => ({ ...f, foto: archivo }));
    setFotoPreview(URL.createObjectURL(archivo));
    setError("");
  };

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true); setError(""); setOk("");
    try {
      const fd = new FormData();
      fd.append('cargo', form.cargo || '');
      fd.append('cargo_tipo', form.cargo_tipo || 'OTRO');
      fd.append('nivel_gobierno', form.nivel_gobierno || 'COMUNAL');
      fd.append('orden', String(form.orden || 1));
      fd.append('periodo', form.periodo || '');
      if (form.periodo_inicio) fd.append('periodo_inicio', form.periodo_inicio);
      if (form.periodo_fin) fd.append('periodo_fin', form.periodo_fin);
      fd.append('duracion_mandato_anos', String(form.duracion_mandato_anos || 2));
      fd.append('descripcion', form.descripcion || '');
      fd.append('sexo', form.sexo || '');
      fd.append('dni', form.dni || '');
      fd.append('telefono', form.telefono || '');
      fd.append('email_institucional', form.email_institucional || '');
      fd.append('nro_partida_sunarp', form.nro_partida_sunarp || '');
      fd.append('sede_inscripcion', form.sede_inscripcion || '');
      fd.append('resolucion_inscripcion', form.resolucion_inscripcion || '');
      if (form.fecha_inscripcion) fd.append('fecha_inscripcion', form.fecha_inscripcion);
      if (form.fecha_vencimiento_inscripcion) fd.append('fecha_vencimiento_inscripcion', form.fecha_vencimiento_inscripcion);
      fd.append('estado_inscripcion', form.estado_inscripcion || '');
      fd.append('es_cargo_tradicional', form.es_cargo_tradicional ? 'true' : 'false');
      fd.append('nombre_tradicional', form.nombre_tradicional || '');
      fd.append('reelegido', form.reelegido ? 'true' : 'false');
      if (form.autoridad_anterior) fd.append('autoridad_anterior', form.autoridad_anterior);
      fd.append('lengua_materna', form.lengua_materna || '');
      fd.append('es_admin', form.es_admin ? 'true' : 'false');
      fd.append('activo', form.activo ? 'true' : 'false');
      if (form.comunero) fd.append('comunero', form.comunero);
      if (form.usuario) fd.append('usuario', form.usuario);
      if (form.foto) fd.append('foto', form.foto);
      const cfg = { headers: { 'Content-Type': 'multipart/form-data' } };
      if (editItem) await api.patch(`/autoridades/${editItem.id}/`, fd, cfg);
      else await api.post("/autoridades/", fd, cfg);
      setOk("Autoridad guardada.");
      cerrar(); cargar();
    } catch (err) {
      const d = err.response?.data;
      setError(d?.detail || (typeof d === 'object' ? JSON.stringify(d) : d) || "Error al guardar.");
    } finally { setSaving(false); }
  };

  const eliminar = async (a) => {
    if (!window.confirm(`¿Eliminar a "${a.cargo}" de ${a.nombre_completo || ''}?`)) return;
    setError(""); setOk("");
    try { await api.delete(`/autoridades/${a.id}/`); setOk("Eliminado."); cargar(); }
    catch (e) { setError("No se pudo eliminar."); }
  };

  if (isStats) {
    return <StatsView stats={stats} loading={statsLoading} error={error} onReload={cargarStats} />;
  }

  // Banner global para vencen_pronto (Fase 4E)
  if (!isStats && items.some(i => i.tiempo_restante != null && i.tiempo_restante > 0 && i.tiempo_restante <= 90)) {
    // continua al render normal, pero el banner se agrega abajo
  }

  const nivelCfg = NIVELES[nivelParam] || NIVELES.COMUNAL;
  const totalActivos = items.filter(i => i.activo).length;

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      {/* Banner: autoridades que vencen en <= 90 dias (Fase 4E) */}
      {vencenPronto.length > 0 && (
        <div className="admin-banner admin-banner--warn mt-4">
          <FaExclamationTriangle />
          <div>
            <strong>Alerta de vencimiento proximo:</strong> {vencenPronto.length} autoridad(es) vencen en menos de 90 dias.
            <ul style={{ margin: "4px 0 0", paddingLeft: 20 }}>
              {vencenPronto.slice(0, 5).map(v => (
                <li key={v.id}>{v.cargo} - {v.nombre_completo} <em>(vence en {v.tiempo_restante} dias, {v.nivel_gobierno})</em></li>
              ))}
            </ul>
            <div className="text-mute" style={{ fontSize: 12, marginTop: 4 }}>
              Use el boton <strong>Dup</strong> para clonar y renovar el periodo antes del vencimiento.
            </div>
          </div>
        </div>
      )}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <div>
            <h3 className="admin-card__title">
              {nivelCfg.icon} {nivelCfg.label} ({totalActivos} activos)
            </h3>
            <p className="admin-card__subtitle">
              Ley 24656 (Comunal) · Ley 28440 (Municipal) · D.Leg. 370 (Politico)
            </p>
          </div>
          <div className="flex gap-2">
            <button className="admin-btn admin-btn-secondary" onClick={() => handleNivelChange("__STATS__")}>
              <FaChartPie /> Ver estadisticas
            </button>
            <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
              <FaPlus /> Nueva autoridad
            </button>
          </div>
        </div>

        {(nivelParam === "COMUNAL" && cuotaMujeres.cumple !== null) && (
          <div className={`admin-banner ${cuotaMujeres.cumple ? 'admin-banner--ok' : 'admin-banner--warn'}`}>
            {cuotaMujeres.cumple ? <FaCheckCircle /> : <FaExclamationTriangle />}
            <div>
              <strong>Cuota de genero (Ley 30982):</strong> {cuotaMujeres.count} mujeres de {cuotaMujeres.total} cargos activos ({cuotaMujeres.pct}%).
              {cuotaMujeres.cumple
                ? " Se cumple la cuota minima del 30%."
                : " Por debajo del 30% requerido por ley."}
            </div>
            <div className="admin-cuota-bar">
              <div
                className={`admin-cuota-bar__fill ${cuotaMujeres.cumple ? 'admin-cuota-bar__fill--ok' : 'admin-cuota-bar__fill--warn'}`}
                style={{ width: `${Math.min(cuotaMujeres.pct, 100)}%` }}
              />
              <span className="admin-cuota-bar__label">30%</span>
            </div>
          </div>
        )}

        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando…</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">
              No hay autoridades en este nivel.
              <div className="text-mute text-sm mt-2">Crea una con el boton "Nueva autoridad".</div>
            </div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Foto</th>
                  <th>Cargo</th>
                  <th>Persona</th>
                  <th>DNI</th>
                  <th>Periodo</th>
                  <th>Restante</th>
                  <th>Estado</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map(a => (
                  <tr key={a.id}>
                    <td>
                      {a.foto_url ? (
                        <img src={a.foto_url} alt={a.nombre_completo}
                             className="w-12 h-12 rounded-full object-cover" />
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-emerald-700 text-white flex items-center justify-center text-sm font-semibold">
                          {(a.nombre_completo?.[0] || '?').toUpperCase()}
                        </div>
                      )}
                    </td>
                    <td>
                      <div className="font-semibold">{a.cargo}</div>
                      <div className="text-xs text-mute">{a.cargo_tipo_display || a.cargo_tipo}</div>
                    </td>
                    <td>
                      {a.nombre_completo}
                      {a.sexo && <span className="ml-1 text-xs text-mute">({a.sexo_display || a.sexo})</span>}
                    </td>
                    <td className="text-mute">{a.dni || "—"}</td>
                    <td className="text-mute">{a.periodo || `${a.periodo_inicio || "?"} → ${a.periodo_fin || "?"}`}</td>
                    <td className="text-mute">
                      {a.tiempo_restante != null ? `${a.tiempo_restante} dias` : "—"}
                    </td>
                    <td>
                      {a.activo
                        ? <span className="admin-badge admin-badge--ok">Activo</span>
                        : <span className="admin-badge admin-badge--mute">Inactivo</span>}
                    </td>
                    <td className="actions justify-end">
                      <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(a)}><FaEdit /> Editar</button>
                      <button className="admin-btn admin-btn-sm admin-btn-secondary" onClick={() => abrirDuplicar(a)} title="Clonar para nuevo periodo electoral">Dup</button>
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
        title={editItem ? `Editar autoridad #${editItem.id}` : `Nueva autoridad - ${nivelCfg.label}`}
        onClose={cerrar}
        size="lg"
        footer={
          <>
            <button className="admin-btn" onClick={cerrar} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              {saving ? "Guardando…" : "Guardar"}
            </button>
          </>
        }
      >
        <form onSubmit={guardar} className="admin-form">
          <fieldset className="admin-form-section">
            <legend>Nivel y cargo</legend>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label admin-form-group__label--required" htmlFor="admin-autoridad-nivel">
                  Nivel de gobierno
                </label>
                <select
                  id="admin-autoridad-nivel"
                  name="nivel_gobierno"
                  className="admin-select"
                  value={form.nivel_gobierno}
                  onChange={(e) => {
                    const nv = e.target.value;
                    const cfg = NIVELES[nv] || NIVELES.COMUNAL;
                    setForm((f) => ({ ...f, nivel_gobierno: nv, duracion_mandato_anos: cfg.duracion }));
                  }}
                  required
                >
                  {Object.entries(NIVELES).map(([k, v]) => (
                    <option key={k} value={k}>{v.label}</option>
                  ))}
                </select>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label admin-form-group__label--required" htmlFor="admin-autoridad-cargo-tipo">
                  Tipo de cargo
                </label>
                <select
                  id="admin-autoridad-cargo-tipo"
                  name="cargo_tipo"
                  className="admin-select"
                  value={form.cargo_tipo}
                  onChange={(e) => {
                    const ct = e.target.value;
                    setForm((f) => ({ ...f, cargo_tipo: ct, cargo: f.cargo || ct }));
                  }}
                  required
                >
                  {(NIVELES[form.nivel_gobierno]?.cargos || NIVELES.COMUNAL.cargos).map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                  <option value="OTRO">OTRO</option>
                </select>
              </div>
            </div>

            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-cargo">Cargo (texto)</label>
                <input
                  id="admin-autoridad-cargo"
                  name="cargo"
                  className="admin-input"
                  value={form.cargo}
                  onChange={(e) => setForm({ ...form, cargo: e.target.value })}
                  maxLength={100}
                  placeholder="Ej. Presidente de la Directiva Comunal"
                />
                <div className="admin-form-hint">Texto libre. Se muestra tal cual en el sitio publico.</div>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-orden">Orden</label>
                <input
                  id="admin-autoridad-orden"
                  name="orden"
                  type="number"
                  min="1"
                  max="999"
                  className="admin-input"
                  value={form.orden}
                  onChange={(e) => setForm({ ...form, orden: Number(e.target.value) || 1 })}
                />
                <div className="admin-form-hint">1 = Presidente, 2 = Vicepresidente, etc.</div>
              </div>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Persona y documento</legend>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-comunero">Comunero</label>
                <select
                  id="admin-autoridad-comunero"
                  name="comunero"
                  className="admin-select"
                  value={form.comunero}
                  onChange={(e) => setForm({ ...form, comunero: e.target.value })}
                >
                  <option value="">— Ninguno (autoridad externa) —</option>
                  {comuneros.map(c => (
                    <option key={c.id} value={c.id}>
                      {c.nombre_completo || `${c.nombres} ${c.apellidos}`} (DNI {c.dni})
                    </option>
                  ))}
                </select>
                <div className="admin-form-hint">Opcional para Gobernador / Teniente.</div>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-usuario">Usuario del sistema</label>
                <select
                  id="admin-autoridad-usuario"
                  name="usuario"
                  className="admin-select"
                  value={form.usuario}
                  onChange={(e) => setForm({ ...form, usuario: e.target.value })}
                >
                  <option value="">— Ninguno —</option>
                  {usuarios.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.nombre_completo || u.email} ({u.tipo_usuario})
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-dni">DNI</label>
                <input
                  id="admin-autoridad-dni"
                  name="dni"
                  className="admin-input"
                  value={form.dni}
                  onChange={(e) => setForm({ ...form, dni: e.target.value.replace(/\D/g, '').slice(0, 8) })}
                  inputMode="numeric"
                  pattern="[0-9]{8}"
                  maxLength={8}
                  autoComplete="off"
                  placeholder="12345678"
                />
                <div className="admin-form-hint">Para autoridades sin Comunero (Gobernador, etc.).</div>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-sexo">
                  <FaVenusMars className="inline" /> Sexo
                </label>
                <select
                  id="admin-autoridad-sexo"
                  name="sexo"
                  className="admin-select"
                  value={form.sexo}
                  onChange={(e) => setForm({ ...form, sexo: e.target.value })}
                >
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                  <option value="O">Otro</option>
                  <option value="">— Prefiero no decir —</option>
                </select>
                <div className="admin-form-hint">Necesario para validar cuota 30% (Ley 30982).</div>
              </div>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>SUNARP y marco legal</legend>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-sunarp">Partida SUNARP</label>
                <input
                  id="admin-autoridad-sunarp"
                  name="nro_partida_sunarp"
                  className="admin-input"
                  value={form.nro_partida_sunarp}
                  onChange={(e) => setForm({ ...form, nro_partida_sunarp: e.target.value })}
                  maxLength={50}
                  placeholder="Ej. 11001234"
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-sede-inscripcion">Oficina registral</label>
                <input
                  id="admin-autoridad-sede-inscripcion"
                  name="sede_inscripcion"
                  className="admin-input"
                  value={form.sede_inscripcion}
                  onChange={(e) => setForm({ ...form, sede_inscripcion: e.target.value })}
                  maxLength={100}
                  placeholder="Ej. Oficina Registral de Jaen"
                />
              </div>
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-resolucion">Resolucion de inscripcion</label>
                <input
                  id="admin-autoridad-resolucion"
                  name="resolucion_inscripcion"
                  className="admin-input"
                  value={form.resolucion_inscripcion}
                  onChange={(e) => setForm({ ...form, resolucion_inscripcion: e.target.value })}
                  maxLength={50}
                  placeholder="R.D. N° 012-2024-GRCAJ/DRA"
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-estado-inscripcion">Estado de inscripcion</label>
                <select
                  id="admin-autoridad-estado-inscripcion"
                  name="estado_inscripcion"
                  className="admin-select"
                  value={form.estado_inscripcion}
                  onChange={(e) => setForm({ ...form, estado_inscripcion: e.target.value })}
                >
                  <option value="">Sin tramite</option>
                  <option value="INSCRITO">Inscrito</option>
                  <option value="EN_TRAMITE">En tramite</option>
                  <option value="OBSERVADO">Observado</option>
                  <option value="PENDIENTE">Pendiente</option>
                  <option value="VENCIDO">Vencido</option>
                </select>
              </div>
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-fecha-inscripcion">Fecha de inscripcion</label>
                <input
                  id="admin-autoridad-fecha-inscripcion"
                  name="fecha_inscripcion"
                  type="date"
                  className="admin-input"
                  value={form.fecha_inscripcion}
                  onChange={(e) => setForm({ ...form, fecha_inscripcion: e.target.value })}
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-fecha-vencimiento">Vencimiento vigencia</label>
                <input
                  id="admin-autoridad-fecha-vencimiento"
                  name="fecha_vencimiento_inscripcion"
                  type="date"
                  className="admin-input"
                  value={form.fecha_vencimiento_inscripcion}
                  onChange={(e) => setForm({ ...form, fecha_vencimiento_inscripcion: e.target.value })}
                />
              </div>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Cargo tradicional y reelegido</legend>
            <div className="admin-form-row">
              <div className="admin-form-group admin-form-group--check">
                <input
                  id="admin-autoridad-es-tradicional"
                  name="es_cargo_tradicional"
                  type="checkbox"
                  className="admin-checkbox"
                  checked={form.es_cargo_tradicional}
                  onChange={(e) => setForm({ ...form, es_cargo_tradicional: e.target.checked })}
                />
                <label htmlFor="admin-autoridad-es-tradicional">Es cargo tradicional andino (Varayoc, Mayordomo, Padrino, etc.)</label>
              </div>
              <div className="admin-form-group admin-form-group--check">
                <input
                  id="admin-autoridad-reelegido"
                  name="reelegido"
                  type="checkbox"
                  className="admin-checkbox"
                  checked={form.reelegido}
                  onChange={(e) => setForm({ ...form, reelegido: e.target.checked })}
                />
                <label htmlFor="admin-autoridad-reelegido">Reelegido (segundo periodo consecutivo)</label>
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label" htmlFor="admin-autoridad-nombre-tradicional">Nombre tradicional (opcional)</label>
              <input
                id="admin-autoridad-nombre-tradicional"
                name="nombre_tradicional"
                className="admin-input"
                value={form.nombre_tradicional}
                onChange={(e) => setForm({ ...form, nombre_tradicional: e.target.value })}
                maxLength={100}
                placeholder="Ej. Varayoc, Mayordomo, Padrino"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label" htmlFor="admin-autoridad-lengua">Lengua materna (requisito Ley 24656 Art. 20.d)</label>
              <select
                id="admin-autoridad-lengua"
                name="lengua_materna"
                className="admin-select"
                value={form.lengua_materna}
                onChange={(e) => setForm({ ...form, lengua_materna: e.target.value })}
              >
                <option value="">— No especificado —</option>
                <option value="ES">Espanol</option>
                <option value="QU">Quechua (Chinchaysuyo)</option>
                <option value="AW">Awajun</option>
                <option value="WP">Wampis</option>
                <option value="OT">Otro</option>
              </select>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Periodo de gestion</legend>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-periodo-inicio">Fecha de inicio</label>
                <input
                  id="admin-autoridad-periodo-inicio"
                  name="periodo_inicio"
                  type="date"
                  className="admin-input"
                  value={form.periodo_inicio}
                  onChange={(e) => setForm({ ...form, periodo_inicio: e.target.value })}
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-periodo-fin">Fecha de fin</label>
                <input
                  id="admin-autoridad-periodo-fin"
                  name="periodo_fin"
                  type="date"
                  className="admin-input"
                  value={form.periodo_fin}
                  onChange={(e) => setForm({ ...form, periodo_fin: e.target.value })}
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-duracion">Duracion (anos)</label>
                <input
                  id="admin-autoridad-duracion"
                  name="duracion_mandato_anos"
                  type="number"
                  min="1"
                  max="10"
                  className="admin-input"
                  value={form.duracion_mandato_anos}
                  onChange={(e) => setForm({ ...form, duracion_mandato_anos: Number(e.target.value) || 2 })}
                />
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label" htmlFor="admin-autoridad-periodo-texto">Periodo (texto)</label>
              <input
                id="admin-autoridad-periodo-texto"
                name="periodo"
                className="admin-input"
                value={form.periodo}
                onChange={(e) => setForm({ ...form, periodo: e.target.value })}
                maxLength={50}
                placeholder="2025-2027"
              />
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Contacto</legend>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-telefono">Telefono</label>
                <input
                  id="admin-autoridad-telefono"
                  name="telefono"
                  type="tel"
                  className="admin-input"
                  value={form.telefono}
                  onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                  maxLength={15}
                  autoComplete="tel"
                  placeholder="+51 999 999 999"
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-autoridad-email">Email institucional</label>
                <input
                  id="admin-autoridad-email"
                  name="email_institucional"
                  type="email"
                  className="admin-input"
                  value={form.email_institucional}
                  onChange={(e) => setForm({ ...form, email_institucional: e.target.value })}
                  maxLength={254}
                  autoComplete="email"
                  placeholder="autoridad@comunidad.gob.pe"
                />
              </div>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Marco legal y descripcion</legend>
            <div className="admin-form-group">
              <label className="admin-form-group__label" htmlFor="admin-autoridad-descripcion">Descripcion del cargo</label>
              <textarea
                id="admin-autoridad-descripcion"
                name="descripcion"
                className="admin-textarea"
                value={form.descripcion}
                onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                rows={3}
                placeholder="Funciones y responsabilidades del cargo (segun Ley 24656, 27972 o 28440)."
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label" htmlFor="admin-autoridad-sunarp">Partida SUNARP</label>
              <input
                id="admin-autoridad-sunarp"
                name="nro_partida_sunarp"
                className="admin-input"
                value={form.nro_partida_sunarp}
                onChange={(e) => setForm({ ...form, nro_partida_sunarp: e.target.value })}
                maxLength={50}
                placeholder="Ej. 11001234"
              />
              <div className="admin-form-hint">Numero de partida registral donde esta inscrita la autoridad.</div>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Estado y permisos</legend>
            <div className="admin-form-row">
              <div className="admin-form-group admin-form-group--check">
                <input
                  id="admin-autoridad-activo"
                  name="activo"
                  type="checkbox"
                  className="admin-checkbox"
                  checked={form.activo}
                  onChange={(e) => setForm({ ...form, activo: e.target.checked })}
                />
                <label htmlFor="admin-autoridad-activo">Autoridad activa (visible en sitio publico)</label>
              </div>
              <div className="admin-form-group admin-form-group--check">
                <input
                  id="admin-autoridad-es-admin"
                  name="es_admin"
                  type="checkbox"
                  className="admin-checkbox"
                  checked={form.es_admin}
                  onChange={(e) => setForm({ ...form, es_admin: e.target.checked })}
                />
                <label htmlFor="admin-autoridad-es-admin">Tiene acceso al panel admin</label>
              </div>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Foto oficial</legend>
            <input
              ref={inputFotoRef}
              id="admin-autoridad-foto"
              name="foto"
              type="file"
              accept="image/*"
              onChange={handleFile}
              className="hidden"
            />
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => inputFotoRef.current?.click()}
                className="admin-btn admin-btn-secondary"
              >
                <FaCloudUploadAlt /> {fotoPreview ? 'Cambiar imagen' : 'Subir imagen'}
              </button>
              {fotoPreview && (
                <button type="button" onClick={limpiarFoto} className="admin-btn admin-btn-sm">
                  Quitar
                </button>
              )}
            </div>
            {fotoPreview && (
              <div className="mt-3 flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <img
                  src={fotoPreview}
                  alt="Preview"
                  className="w-16 h-16 rounded-full object-cover border-2 border-emerald-500"
                />
                <div className="text-sm text-gray-600">
                  {form.foto
                    ? <><strong>Nuevo archivo:</strong> {form.foto.name} ({(form.foto.size / 1024).toFixed(1)} KB)</>
                    : <><strong>Foto actual:</strong> se mantiene a menos que subas otra</>
                  }
                </div>
              </div>
            )}
            <div className="admin-form-hint">Si no subes imagen, se usaran las iniciales o la foto del usuario asociado.</div>
          </fieldset>
        </form>
      </AdminModal>
    </div>
  );
}

function StatsView({ stats, loading, error, onReload }) {
  return (
    <div className="admin-card mt-4">
      <div className="admin-card__header">
        <h3 className="admin-card__title"><FaChartPie /> Estadisticas de autoridades</h3>
        <button className="admin-btn admin-btn-sm" onClick={onReload} disabled={loading}>
          {loading ? "Cargando…" : "Recargar"}
        </button>
      </div>
      <div className="admin-card__body">
        {error && <div className="admin-error">{error}</div>}
        {loading && !stats ? (
          <div className="admin-loading">Cargando…</div>
        ) : !stats ? (
          <div className="admin-empty">Sin datos disponibles.</div>
        ) : (
          <>
            <div className="admin-stats-grid">
              <div className="admin-stat">
                <div className="admin-stat__label">Total activos</div>
                <div className="admin-stat__value">{stats.total ?? "—"}</div>
              </div>
              {Object.entries(stats.por_nivel || {}).map(([nivel, count]) => {
                const cfg = NIVELES[nivel] || { label: nivel, icon: <FaUsers /> };
                return (
                  <div key={nivel} className="admin-stat">
                    <div className="admin-stat__label">{cfg.icon} {cfg.label}</div>
                    <div className="admin-stat__value">{count}</div>
                  </div>
                );
              })}
            </div>

            {stats.cuota_genero && Object.keys(stats.cuota_genero).length > 0 && (
              <div className="admin-card mt-4">
                <div className="admin-card__header">
                  <h4 className="admin-card__title">Cuota de genero (Ley 30982 - 30%)</h4>
                </div>
                <div className="admin-card__body">
                  {Object.entries(stats.cuota_genero).map(([nivel, info]) => (
                    <div key={nivel} className="admin-cuota-row">
                      <div className="admin-cuota-row__head">
                        <strong>{NIVELES[nivel]?.label || nivel}</strong>
                        <span className={info.cumple_cuota_30 ? 'admin-badge admin-badge--ok' : 'admin-badge admin-badge--warn'}>
                          {info.cumple_cuota_30 === null ? "N/A (< 3 cargos)" : info.cumple_cuota_30 ? "Cumple" : "No cumple"}
                        </span>
                      </div>
                      <div className="admin-cuota-bar">
                        <div
                          className={`admin-cuota-bar__fill ${info.cumple_cuota_30 ? 'admin-cuota-bar__fill--ok' : 'admin-cuota-bar__fill--warn'}`}
                          style={{ width: `${Math.min(info.porcentaje || 0, 100)}%` }}
                        />
                        <span className="admin-cuota-bar__label">
                          {info.porcentaje || 0}% ({info.mujeres}/{info.total})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {stats.proxima_eleccion && Object.keys(stats.proxima_eleccion).length > 0 && (
              <div className="admin-card mt-4">
                <div className="admin-card__header">
                  <h4 className="admin-card__title">Proximas elecciones</h4>
                </div>
                <div className="admin-card__body">
                  <table className="admin-table">
                    <thead><tr><th>Nivel</th><th>Fecha</th></tr></thead>
                    <tbody>
                      {Object.entries(stats.proxima_eleccion).map(([nivel, fecha]) => (
                        <tr key={nivel}>
                          <td>{NIVELES[nivel]?.label || nivel}</td>
                          <td className="text-mute">{fecha || "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
