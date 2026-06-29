import { useEffect, useState } from 'react';
import api from '../api';

/**
 * Hook para consumir los textos editables de las paginas internas
 * de /nosotros (Conocenos, MarcoLegal, Galeria, NuestraHistoria).
 *
 * El backend sirve estos textos en /api/v1/textos-seccion/?seccion=X
 * y opcionalmente &idioma=es-PE. La respuesta es una lista de objetos
 * { key, seccion, tipo, titulo, contenido, idioma, activo }.
 *
 * El mismo endpoint lo consume React y Spring Boot (misma fuente
 * de verdad).
 *
 * Ejemplo de uso:
 *   const { data: textos } = useTextosSeccion({ seccion: 'CONOCENOS_HERO' });
 *   const subtitulo = textos.find(t => t.key === 'conocenos.hero.subtitulo')?.contenido;
 */
export function useTextosSeccion({ seccion, idioma = 'es-PE' } = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (seccion) params.seccion = seccion;
    if (idioma) params.idioma = idioma;
    api.get('/textos-seccion/', { params })
      .then((r) => setData(r.data.results || r.data || []))
      .catch((e) => setError(e))
      .finally(() => setLoading(false));
  }, [seccion, idioma]);

  return { data, loading, error };
}

/**
 * Hook para consumir las categorias de la galeria.
 *
 * GET /api/v1/galerias/categorias/ -> lista de categorias activas.
 * Antes estaban hardcoded en Galeria.jsx, ahora se sirven desde la BD.
 */
export function useCategoriasGaleria() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.get('/galerias/categorias/')
      .then((r) => setData(Array.isArray(r.data) ? r.data : (r.data?.results || [])))
      .catch((e) => setError(e))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

export default useTextosSeccion;
