import { useEffect, useState } from 'react';
import api from '../api';

/**
 * Hook para consumir la ConfiguracionComunidad (singleton).
 * Cache en memoria: una sola llamada por sesion.
 */
let cache = null;
let pendingPromise = null;

export function useConfiguracion() {
  const [data, setData] = useState(cache);
  const [loading, setLoading] = useState(!cache);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (cache) {
      setData(cache);
      setLoading(false);
      return;
    }
    if (pendingPromise) {
      pendingPromise.then((d) => {
        cache = d;
        setData(d);
        setLoading(false);
      }).catch((e) => {
        setError(e);
        setLoading(false);
      });
      return;
    }
    setLoading(true);
    pendingPromise = api.get('/configuracion/')
      .then((r) => r.data)
      .then((d) => {
        cache = d;
        setData(d);
        return d;
      })
      .catch((e) => {
        setError(e);
        throw e;
      })
      .finally(() => {
        pendingPromise = null;
        setLoading(false);
      });
  }, []);

  return { data, loading, error, refresh: () => { cache = null; setData(null); setLoading(true); } };
}

export default useConfiguracion;
