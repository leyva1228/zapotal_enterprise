import { useMemo } from "react";

/**
 * Genera (o reutiliza) un identificador anonimo estable por navegador.
 *
 * - SIEMPRE devuelve un ID valido (incluso si localStorage falla o
 *   esta bloqueado por modo privado del browser). Si no se puede
 *   persistir, se genera un ID temporal para esta sesion; el
 *   contador de vistas seguira funcionando aunque no sobreviva
 *   al refresh.
 * - Persiste en `localStorage` bajo la clave `zapotal_anon_id` cuando
 *   es posible, asi sobrevive a recargas y cierres de browser.
 * - Se usa como discriminador "quien vio" para usuarios no logueados
 *   en el contador de visualizaciones de noticias y eventos.
 * - Si el usuario se loguea despues, su `userId` toma precedencia;
 *   si luego se desloguea, este `anonId` sigue siendo el mismo
 *   (mientras localStorage funcione) para que las claves en
 *   `localStorage` sean estables y no se rompa la regla de
 *   "ya vio esta noticia".
 */
function _generarAnonId() {
  // crypto.randomUUID() esta disponible en browsers modernos.
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    try { return crypto.randomUUID(); } catch (e) { /* noop */ }
  }
  // Fallback: random + timestamp.
  return "anon-" + Math.random().toString(36).slice(2) + "-" + Date.now().toString(36);
}

const STORAGE_KEY = "zapotal_anon_id";

function _obtenerOGenerarId() {
  if (typeof window === "undefined") return null;
  // 1) Intentar leer de localStorage.
  try {
    const id = window.localStorage?.getItem(STORAGE_KEY);
    if (id) return id;
  } catch (e) { /* noop */ }
  // 2) Generar uno nuevo.
  const nuevo = _generarAnonId();
  // 3) Intentar persistir.
  try { window.localStorage?.setItem(STORAGE_KEY, nuevo); } catch (e) { /* noop */ }
  return nuevo;
}

export function useAnonymousId() {
  // useMemo con [] garantiza que el ID sea estable durante toda la
  // vida del componente (no cambia entre renders). Si por algun
  // motivo el primer compute devuelve null, NO se reintenta: el
  // caller debe manejar ese caso (logueado o saltar el conteo).
  return useMemo(() => _obtenerOGenerarId(), []);
}

export default useAnonymousId;
