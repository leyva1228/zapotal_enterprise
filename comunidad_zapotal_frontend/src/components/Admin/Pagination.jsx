import React from "react";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa";

/**
 * Pagination - Paginacion reutilizable para el panel admin.
 *
 * Props:
 *   - page: numero de pagina actual (1-based).
 *   - totalPages: total de paginas.
 *   - totalItems: total de items (para mostrar "X items").
 *   - onPageChange: (newPage) => void.
 *   - pageSize: tamano de pagina (opcional, para mostrar).
 *
 * Si totalPages <= 1, retorna null (no muestra controles).
 *
 * @example
 *   <Pagination
 *     page={filters.page}
 *     totalPages={Math.ceil(totalItems / 20)}
 *     totalItems={totalItems}
 *     onPageChange={(p) => setFilters({ page: p })}
 *   />
 */
export default function Pagination({
  page = 1,
  totalPages = 1,
  totalItems = 0,
  pageSize = 20,
  onPageChange,
}) {
  if (!onPageChange || totalPages <= 1) {
    if (totalItems > 0) {
      return (
        <div className="admin-pagination">
          <span className="admin-pagination__info">
            {totalItems} item{totalItems !== 1 ? "s" : ""}
          </span>
        </div>
      );
    }
    return null;
  }

  return (
    <div className="admin-pagination">
      <span className="admin-pagination__info">
        {totalItems} item{totalItems !== 1 ? "s" : ""} | Pagina {page} de {totalPages}
      </span>
      <div className="admin-pagination__buttons">
        <button
          type="button"
          className="admin-btn admin-btn-sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          aria-label="Pagina anterior"
        >
          <FaChevronLeft /> Anterior
        </button>
        <button
          type="button"
          className="admin-btn admin-btn-sm"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          aria-label="Pagina siguiente"
        >
          Siguiente <FaChevronRight />
        </button>
      </div>
    </div>
  );
}
