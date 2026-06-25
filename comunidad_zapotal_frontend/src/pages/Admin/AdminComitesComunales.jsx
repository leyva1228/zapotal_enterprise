import React, { useEffect, useState, useRef } from "react";
import {
  FaPlus, FaEdit, FaTrash, FaGavel, FaCalendarAlt, FaUserShield,
  FaBalanceScale, FaSeedling, FaHome, FaUserTie, FaUsers,
} from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

const TIPOS = {
  ELECTORAL: { label: "Comite Electoral",         icon: <FaGavel /> },
  REVISOR_CUENTAS: { label: "Revisor de Cuentas",  icon: <FaBalanceScale /> },
  RONDAS: { label: "Rondas Campesinas",          icon: <FaUserShield /> },
  GESTION: { label: "Comite de Gestion",         icon: <FaSeedling /> },
  OBRAS: { label: "Comite de Obras",             icon: <FaHome /> },
  EDUCACION: { label: "Comite de Educacion",     icon: <FaUserTie /> },
  OTRO: { label: "Otro",                         icon: <FaUsers /> },
};

const EMPTY = {
  nombre: "", tipo: "GESTION", nivel: "COMUNAL",
  descripcion: "",
  presidente: "", secretario: "", vocal: "",
  fecha_constitucion: "", periodo_inicio: "", periodo_fin: "",
  activo: true, acta_pdf: null,
};

