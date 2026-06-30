import React, { useEffect, useState, useCallback, useMemo } from "react";
import {
  FaUsers, FaUniversity, FaShieldAlt, FaCalendarAlt, FaPhone,
  FaEnvelope, FaFileSignature, FaVenus, FaMars, FaGenderless,
  FaSearch, FaArrowRight, FaIdCard, FaWhatsapp,
  FaClock, FaExclamationTriangle, FaSeedling, FaGavel,
  FaBalanceScale, FaUserTie, FaMapMarkerAlt, FaUserShield,
  FaScroll,
} from "react-icons/fa";
import api, { extractList } from "../../api";
import AutoridadDetalle from "../../components/Autoridades/AutoridadDetalle";
import useConfiguracion from "../../hooks/useConfiguracion";
import { useTextosSeccion } from "../../hooks/useTextosSeccion";
import PageLoader from "../../components/common/PageLoader/PageLoader";
import { useTaskLifecycle } from "../../context/LoaderContext";
import "./AutoridadesPage.css";

// Tabs en orden jerarquico: Centro Poblado > Directiva Comunal > Autoridad Politica
const NIVELES = [
  {
    id: "MUNICIPAL", key: "municipal",
    label: "Municipalidad del C.P.",
    icon: <FaUniversity />,
    desc: "Gobierno municipal del Centro Poblado, elegido por voto popular. Periodo: 4 anos.",
    dbField: "MUNICIPAL",
  },
  {
    id: "COMUNAL", key: "comunal",
    label: "Directiva Comunal",
    icon: <FaUsers />,
    desc: "Gobierno de la Comunidad Campesina, elegido por voto personal, libre, secreto y obligatorio. Periodo: 2 anos.",
    dbField: "COMUNAL",
  },
  {
    id: "POLITICO", key: "politico",
    label: "Autoridad Politica",
    icon: <FaShieldAlt />,
    desc: "Representante del Poder Ejecutivo en el Centro Poblado, designado por el Ministerio del Interior.",
    dbField: "POLITICO",
  },
];

const ICONOS_COMITE = {
  ELECTORAL: <FaGavel />,
  REVISOR_CUENTAS: <FaBalanceScale />,
  RONDAS: <FaUserShield />,
  GESTION: <FaSeedling />,
  OBRAS: <FaUserTie />,
  EDUCACION: <FaUserTie />,
  OTRO: <FaUsers />,
};

const SexoIcon = ({ sexo }) => {
  if (sexo === "F") return <FaVenus className="au-sexo au-sexo--femenino" />;
  if (sexo === "M") return <FaMars className="au-sexo au-sexo--masculino" />;
  return <FaGenderless className="au-sexo" />;
};

function Iniciales({ nombre, apellido }) {
  const inicial = (s) => (s && s[0] ? s[0].toUpperCase() : "");
  return (
    <span className="au-card-iniciales">
      {inicial(nombre)}{inicial(apellido)}
    </span>
  );
}

function whatsappLink(telefono) {
  if (!telefono) return null;
  const limpio = String(telefono).replace(/[^0-9]/g, "");
  return `https://wa.me/${limpio}`;
}

