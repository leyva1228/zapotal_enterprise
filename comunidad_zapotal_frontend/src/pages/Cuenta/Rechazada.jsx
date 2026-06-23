import React from 'react';
import { Link } from 'react-router-dom';
import { FaTimesCircle, FaShieldAlt } from 'react-icons/fa';

export default function CuentaRechazada() {
  return (
    <main className="main-container py-16 px-4 min-h-[50vh]">
      <section className="home-hero">
        <div className="home-hero-content">
          <FaTimesCircle size={64} color="#dc3545" />
          <h1>Solicitud rechazada</h1>
          <p>Tu solicitud de registro no fue aprobada por el administrador.</p>
          <Link to="/" className="btn-principal">Volver al inicio</Link>
          <div className="mt-6">
            <FaShieldAlt /> Soporte: admin@comunidadzapotal.com
          </div>
        </div>
      </section>
    </main>
  );
}
