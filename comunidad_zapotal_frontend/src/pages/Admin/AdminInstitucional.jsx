// Admin consolidado para configuracion institucional y paginas legales.
//
// Tabs:
// 1. Configuracion - datos institucionales, contacto, ubicacion
// 2. Marco Legal - lista de items
// 3. Paginas Legales - Terminos, Privacidad, Cookies
// 4. Hitos Historicos
// 5. Galeria
// (Los mensajes de contacto se gestionan en /admin/contacto)
import React, { useEffect, useState, useMemo } from "react";
import {
  FaCog, FaBalanceScale, FaScroll, FaHistory, FaImages,
  FaPlus, FaEdit, FaTrash, FaSave, FaTimes,
  FaCheckCircle, FaSpinner, FaExternalLinkAlt,
  FaAlignLeft, FaTags,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import { useConfirm } from "../../components/Admin/AdminConfirmDialog";

const TABS = [
  { id: 'configuracion',     label: 'Configuracion',      icon: <FaCog /> },
  { id: 'textos',            label: 'Textos Internos',     icon: <FaAlignLeft /> },
  { id: 'categorias-galeria',label: 'Categorias Galeria',  icon: <FaTags /> },
  { id: 'marco-legal',       label: 'Marco Legal',         icon: <FaBalanceScale /> },
  { id: 'paginas-legales',   label: 'Paginas Legales',     icon: <FaScroll /> },
  { id: 'hitos',             label: 'Hitos Historicos',    icon: <FaHistory /> },
  { id: 'galeria',           label: 'Galeria',             icon: <FaImages /> },
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
            {tab === 'configuracion'   && <ConfiguracionTab />}
            {tab === 'textos'          && <TextosInternosTab />}
            {tab === 'categorias-galeria' && <CategoriasGaleriaTab />}
            {tab === 'marco-legal'      && <MarcoLegalTab />}
            {tab === 'paginas-legales'  && <PaginasLegalesTab />}
            {tab === 'hitos'            && <HitosTab />}
            {tab === 'galeria'          && <GaleriaTab />}
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

      <TextosHistoriaFieldset data={data} update={update} />
      <TextosConocenosFieldset data={data} update={update} />
      <MisionVisionValoresFieldset data={data} update={update} />
      <TextosMarcoLegalGaleriaFieldset data={data} update={update} />
      <TextosContactoFieldset data={data} update={update} />

      <div style={{ textAlign: 'right' }}>
        <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving} type="button">
          <FaSave /> {saving ? 'Guardando...' : 'Guardar configuracion'}
        </button>
      </div>
    </div>
  );
}

