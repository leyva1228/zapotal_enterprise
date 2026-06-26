import { useEffect } from "react";

/**
 * useAdminRefresh - Escucha el evento `admin:refresh` disparado por el
 * boton Refresh del header del AdminLayout.
 *
 * El header (en AdminLayout.jsx) dispara `window.dispatchEvent(new CustomEvent('admin:refresh'))`
 * cuando el admin hace click en el icono de refresh.
 *
 * Este hook se monta en cada pagina admin y, al recibir el evento, invoca
 * el callback `onRefresh` que la pagina le pasa (tipicamente su funcion
 * `cargar()` que recarga la data del backend).
 *
 * @param {Function} onRefresh - callback a invocar cuando se dispara el evento.
 *
 * @example
 *   useAdminRefresh(cargar);
 */
export default function useAdminRefresh(onRefresh) {
  useEffect(() => {
    if (typeof onRefresh !== "function") return undefined;
    const handler = () => {
      try {
        onRefresh();
      } catch (e) {
        // No romper la app si el callback falla
        console.warn("useAdminRefresh callback error:", e);
      }
    };
    window.addEventListener("admin:refresh", handler);
    return () => window.removeEventListener("admin:refresh", handler);
  }, [onRefresh]);
}