export default function AdminComitesComunales() {
  const [items, setItems] = useState([]);
  const [autoridades, setAutoridades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const inputActaRef = useRef(null);

  const cargar = async () => {
    setLoading(true);
    setError("");
    try {
      const [r1, r2] = await Promise.all([
        api.get("/comites-comunales/?page_size=200"),
        api.get("/autoridades/?page_size=200").catch(() => ({ data: { data: [] } })),
      ]);
      setItems(extractList(r1.data));
      setAutoridades(extractList(r2.data));
    } catch (e) {
      setError("No se pudieron cargar los comites.");
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { cargar(); }, []);

  const abrirNuevo = () => {
    setEditItem(null);
    setForm(EMPTY);
    setModalOpen(true);
  };
  const abrirEditar = (c) => {
    setEditItem(c);
    setForm({
      nombre: c.nombre || "",
      tipo: c.tipo || "GESTION",
      nivel: c.nivel || "COMUNAL",
      descripcion: c.descripcion || "",
      presidente: c.presidente || "",
      secretario: c.secretario || "",
      vocal: c.vocal || "",
      fecha_constitucion: c.fecha_constitucion || "",
      periodo_inicio: c.periodo_inicio || "",
      periodo_fin: c.periodo_fin || "",
      activo: c.activo !== false,
      acta_pdf: null,
    });
    setModalOpen(true);
  };
  const cerrar = () => {
    setModalOpen(false);
    setEditItem(null);
    setForm(EMPTY);
  };

  const handleActa = (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    if (f.type !== "application/pdf") {
      setError("Solo se permiten archivos PDF.");
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      setError("PDF demasiado grande (max 5 MB).");
      return;
    }
    setForm((s) => ({ ...s, acta_pdf: f }));
  };

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true); setError(""); setOk("");
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => {
        if (v != null && v !== "" && k !== "acta_pdf") fd.append(k, v);
      });
      fd.append("activo", form.activo ? "true" : "false");
      if (form.acta_pdf) fd.append("acta_pdf", form.acta_pdf);
      const cfg = { headers: { "Content-Type": "multipart/form-data" } };
      if (editItem) await api.patch(`/comites-comunales/${editItem.id}/`, fd, cfg);
      else await api.post("/comites-comunales/", fd, cfg);
      setOk("Comite guardado.");
      cerrar(); cargar();
    } catch (err) {
      const d = err.response?.data;
      setError(d?.detail || (typeof d === "object" ? JSON.stringify(d) : d) || "Error al guardar.");
    } finally { setSaving(false); }
  };

  const eliminar = async (c) => {
    if (!window.confirm(`¿Eliminar el comite "${c.nombre}"?`)) return;
    setError(""); setOk("");
    try { await api.delete(`/comites-comunales/${c.id}/`); setOk("Eliminado."); cargar(); }
    catch (e) { setError("No se pudo eliminar."); }
  };

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <div>
            <h3 className="admin-card__title"><FaGavel /> Comites Comunales ({items.length})</h3>
            <p className="admin-card__subtitle">
              Ley 24656 Art. 16.c - Comites Especializados. Incluye Comite Electoral, Revisor de Cuentas, Rondas Campesinas.
            </p>
          </div>
          <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
            <FaPlus /> Nuevo comite
          </button>
        </div>
        <div className="admin-card__body">
          {loading ? (
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">No hay comites registrados.</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Tipo</th>
                  <th>Nivel</th>
                  <th>Presidente</th>
                  <th>Constituido</th>
                  <th>Vence en</th>
                  <th>Estado</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map(c => {
                  const cfg = TIPOS[c.tipo] || TIPOS.OTRO;
                  return (
                    <tr key={c.id}>
                      <td>
                        <div className="font-semibold">{c.nombre}</div>
                        {c.descripcion && (
                          <div className="text-xs text-mute" style={{ maxWidth: 320 }}>
                            {c.descripcion.length > 80 ? c.descripcion.slice(0, 80) + "..." : c.descripcion}
                          </div>
                        )}
                      </td>
                      <td><span className="admin-badge admin-badge--info">{cfg.icon} {cfg.label}</span></td>
                      <td className="text-mute">{c.nivel_display || c.nivel}</td>
                      <td className="text-mute">{c.presidente_info ? c.presidente_info.nombre_completo : "—"}</td>
                      <td className="text-mute">{c.fecha_constitucion || "—"}</td>
                      <td className="text-mute">
                        {c.tiempo_restante != null && c.tiempo_restante > 0
                          ? <span className={c.tiempo_restante < 90 ? "au-card-vence-pronto" : ""}>{c.tiempo_restante} dias</span>
                          : "—"}
                      </td>
                      <td>
                        {c.activo
                          ? <span className="admin-badge admin-badge--ok">Activo</span>
                          : <span className="admin-badge admin-badge--mute">Inactivo</span>}
                      </td>
                      <td className="actions justify-end">
                        <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(c)}><FaEdit /> Editar</button>
                        <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(c)}><FaTrash /></button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <AdminModal
        open={modalOpen}
        title={editItem ? `Editar comite #${editItem.id}` : "Nuevo comite comunal"}
        onClose={cerrar}
        size="lg"
        footer={
          <>
            <button className="admin-btn" onClick={cerrar} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              {saving ? "Guardando..." : "Guardar"}
            </button>
          </>
        }
      >
        <form onSubmit={guardar} className="admin-form">
          <fieldset className="admin-form-section">
            <legend>Identificacion</legend>
            <div className="admin-form-group">
              <label className="admin-form-group__label admin-form-group__label--required" htmlFor="admin-comite-nombre">Nombre del comite</label>
              <input
                id="admin-comite-nombre"
                name="nombre"
                className="admin-input"
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                maxLength={150}
                required
                placeholder="Ej. Comite Electoral 2026"
              />
            </div>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label admin-form-group__label--required" htmlFor="admin-comite-tipo">Tipo</label>
                <select
                  id="admin-comite-tipo"
                  name="tipo"
                  className="admin-select"
                  value={form.tipo}
                  onChange={(e) => setForm({ ...form, tipo: e.target.value })}
                  required
                >
                  {Object.entries(TIPOS).map(([k, v]) => (
                    <option key={k} value={k}>{v.label}</option>
                  ))}
                </select>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-comite-nivel">Nivel</label>
                <select
                  id="admin-comite-nivel"
                  name="nivel"
                  className="admin-select"
                  value={form.nivel}
                  onChange={(e) => setForm({ ...form, nivel: e.target.value })}
                >
                  <option value="COMUNAL">Nivel Comunal</option>
                  <option value="ANEXO">Anexo / Sector</option>
                  <option value="DISTRITAL">Nivel Distrital</option>
                </select>
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label" htmlFor="admin-comite-descripcion">Descripcion / funciones</label>
              <textarea
                id="admin-comite-descripcion"
                name="descripcion"
                className="admin-textarea"
                value={form.descripcion}
                onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                rows={3}
                placeholder="Funciones del comite y marco legal aplicable."
              />
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Integrantes</legend>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-comite-presidente">Presidente</label>
                <select
                  id="admin-comite-presidente"
                  name="presidente"
                  className="admin-select"
                  value={form.presidente}
                  onChange={(e) => setForm({ ...form, presidente: e.target.value })}
                >
                  <option value="">— Ninguno —</option>
                  {autoridades.map(a => (
                    <option key={a.id} value={a.id}>
                      {a.cargo} - {a.nombre_completo || `DNI ${a.dni}`}
                    </option>
                  ))}
                </select>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-comite-secretario">Secretario</label>
                <select
                  id="admin-comite-secretario"
                  name="secretario"
                  className="admin-select"
                  value={form.secretario}
                  onChange={(e) => setForm({ ...form, secretario: e.target.value })}
                >
                  <option value="">— Ninguno —</option>
                  {autoridades.map(a => (
                    <option key={a.id} value={a.id}>
                      {a.cargo} - {a.nombre_completo || `DNI ${a.dni}`}
                    </option>
                  ))}
                </select>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-comite-vocal">Vocal</label>
                <select
                  id="admin-comite-vocal"
                  name="vocal"
                  className="admin-select"
                  value={form.vocal}
                  onChange={(e) => setForm({ ...form, vocal: e.target.value })}
                >
                  <option value="">— Ninguno —</option>
                  {autoridades.map(a => (
                    <option key={a.id} value={a.id}>
                      {a.cargo} - {a.nombre_completo || `DNI ${a.dni}`}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </fieldset>

          <fieldset className="admin-form-section">
            <legend>Vigencia y acta</legend>
            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-comite-fecha-constitucion">Fecha de constitucion</label>
                <input
                  id="admin-comite-fecha-constitucion"
                  name="fecha_constitucion"
                  type="date"
                  className="admin-input"
                  value={form.fecha_constitucion}
                  onChange={(e) => setForm({ ...form, fecha_constitucion: e.target.value })}
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-comite-periodo-inicio">Inicio del periodo</label>
                <input
                  id="admin-comite-periodo-inicio"
                  name="periodo_inicio"
                  type="date"
                  className="admin-input"
                  value={form.periodo_inicio}
                  onChange={(e) => setForm({ ...form, periodo_inicio: e.target.value })}
                />
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label" htmlFor="admin-comite-periodo-fin">Fin del periodo</label>
                <input
                  id="admin-comite-periodo-fin"
                  name="periodo_fin"
                  type="date"
                  className="admin-input"
                  value={form.periodo_fin}
                  onChange={(e) => setForm({ ...form, periodo_fin: e.target.value })}
                />
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label admin-form-group__label--required" htmlFor="admin-comite-acta">Acta de constitucion (PDF)</label>
              <input
                ref={inputActaRef}
                id="admin-comite-acta"
                name="acta_pdf"
                type="file"
                accept="application/pdf"
                onChange={handleActa}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => inputActaRef.current?.click()}
                className="admin-btn admin-btn-secondary"
              >
                Subir PDF
              </button>
              {form.acta_pdf && (
                <span style={{ marginLeft: 12, fontSize: 13 }}>
                  {form.acta_pdf.name} ({(form.acta_pdf.size / 1024).toFixed(1)} KB)
                </span>
              )}
              <div className="admin-form-hint">Solo PDF, max 5 MB. Obligatorio para validar la constitucion del comite.</div>
            </div>
            <div className="admin-form-group admin-form-group--check">
              <input
                id="admin-comite-activo"
                name="activo"
                type="checkbox"
                className="admin-checkbox"
                checked={form.activo}
                onChange={(e) => setForm({ ...form, activo: e.target.checked })}
              />
              <label htmlFor="admin-comite-activo">Comite activo (visible en sitio publico)</label>
            </div>
          </fieldset>
        </form>
      </AdminModal>
    </div>
  );
}
