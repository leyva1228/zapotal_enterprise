/**
 * useResizableSidebar - Hook para gestionar el ancho del sidebar admin
 * con soporte de drag y auto-hide.
 *
 * Comportamiento:
 * - El usuario arrastra el borde derecho del sidebar para ajustar el ancho.
 * - Si arrastra muy a la izquierda (<AUTO_HIDE_THRESHOLD), el sidebar
 *   se oculta completamente (modo collapsed).
 * - El ancho y el estado collapsed se persisten en localStorage
 *   para que sobrevivan reloads.
 * - El ancho esta acotado entre MIN_WIDTH y un maximo proporcional
 *   al ancho de la ventana (3/4 de la mitad = 50%).
 *
 * @returns {Object} estado y handlers del sidebar.
 *   - width: ancho actual en pixeles (cuando no esta colapsado).
 *   - isCollapsed: true si el sidebar esta oculto.
 *   - isDragging: true mientras el usuario arrastra.
 *   - sidebarRef: ref para asignar al <aside>.
 *   - dragHandleProps: { onMouseDown } para asignar al handle.
 *   - toggleCollapsed: funcion para mostrar/ocultar.
 */
import { useState, useEffect, useRef, useCallback } from "react";

const DEFAULT_WIDTH = 250;
const MIN_WIDTH = 240;
const MAX_WIDTH = 480;
const AUTO_HIDE_THRESHOLD = 60;
const STORAGE_KEY_WIDTH = "admin-sidebar-width";
const STORAGE_KEY_COLLAPSED = "admin-sidebar-collapsed";

export function useResizableSidebar() {
  const [width, setWidth] = useState(DEFAULT_WIDTH);
  const [isDragging, setIsDragging] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(0);
  const sidebarRef = useRef(null);

  const onMouseDown = useCallback((e) => {
    if (e.button !== 0) return; // solo click izquierdo
    e.preventDefault();
    setIsDragging(true);
    dragStartX.current = e.clientX;
    dragStartWidth.current = width;
    document.body.style.cursor = "ew-resize";
    document.body.style.userSelect = "none";
  }, [width]);

  useEffect(() => {
    if (!isDragging) return undefined;
    const onMouseMove = (e) => {
      const delta = e.clientX - dragStartX.current;
      const nuevo = dragStartWidth.current + delta;
      // Auto-hide: si el ancho cae por debajo del umbral, ocultar.
      if (nuevo < AUTO_HIDE_THRESHOLD) {
        setIsCollapsed(true);
        setIsDragging(false);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        return;
      }
      // Acotar entre MIN_WIDTH y MAX_WIDTH.
      setWidth(Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, nuevo)));
    };
    const onMouseUp = () => {
      setIsDragging(false);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
    return () => {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isDragging]);

  const toggleCollapsed = useCallback(() => {
    setIsCollapsed((c) => {
      if (c) {
        // Al expandir, restaurar el ancho previo (o el default si es < MIN_WIDTH).
        setWidth((w) => (w < MIN_WIDTH ? DEFAULT_WIDTH : w));
      }
      return !c;
    });
  }, []);

  // Hidratar desde localStorage al montar.
  useEffect(() => {
    try {
      const savedW = localStorage.getItem(STORAGE_KEY_WIDTH);
      if (savedW) {
        const w = parseInt(savedW, 10);
        if (Number.isFinite(w) && w >= MIN_WIDTH && w <= MAX_WIDTH) {
          setWidth(w);
        }
      }
      const savedC = localStorage.getItem(STORAGE_KEY_COLLAPSED);
      if (savedC === "1") setIsCollapsed(true);
    } catch {
      /* localStorage no disponible (modo incognito, etc) */
    }
  }, []);

  // Persistir ancho.
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_WIDTH, String(width));
    } catch { /* ignore */ }
  }, [width]);

  // Persistir collapsed.
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_COLLAPSED, isCollapsed ? "1" : "0");
    } catch { /* ignore */ }
  }, [isCollapsed]);

  return {
    width,
    isCollapsed,
    isDragging,
    sidebarRef,
    dragHandleProps: { onMouseDown, role: "separator", "aria-orientation": "vertical" },
    toggleCollapsed,
  };
}

export const ADMIN_SIDEBAR_DEFAULTS = {
  DEFAULT_WIDTH,
  MIN_WIDTH,
  MAX_WIDTH,
  AUTO_HIDE_THRESHOLD,
};
