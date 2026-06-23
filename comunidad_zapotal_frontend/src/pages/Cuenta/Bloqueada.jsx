import React from 'react';
import { Link } from 'react-router-dom';
import { FaBan, FaShieldAlt } from 'react-icons/fa';

export default function CuentaBloqueada() {
  return (
    <main className="main-container py-16 px-4 min-h-[50vh]">
      <section className="home-hero">
        <div className="home-hero-content">
          <FaBan size={64} color="#dc3545" />
          <h1>Cuenta bloqueada</h1>
          <p>Tu cuenta ha sido bloqueada por el administrador. Contactanos para mas informacion.</p>
          <Link to="/login" className="btn-principal">Volver</Link>
          <div className="mt-6">
            <FaShieldAlt /> Soporte: admin@comunidadzapotal.com
          </div>
        </div>
      </section>
    </main>
  );
}
