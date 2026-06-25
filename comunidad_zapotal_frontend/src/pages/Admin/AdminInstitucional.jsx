// Admin consolidado para configuracion institucional y paginas legales.
//
// Tabs:
// 1. Configuracion - datos institucionales, contacto, ubicacion
// 2. Marco Legal - lista de items
// 3. Paginas Legales - Terminos, Privacidad, Cookies
// 4. Hitos Historicos
// 5. Galeria
// (Los mensajes de contacto se gestionan en /admin/contacto)
import React, { useEffect, useState } from "react";
import {
  FaCog, FaBalanceScale, FaScroll, FaHistory, FaImages,
  FaPlus, FaEdit, FaTrash, FaSave, FaTimes,
  FaCheckCircle, FaSpinner, FaExternalLinkAlt,
} from "react-icons/fa";
import api from "../../api";
import AdminModal from "../../components/Admin/AdminModal";

const TABS = [
  { id: 'configuracion', label: 'Configuracion',   icon: <FaCog /> },
  { id: 'marco-legal',    label: 'Marco Legal',      icon: <FaBalanceScale /> },
  { id: 'paginas-legales',label: 'Paginas Legales',  icon: <FaScroll /> },
  { id: 'hitos',          label: 'Hitos Historicos', icon: <FaHistory /> },
  { id: 'galeria',        label: 'Galeria',          icon: <FaImages /> },
];

