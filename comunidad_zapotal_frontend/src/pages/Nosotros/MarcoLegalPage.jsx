import React from "react";
import useMarcoLegal from "../../hooks/useMarcoLegal";
import useConfiguracion from "../../hooks/useConfiguracion";
import {
  FaBalanceScale, FaSpinner, FaExclamationTriangle,
  FaExternalLinkAlt, FaGavel, FaUserShield, FaUniversity,
  FaShieldAlt, FaFileSignature,
} from "react-icons/fa";
import "./MarcoLegalPage.css";

const ICONOS = {
  FaGavel, FaUserShield, FaUniversity, FaShieldAlt, FaFileSignature,
  FaBalanceScale,
};

export default function MarcoLegalPage() {
  const { data, loading, error } = useMarcoLegal();
  const { data: cfg } = useConfiguracion();

  // Textos que antes estaban hardcoded en el JSX. Ahora vienen de la
  // BD (ConfiguracionComunidad, campos marcolocal_*).
  const titulo = cfg?.marcolocal_titulo || 'Marco Legal';
  const subtitulo =
    cfg?.marcolocal_subtitulo
    || (cfg
      ? `Marco normativo que rige el funcionamiento de la ${cfg.nombre_oficial} y sus autoridades.`
      : 'Marco normativo que rige el funcionamiento de la Comunidad y sus autoridades.');

  if (loading) {
    return (
      <main className="ml-page">
        <div className="ml-loading"><FaSpinner className="ml-spin" /> Cargando...</div>
      </main>
    );
  }
  if (error) {
    return (
      <main className="ml-page">
        <div className="ml-error">
          <FaExclamationTriangle /> No se pudo cargar el marco legal.
        </div>
      </main>
    );
  }

  return (
    <main className="ml-page">
      <section className="ml-hero">
        <div className="ml-hero-content">
          <FaBalanceScale className="ml-hero-icon" />
          <h1>{titulo}</h1>
          <p>{subtitulo}</p>
        </div>
      </section>

      <div className="ml-container">
        <div className="ml-grid">
          {data.map((item) => {
            const Icon = ICONOS[item.icono] || FaBalanceScale;
            return (
              <article key={item.id} className="ml-card">
                <header className="ml-card__header">
                  <Icon className="ml-card__icon" />
                  <div>
                    <h2 className="ml-card__title">{item.titulo}</h2>
                    <p className="ml-card__norma">{item.norma}</p>
                  </div>
                </header>
                <p className="ml-card__descripcion">{item.descripcion}</p>
                {item.url_externa && (
                  <a
                    href={item.url_externa}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-card__link"
                  >
                    Ver texto oficial <FaExternalLinkAlt />
                  </a>
                )}
              </article>
            );
          })}
        </div>
      </div>
    </main>
  );
}
