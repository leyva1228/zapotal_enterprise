/**
 * useUrlFilters - Hook para leer/escribir filtros en la URL (?key=value).
 *
 * Sincroniza el estado de los filtros con los query params de la URL,
 * permitiendo:
 * - Recargar la pagina preservando el filtro.
 * - Compartir el link con el filtro aplicado.
 * - Botones "atras/adelante" del navegador preservan el filtro.
 *
 * @param {Object} schema - { nombreParam: { defaultValue, parser } }
 *   parser: (string) => parsed value (e.g. parseIntParam).
 *
 * @returns {[filters, setFilters]}
 *   filters: objeto con valores parseados.
 *   setFilters: (partial) => void  (merge con URL actual, replace).
 *
 * @example
 *   const [filters, setFilters] = useUrlFilters({
 *     estado: { defaultValue: "" },
 *     search: { defaultValue: "" },
 *     page: { defaultValue: 1, parser: parseIntParam },
 *   });
 *   // filters = { estado: "ACTIVO", search: "juan", page: 1 }
 *   setFilters({ estado: "BLOQUEADO" });
 *   // URL = ?estado=BLOQUEADO (search/page se mantienen si estaban)
 */
import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";

export const parseIntParam = (v) => {
  const n = parseInt(v, 10);
  return Number.isFinite(n) && n > 0 ? n : 1;
};

export const parseBoolParam = (v) => {
  if (v === "true" || v === "1") return true;
  if (v === "false" || v === "0") return false;
  return null;
};

export function useUrlFilters(schema) {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo(() => {
    const result = {};
    for (const [key, def] of Object.entries(schema)) {
      const raw = searchParams.get(key);
      if (raw === null || raw === "") {
        result[key] = def.defaultValue;
      } else if (def.parser) {
        try {
          result[key] = def.parser(raw);
        } catch {
          result[key] = def.defaultValue;
        }
      } else {
        result[key] = raw;
      }
    }
    return result;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const setFilters = useCallback(
    (partial) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          for (const [key, value] of Object.entries(partial)) {
            if (
              value === "" ||
              value === null ||
              value === undefined ||
              (typeof value === "number" && Number.isNaN(value))
            ) {
              next.delete(key);
            } else {
              next.set(key, String(value));
            }
          }
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  const clearFilters = useCallback(
    (keysToKeep = []) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams();
          for (const key of keysToKeep) {
            const v = prev.get(key);
            if (v !== null) next.set(key, v);
          }
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  return [filters, setFilters, clearFilters];
}