export default function AdminInstitucional() {
  const [tab, setTab] = useState('configuracion');
  return (
    <div>
      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaCog /> Configuracion Institucional
          </h3>
          <p className="admin-card__subtitle">
            Datos institucionales, marco legal, paginas legales, hitos y galeria.
            Los mensajes de contacto se gestionan en <a href="/admin/contacto">/admin/contacto</a>.
          </p>
        </div>
        <div className="admin-card__body" style={{ padding: 0 }}>
          <div className="admin-tabs" style={{ display: 'flex', borderBottom: '1px solid #e5e7eb' }}>
            {TABS.map(t => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                className={`admin-tab ${tab === t.id ? 'admin-tab--active' : ''}`}
                style={{
                  padding: '12px 20px', background: 'transparent', border: 0,
                  borderBottom: tab === t.id ? '3px solid #0a3d1f' : '3px solid transparent',
                  color: tab === t.id ? '#0a3d1f' : '#6b7280',
                  fontWeight: tab === t.id ? 700 : 500, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 6,
                }}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </div>
          <div style={{ padding: 20 }}>
            {tab === 'configuracion'  && <ConfiguracionTab />}
            {tab === 'marco-legal'     && <MarcoLegalTab />}
            {tab === 'paginas-legales' && <PaginasLegalesTab />}
            {tab === 'hitos'           && <HitosTab />}
            {tab === 'galeria'         && <GaleriaTab />}
          </div>
        </div>
      </div>
    </div>
  );
}

/* =================== TABS =================== */

function ConfiguracionTab() {
  const [data, setData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [ok, setOk] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/configuracion/').then((r) => setData(r.data)).catch(() => setError('No se pudo cargar.'));
  }, []);

  const update = (k, v) => setData((d) => ({ ...d, [k]: v }));

  const guardar = async () => {
    setSaving(true); setError(''); setOk('');
    try {
      const r = await api.patch('/configuracion/', data);
      setData(r.data);
      setOk('Configuracion guardada.');
    } catch (e) {
      setError('Error al guardar.');
    } finally { setSaving(false); }
  };

  if (!data) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando...</div>;

  return (
    <div>
      {ok && <div className="admin-success">{ok}</div>}
      {error && <div className="admin-error">{error}</div>}

      <fieldset className="admin-form-section">
        <legend>Identidad</legend>
        <div className="admin-form-row">
          <div className="admin-form-group">
            <label htmlFor="cfg-nombre-oficial" className="admin-form-group__label">Nombre oficial</label>
            <input id="cfg-nombre-oficial" name="nombre_oficial" className="admin-input"
              value={data.nombre_oficial || ''} onChange={(e) => update('nombre_oficial', e.target.value)} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="cfg-nombre-corto" className="admin-form-group__label">Nombre corto</label>
            <input id="cfg-nombre-corto" name="nombre_corto" className="admin-input"
              value={data.nombre_corto || ''} onChange={(e) => update('nombre_corto', e.target.value)} />
          </div>
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-eslogan" className="admin-form-group__label">Eslogan</label>
          <input id="cfg-eslogan" name="eslogan" className="admin-input"
            value={data.eslogan || ''} onChange={(e) => update('eslogan', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-descripcion" className="admin-form-group__label">Descripcion corta</label>
          <textarea id="cfg-descripcion" name="descripcion_corta" className="admin-textarea"
            value={data.descripcion_corta || ''} onChange={(e) => update('descripcion_corta', e.target.value)} rows={3} />
        </div>
      </fieldset>

      <fieldset className="admin-form-section">
        <legend>Contacto</legend>
        <div className="admin-form-row">
          <div className="admin-form-group">
            <label htmlFor="cfg-tel" className="admin-form-group__label">Telefono fijo</label>
            <input id="cfg-tel" name="telefono_fijo" className="admin-input" autoComplete="tel"
              value={data.telefono_fijo || ''} onChange={(e) => update('telefono_fijo', e.target.value)} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="cfg-whatsapp" className="admin-form-group__label">WhatsApp (con prefijo pais)</label>
            <input id="cfg-whatsapp" name="whatsapp_numero" className="admin-input" type="tel"
              value={data.whatsapp_numero || ''} onChange={(e) => update('whatsapp_numero', e.target.value)}
              placeholder="+51931757530" />
          </div>
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-email" className="admin-form-group__label">Email de contacto</label>
          <input id="cfg-email" name="email_contacto" type="email" className="admin-input" autoComplete="email"
            value={data.email_contacto || ''} onChange={(e) => update('email_contacto', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-email-priv" className="admin-form-group__label">Email privacidad / DPO</label>
          <input id="cfg-email-priv" name="email_privacidad" type="email" className="admin-input"
            value={data.email_privacidad || ''} onChange={(e) => update('email_privacidad', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-email-den" className="admin-form-group__label">Email de denuncias</label>
          <input id="cfg-email-den" name="email_denuncias" type="email" className="admin-input"
            value={data.email_denuncias || ''} onChange={(e) => update('email_denuncias', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-horario" className="admin-form-group__label">Horario de atencion</label>
          <input id="cfg-horario" name="horario_atencion" className="admin-input"
            value={data.horario_atencion || ''} onChange={(e) => update('horario_atencion', e.target.value)} />
        </div>
      </fieldset>

      <fieldset className="admin-form-section">
        <legend>Ubicacion</legend>
        <div className="admin-form-row">
          <div className="admin-form-group">
            <label htmlFor="cfg-dist" className="admin-form-group__label">Distrito</label>
            <input id="cfg-dist" name="distrito" className="admin-input"
              value={data.distrito || ''} onChange={(e) => update('distrito', e.target.value)} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="cfg-prov" className="admin-form-group__label">Provincia</label>
            <input id="cfg-prov" name="provincia" className="admin-input"
              value={data.provincia || ''} onChange={(e) => update('provincia', e.target.value)} />
          </div>
        </div>
        <div className="admin-form-row">
          <div className="admin-form-group">
            <label htmlFor="cfg-reg" className="admin-form-group__label">Region</label>
            <input id="cfg-reg" name="region" className="admin-input"
              value={data.region || ''} onChange={(e) => update('region', e.target.value)} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="cfg-ubi" className="admin-form-group__label">Ubigeo</label>
            <input id="cfg-ubi" name="ubigeo" className="admin-input"
              value={data.ubigeo || ''} onChange={(e) => update('ubigeo', e.target.value)} />
          </div>
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-dir" className="admin-form-group__label">Direccion Casa Comunal</label>
          <input id="cfg-dir" name="direccion_casa_comunal" className="admin-input"
            value={data.direccion_casa_comunal || ''} onChange={(e) => update('direccion_casa_comunal', e.target.value)} />
        </div>
        <div className="admin-form-row">
          <div className="admin-form-group">
            <label htmlFor="cfg-lat" className="admin-form-group__label">Latitud</label>
            <input id="cfg-lat" name="coordenadas_lat" type="number" step="any" className="admin-input"
              value={data.coordenadas_lat || ''} onChange={(e) => update('coordenadas_lat', e.target.value)} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="cfg-lng" className="admin-form-group__label">Longitud</label>
            <input id="cfg-lng" name="coordenadas_lng" type="number" step="any" className="admin-input"
              value={data.coordenadas_lng || ''} onChange={(e) => update('coordenadas_lng', e.target.value)} />
          </div>
        </div>
      </fieldset>

      <div style={{ textAlign: 'right' }}>
        <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving} type="button">
          <FaSave /> {saving ? 'Guardando...' : 'Guardar configuracion'}
        </button>
      </div>
    </div>
  );
}

function MarcoLegalTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [edit, setEdit] = useState(null);
  const [form, setForm] = useState({ titulo: '', norma: '', descripcion: '', icono: 'FaGavel', url_externa: '', orden: 0, activo: true });
  const [saving, setSaving] = useState(false);

  const cargar = () => {
    setLoading(true);
    api.get('/marco-legal/').then((r) => {
      setItems(r.data.results || r.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };
  useEffect(cargar, []);

  const abrirNuevo = () => {
    setEdit(null);
    setForm({ titulo: '', norma: '', descripcion: '', icono: 'FaGavel', url_externa: '', orden: 0, activo: true });
    setModal(true);
  };
  const abrirEditar = (it) => {
    setEdit(it);
    setForm({
      titulo: it.titulo, norma: it.norma, descripcion: it.descripcion,
      icono: it.icono, url_externa: it.url_externa || '',
      orden: it.orden, activo: it.activo,
    });
    setModal(true);
  };
  const guardar = async () => {
    setSaving(true);
    try {
      if (edit) await api.patch(`/marco-legal/${edit.id}/`, form);
      else await api.post('/marco-legal/', form);
      setModal(false);
      cargar();
    } finally { setSaving(false); }
  };
  const eliminar = async (it) => {
    if (!window.confirm(`Eliminar "${it.titulo}"?`)) return;
    await api.delete(`/marco-legal/${it.id}/`);
    cargar();
  };

  if (loading) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando...</div>;
  return (
    <div>
      <div style={{ marginBottom: 12, textAlign: 'right' }}>
        <button className="admin-btn admin-btn-primary" onClick={abrirNuevo} type="button">
          <FaPlus /> Nuevo item
        </button>
      </div>
      <table className="admin-table">
        <thead><tr><th>Orden</th><th>Titulo</th><th>Norma</th><th>Activo</th><th className="text-right">Acciones</th></tr></thead>
        <tbody>
          {items.map(it => (
            <tr key={it.id}>
              <td>{it.orden}</td>
              <td className="font-semibold">{it.titulo}</td>
              <td className="text-mute">{it.norma}</td>
              <td>{it.activo ? <FaCheckCircle style={{ color: '#047857' }} /> : <FaTimes style={{ color: '#b91c1c' }} />}</td>
              <td className="actions justify-end">
                <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(it)}><FaEdit /> Editar</button>
                <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(it)}><FaTrash /></button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <AdminModal open={modal} title={edit ? 'Editar item' : 'Nuevo item de Marco Legal'} onClose={() => setModal(false)} size="lg"
        footer={<><button className="admin-btn" onClick={() => setModal(false)}>Cancelar</button>
        <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}><FaSave /> Guardar</button></>}>
        <form className="admin-form">
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="ml-titulo" className="admin-form-group__label admin-form-group__label--required">Titulo</label>
              <input id="ml-titulo" name="titulo" className="admin-input" required
                value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} />
            </div>
            <div className="admin-form-group">
              <label htmlFor="ml-norma" className="admin-form-group__label admin-form-group__label--required">Norma</label>
              <input id="ml-norma" name="norma" className="admin-input" required
                value={form.norma} onChange={(e) => setForm({ ...form, norma: e.target.value })} />
            </div>
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="ml-icono" className="admin-form-group__label">Icono (react-icons)</label>
              <select id="ml-icono" name="icono" className="admin-select"
                value={form.icono} onChange={(e) => setForm({ ...form, icono: e.target.value })}>
                <option>FaGavel</option><option>FaUserShield</option><option>FaUniversity</option>
                <option>FaShieldAlt</option><option>FaFileSignature</option><option>FaBalanceScale</option>
              </select>
            </div>
            <div className="admin-form-group">
              <label htmlFor="ml-orden" className="admin-form-group__label">Orden</label>
              <input id="ml-orden" name="orden" type="number" className="admin-input"
                value={form.orden} onChange={(e) => setForm({ ...form, orden: Number(e.target.value) || 0 })} />
            </div>
          </div>
          <div className="admin-form-group">
            <label htmlFor="ml-url" className="admin-form-group__label">URL externa (opcional)</label>
            <input id="ml-url" name="url_externa" type="url" className="admin-input"
              value={form.url_externa} onChange={(e) => setForm({ ...form, url_externa: e.target.value })} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="ml-desc" className="admin-form-group__label admin-form-group__label--required">Descripcion</label>
            <textarea id="ml-desc" name="descripcion" className="admin-textarea" required rows={4}
              value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          </div>
        </form>
      </AdminModal>
    </div>
  );
}

function PaginasLegalesTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [edit, setEdit] = useState(null);
  const [form, setForm] = useState({ titulo: '', contenido: '', resumen_corto: '', version: '1.0', activo: true });
  const [saving, setSaving] = useState(false);

  const cargar = () => {
    setLoading(true);
    api.get('/paginas-legales/').then((r) => {
      setItems(r.data.results || r.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };
  useEffect(cargar, []);

  const abrirEditar = async (it) => {
    const r = await api.get(`/paginas-legales/${it.slug}/`).catch(() => ({ data: it }));
    setEdit(r.data);
    setForm({
      titulo: r.data.titulo, contenido: r.data.contenido,
      resumen_corto: r.data.resumen_corto || '',
      version: r.data.version, activo: r.data.activo,
    });
    setModal(true);
  };

  const guardar = async () => {
    setSaving(true);
    try {
      await api.put(`/paginas-legales/${edit.slug}/`, form);
      setModal(false);
      cargar();
    } finally { setSaving(false); }
  };

  if (loading) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando...</div>;
  return (
    <div>
      <table className="admin-table">
        <thead><tr><th>Slug</th><th>Titulo</th><th>Version</th><th>Activo</th><th className="text-right">Acciones</th></tr></thead>
        <tbody>
          {items.map(it => (
            <tr key={it.id}>
              <td><code>/{it.slug}</code></td>
              <td className="font-semibold">{it.titulo}</td>
              <td>{it.version}</td>
              <td>{it.activo ? <FaCheckCircle style={{ color: '#047857' }} /> : <FaTimes style={{ color: '#b91c1c' }} />}</td>
              <td className="actions justify-end">
                <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(it)}><FaEdit /> Editar</button>
                <a className="admin-btn admin-btn-sm admin-btn-secondary" href={`/${it.slug}`} target="_blank" rel="noopener noreferrer">
                  <FaExternalLinkAlt /> Ver
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <AdminModal open={modal} title={`Editar ${edit?.slug}`} onClose={() => setModal(false)} size="xl"
        footer={<><button className="admin-btn" onClick={() => setModal(false)}>Cancelar</button>
        <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}><FaSave /> Guardar</button></>}>
        <form className="admin-form">
          <div className="admin-form-group">
            <label htmlFor="pl-titulo" className="admin-form-group__label">Titulo</label>
            <input id="pl-titulo" name="titulo" className="admin-input"
              value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="pl-resumen" className="admin-form-group__label">Resumen corto</label>
            <input id="pl-resumen" name="resumen_corto" className="admin-input"
              value={form.resumen_corto} onChange={(e) => setForm({ ...form, resumen_corto: e.target.value })} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="pl-contenido" className="admin-form-group__label">Contenido (HTML)</label>
            <textarea id="pl-contenido" name="contenido" className="admin-textarea" rows={20}
              value={form.contenido} onChange={(e) => setForm({ ...form, contenido: e.target.value })} />
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="pl-version" className="admin-form-group__label">Version</label>
              <input id="pl-version" name="version" className="admin-input"
                value={form.version} onChange={(e) => setForm({ ...form, version: e.target.value })} />
            </div>
            <div className="admin-form-group admin-form-group--check">
              <input id="pl-activo" name="activo" type="checkbox" className="admin-checkbox"
                checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} />
              <label htmlFor="pl-activo">Activo</label>
            </div>
          </div>
        </form>
      </AdminModal>
    </div>
  );
}

function HitosTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [edit, setEdit] = useState(null);
  const [form, setForm] = useState({ anio: '', titulo: '', descripcion: '', orden: 0, activo: true });
  const [saving, setSaving] = useState(false);

  const cargar = () => {
    setLoading(true);
    api.get('/hitos-historicos/').then((r) => {
      setItems(r.data.results || r.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };
  useEffect(cargar, []);

  const abrirNuevo = () => {
    setEdit(null);
    setForm({ anio: new Date().getFullYear(), titulo: '', descripcion: '', orden: 0, activo: true });
    setModal(true);
  };
  const abrirEditar = (it) => {
    setEdit(it);
    setForm({
      anio: it.anio || '', titulo: it.titulo,
      descripcion: it.descripcion || '',
      orden: it.orden, activo: it.activo,
    });
    setModal(true);
  };
  const guardar = async () => {
    setSaving(true);
    try {
      const data = { ...form, anio: form.anio ? Number(form.anio) : null };
      if (edit) await api.patch(`/hitos-historicos/${edit.id}/`, data);
      else await api.post('/hitos-historicos/', data);
      setModal(false); cargar();
    } finally { setSaving(false); }
  };
  const eliminar = async (it) => {
    if (!window.confirm(`Eliminar "${it.titulo}"?`)) return;
    await api.delete(`/hitos-historicos/${it.id}/`);
    cargar();
  };

  if (loading) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando...</div>;
  return (
    <div>
      <div style={{ marginBottom: 12, textAlign: 'right' }}>
        <button className="admin-btn admin-btn-primary" onClick={abrirNuevo} type="button">
          <FaPlus /> Nuevo hito
        </button>
      </div>
      <table className="admin-table">
        <thead><tr><th>Anio</th><th>Titulo</th><th>Orden</th><th>Activo</th><th className="text-right">Acciones</th></tr></thead>
        <tbody>
          {items.map(it => (
            <tr key={it.id}>
              <td className="font-semibold">{it.anio}</td>
              <td>{it.titulo}</td>
              <td>{it.orden}</td>
              <td>{it.activo ? <FaCheckCircle style={{ color: '#047857' }} /> : <FaTimes style={{ color: '#b91c1c' }} />}</td>
              <td className="actions justify-end">
                <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(it)}><FaEdit /></button>
                <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(it)}><FaTrash /></button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <AdminModal open={modal} title={edit ? 'Editar hito' : 'Nuevo hito'} onClose={() => setModal(false)} size="lg"
        footer={<><button className="admin-btn" onClick={() => setModal(false)}>Cancelar</button>
        <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}><FaSave /> Guardar</button></>}>
        <form className="admin-form">
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="hi-anio" className="admin-form-group__label">Anio</label>
              <input id="hi-anio" name="anio" type="number" className="admin-input"
                value={form.anio} onChange={(e) => setForm({ ...form, anio: e.target.value })} />
            </div>
            <div className="admin-form-group">
              <label htmlFor="hi-orden" className="admin-form-group__label">Orden</label>
              <input id="hi-orden" name="orden" type="number" className="admin-input"
                value={form.orden} onChange={(e) => setForm({ ...form, orden: Number(e.target.value) || 0 })} />
            </div>
          </div>
          <div className="admin-form-group">
            <label htmlFor="hi-titulo" className="admin-form-group__label admin-form-group__label--required">Titulo</label>
            <input id="hi-titulo" name="titulo" className="admin-input" required
              value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="hi-desc" className="admin-form-group__label">Descripcion</label>
            <textarea id="hi-desc" name="descripcion" className="admin-textarea" rows={3}
              value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          </div>
        </form>
      </AdminModal>
    </div>
  );
}

function GaleriaTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.get('/galeria/').then((r) => {
      setItems(r.data.results || r.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando...</div>;
  return (
    <div>
      <p className="text-mute" style={{ marginBottom: 12 }}>
        Para agregar imagenes a la galeria, usa el panel admin de Django:{' '}
        <a href="/admin/comunidad/galeriaimagen/" target="_blank" rel="noopener noreferrer">
          /admin/comunidad/galeriaimagen/ <FaExternalLinkAlt />
        </a>
      </p>
      <table className="admin-table">
        <thead><tr><th>Titulo</th><th>Categoria</th><th>Fecha</th><th>Imagen</th></tr></thead>
        <tbody>
          {items.map(it => (
            <tr key={it.id}>
              <td className="font-semibold">{it.titulo}</td>
              <td>{it.categoria_display || it.categoria}</td>
              <td>{it.fecha || '—'}</td>
              <td>
                {it.imagen_url ? (
                  <img src={it.imagen_url} alt={it.titulo} style={{ width: 60, height: 40, objectFit: 'cover', borderRadius: 4 }} />
                ) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