function TextosHistoriaFieldset({ data, update }) {
  return (
    <fieldset className="admin-form-section">
      <legend>Textos Historia</legend>
      <div className="admin-form-row">
        <div className="admin-form-group">
          <label htmlFor="cfg-historia-etiqueta" className="admin-form-group__label">Etiqueta superior</label>
          <input id="cfg-historia-etiqueta" name="historia_etiqueta" className="admin-input"
            value={data.historia_etiqueta || ''} onChange={(e) => update('historia_etiqueta', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-historia-hero-titulo" className="admin-form-group__label">Titulo del hero</label>
          <input id="cfg-historia-hero-titulo" name="historia_hero_titulo" className="admin-input"
            value={data.historia_hero_titulo || ''} onChange={(e) => update('historia_hero_titulo', e.target.value)} />
        </div>
      </div>
      <div className="admin-form-row">
        <div className="admin-form-group">
          <label htmlFor="cfg-historia-hero-subtitulo" className="admin-form-group__label">Subtitulo del hero (override de TextoSeccionInterna)</label>
          <input id="cfg-historia-hero-subtitulo" name="historia_hero_subtitulo" className="admin-input"
            value={data.historia_hero_subtitulo || ''} onChange={(e) => update('historia_hero_subtitulo', e.target.value)}
            placeholder="(vacio = usa TextoSeccionInterna 'historia.hero.subtitulo' o el eslogan)" />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-historia-seccion-titulo" className="admin-form-group__label">Titulo seccion contenido</label>
          <input id="cfg-historia-seccion-titulo" name="historia_seccion_titulo" className="admin-input"
            value={data.historia_seccion_titulo || ''} onChange={(e) => update('historia_seccion_titulo', e.target.value)} />
        </div>
      </div>
      <div className="admin-form-row">
        <div className="admin-form-group">
          <label htmlFor="cfg-historia-timeline-titulo" className="admin-form-group__label">Titulo timeline</label>
          <input id="cfg-historia-timeline-titulo" name="historia_timeline_titulo" className="admin-input"
            value={data.historia_timeline_titulo || ''} onChange={(e) => update('historia_timeline_titulo', e.target.value)} />
        </div>
      </div>
      <div className="admin-form-group">
        <label htmlFor="cfg-historia-html" className="admin-form-group__label">Historia (HTML)</label>
        <textarea id="cfg-historia-html" name="historia_html" className="admin-textarea" rows={14}
          value={data.historia_html || ''} onChange={(e) => update('historia_html', e.target.value)} />
        <div className="admin-form-hint">
          HTML/Markdown. Se sanitiza en backend (se eliminan &lt;script&gt;, on*=, javascript:).
          Tags permitidos: p, h1-h6, ul, ol, li, a, img, strong, em, blockquote, table, etc.
        </div>
      </div>
    </fieldset>
  );
}

function TextosConocenosFieldset({ data, update }) {
  return (
    <fieldset className="admin-form-section">
      <legend>Textos Conocenos</legend>
      <div className="admin-form-row">
        <div className="admin-form-group">
          <label htmlFor="cfg-conocenos-etiqueta" className="admin-form-group__label">Etiqueta superior</label>
          <input id="cfg-conocenos-etiqueta" name="conocenos_etiqueta" className="admin-input"
            value={data.conocenos_etiqueta || ''} onChange={(e) => update('conocenos_etiqueta', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-conocenos-hero-titulo" className="admin-form-group__label">Titulo del hero</label>
          <input id="cfg-conocenos-hero-titulo" name="conocenos_hero_titulo" className="admin-input"
            value={data.conocenos_hero_titulo || ''} onChange={(e) => update('conocenos_hero_titulo', e.target.value)} />
        </div>
      </div>
      <div className="admin-form-group">
        <label htmlFor="cfg-conocenos-hero-subtitulo" className="admin-form-group__label">Subtitulo del hero</label>
        <textarea id="cfg-conocenos-hero-subtitulo" name="conocenos_hero_subtitulo" className="admin-textarea" rows={2}
          value={data.conocenos_hero_subtitulo || ''} onChange={(e) => update('conocenos_hero_subtitulo', e.target.value)}
          placeholder="(vacio = usa TextoSeccionInterna 'conocenos.hero.subtitulo' o el eslogan)" />
      </div>
      <div className="admin-form-row">
        <div className="admin-form-group">
          <label htmlFor="cfg-conocenos-ubicacion-titulo" className="admin-form-group__label">Titulo ubicacion</label>
          <input id="cfg-conocenos-ubicacion-titulo" name="conocenos_ubicacion_titulo" className="admin-input"
            value={data.conocenos_ubicacion_titulo || ''} onChange={(e) => update('conocenos_ubicacion_titulo', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-conocenos-cta-titulo" className="admin-form-group__label">Titulo CTA final</label>
          <input id="cfg-conocenos-cta-titulo" name="conocenos_cta_titulo" className="admin-input"
            value={data.conocenos_cta_titulo || ''} onChange={(e) => update('conocenos_cta_titulo', e.target.value)} />
        </div>
      </div>
      <div className="admin-form-group">
        <label htmlFor="cfg-conocenos-cta-descripcion" className="admin-form-group__label">Descripcion CTA final</label>
        <textarea id="cfg-conocenos-cta-descripcion" name="conocenos_cta_descripcion" className="admin-textarea" rows={3}
          value={data.conocenos_cta_descripcion || ''} onChange={(e) => update('conocenos_cta_descripcion', e.target.value)} />
      </div>
    </fieldset>
  );
}

function MisionVisionValoresFieldset({ data, update }) {
  const valoresStr = useMemo(() => {
    if (Array.isArray(data.valores)) return JSON.stringify(data.valores, null, 2);
    return '[]';
  }, [data.valores]);
  const [valoresLocal, setValoresLocal] = useState(valoresStr);
  useEffect(() => setValoresLocal(valoresStr), [valoresStr]);

  const handleValoresChange = (raw) => {
    setValoresLocal(raw);
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        update('valores', parsed);
      }
    } catch {
      // Mantener string invalido en el textarea; no propagar al state hasta que sea valido.
    }
  };

  return (
    <fieldset className="admin-form-section">
      <legend>Mision / Vision / Valores</legend>
      <div className="admin-form-group">
        <label htmlFor="cfg-mision" className="admin-form-group__label">Mision</label>
        <textarea id="cfg-mision" name="mision" className="admin-textarea" rows={4}
          value={data.mision || ''} onChange={(e) => update('mision', e.target.value)} />
      </div>
      <div className="admin-form-group">
        <label htmlFor="cfg-vision" className="admin-form-group__label">Vision</label>
        <textarea id="cfg-vision" name="vision" className="admin-textarea" rows={4}
          value={data.vision || ''} onChange={(e) => update('vision', e.target.value)} />
      </div>
      <div className="admin-form-group">
        <label htmlFor="cfg-valores" className="admin-form-group__label">Valores (JSON array)</label>
        <textarea id="cfg-valores" name="valores" className="admin-textarea" rows={10} style={{ fontFamily: 'monospace', fontSize: 12 }}
          value={valoresLocal} onChange={(e) => handleValoresChange(e.target.value)} />
        <div className="admin-form-hint">
          Array de objetos {"{ nombre, descripcion, icono }"}. <code>icono</code> es un nombre de react-icons/fa (ej. <code>FaHandsHelping</code>).
          Si el JSON es invalido, no se guarda.
        </div>
      </div>
    </fieldset>
  );
}

function TextosMarcoLegalGaleriaFieldset({ data, update }) {
  return (
    <fieldset className="admin-form-section">
      <legend>Textos Marco Legal y Galeria</legend>
      <div className="admin-form-row">
        <div className="admin-form-group">
          <label htmlFor="cfg-marcolocal-titulo" className="admin-form-group__label">Marco Legal: titulo</label>
          <input id="cfg-marcolocal-titulo" name="marcolocal_titulo" className="admin-input"
            value={data.marcolocal_titulo || ''} onChange={(e) => update('marcolocal_titulo', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-marcolocal-subtitulo" className="admin-form-group__label">Marco Legal: subtitulo</label>
          <input id="cfg-marcolocal-subtitulo" name="marcolocal_subtitulo" className="admin-input"
            value={data.marcolocal_subtitulo || ''} onChange={(e) => update('marcolocal_subtitulo', e.target.value)} />
        </div>
      </div>
      <div className="admin-form-row">
        <div className="admin-form-group">
          <label htmlFor="cfg-galeria-titulo" className="admin-form-group__label">Galeria: titulo</label>
          <input id="cfg-galeria-titulo" name="galeria_titulo" className="admin-input"
            value={data.galeria_titulo || ''} onChange={(e) => update('galeria_titulo', e.target.value)} />
        </div>
        <div className="admin-form-group">
          <label htmlFor="cfg-galeria-subtitulo" className="admin-form-group__label">Galeria: subtitulo</label>
          <input id="cfg-galeria-subtitulo" name="galeria_subtitulo" className="admin-input"
            value={data.galeria_subtitulo || ''} onChange={(e) => update('galeria_subtitulo', e.target.value)} />
        </div>
      </div>
    </fieldset>
  );
}

function TextosContactoFieldset({ data, update }) {
  return (
    <fieldset className="admin-form-section">
      <legend>Textos Contacto (columna izquierda)</legend>
      <div className="admin-form-group">
        <label htmlFor="cfg-contacto-casa-comunal" className="admin-form-group__label">Casa Comunal: descripcion</label>
        <textarea id="cfg-contacto-casa-comunal" name="contacto_casa_comunal_descripcion" className="admin-textarea" rows={2}
          value={data.contacto_casa_comunal_descripcion || ''} onChange={(e) => update('contacto_casa_comunal_descripcion', e.target.value)} />
        <div className="admin-form-hint">Parrafo bajo el titulo "Casa Comunal" en /contacto.</div>
      </div>
      <div className="admin-form-group">
        <label htmlFor="cfg-contacto-denuncias" className="admin-form-group__label">Canal de Denuncias: descripcion</label>
        <textarea id="cfg-contacto-denuncias" name="contacto_denuncias_descripcion" className="admin-textarea" rows={3}
          value={data.contacto_denuncias_descripcion || ''} onChange={(e) => update('contacto_denuncias_descripcion', e.target.value)} />
        <div className="admin-form-hint">Parrafo bajo el titulo "Canal de Denuncias" en /contacto.</div>
      </div>
    </fieldset>
  );
}

function TextosInternosTab() {
  const { confirm, ConfirmDialog } = useConfirm();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [edit, setEdit] = useState(null);
  const [seccionFiltro, setSeccionFiltro] = useState('');
  const [form, setForm] = useState({
    key: '', seccion: 'CONOCENOS_HERO', tipo: 'TITULO',
    titulo: '', contenido: '', idioma: 'es-PE', activo: true,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const SECCIONES = [
    ['CONOCENOS_HERO',      'Conocenos - Hero'],
    ['CONOCENOS_MV',        'Conocenos - Mision y Vision'],
    ['CONOCENOS_UBICACION', 'Conocenos - Ubicacion'],
    ['CONOCENOS_CTA',       'Conocenos - CTA Final'],
    ['MARCOLOCAL_HERO',     'Marco Legal - Hero'],
    ['GALERIA_HERO',        'Galeria - Hero'],
    ['HISTORIA_HERO',       'Nuestra Historia - Hero'],
    ['HISTORIA_CONTENIDO',  'Nuestra Historia - Contenido'],
    ['HISTORIA_TIMELINE',   'Nuestra Historia - Timeline'],
    ['AUTORIDADES_COMITES', 'Autoridades - Comites Especializados'],
  ];

  const cargar = () => {
    setLoading(true);
    const params = seccionFiltro ? { seccion: seccionFiltro } : {};
    api.get('/textos-seccion-admin/', { params })
      .then((r) => setItems(extractList(r.data)))
      .catch(() => setError('No se pudieron cargar los textos.'))
      .finally(() => setLoading(false));
  };
  useEffect(cargar, [seccionFiltro]);

  const abrirNuevo = () => {
    setEdit(null);
    setForm({
      key: '', seccion: seccionFiltro || 'CONOCENOS_HERO', tipo: 'TITULO',
      titulo: '', contenido: '', idioma: 'es-PE', activo: true,
    });
    setError('');
    setModal(true);
  };
  const abrirEditar = (it) => {
    setEdit(it);
    setForm({
      key: it.key, seccion: it.seccion, tipo: it.tipo,
      titulo: it.titulo || '',
      contenido: it.contenido,
      idioma: it.idioma || 'es-PE', activo: it.activo !== false,
    });
    setError('');
    setModal(true);
  };
  const guardar = async () => {
    if (!form.key || !form.contenido) {
      setError('Key y Contenido son obligatorios.');
      return;
    }
    setSaving(true); setError('');
    try {
      if (edit) await api.patch(`/textos-seccion-admin/${edit.id}/`, form);
      else await api.post('/textos-seccion-admin/', form);
      setModal(false);
      cargar();
    } catch (err) {
      const d = err.response?.data;
      setError(typeof d === 'object' ? JSON.stringify(d) : (d?.detail || 'Error al guardar.'));
    } finally { setSaving(false); }
  };
  const eliminar = async (it) => {
    if (!await confirm({
      title: 'Eliminar texto',
      message: `Eliminar "${it.key}"? Esta accion no se puede deshacer.`,
    })) return;
    await api.delete(`/textos-seccion-admin/${it.id}/`);
    cargar();
  };

  if (loading) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando...</div>;
  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12, alignItems: 'center' }}>
        <label htmlFor="ti-seccion-filter" className="admin-form-group__label" style={{ marginBottom: 0 }}>Filtrar por seccion:</label>
        <select
          id="ti-seccion-filter"
          className="admin-select"
          value={seccionFiltro}
          onChange={(e) => setSeccionFiltro(e.target.value)}
          style={{ maxWidth: 320 }}
        >
          <option value="">Todas</option>
          {SECCIONES.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <div style={{ marginLeft: 'auto' }}>
          <button className="admin-btn admin-btn-primary" onClick={abrirNuevo} type="button">
            <FaPlus /> Nuevo texto
          </button>
        </div>
      </div>
      {error && <div className="admin-error">{error}</div>}
      <table className="admin-table">
        <thead>
          <tr>
            <th>Seccion</th>
            <th>Key</th>
            <th>Tipo</th>
            <th>Contenido (preview)</th>
            <th>Idioma</th>
            <th>Activo</th>
            <th className="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <tr><td colSpan={7} className="text-mute" style={{ textAlign: 'center' }}>No hay textos para esta seccion.</td></tr>
          ) : items.map(it => (
            <tr key={it.id}>
              <td><span className="admin-badge admin-badge--info">{it.seccion}</span></td>
              <td><code>{it.key}</code></td>
              <td>{it.tipo}</td>
              <td className="text-mute" style={{ maxWidth: 360 }}>
                {it.contenido.length > 100 ? it.contenido.slice(0, 100) + '...' : it.contenido}
              </td>
              <td className="text-mute">{it.idioma}</td>
              <td>{it.activo ? <FaCheckCircle style={{ color: '#047857' }} /> : <FaTimes style={{ color: '#b91c1c' }} />}</td>
              <td className="actions justify-end">
                <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(it)}><FaEdit /> Editar</button>
                <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(it)}><FaTrash /></button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <AdminModal open={modal} title={edit ? `Editar texto: ${edit.key}` : 'Nuevo texto'} onClose={() => setModal(false)} size="lg"
        footer={
          <>
            <button className="admin-btn" onClick={() => setModal(false)} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              <FaSave /> {saving ? 'Guardando...' : 'Guardar'}
            </button>
          </>
        }>
        <form className="admin-form" onSubmit={(e) => { e.preventDefault(); guardar(); }}>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="ti-seccion" className="admin-form-group__label admin-form-group__label--required">Seccion</label>
              <select id="ti-seccion" name="seccion" className="admin-select" required
                value={form.seccion} onChange={(e) => setForm({ ...form, seccion: e.target.value })}>
                {SECCIONES.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div className="admin-form-group">
              <label htmlFor="ti-key" className="admin-form-group__label admin-form-group__label--required">Key (slug)</label>
              <input id="ti-key" name="key" className="admin-input" required
                value={form.key} onChange={(e) => setForm({ ...form, key: e.target.value })}
                placeholder="ej. conocenos.hero.titulo" />
              <div className="admin-form-hint">Identificador unico. Combinar con idioma (es-PE) genera la unicidad.</div>
            </div>
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="ti-tipo" className="admin-form-group__label">Tipo</label>
              <select id="ti-tipo" name="tipo" className="admin-select"
                value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
                <option value="TITULO">Titulo</option>
                <option value="SUBTITULO">Subtitulo / descripcion</option>
                <option value="HTML">HTML libre</option>
                <option value="JSON">JSON estructurado</option>
              </select>
            </div>
            <div className="admin-form-group">
              <label htmlFor="ti-idioma" className="admin-form-group__label">Idioma</label>
              <input id="ti-idioma" name="idioma" className="admin-input"
                value={form.idioma} onChange={(e) => setForm({ ...form, idioma: e.target.value })} />
            </div>
          </div>
          <div className="admin-form-group">
            <label htmlFor="ti-titulo-admin" className="admin-form-group__label">Titulo descriptivo (solo admin)</label>
            <input id="ti-titulo-admin" name="titulo" className="admin-input"
              value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} />
          </div>
          <div className="admin-form-group">
            <label htmlFor="ti-contenido" className="admin-form-group__label admin-form-group__label--required">Contenido</label>
            <textarea id="ti-contenido" name="contenido" className="admin-textarea" required rows={6}
              value={form.contenido} onChange={(e) => setForm({ ...form, contenido: e.target.value })} />
          </div>
          <div className="admin-form-group admin-form-group--check">
            <input id="ti-activo" name="activo" type="checkbox" className="admin-checkbox"
              checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} />
            <label htmlFor="ti-activo">Activo (visible en sitio publico)</label>
          </div>
        </form>
      </AdminModal>
      {ConfirmDialog}
    </div>
  );
}

function CategoriasGaleriaTab() {
  const { confirm, ConfirmDialog } = useConfirm();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [edit, setEdit] = useState(null);
  const [form, setForm] = useState({ nombre: '', label: '', descripcion: '', orden: 0, activo: true });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const cargar = () => {
    setLoading(true);
    api.get('/galerias/categorias-admin/')
      .then((r) => setItems(extractList(r.data)))
      .catch(() => setError('No se pudieron cargar las categorias.'))
      .finally(() => setLoading(false));
  };
  useEffect(cargar, []);

  const abrirNuevo = () => {
    setEdit(null);
    setForm({ nombre: '', label: '', descripcion: '', orden: 0, activo: true });
    setError(''); setModal(true);
  };
  const abrirEditar = (it) => {
    setEdit(it);
    setForm({
      nombre: it.nombre, label: it.label, descripcion: it.descripcion || '',
      orden: it.orden || 0, activo: it.activo !== false,
    });
    setError(''); setModal(true);
  };
  const guardar = async () => {
    if (!form.nombre || !form.label) {
      setError('Nombre y Etiqueta son obligatorios.');
      return;
    }
    setSaving(true); setError('');
    try {
      if (edit) await api.patch(`/galerias/categorias-admin/${edit.id}/`, form);
      else await api.post('/galerias/categorias-admin/', form);
      setModal(false); cargar();
    } catch (err) {
      const d = err.response?.data;
      setError(typeof d === 'object' ? JSON.stringify(d) : (d?.detail || 'Error al guardar.'));
    } finally { setSaving(false); }
  };
  const eliminar = async (it) => {
    if (!await confirm({
      title: 'Eliminar categoria',
      message: `Eliminar "${it.label}"? Las imagenes asociadas no se borran, pero la categoria desaparece del sitio publico.`,
    })) return;
    await api.delete(`/galerias/categorias-admin/${it.id}/`);
    cargar();
  };

  if (loading) return <div className="admin-loading"><FaSpinner className="fa-spin" /> Cargando...</div>;
  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      <div style={{ marginBottom: 12, textAlign: 'right' }}>
        <button className="admin-btn admin-btn-primary" onClick={abrirNuevo} type="button">
          <FaPlus /> Nueva categoria
        </button>
      </div>
      <table className="admin-table">
        <thead>
          <tr>
            <th>Orden</th>
            <th>Nombre (slug)</th>
            <th>Etiqueta visible</th>
            <th>Descripcion</th>
            <th>Activo</th>
            <th className="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? (
            <tr><td colSpan={6} className="text-mute" style={{ textAlign: 'center' }}>No hay categorias.</td></tr>
          ) : items.map(it => (
            <tr key={it.id}>
              <td>{it.orden}</td>
              <td><code>{it.nombre}</code></td>
              <td className="font-semibold">{it.label}</td>
              <td className="text-mute" style={{ maxWidth: 360 }}>
                {it.descripcion ? (it.descripcion.length > 100 ? it.descripcion.slice(0, 100) + '...' : it.descripcion) : '—'}
              </td>
              <td>{it.activo ? <FaCheckCircle style={{ color: '#047857' }} /> : <FaTimes style={{ color: '#b91c1c' }} />}</td>
              <td className="actions justify-end">
                <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(it)}><FaEdit /> Editar</button>
                <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(it)}><FaTrash /></button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <AdminModal open={modal} title={edit ? `Editar categoria: ${edit.nombre}` : 'Nueva categoria'} onClose={() => setModal(false)}
        footer={
          <>
            <button className="admin-btn" onClick={() => setModal(false)} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              <FaSave /> {saving ? 'Guardando...' : 'Guardar'}
            </button>
          </>
        }>
        <form className="admin-form" onSubmit={(e) => { e.preventDefault(); guardar(); }}>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="cg-nombre" className="admin-form-group__label admin-form-group__label--required">Nombre (slug)</label>
              <input id="cg-nombre" name="nombre" className="admin-input" required
                value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value.toUpperCase() })}
                placeholder="ej. PATRIMONIO" />
              <div className="admin-form-hint">Mayusculas, sin espacios. Usado como clave en el filtro de galeria.</div>
            </div>
            <div className="admin-form-group">
              <label htmlFor="cg-label" className="admin-form-group__label admin-form-group__label--required">Etiqueta visible</label>
              <input id="cg-label" name="label" className="admin-input" required
                value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} />
            </div>
          </div>
          <div className="admin-form-group">
            <label htmlFor="cg-descripcion" className="admin-form-group__label">Descripcion</label>
            <textarea id="cg-descripcion" name="descripcion" className="admin-textarea" rows={2}
              value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label htmlFor="cg-orden" className="admin-form-group__label">Orden</label>
              <input id="cg-orden" name="orden" type="number" className="admin-input"
                value={form.orden} onChange={(e) => setForm({ ...form, orden: Number(e.target.value) || 0 })} />
            </div>
            <div className="admin-form-group admin-form-group--check" style={{ alignSelf: 'flex-end' }}>
              <input id="cg-activo" name="activo" type="checkbox" className="admin-checkbox"
                checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} />
              <label htmlFor="cg-activo">Activo (visible en sitio publico)</label>
            </div>
          </div>
        </form>
      </AdminModal>
      {ConfirmDialog}
    </div>
  );
}

function MarcoLegalTab() {
  const { confirm, ConfirmDialog } = useConfirm();
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
    if (!await confirm({
      title: "Eliminar item de Marco Legal",
      message: `Eliminar "${it.titulo}"? Esta acción no se puede deshacer.`,
    })) return;
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
      // PATCH (no PUT) para no requerir reenviar todos los campos del modelo.
      // El slug se mantiene del URL; los demas campos se actualizan parcialmente.
      await api.patch(`/paginas-legales/${edit.slug}/`, form);
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
  const { confirm, ConfirmDialog } = useConfirm();
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
    if (!await confirm({
      title: "Eliminar hito histórico",
      message: `Eliminar "${it.titulo}"? Esta acción no se puede deshacer.`,
    })) return;
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
      {ConfirmDialog}
    </div>
  );
}

function GaleriaTab() {
  const navigate = useNavigate();
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
      <div className="flex items-center justify-between mb-3">
        <p className="text-mute">Ultimas imagenes de la galeria.</p>
        <button className="admin-btn admin-btn-primary" onClick={() => navigate('/admin/galeria')}>
          <FaImages /> Gestion completa de galeria
        </button>
      </div>
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


