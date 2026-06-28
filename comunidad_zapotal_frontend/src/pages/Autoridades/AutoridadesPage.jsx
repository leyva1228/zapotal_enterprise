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
    <button type="button" className="au-card" onClick={() => onClick(autoridad)}>
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
          <p className="au-card-tradic" style={{ fontSize: 12, color: "#b8972a", fontStyle: "italic" }}>
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
    <section className="au-calendario" aria-labelledby="calendario-title">
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
        <div style={{ fontSize: 13, marginTop: 4, opacity: 0.8 }}>
          {proxima.cargo} ({nivelLabel})
        </div>
      </div>
    </section>
  );
}

function Organigrama({ cfg }) {
  return (
    <section className="au-organigrama" aria-labelledby="organigrama-title">
      <h2 id="organigrama-title" className="au-comites__title">
        <FaUsers /> Estructura Organica
      </h2>
      <p className="au-comites__subtitle">
        Organizacion de los tres niveles de gobierno que coexisten en el ambito de la Comunidad.
      </p>
      <div className="au-organigrama__contenedor">
        <svg viewBox="0 0 800 380" xmlns="http://www.w3.org/2000/svg" role="img"
             aria-label={`Organigrama de ${cfg?.nombre_oficial || 'la Comunidad'}`}>
          <g>
            <rect x="280" y="20" width="240" height="50" rx="8" fill="#0a3d1f" />
            <text x="400" y="50" textAnchor="middle" fill="#fff" fontSize="14" fontWeight="700">
              Asamblea General
            </text>
            <text x="400" y="66" textAnchor="middle" fill="#fff" fontSize="10">
              (Todos los comuneros)
            </text>
          </g>
          <line x1="400" y1="70" x2="400" y2="95" stroke="#0a3d1f" strokeWidth="2" />
          <g>
            <rect x="40" y="100" width="200" height="80" rx="8" fill="#1a7a42" />
            <text x="140" y="125" textAnchor="middle" fill="#fff" fontSize="13" fontWeight="700">
              Directiva Comunal
            </text>
            <text x="140" y="145" textAnchor="middle" fill="#fff" fontSize="10">
              Presidente, Vice, Sec, Tes, Fis, Voc
            </text>
            <text x="140" y="162" textAnchor="middle" fill="#b8972a" fontSize="10" fontWeight="600">
              Periodo: 2 anos
            </text>
          </g>
          <line x1="140" y1="100" x2="140" y2="95" stroke="#0a3d1f" strokeWidth="2" />
          <line x1="400" y1="95" x2="400" y2="100" stroke="#0a3d1f" strokeWidth="2" />
          <g>
            <rect x="300" y="100" width="200" height="80" rx="8" fill="#0f5c2e" />
            <text x="400" y="125" textAnchor="middle" fill="#fff" fontSize="13" fontWeight="700">
              Comites Especializados
            </text>
            <text x="400" y="145" textAnchor="middle" fill="#fff" fontSize="10">
              Electoral · Revisor · Rondas
            </text>
            <text x="400" y="162" textAnchor="middle" fill="#b8972a" fontSize="10" fontWeight="600">
              Variable
            </text>
          </g>
          <line x1="400" y1="100" x2="400" y2="95" stroke="#0a3d1f" strokeWidth="2" />
          <g>
            <rect x="560" y="100" width="200" height="80" rx="8" fill="#1a7a42" />
            <text x="660" y="125" textAnchor="middle" fill="#fff" fontSize="13" fontWeight="700">
              Municipalidad C.P.
            </text>
            <text x="660" y="145" textAnchor="middle" fill="#fff" fontSize="10">
              Alcalde + 5 Regidores
            </text>
            <text x="660" y="162" textAnchor="middle" fill="#b8972a" fontSize="10" fontWeight="600">
              Periodo: 4 anos
            </text>
          </g>
          <line x1="660" y1="100" x2="660" y2="95" stroke="#0a3d1f" strokeWidth="2" />
          <line x1="400" y1="95" x2="660" y2="95" stroke="#0a3d1f" strokeWidth="2" />
          <line x1="400" y1="180" x2="400" y2="220" stroke="#0a3d1f" strokeWidth="2" />
          <g>
            <rect x="280" y="220" width="240" height="50" rx="8" fill="#b8972a" />
            <text x="400" y="245" textAnchor="middle" fill="#0a3d1f" fontSize="13" fontWeight="700">
              Autoridad Politica
            </text>
            <text x="400" y="262" textAnchor="middle" fill="#0a3d1f" fontSize="10">
              Teniente Gobernador (designado)
            </text>
          </g>
          <line x1="140" y1="180" x2="140" y2="220" stroke="#0a3d1f" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="400" y1="180" x2="400" y2="220" stroke="#0a3d1f" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="660" y1="180" x2="660" y2="220" stroke="#0a3d1f" strokeWidth="1" strokeDasharray="4 4" />
          <text x="400" y="350" textAnchor="middle" fill="#6b7c72" fontSize="10" fontStyle="italic">
            {cfg?.nombre_oficial || 'Comunidad'}
          </text>
        </svg>
      </div>
    </section>
  );
}

