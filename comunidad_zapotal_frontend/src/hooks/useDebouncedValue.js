/**
 * useDebouncedValue - Hook para retrasar la actualizacion de un valor.
 *
 * Util para campos de busqueda: no dispara fetch en cada keystroke,
 * solo cuando el usuario deja de tipear por `delayMs` milisegundos.
 *
 * @param {*} value - Valor a "retrasar".
 * @param {number} delayMs - Tiempo de espera en ms (default 300).
 * @returns {*} - El valor debounced (retrasado).
 *
 * @example
 *   const [search, setSearch] = useState("");
 *   const debouncedSearch = useDebouncedValue(search, 300);
 *   useEffect(() => { cargar(debouncedSearch); }, [debouncedSearch]);
 */
import { useEffect, useState } from "react";

export function useDebouncedValue(value, delayMs = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(t);
  }, [value, delayMs]);

  return debounced;
}
