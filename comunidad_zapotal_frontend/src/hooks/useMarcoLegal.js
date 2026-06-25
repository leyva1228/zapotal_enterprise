import { useEffect, useState } from 'react';
import api from '../api';

export function useMarcoLegal() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.get('/marco-legal/')
      .then((r) => setData(r.data.results || r.data || []))
      .catch((e) => setError(e))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

export default useMarcoLegal;