function Comites({ comites }) {
  if (!comites || comites.length === 0) return null;
  return (
    <section className="au-comites" aria-labelledby="comites-title">
      <h2 id="comites-title" className="au-comites__title">
        <FaGavel /> Comites Especializados
      </h2>
      <p className="au-comites__subtitle">
        Organo de gobierno comunal que incluye Comite Electoral,
        Comite Revisor de Cuentas y Rondas Campesinas.
      </p>
      <div className="au-comites__grid">
        {comites.map((c) => (
          <div key={c.id} className="au-comite-card">
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
                <div style={{ color: c.tiempo_restante < 90 ? "#b91c1c" : "var(--au-text-soft)" }}>
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
    <main className="au-page">
      <section className="au-hero">
        <div className="au-hero-overlay" />
        <div className="au-hero-content">
          <div className="au-hero-eyebrow">
            <FaUsers /> Gobierno de {cfg?.nombre_corto || 'la Comunidad'}
          </div>
          <h1>Nuestras Autoridades</h1>
          <p>
            {cfg?.eslogan ||
              'Conoce a los lideres que dirigen la comunidad. Tres niveles de gobierno elegidos democraticamente.'}
          </p>
          {cfg && (
            <p style={{ fontSize: 14, opacity: 0.85, marginTop: 8 }}>
              <FaMapMarkerAlt /> {cfg.direccion_casa_comunal}
            </p>
          )}
          <div className="au-hero-stats">
            <div className="au-hero-stat">
              <strong>{totalAutoridades}</strong>
              <span>Autoridades activas</span>
            </div>
            {NIVELES.map((n) => (
              <div key={n.id} className="au-hero-stat">
                <strong>{(niveles[n.dbField] || []).length}</strong>
                <span>{n.label}</span>
              </div>
            ))}
            <div className="au-hero-stat">
              <strong>{comites.length}</strong>
              <span>Comites</span>
            </div>
          </div>
        </div>
      </section>

      <div className="au-container">
        <CalendarioElectoral autoridades={allAutoridades} />

        <Organigrama cfg={cfg} />

        <div className="au-tabs" role="tablist" aria-label="Niveles de gobierno">
          {NIVELES.map((n) => {
            const count = (niveles[n.dbField] || []).length;
            const activa = tabActiva === n.id;
            return (
              <button
                key={n.id}
                type="button"
                role="tab"
                aria-selected={activa}
                className={`au-tab ${activa ? "au-tab--active" : ""}`}
                onClick={() => { setTabActiva(n.id); setBusqueda(""); }}
              >
                <span className="au-tab-icon">{n.icon}</span>
                <span className="au-tab-label">{n.label}</span>
                <span className="au-tab-count">{count}</span>
              </button>
            );
          })}
        </div>

        {nivelActivo && (
          <div className="au-nivel-info">
            <h2>
              {nivelActivo.icon} {nivelActivo.label}
            </h2>
            <p>{nivelActivo.desc}</p>
          </div>
        )}

        <div className="au-busqueda">
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
          <div className="au-loading">
            <PageLoader variant="section" mensaje="Cargando autoridades" />
          </div>
        ) : listaActual.length === 0 ? (
          <div className="au-empty">
            <FaUsers className="au-empty-icon" />
            <p>No hay autoridades {busqueda ? "que coincidan con la busqueda" : `en ${nivelActivo?.label}`}.</p>
          </div>
        ) : (
          <div className="au-grid">
            {listaActual.map((a) => (
              <Tarjeta key={a.id} autoridad={a} onClick={setAutoridadDetalle} />
            ))}
          </div>
        )}

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
