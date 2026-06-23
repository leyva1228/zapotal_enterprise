import React from 'react';
import { Link } from 'react-router-dom';
import { FaHourglassHalf } from 'react-icons/fa';

export default function RegistroPendiente({ aprobacion = false }) {
  return (
    <main className="main-container py-16 px-4 min-h-[50vh]">
      <section className="home-hero">
        <div className="home-hero-content">
          <FaHourglassHalf size={64} />
          <h1>{aprobacion ? 'Esperando aprobacion' : 'Registro en proceso'}</h1>
          <p>
            {aprobacion
              ? 'Tu cuenta ha sido verificada. Esta pendiente de aprobacion por el administrador.'
              : 'Tu registro se ha completado. Sigue las instrucciones enviadas a tu correo.'}
          </p>
          <Link to="/login" className="btn-principal">Ir a iniciar sesion</Link>
        </div>
      </section>
    </main>
  );
}
