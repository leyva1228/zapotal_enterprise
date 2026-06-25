import React from "react";
import { FaSearch, FaTimes } from "react-icons/fa";

/**
 * FiltersBar - Barra de filtros reutilizable para el panel admin.
 *
 * Props:
 *   - filters: objeto con valores actuales (de useUrlFilters).
 *   - setFilters: (partial) => void (de useUrlFilters).
 *   - clearFilters: (keysToKeep?) => void (opcional, de useUrlFilters).
 *   - chips: [{ key, label, value, count? }] - chips/segmented control.
 *           Si el chip tiene `count`, se muestra "(N)".
 *           El value "" representa "Todos" (sin filtro).
 *   - searchKey: nombre del param de busqueda (default "search").
 *   - searchPlaceholder: string.
 *   - extra: ReactNode (filtros adicionales, ej. selects, fechas).
 *
 * @example
 *   const [filters, setFilters, clearFilters] = useUrlFilters({
 *     estado: { defaultValue: "" },
 *     search: { defaultValue: "" },
 *   });
 *   <FiltersBar
 *     filters={filters}
 *     setFilters={setFilters}
 *     clearFilters={clearFilters}
 *     chips={[
 *       { key: "estado", value: "", label: "Todos" },
 *       { key: "estado", value: "ACTIVO", label: "Activos", count: 42 },
 *       { key: "estado", value: "BLOQUEADO", label: "Bloqueados", count: 3 },
 *     ]}
 *     searchKey="search"
 *     searchPlaceholder="Buscar por email o nombre..."
 *   />
 */
export default function FiltersBar({
  filters = {},
  setFilters,
  clearFilters,
  chips = [],
  searchKey = "search",
  searchPlaceholder = "Buscar...",
  extra = null,
  hasActiveFilters = null,
}) {
  const activeSearch = filters[searchKey] || "";
  const hayFiltrosActivos =
    typeof hasActiveFilters === "function"
      ? hasActiveFilters(filters)
      : Object.entries(filters).some(
          ([key, value]) =>
            key !== "page" &&
            value !== "" &&
            value !== null &&
            value !== undefined &&
            !(Array.isArray(value) && value.length === 0)
        );

  return (
    <div className="admin-filters-bar">
      {chips.length > 0 && (
        <div className="admin-filters-bar__chips">
          {chips.map((c, idx) => {
            const isActive =
              (filters[c.key] || "") === (c.value || "");
            return (
              <button
                key={`${c.key}-${c.value || "__all__"}-${idx}`}
                type="button"
                className={`admin-chip ${isActive ? "admin-chip--active" : ""}`}
                onClick={() => setFilters({ [c.key]: c.value, page: 1 })}
                title={c.title || c.label}
              >
                {c.label}
                {typeof c.count === "number" && (
                  <span className="admin-chip__count"> ({c.count})</span>
                )}
              </button>
            );
          })}
        </div>
      )}
      <div className="admin-filters-bar__search">
        <FaSearch className="admin-filters-bar__icon" aria-hidden="true" />
        <input
          type="text"
          className="admin-input"
          placeholder={searchPlaceholder}
          value={activeSearch}
          onChange={(e) => setFilters({ [searchKey]: e.target.value, page: 1 })}
          aria-label={searchPlaceholder}
        />
        {activeSearch && (
          <button
            type="button"
            className="admin-filters-bar__clear"
            onClick={() => setFilters({ [searchKey]: "", page: 1 })}
            aria-label="Limpiar busqueda"
          >
            <FaTimes />
          </button>
        )}
      </div>
      {extra}
      {hayFiltrosActivos && clearFilters && (
        <button
          type="button"
          className="admin-btn admin-btn-sm admin-btn-secondary"
          onClick={() => clearFilters()}
        >
          <FaTimes /> Limpiar filtros
        </button>
      )}
    </div>
  );
}
