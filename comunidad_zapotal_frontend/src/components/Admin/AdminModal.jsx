import React, { useEffect } from "react";
import { FaTimes } from "react-icons/fa";
import "../../pages/Admin/AdminLayout.css";

export default function AdminModal({ open, title, onClose, children, footer, wide }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === "Escape") onClose?.(); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="admin-modal-backdrop" onClick={onClose}>
      <div
        className={"admin-modal" + (wide ? " admin-modal--wide" : "")}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="admin-modal__header">
          <h2 className="admin-modal__title">{title}</h2>
          <button type="button" className="admin-modal__close" onClick={onClose} aria-label="Cerrar">
            <FaTimes />
          </button>
        </header>
        <div className="admin-modal__body">{children}</div>
        {footer && <footer className="admin-modal__footer">{footer}</footer>}
      </div>
    </div>
  );
}
