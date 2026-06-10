import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import { FaArrowRight } from "react-icons/fa";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

import Donaciones from "./pages/Donaciones/Donaciones";
import Noticias from "./pages/Noticias/Noticias";
import DetalleNoticia from "./pages/Noticias/DetalleNoticia";
import Eventos from "./pages/Eventos/Eventos";
import DetalleEvento from "./pages/Eventos/DetalleEvento";
import NuestraHistoria from "./pages/Nosotros/NuestraHistoria";
import Conocenos from "./pages/Nosotros/Conocenos";
import Autoridades from "./components/Autoridades/Autoridades";
import Contacto from "./components/Contacto/Contacto";
import LibroReclamaciones from "./components/LibroReclamaciones/LibroReclamaciones";
import Login from "./pages/Login/Login";
import Perfil from "./pages/Perfil/Perfil";
import LoadingScreen from "./pages/LoadingScreen/LoadingScreen";

import "./App.css";

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [pathname]);

  return null;
}

function Home() {
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

  const ocultarNavbar =
    location.pathname.startsWith("/noticias/") ||
    location.pathname.startsWith("/eventos/") ||
    location.pathname.startsWith("/libro-reclamaciones") ||
    location.pathname.startsWith("/login");

  return (
    <>
      <ScrollToTop />

      {!ocultarNavbar && <Navbar />}

      <Routes>
        <Route path="/" element={localStorage.getItem("usuario") ? <Home /> : <Login />} />
        <Route path="/noticias" element={<Noticias />} />
        <Route path="/noticias/:id" element={<DetalleNoticia />} />
        <Route path="/eventos" element={<Eventos />} />
        <Route path="/eventos/:id" element={<DetalleEvento />} />
        <Route path="/nosotros/historia" element={<NuestraHistoria />} />
        <Route path="/nosotros/conocenos" element={<Conocenos />} />
        <Route path="/autoridades" element={<Autoridades />} />
        <Route path="/contactanos" element={<Contacto />} />
        <Route path="/libro-reclamaciones" element={<LibroReclamaciones />} />
        <Route path="/login" element={<Login />} />
        <Route path="/perfil" element={<Perfil />} />
        <Route path="/donaciones" element={<Donaciones />}/>
      </Routes>

      {!ocultarNavbar && <Footer />}
    </>
  );
}

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tiempo = setTimeout(() => setLoading(false), 2500);
    return () => clearTimeout(tiempo);
  }, []);

  if (loading) return <LoadingScreen />;

  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
}

export default App;