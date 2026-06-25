import { useEffect, useState } from 'react';
import api from '../api';

export function useHitosHistoricos() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.get('/hitos-historicos/')
      .then((r) => setData(r.data.results || r.data || []))
      .catch((e) => setError(e))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

export default useHitosHistoricos;
