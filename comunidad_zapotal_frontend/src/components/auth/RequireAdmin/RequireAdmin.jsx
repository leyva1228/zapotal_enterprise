import React from 'react';
import { Link, Navigate } from 'react-router-dom';
import { FaShieldAlt } from 'react-icons/fa';
import { useAuth } from '../../../context/AuthContext';

export default function RequireAdmin({ children }) {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return <div className="admin-loading">Cargando...</div>;
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (!isAdmin) {
    return (
      <main className="main-container">
        <section className="home-hero">
          <div className="home-hero-content">
            <FaShieldAlt size={48} />
            <h1>Acceso restringido</h1>
            <p>Solo los administradores pueden acceder a este panel.</p>
            <Link to="/" className="btn-principal">Volver al inicio</Link>
          </div>
        </section>
      </main>
    );
  }
  return children;
}
