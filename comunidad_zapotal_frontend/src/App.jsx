import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { FaArrowRight, FaShieldAlt } from 'react-icons/fa';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Breadcrumb from './components/Breadcrumb';
import RequireAuth from './components/RequireAuth';
import RequireAdmin from './components/RequireAdmin';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider, useToast } from './components/ToastCenter';

import Donaciones from './pages/Donaciones/Donaciones';
import Noticias from './pages/Noticias/Noticias';
import DetalleNoticia from './pages/Noticias/DetalleNoticia';
import Eventos from './pages/Eventos/Eventos';
import DetalleEvento from './pages/Eventos/DetalleEvento';
import NuestraHistoria from './pages/Nosotros/NuestraHistoria';
import Conocenos from './pages/Nosotros/Conocenos';
import MarcoLegalPage from './pages/Nosotros/MarcoLegalPage';
import Autoridades from './components/Autoridades/Autoridades';
import AutoridadesPage from './pages/Autoridades/AutoridadesPage';
import Contacto from './components/Contacto/Contacto';
import TerminosPage from './pages/Legal/TerminosPage';
import PrivacidadPage from './pages/Legal/PrivacidadPage';
import CookiesPage from './pages/Legal/CookiesPage';
import BannerCookies from './components/Legal/BannerCookies';
import LibroReclamaciones from './components/LibroReclamaciones/LibroReclamaciones';
import Login from './pages/Login/Login';
import Perfil from './pages/Perfil/Perfil';
import LoadingScreen from './pages/LoadingScreen/LoadingScreen';
import Registro from './pages/Registro/Registro';
import RegistroPendiente from './pages/Registro/RegistroPendiente';
import TwoFactorVerify from './components/TwoFactorVerify';
import SolicitarRecuperacion from './pages/RecuperarPassword/SolicitarRecuperacion';
import ConfirmarRecuperacion from './pages/RecuperarPassword/ConfirmarRecuperacion';
import CuentaBloqueada from './pages/Cuenta/Bloqueada';
import CuentaRechazada from './pages/Cuenta/Rechazada';

import AdminLayout from './pages/Admin/AdminLayout';
import AdminDashboard from './pages/Admin/AdminDashboard';
import AdminNoticias from './pages/Admin/AdminNoticias';
import AdminEventos from './pages/Admin/AdminEventos';
import AdminCategorias from './pages/Admin/AdminCategorias';
import AdminAutoridades from './pages/Admin/AdminAutoridades';
import AdminComitesComunales from './pages/Admin/AdminComitesComunales';
import AdminUsuarios from './pages/Admin/AdminUsuarios';
import AdminComentarios from './pages/Admin/AdminComentarios';
import AdminAuditoria from './pages/Admin/AdminAuditoria';
import AdminReclamaciones from './pages/Admin/AdminReclamaciones';
import AdminContacto from './pages/Admin/AdminContacto';
import AdminNotificaciones from './pages/Admin/AdminNotificaciones';
import AdminBajas from './pages/Admin/AdminBajas';
import AdminCms from './pages/Admin/AdminCms';
import AdminDonaciones from './pages/Admin/AdminDonaciones';
import AdminInstitucional from './pages/Admin/AdminInstitucional';
import AdminConfiguracion from './pages/Admin/AdminConfiguracion';
import AdminGaleria from './pages/Admin/AdminGaleria';
import Buscar from './pages/Buscar/Buscar';

import './App.css';

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [pathname]);
  return null;
}

function Home() {
  const toast = useToast();
  React.useEffect(() => {
    // Mostrar toast de pendiente de aprobacion si existe
    const pending = sessionStorage.getItem('pending_approval');
    if (pending) {
      try {
        const { email, ts } = JSON.parse(pending);
        const minutos = Math.max(1, Math.floor((Date.now() - ts) / 60000));
        toast.push({
          type: 'info',
          title: 'Cuenta pendiente de aprobacion',
          text: `Tu cuenta ${email} esta siendo revisada por un administrador. Te enviaremos un correo cuando sea aprobada. Esto puede tardar unos minutos.`,
          duration: 10000,
          action: { label: 'Entendido', onClick: () => { sessionStorage.removeItem('pending_approval'); toast.push({ type: 'success', text: 'Te avisaremos por correo.', duration: 4000 }); } },
        });
        sessionStorage.removeItem('pending_approval');
      } catch (e) { /* noop */ }
    }
  }, []);
  return (
    <main className="main-container">
      <section className="home-hero">
        <div className="home-hero-overlay"></div>
        <div className="home-hero-content">
          <h1>
            ¿Por qué Zapotal? Somos una comunidad campesina comprometida con
            el desarrollo, la unión y la preservación de nuestra identidad.
          </h1>
          <p>Comunidad Campesina Zapotal</p>
          <Link to="/nosotros/conocenos" className="btn-principal">
            CONÓCENOS <FaArrowRight />
          </Link>
        </div>
      </section>
    </main>
  );
}

