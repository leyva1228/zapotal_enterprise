import { useEffect, useState } from 'react';
import api from '../api';

export function usePaginaLegal(slug) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    api.get(`/paginas-legales/${slug}/`)
      .then((r) => setData(r.data))
      .catch((e) => setError(e))
      .finally(() => setLoading(false));
  }, [slug]);

  return { data, loading, error };
}

export default usePaginaLegal;
