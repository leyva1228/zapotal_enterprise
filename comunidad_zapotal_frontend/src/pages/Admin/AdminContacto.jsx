import React from 'react';
import { FaEnvelope } from 'react-icons/fa';
import AdminMensajes from '../../components/Admin/AdminMensajes';

export default function AdminContacto() {
  return (
    <div>
      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaEnvelope className="mr-[6px]" />
            Inbox de mensajes de contacto
          </h3>
          <p className="admin-card__subtitle">
            Mensajes enviados por el formulario publico de contacto.
            Cada mensaje tambien genera una notificacion interna para los admins.
          </p>
        </div>
        <div className="admin-card__body">
          <AdminMensajes />
        </div>
      </div>
    </div>
  );
}