function Tarjeta({ autoridad, onClick }) {
  const cargo = autoridad.cargo;
  const esTradicional = autoridad.es_cargo_tradicional;
  const wa = whatsappLink(autoridad.telefono);
  const vencePronto = autoridad.tiempo_restante != null
    && autoridad.tiempo_restante > 0
    && autoridad.tiempo_restante <= 90;

  return (
    <button
      type="button"
      className="au-card h-full min-h-[100%]"
      onClick={() => onClick(autoridad)}
    >
      <div className="au-card-foto">
        {esTradicional && (
          <span className="au-card-cargo-tradicional" title="Cargo tradicional andino">
            <FaSeedling className="au-tradicional-icon" /> Tradicional
          </span>
        )}
        {autoridad.foto_url ? (
          <img src={autoridad.foto_url} alt={autoridad.nombre_completo || cargo} loading="lazy" />
        ) : (
          <div className="au-card-foto-placeholder">
            <Iniciales nombre={autoridad.nombres} apellido={autoridad.apellidos} />
          </div>
        )}
        <div className="au-card-cargo-badge">{cargo}</div>
      </div>
      <div className="au-card-body">
        <h3 className="au-card-nombre">
          {autoridad.nombre_completo || "Sin nombre"}
          <SexoIcon sexo={autoridad.sexo} />
        </h3>
        {autoridad.nombre_tradicional && (
          <p className="au-card-tradic" style={{ fontSize: 12, color: "var(--nb-dorado, #b8963e)", fontStyle: "italic" }}>
            {autoridad.nombre_tradicional}
          </p>
        )}
        {autoridad.dni && (
          <p className="au-card-dni">
            <FaIdCard /> DNI {autoridad.dni}
          </p>
        )}
        {autoridad.periodo && (
          <p className="au-card-periodo">
            <FaCalendarAlt /> {autoridad.periodo}
          </p>
        )}
        {vencePronto && (
          <p className="au-card-alerta">
            <FaExclamationTriangle /> Vence en {autoridad.tiempo_restante} dias
          </p>
        )}
        {wa && (
          <a
            href={wa}
            target="_blank"
            rel="noopener noreferrer"
            className="au-whatsapp"
            onClick={(e) => e.stopPropagation()}
          >
            <FaWhatsapp /> WhatsApp
          </a>
        )}
      </div>
      <div className="au-card-footer">
        <span>Ver detalle</span>
        <FaArrowRight />
      </div>
    </button>
  );
}

function CalendarioElectoral({ autoridades }) {
  const hoy = new Date();
  const futuras = (autoridades || [])
    .filter((a) => a.periodo_fin && new Date(a.periodo_fin) > hoy)
    .map((a) => ({ cargo: a.cargo, fin: new Date(a.periodo_fin), nivel: a.nivel_gobierno }))
    .sort((a, b) => a.fin - b.fin);

  const proxima = futuras[0];
  if (!proxima) return null;

  const dias = Math.ceil((proxima.fin - hoy) / (1000 * 60 * 60 * 24));
  const fmtFecha = (d) =>
    d.toLocaleDateString("es-PE", { day: "2-digit", month: "long", year: "numeric" });
  const nivelLabel = NIVELES.find((n) => n.dbField === proxima.nivel)?.label || proxima.nivel;

  return (
    <section
      className="au-calendario grid grid-cols-1 gap-5 lg:grid-cols-[minmax(0,1.5fr)_minmax(260px,0.9fr)] lg:items-center"
      aria-labelledby="calendario-title"
    >
      <div>
        <h2 id="calendario-title" className="au-calendario__title">
          <FaClock /> Calendario Electoral
        </h2>
        <div className="au-calendario__leyenda">
          <p>
            La Directiva Comunal se renueva cada <strong>2 anos</strong> y la
            Municipalidad del Centro Poblado cada <strong>4 anos</strong>.
            El Comite Electoral se elige a mas tardar el 15 de octubre.
          </p>
        </div>
      </div>
      <div className="au-calendario__proxima">
        <div className="au-calendario__dias-label">Proxima renovacion en</div>
        <div className="au-calendario__dias">{dias}</div>
        <div className="au-calendario__dias-label">dias</div>
        <div className="au-calendario__fecha">{fmtFecha(proxima.fin)}</div>
        <div className="mt-1 text-[13px] opacity-80">
          {proxima.cargo} ({nivelLabel})
        </div>
      </div>
    </section>
  );
}

