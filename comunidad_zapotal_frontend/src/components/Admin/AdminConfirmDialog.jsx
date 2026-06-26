import React, { useState, useCallback } from "react";
import { FaSpinner, FaCheck, FaTimes, FaExclamationTriangle, FaTrash, FaQuestion } from "react-icons/fa";

const VARIANT_ICON = {
  danger: <FaTrash />,
  warning: <FaExclamationTriangle />,
  primary: <FaQuestion />,
};

const VARIANT_BTN = {
  danger: "admin-btn-danger",
  warning: "admin-btn-warning",
  primary: "admin-btn-primary",
};

/**
 * Modal de confirmacion con diseno admin.
 * Reemplaza `window.confirm()` en paginas admin y publicas.
 */
export default function AdminConfirmDialog({
  open,
  title = "¿Estas seguro?",
  message,
  confirmText = "Confirmar",
  cancelText = "Cancelar",
  variant = "danger",
  loading = false,
  onConfirm,
  onCancel,
}) {
  const handleConfirm = async () => {
    if (loading) return;
    try {
      await onConfirm?.();
    } catch (e) {
      console.error("[AdminConfirmDialog] onConfirm error:", e);
    }
  };

  if (!open) return null;

  return (
    <div className="admin-modal-backdrop" onClick={onCancel}>
      <div className="admin-modal" style={{ maxWidth: 480 }} onClick={(e) => e.stopPropagation()}>
        <header className="admin-modal__header">
          <h2 className="admin-modal__title">
            <span style={{ marginRight: 8, color: variant === "danger" ? "#dc2626" : variant === "warning" ? "#d97706" : "#0a3d1f" }}>
              {VARIANT_ICON[variant] || VARIANT_ICON.danger}
            </span>
            {title}
          </h2>
          <button type="button" className="admin-modal__close" onClick={onCancel} aria-label="Cerrar" disabled={loading}>
            <FaTimes />
          </button>
        </header>
        <div className="admin-modal__body">
          {typeof message === "string" ? (
            <p className="m-0 text-[14px] leading-relaxed text-soft">{message}</p>
          ) : (message)}
        </div>
        <footer className="admin-modal__footer">
          <button type="button" className="admin-btn" onClick={onCancel} disabled={loading}>
            {cancelText}
          </button>
          <button
            type="button"
            className={`admin-btn ${VARIANT_BTN[variant] || VARIANT_BTN.danger}`}
            onClick={handleConfirm}
            disabled={loading}
            autoFocus
          >
            {loading ? (<><FaSpinner className="fa-spin" /> Procesando...</>) : (<><FaCheck /> {confirmText}</>)}
          </button>
        </footer>
      </div>
    </div>
  );
}

/**
 * Hook `useConfirm` para reemplazar `window.confirm()` con un solo componente inline.
 */
export function useConfirm() {
  const [state, setState] = useState({
    open: false, title: "", message: "", confirmText: "Confirmar",
    cancelText: "Cancelar", variant: "danger", loading: false, onResolve: null,
  });

  const confirm = useCallback((opts) => {
    return new Promise((resolve) => {
      setState({
        open: true,
        title: opts.title || "¿Estas seguro?",
        message: opts.message || "",
        confirmText: opts.confirmText || "Confirmar",
        cancelText: opts.cancelText || "Cancelar",
        variant: opts.variant || "danger",
        loading: false,
        onResolve: resolve,
      });
    });
  }, []);

  const handleConfirm = useCallback(async () => {
    setState((s) => ({ ...s, loading: true }));
    try {
      state.onResolve?.(true);
    } finally {
      setState({ open: false, title: "", message: "", confirmText: "Confirmar", cancelText: "Cancelar", variant: "danger", loading: false, onResolve: null });
    }
  }, [state.onResolve]);

  const handleCancel = useCallback(() => {
    state.onResolve?.(false);
    setState({ open: false, title: "", message: "", confirmText: "Confirmar", cancelText: "Cancelar", variant: "danger", loading: false, onResolve: null });
  }, [state.onResolve]);

  const ConfirmDialog = (
    <AdminConfirmDialog
      open={state.open}
      title={state.title}
      message={state.message}
      confirmText={state.confirmText}
      cancelText={state.cancelText}
      variant={state.variant}
      loading={state.loading}
      onConfirm={handleConfirm}
      onCancel={handleCancel}
    />
  );

  return { confirm, ConfirmDialog };
}
