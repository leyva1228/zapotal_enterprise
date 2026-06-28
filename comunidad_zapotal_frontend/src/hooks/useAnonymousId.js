import { useMemo } from "react";

/**
 * Genera (o reutiliza) un identificador anonimo estable por navegador.
 *
 * - Persiste en `localStorage` bajo la clave `zapotal_anon_id`, asi que
 *   sobrevive a recargas y cierres de browser.
 * - Se usa como discriminador "quien vio" para usuarios no logueados
 *   en el contador de visualizaciones de noticias y eventos.
 * - Si el usuario se loguea despues, su `userId` toma precedencia;
 *   si luego se desloguea, este `anonId` sigue siendo el mismo
 *   para que las claves en `localStorage` sean estables y no
 *   se rompa la regla de "ya vio esta noticia".
 *
 * Retorna `null` en SSR (sin `window`).
 */
function _generarAnonId() {
  // crypto.randomUUID() esta disponible en browsers modernos.
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Fallback para browsers antiguos.
  return "anon-" + Math.random().toString(36).slice(2) + "-" + Date.now().toString(36);
}

export function useAnonymousId() {
  return useMemo(() => {
    if (typeof window === "undefined" || !window.localStorage) return null;
    const STORAGE_KEY = "zapotal_anon_id";
    try {
      let id = window.localStorage.getItem(STORAGE_KEY);
      if (!id) {
        id = _generarAnonId();
        window.localStorage.setItem(STORAGE_KEY, id);
      }
      return id;
    } catch (e) {
      // Modo privado de iOS, localStorage bloqueado, etc.
      return null;
    }
  }, []);
}

export default useAnonymousId;
