import { useEffect, useState } from 'react';
import api from '../api';

let cache = null;
let cachePromise = null;
let cacheTimestamp = 0;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutos

/**
 * Hook que retorna el email destino activo para el formulario publico.
 * Usa el endpoint /api/v1/public/email-contacto/ que aplica el override
 * settings.EMAIL_DESTINO_TEMPORAL del backend.
 *
 * Cachea en memoria por 5 minutos para evitar requests repetidos.
 */
export default function useEmailDestino() {
  const fallback = 'john.leyva@tecsup.edu.pe';
  const [email, setEmail] = useState(cache?.email_contacto || fallback);

  useEffect(() => {
    if (cache && Date.now() - cacheTimestamp < CACHE_TTL_MS) {
      setEmail(cache.email_contacto || fallback);
      return;
    }
    if (cachePromise) {
      cachePromise.then((data) => setEmail(data?.email_contacto || fallback));
      return;
    }
    cachePromise = api.get('/public/email-contacto/')
      .then((r) => {
        cache = r.data;
        cacheTimestamp = Date.now();
        setEmail(r.data?.email_contacto || fallback);
        return r.data;
      })
      .catch(() => {
        setEmail(fallback);
        return null;
      })
      .finally(() => {
        cachePromise = null;
      });
  }, []);

  return {
    email_contacto: email,
    fallback,
  };
}