function Layout() {
  const location = useLocation();
  const { user, isAuthenticated } = useAuth();
  const ocultarNavbar =
    location.pathname.startsWith('/login') ||
    location.pathname.startsWith('/registro') ||
    location.pathname.startsWith('/recuperar-password') ||
    location.pathname.startsWith('/cuenta') ||
    location.pathname.startsWith('/2fa') ||
    location.pathname.startsWith('/admin');

  const esperandoAprobacion =
    isAuthenticated && user?.estado === 'PENDIENTE_APROBACION';

  const ocultarFooter =
    location.pathname.startsWith('/perfil') ||
    location.pathname.startsWith('/admin') ||
    ocultarNavbar;

  return (
    <>
      <ScrollToTop />
      {!ocultarNavbar && <Navbar />}
      {esperandoAprobacion && (
        <div className="lp-aprobacion-banner" role="alert">
          <FaShieldAlt />
          <div>
            <strong>Tu cuenta esta esperando aprobacion del administrador.</strong>
            <p>Recibiras un correo electronico cuando tu cuenta sea aprobada. Esto puede tardar unos minutos.</p>
          </div>
        </div>
      )}
      {!ocultarNavbar && (
        <Breadcrumb
          items={(() => {
            const p = location.pathname;
            if (p.match(/^\/noticias\/\d+/)) {
              return [{ label: 'Noticias', to: '/noticias' }, { label: 'Detalle' }];
            }
            if (p.match(/^\/eventos\/\d+/)) {
              return [{ label: 'Eventos', to: '/eventos' }, { label: 'Detalle' }];
            }
            if (p === '/noticias') return [{ label: 'Noticias' }];
            if (p === '/eventos') return [{ label: 'Eventos' }];
            if (p === '/autoridades') return [{ label: 'Autoridades' }];
            if (p === '/contactanos') return [{ label: 'Contactanos' }];
            if (p === '/libro-reclamaciones') return [{ label: 'Libro de Reclamaciones' }];
            if (p === '/donaciones') return [{ label: 'Donaciones' }];
            if (p === '/buscar') return [{ label: 'Busqueda' }];
            if (p === '/perfil') return [{ label: 'Mi Perfil' }];
            return [];
          })()}
        />
      )}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/noticias" element={<Noticias />} />
        <Route path="/noticias/:id" element={<DetalleNoticia />} />
        <Route path="/eventos" element={<Eventos />} />
        <Route path="/eventos/:id" element={<DetalleEvento />} />
        <Route path="/nosotros/historia" element={<NuestraHistoria />} />
        <Route path="/nosotros/conocenos" element={<Conocenos />} />
        <Route path="/nosotros/marco-legal" element={<MarcoLegalPage />} />
        <Route path="/terminos" element={<TerminosPage />} />
        <Route path="/privacidad" element={<PrivacidadPage />} />
        <Route path="/cookies" element={<CookiesPage />} />
        <Route path="/politica-cookies" element={<CookiesPage />} />
        <Route path="/autoridades" element={<AutoridadesPage />} />
        <Route path="/contactanos" element={<Contacto />} />
        <Route path="/libro-reclamaciones" element={<LibroReclamaciones />} />

        <Route path="/login" element={<Login />} />
        <Route path="/2fa" element={<TwoFactorVerify />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/registro/pendiente" element={<RegistroPendiente />} />
        <Route path="/registro/pendiente-aprobacion" element={<RegistroPendiente aprobacion />} />
        <Route path="/recuperar-password" element={<SolicitarRecuperacion />} />
        <Route path="/recuperar-password/confirmar" element={<ConfirmarRecuperacion />} />
        <Route path="/cuenta/bloqueada" element={<CuentaBloqueada />} />
        <Route path="/cuenta/rechazada" element={<CuentaRechazada />} />

        <Route
          path="/perfil"
          element={
            <RequireAuth>
              <Perfil />
            </RequireAuth>
          }
        />

        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <AdminLayout />
            </RequireAdmin>
          }
        >
          <Route index element={<AdminDashboard />} />
          <Route path="noticias" element={<AdminNoticias />} />
          <Route path="eventos" element={<AdminEventos />} />
          <Route path="categorias" element={<AdminCategorias />} />
          <Route path="autoridades" element={<AdminAutoridades />} />
          <Route path="comites-comunales" element={<AdminComitesComunales />} />
          <Route path="usuarios" element={<AdminUsuarios />} />
          <Route path="comentarios" element={<AdminComentarios />} />
          <Route path="auditoria" element={<AdminAuditoria />} />
          <Route path="reclamaciones" element={<AdminReclamaciones />} />
          <Route path="contacto" element={<AdminContacto />} />
          <Route path="notificaciones" element={<AdminNotificaciones />} />
          <Route path="bajas" element={<AdminBajas />} />
          <Route path="cms" element={<AdminCms />} />
          <Route path="donaciones" element={<AdminDonaciones />} />
          <Route path="institucional" element={<AdminInstitucional />} />
          <Route path="perfil" element={<AdminConfiguracion />} />
        </Route>

        <Route path="/donaciones" element={<Donaciones />} />
        <Route path="/buscar" element={<Buscar />} />

        <Route
          path="*"
          element={
            <main className="main-container">
              <h1 className="text-center">404 - Pagina no encontrada</h1>
            </main>
          }
        />
      </Routes>
      {!ocultarFooter && <Footer />}
    </>
  );
}

function App() {
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(t);
  }, []);
  if (loading) return <LoadingScreen />;

  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Layout />
          <BannerCookies />
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
