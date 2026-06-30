import React, { useEffect, useState, useCallback } from 'react';
import { createContext, useContext } from 'react';
import {
  FaCheckCircle, FaExclamationCircle, FaInfoCircle, FaExclamationTriangle,
  FaTimes,
} from 'react-icons/fa';
import './ToastCenter.css';

const ToastCtx = createContext({ push: () => {} });

export function useToast() {
  return useContext(ToastCtx);
}

let _id = 0;
const nextId = () => ++_id;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const push = useCallback((toast) => {
    const id = nextId();
    const item = {
      id,
      type: toast.type || 'info',
      title: toast.title || '',
      text: toast.text || '',
      duration: toast.duration ?? 6000,
      onClose: toast.onClose,
      action: toast.action,
    };
    setToasts((prev) => [...prev, item]);
    if (item.duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, item.duration);
    }
    return id;
  }, []);

  const close = useCallback((id) => {
    setToasts((prev) => {
      const found = prev.find((t) => t.id === id);
      if (found?.onClose) found.onClose();
      return prev.filter((t) => t.id !== id);
    });
  }, []);

  return (
    <ToastCtx.Provider value={{ push, close }}>
      {children}
      <div className="toast-center" role="status" aria-live="polite">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onClose={() => close(t.id)} />
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

function ToastItem({ toast, onClose }) {
  const icon = {
    success: <FaCheckCircle />,
    error: <FaExclamationCircle />,
    warning: <FaExclamationTriangle />,
    info: <FaInfoCircle />,
  }[toast.type] || <FaInfoCircle />;

  return (
    <div className={`toast-item toast-item--${toast.type}`} role="alert">
      <span className="toast-item__icon">{icon}</span>
      <div className="toast-item__body">
        {toast.title && <div className="toast-item__title">{toast.title}</div>}
        <div className="toast-item__text">{toast.text}</div>
        {toast.action && (
          <button className="toast-item__action" type="button" onClick={toast.action.onClick}>
            {toast.action.label}
          </button>
        )}
      </div>
      <button className="toast-item__close" type="button" onClick={onClose} aria-label="Cerrar">
        <FaTimes />
      </button>
    </div>
  );
}
