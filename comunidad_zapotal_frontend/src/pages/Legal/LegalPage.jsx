import usePaginaLegal from "../../hooks/usePaginaLegal";
import { FaSpinner, FaExclamationTriangle, FaCalendarAlt, FaCode } from "react-icons/fa";
import "./LegalPage.css";

export default function LegalPage({ slug }) {
  const { data, loading, error } = usePaginaLegal(slug);

  if (loading) {
    return (
      <main className="legal-page">
        <div className="legal-loading"><FaSpinner className="legal-spin" /> Cargando...</div>
      </main>
    );
  }
  if (error || !data) {
    return (
      <main className="legal-page">
        <div className="legal-error">
          <FaExclamationTriangle /> No se pudo cargar la pagina legal.
        </div>
      </main>
    );
  }

  return (
    <main className="legal-page">
      <section className="legal-hero">
        <div className="legal-hero__overlay" />
        <div className="legal-hero-content">
          <h1>{data.titulo}</h1>
          {data.resumen_corto && <p>{data.resumen_corto}</p>}
          <div className="legal-hero-meta">
            <span><FaCalendarAlt /> Vigente desde {new Date(data.fecha_vigencia).toLocaleDateString("es-PE")}</span>
            <span><FaCode /> Version {data.version}</span>
          </div>
        </div>
      </section>
      <div className="legal-container">
        <article
          className="legal-content"
          dangerouslySetInnerHTML={{ __html: data.contenido }}
        />
        <footer className="legal-footer">
          <small>
            Ultima actualizacion: {new Date(data.fecha_actualizacion).toLocaleString("es-PE")}
          </small>
        </footer>
      </div>
    </main>
  );
}