function Comites({ comites }) {
  // Textos del header de la seccion "Comites Especializados" ahora son
  // editables desde el panel admin institucional (tab "Textos Internos",
  // seccion AUTORIDADES_COMITES). Si la BD esta vacia, fallback a los
  // textos canonicos originales.
  const { data: textosComites } = useTextosSeccion({ seccion: 'AUTORIDADES_COMITES' });
  const titulo = textosComites.find(t => t.key === 'autoridades.comites.titulo')?.contenido
    || 'Comites Especializados';
  const subtitulo = textosComites.find(t => t.key === 'autoridades.comites.subtitulo')?.contenido
    || 'Organo de gobierno comunal que incluye Comite Electoral, Comite Revisor de Cuentas y Rondas Campesinas.';

  if (!comites || comites.length === 0) return null;
  return (
    <section className="au-comites" aria-labelledby="comites-title">
      <h2 id="comites-title" className="au-comites__title">
        <FaGavel /> {titulo}
      </h2>
      <p className="au-comites__subtitle">
        {subtitulo}
      </p>
      <div className="au-comites__grid grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {comites.map((c) => (
          <div key={c.id} className="au-comite-card h-full">
            <div className="au-comite-card__header">
              <span className="au-comite-card__icon">
                {ICONOS_COMITE[c.tipo] || <FaUsers />}
              </span>
              <h3 className="au-comite-card__title">{c.nombre}</h3>
              <span className="au-comite-card__tipo">{c.tipo_display || c.tipo}</span>
            </div>
            {c.descripcion && (
              <p className="au-comite-card__descripcion">{c.descripcion}</p>
            )}
            <div className="au-comite-card__meta">
              {c.presidente_info && (
                <div><strong>Presidente:</strong> {c.presidente_info.cargo} - {c.presidente_info.nombre_completo || `DNI ${c.presidente_info.dni}`}</div>
              )}
              {c.fecha_constitucion && (
                <div><strong>Constituido:</strong> {new Date(c.fecha_constitucion).toLocaleDateString("es-PE")}</div>
              )}
              {c.tiempo_restante != null && c.tiempo_restante > 0 && (
                <div className={c.tiempo_restante < 90 ? "text-red-700" : "text-[color:var(--au-text-soft)]"}>
                  <strong>Vence en:</strong> {c.tiempo_restante} dias
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function AutoridadesPage() {
  const [niveles, setNiveles] = useState({});
  const [comites, setComites] = useState([]);
  const [loading, setLoading] = useState(true);

  useTaskLifecycle("autoridades:page", loading);
  const [tabActiva, setTabActiva] = useState("MUNICIPAL");
  const [busqueda, setBusqueda] = useState("");
  const [autoridadDetalle, setAutoridadDetalle] = useState(null);
  const { data: cfg } = useConfiguracion();

  const cargar = useCallback(async () => {
    setLoading(true);
    try {
      const [r1, r2] = await Promise.all([
        api.get("/autoridades/agrupadas/").catch(() => null),
        api.get("/comites-comunales/?page_size=20").catch(() => ({ data: { data: [] } })),
      ]);
      if (r1) setNiveles(r1.data.niveles || {});
      setComites(extractList(r2.data));
    } catch (e) {
      try {
        const r2 = await api.get("/autoridades/?page_size=200");
        const items = extractList(r2.data);
        const grouped = {};
        for (const a of items) {
          if (!a.activo) continue;
          (grouped[a.nivel_gobierno] = grouped[a.nivel_gobierno] || []).push(a);
        }
        setNiveles(grouped);
      } catch (_) { /* noop */ }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { cargar(); }, [cargar]);

  const listaActual = (niveles[tabActiva] || []).filter((a) => {
    if (!busqueda.trim()) return true;
    const q = busqueda.toLowerCase();
    return (a.nombre_completo || "").toLowerCase().includes(q)
        || (a.cargo || "").toLowerCase().includes(q)
        || (a.dni || "").includes(busqueda);
  });

  const nivelActivo = NIVELES.find((n) => n.id === tabActiva);
  const totalAutoridades = Object.values(niveles).reduce((acc, arr) => acc + arr.length, 0);
  const allAutoridades = Object.values(niveles).flat();

  return (
    <main className="au-page min-h-screen overflow-x-hidden">
      <section className="au-hero px-4 pb-24 pt-24 sm:px-6 sm:pb-28 sm:pt-28 lg:px-8 lg:pb-32 lg:pt-32">
        <div className="au-hero-overlay" />
        <div className="au-hero-content mx-auto max-w-6xl">
          <div className="au-hero-eyebrow max-w-max px-4 py-2 text-[11px] sm:text-xs">
            <FaUsers /> Gobierno de {cfg?.nombre_corto || 'la Comunidad'}
          </div>
          <h1 className="text-center font-display text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
            Nuestras Autoridades
          </h1>
          <p className="mx-auto mt-4 max-w-3xl text-pretty text-sm leading-7 sm:text-base lg:text-lg">
            {cfg?.eslogan ||
              'Conoce a los lideres que dirigen la comunidad. Tres niveles de gobierno elegidos democraticamente.'}
          </p>
          {cfg && (
            <p className="mt-2 inline-flex max-w-3xl items-center justify-center gap-2 text-center text-sm opacity-85">
              <FaMapMarkerAlt /> {cfg.direccion_casa_comunal}
            </p>
          )}
          <div className="au-hero-stats mt-8 grid grid-cols-2 gap-3 sm:gap-4 lg:mt-10 lg:grid-cols-3 xl:grid-cols-5">
            <div className="au-hero-stat min-w-0 px-4 py-4 sm:px-5 sm:py-5">
              <strong>{totalAutoridades}</strong>
              <span>Autoridades activas</span>
            </div>
            {NIVELES.map((n) => (
              <div key={n.id} className="au-hero-stat min-w-0 px-4 py-4 sm:px-5 sm:py-5">
                <strong>{(niveles[n.dbField] || []).length}</strong>
                <span>{n.label}</span>
              </div>
            ))}
            <div className="au-hero-stat min-w-0 px-4 py-4 sm:px-5 sm:py-5">
              <strong>{comites.length}</strong>
              <span>Comites</span>
            </div>
          </div>
        </div>
      </section>

      <div className="au-container relative z-[5] mx-auto -mt-10 max-w-[1200px] px-4 pb-16 sm:-mt-12 sm:px-6 lg:-mt-16 lg:px-8">
        <div
          className="au-tabs grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3"
          role="tablist"
          aria-label="Niveles de gobierno"
        >
          {NIVELES.map((n) => {
            const count = (niveles[n.dbField] || []).length;
            const activa = tabActiva === n.id;
            return (
              <button
                key={n.id}
                type="button"
                role="tab"
                aria-selected={activa}
                className={`au-tab min-w-0 justify-start text-left sm:justify-center sm:text-center ${activa ? "au-tab--active" : ""}`}
                onClick={() => { setTabActiva(n.id); setBusqueda(""); }}
              >
                <span className="au-tab-icon shrink-0">{n.icon}</span>
                <span className="au-tab-label min-w-0 flex-1 whitespace-normal leading-snug">{n.label}</span>
                <span className="au-tab-count shrink-0">{count}</span>
              </button>
            );
          })}
        </div>

        {nivelActivo && (
          <div className="au-nivel-info mt-6 rounded-xl px-4 py-4 sm:px-5 sm:py-5">
            <h2>
              {nivelActivo.icon} {nivelActivo.label}
            </h2>
            <p>{nivelActivo.desc}</p>
          </div>
        )}

        <div className="au-busqueda mb-6 mt-6">
          <FaSearch className="au-busqueda-icon" />
          <input
            id="au-busqueda-autoridad"
            name="busqueda_autoridad"
            type="text"
            placeholder="Buscar por nombre, cargo o DNI..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            aria-label="Buscar autoridad"
            autoComplete="off"
          />
        </div>

        {loading ? (
          <div className="au-loading rounded-2xl bg-white/70 px-4 py-12 sm:px-6">
            <PageLoader variant="section" mensaje="Cargando autoridades" />
          </div>
        ) : listaActual.length === 0 ? (
          <div className="au-empty rounded-2xl px-4 py-12 sm:px-6">
            <FaUsers className="au-empty-icon" />
            <p>No hay autoridades {busqueda ? "que coincidan con la busqueda" : `en ${nivelActivo?.label}`}.</p>
          </div>
        ) : (
          <div className="au-grid grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5 xl:grid-cols-3">
            {listaActual.map((a) => (
              <Tarjeta key={a.id} autoridad={a} onClick={setAutoridadDetalle} />
            ))}
          </div>
        )}

        <CalendarioElectoral autoridades={allAutoridades} />

        <Comites comites={comites} />

      </div>

      {autoridadDetalle && (
        <AutoridadDetalle
          autoridad={autoridadDetalle}
          onClose={() => setAutoridadDetalle(null)}
        />
      )}
    </main>
  );
}
