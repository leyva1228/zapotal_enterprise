import { useEffect, useState } from 'react';
import api from '../api';

export function useGaleria(categoria = null) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    const params = categoria ? { categoria } : {};
    api.get('/galeria/', { params })
      .then((r) => setData(r.data.results || r.data || []))
      .catch((e) => setError(e))
      .finally(() => setLoading(false));
  }, [categoria]);

  return { data, loading, error };
}

export default useGaleria;
