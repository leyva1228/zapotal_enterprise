import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { FaSearch, FaUserShield, FaNewspaper, FaCalendarAlt } from "react-icons/fa";
import { useSearchParams } from "react-router-dom";
import api, { extractList } from "../../api";
import PageLoader from "../../components/common/PageLoader/PageLoader";
import "./Buscar.css";

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export default function Buscar() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [q, setQ] = useState(searchParams.get('q') || '');
  const [tab, setTab] = useState('TODOS');
  const [results, setResults] = useState({ noticias: [], eventos: [], autoridades: [] });
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const debouncedQ = useDebounce(q, 300);

  const buscar = useCallback(async (query) => {
    if (!query || query.length < 3) {
      setResults({ noticias: [], eventos: [], autoridades: [] });
      setTotal(0);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const { data } = await api.get(`/buscar/?q=${encodeURIComponent(query)}`);
      setResults({
        noticias: data?.resultados?.noticias || [],
        eventos: data?.resultados?.eventos || [],
        autoridades: data?.resultados?.autoridades || [],
      });
      setTotal(data?.total || 0);
    } catch (e) {
      setError('No se pudo realizar la busqueda.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    buscar(debouncedQ);
    if (debouncedQ) setSearchParams({ q: debouncedQ });
    else setSearchParams({});
  }, [debouncedQ, buscar, setSearchParams]);

  const data = (() => {
    if (tab === 'NOTICIA') return { items: results.noticias, tipo: 'NOTICIA' };
    if (tab === 'EVENTO') return { items: results.eventos, tipo: 'EVENTO' };
    if (tab === 'AUTORIDAD') return { items: results.autoridades, tipo: 'AUTORIDAD' };
    return { items: [
      ...results.noticias.map((n) => ({ ...n, __tipo: 'NOTICIA' })),
      ...results.eventos.map((e) => ({ ...e, __tipo: 'EVENTO' })),
      ...results.autoridades.map((a) => ({ ...a, __tipo: 'AUTORIDAD' })),
    ], tipo: 'TODOS' };
  })();

  return (
    <div className="buscar-page">
      <section className="buscar-hero">
        <div className="buscar-hero-overlay" />
        <div className="buscar-hero-content">
          <h1>Busqueda</h1>
          <p>Encuentra noticias, eventos y autoridades de la comunidad.</p>
          <div className="buscar-searchbox">
            <FaSearch />
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Buscar por palabra clave (minimo 3 caracteres)..."
              autoFocus
            />
            {q && (
              <button type="button" className="buscar-searchbox__clear" onClick={() => setQ('')} title="Limpiar">
                x
              </button>
            )}
          </div>
          {q && q.length < 3 && (
            <div className="buscar-hint">Escribe al menos 3 caracteres para buscar.</div>
          )}
        </div>
      </section>

      <main className="buscar-container">
        {q && q.length >= 3 && (
          <>
            <div className="buscar-tabs">
              <button
                className={`buscar-tab ${tab === 'TODOS' ? 'buscar-tab--active' : ''}`}
                onClick={() => setTab('TODOS')}
              >
                Todos ({total})
              </button>
              <button
                className={`buscar-tab ${tab === 'NOTICIA' ? 'buscar-tab--active' : ''}`}
                onClick={() => setTab('NOTICIA')}
              >
                <FaNewspaper /> Noticias ({results.noticias.length})
              </button>
              <button
                className={`buscar-tab ${tab === 'EVENTO' ? 'buscar-tab--active' : ''}`}
                onClick={() => setTab('EVENTO')}
              >
                <FaCalendarAlt /> Eventos ({results.eventos.length})
              </button>
              <button
                className={`buscar-tab ${tab === 'AUTORIDAD' ? 'buscar-tab--active' : ''}`}
                onClick={() => setTab('AUTORIDAD')}
              >
                <FaUserShield /> Autoridades ({results.autoridades.length})
              </button>
            </div>

            {loading ? (
              <div className="buscar-loading">
                <PageLoader variant="section" mensaje="Buscando" />
              </div>
            ) : error ? (
              <div className="buscar-error">{error}</div>
            ) : data.items.length === 0 ? (
              <div className="buscar-empty">
                No se encontraron resultados para <strong>"{q}"</strong>.
              </div>
            ) : (
              <ul className="buscar-results">
                {data.items.map((it, i) => {
                  const tipo = it.__tipo || data.tipo;
                  if (tipo === 'NOTICIA') {
                    return (
                      <li key={`n-${it.id}`} className="buscar-item">
                        <span className="buscar-item__badge buscar-item__badge--noticia">Noticia</span>
                        <div className="buscar-item__body">
                          <Link to={`/noticias/${it.id}`} className="buscar-item__title">{it.titulo}</Link>
                          <div className="buscar-item__meta">
                            {it.categoria_nombre && <span>{it.categoria_nombre}</span>}
                            {it.fecha_publicacion && <span> {new Date(it.fecha_publicacion).toLocaleDateString('es-PE')}</span>}
                          </div>
                          {it.resumen && <p className="buscar-item__resumen">{it.resumen}</p>}
                        </div>
                      </li>
                    );
                  }
                  if (tipo === 'EVENTO') {
                    return (
                      <li key={`e-${it.id}`} className="buscar-item">
                        <span className="buscar-item__badge buscar-item__badge--evento">Evento</span>
                        <div className="buscar-item__body">
                          <Link to={`/eventos/${it.id}`} className="buscar-item__title">{it.titulo}</Link>
                          <div className="buscar-item__meta">
                            {it.lugar && <span>{it.lugar}</span>}
                            {it.fecha && <span> {new Date(it.fecha).toLocaleDateString('es-PE')}</span>}
                          </div>
                          {it.descripcion && <p className="buscar-item__resumen">{it.descripcion}</p>}
                        </div>
                      </li>
                    );
                  }
                  return (
                    <li key={`a-${it.id}`} className="buscar-item">
                      <span className="buscar-item__badge buscar-item__badge--autoridad">Autoridad</span>
                      <div className="buscar-item__body">
                        <div className="buscar-item__title">
                          {(it.comunero_info || `${it.comunero_nombres || ''} ${it.comunero_apellidos || ''}`.trim() || 'Autoridad')}
                        </div>
                        <div className="buscar-item__meta">
                          {it.cargo && <span>{it.cargo}</span>}
                          {it.periodo && <span> {it.periodo}</span>}
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </>
        )}

        {!q && (
          <div className="buscar-help">
            <h3>Como buscar</h3>
            <ul>
              <li>Escribe al menos 3 caracteres.</li>
              <li>La busqueda es parcial: encuentra palabras que contengan tu texto.</li>
              <li>Los resultados se actualizan automaticamente.</li>
              <li>Puedes filtrar por tipo: Noticias, Eventos o Autoridades.</li>
            </ul>
          </div>
        )}
      </main>
    </div>
  );
}
