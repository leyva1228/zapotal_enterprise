// App.js

import React, { useState, useEffect } from "react";

import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";

import {
  FaUsers,
  FaLeaf,
  FaHandsHelping,
  FaCalendarAlt,
  FaNewspaper,
  FaLandmark,
  FaPhoneAlt,
  FaFileAlt,
  FaArrowRight,
  FaMapMarkerAlt,
  FaClock,
} from "react-icons/fa";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

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

/* SCROLL ARRIBA AUTOMÁTICO */
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }, [pathname]);

  return null;
}

/* HOME */
function Home() {
  const [faqAbierta, setFaqAbierta] = useState(null);

  const [noticias, setNoticias] = useState([]);
  const [eventos, setEventos] = useState([]);

  useEffect(() => {

    fetch("http://localhost:8000/api/noticias/")
      .then((res) => res.json())
      .then((data) => {

        const datos = Array.isArray(data)
          ? data
          : data.results || [];

        setNoticias(datos);

      })
      .catch((error) => {
        console.log("Error noticias:", error);
      });

    fetch("http://localhost:8000/api/eventos/")
      .then((res) => res.json())
      .then((data) => {

        const datos = Array.isArray(data)
          ? data
          : data.results || [];

        setEventos(datos);

      })
      .catch((error) => {
        console.log("Error eventos:", error);
      });

  }, []);

  /* SOLO LA NOTICIA MÁS RECIENTE */
  const noticiasOrdenadas = [...noticias].sort(
    (a, b) =>
      new Date(
        b.fecha_publicacion ||
        b.fecha_creacion ||
        b.created_at
      ) -
      new Date(
        a.fecha_publicacion ||
        a.fecha_creacion ||
        a.created_at
      )
  );

  const noticiaPrincipal = noticiasOrdenadas[0];

  /* EVENTOS MÁS PRÓXIMOS */
  const eventosProximos = [...eventos]
    .sort(
      (a, b) =>
        new Date(a.fecha_evento) -
        new Date(b.fecha_evento)
    )
    .slice(0, 3);

  const preguntas = [
    {
      pregunta: "¿Qué información ofrece esta plataforma?",
      respuesta:
        "La plataforma brinda acceso a noticias, eventos, comunicados, información institucional y servicios digitales de la Comunidad Campesina Zapotal.",
    },
    {
      pregunta: "¿Quiénes pueden usar esta página?",
      respuesta:
        "Está dirigida a comuneros, autoridades, visitantes y ciudadanos interesados en conocer las actividades, organización y desarrollo de la comunidad.",
    },
    {
      pregunta: "¿Dónde puedo revisar los eventos comunales?",
      respuesta:
        "Puedes ingresar a la sección Eventos para consultar reuniones, jornadas, campañas y actividades importantes.",
    },
  ];

  /* OBTENER IMAGEN */
  const obtenerImagen = (item) => {

    const media = item?.multimedia?.find(
      (archivo) => archivo.tipo === "IMAGEN"
    );

    return media?.archivo_url || "/img/fondo.png";
  };

  return (
    <main className="main-container">

      {/* HERO */}
      <section className="home-hero">

        <div className="home-hero-overlay"></div>

        <div className="home-hero-content">

          <span className="home-etiqueta">
            Bienvenidos a nuestra comunidad
          </span>

          <h1>
            Unidos trabajamos por el desarrollo de Zapotal
          </h1>

          <p>
            Promovemos el bienestar de nuestros comuneros,
            la gestión responsable de nuestros recursos
            y el desarrollo sostenible de nuestra tierra.
          </p>

          <div className="home-botones">

            <Link
              to="/nosotros/conocenos"
              className="btn-principal"
            >
              Conoce más sobre nosotros
              <FaArrowRight />
            </Link>

            <Link
              to="/noticias"
              className="btn-secundario"
            >
              <FaNewspaper />
              Ver noticias
            </Link>

          </div>

        </div>

      </section>

      {/* VALORES */}
      <section className="home-valores">

        <div className="valor-item">

          <div className="valor-icono">
            <FaUsers />
          </div>

          <div>
            <h3>Nuestra Comunidad</h3>

            <p>
              Conoce nuestra historia,
              valores y organización comunal.
            </p>
          </div>

        </div>

        <div className="valor-item">

          <div className="valor-icono">
            <FaLeaf />
          </div>

          <div>
            <h3>Gestión Responsable</h3>

            <p>
              Trabajamos por el uso sostenible
              de nuestros recursos.
            </p>
          </div>

        </div>

        <div className="valor-item">

          <div className="valor-icono">
            <FaHandsHelping />
          </div>

          <div>
            <h3>Participación Activa</h3>

            <p>
              La participación comunal
              fortalece nuestro desarrollo.
            </p>
          </div>

        </div>

        <div className="valor-item">

          <div className="valor-icono">
            <FaCalendarAlt />
          </div>

          <div>
            <h3>Eventos y Actividades</h3>

            <p>
              Infórmate sobre reuniones,
              jornadas y actividades.
            </p>
          </div>

        </div>

      </section>

      {/* CONTENIDO */}
      <section className="home-contenido">

        {/* NOTICIA PRINCIPAL */}
        <div className="home-bloque noticias-destacadas">

          <div className="home-bloque-header">

            <h2>Noticia Destacada</h2>

            <Link to="/noticias">
              Ver todas
              <FaArrowRight />
            </Link>

          </div>

          {noticiaPrincipal ? (

            <article className="noticia-principal">

              <img
                src={obtenerImagen(noticiaPrincipal)}
                alt={noticiaPrincipal.titulo}
              />

              <div className="noticia-info">

                <span>Comunidad</span>

                <h3>
                  {noticiaPrincipal.titulo}
                </h3>

                <p>
                  {noticiaPrincipal.descripcion?.length > 140
                    ? noticiaPrincipal.descripcion.substring(0, 140) + "..."
                    : noticiaPrincipal.descripcion}
                </p>

                <Link
                  to={`/noticias/${noticiaPrincipal.id}`}
                  className="noticia-link"
                >
                  Leer más
                  <FaArrowRight />
                </Link>

              </div>

            </article>

          ) : (

            <p className="home-mensaje">
              No hay noticias registradas.
            </p>

          )}

        </div>

        {/* EVENTOS */}
        <div className="home-bloque eventos-proximos">

          <div className="home-bloque-header">

            <h2>Próximos Eventos</h2>

            <Link to="/eventos">
              Ver todos
              <FaArrowRight />
            </Link>

          </div>

          {eventosProximos.length > 0 ? (

            eventosProximos.map((evento) => {

              const fecha = new Date(evento.fecha_evento);

              return (

                <Link
                  to={`/eventos/${evento.id}`}
                  className="evento-home"
                  key={evento.id}
                >

                  <div className="evento-fecha-home">

                    <strong>
                      {fecha.toLocaleDateString("es-PE", {
                        day: "2-digit",
                      })}
                    </strong>

                    <span>
                      {fecha.toLocaleDateString("es-PE", {
                        month: "short",
                      })}
                    </span>

                  </div>

                  <div>

                    <h3>{evento.titulo}</h3>

                    <p>
                      <FaClock />
                      {" "}
                      {fecha.toLocaleTimeString("es-PE", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>

                    <p>
                      <FaMapMarkerAlt />
                      {" "}
                      {evento.lugar || "Lugar por confirmar"}
                    </p>

                  </div>

                </Link>

              );
            })

          ) : (

            <p className="home-mensaje">
              No hay eventos registrados.
            </p>

          )}

          <Link
            to="/eventos"
            className="btn-eventos-home"
          >
            <FaCalendarAlt />
            Ver todos los eventos
          </Link>

        </div>

        {/* ACCESO RÁPIDO */}
        <div className="home-bloque acceso-rapido">

          <div className="home-bloque-header">
            <h2>Acceso Rápido</h2>
          </div>

          <div className="acceso-grid">

            <Link to="/nosotros/historia">
              <FaLandmark />
              <span>Historia</span>
            </Link>

            <Link to="/autoridades">
              <FaUsers />
              <span>Autoridades</span>
            </Link>

            <Link to="/eventos">
              <FaCalendarAlt />
              <span>Eventos</span>
            </Link>

            <Link to="/contactanos">
              <FaPhoneAlt />
              <span>Contacto</span>
            </Link>

            <Link to="/libro-reclamaciones">
              <FaFileAlt />
              <span>Reclamaciones</span>
            </Link>

            <Link to="/noticias">
              <FaNewspaper />
              <span>Noticias</span>
            </Link>

          </div>

        </div>

      </section>

      {/* FAQ */}
      <section className="faq-section">

        <div className="faq-header">

          <span className="faq-subtitle">
            Centro de información
          </span>

          <h2>Preguntas Frecuentes</h2>

          <p>
            Resolvemos las principales dudas relacionadas
            con la plataforma digital de la Comunidad
            Campesina Zapotal.
          </p>

        </div>

        <div className="faq-list">

          {preguntas.map((item, index) => (

            <div
              className={`faq-item ${
                faqAbierta === index ? "faq-activa" : ""
              }`}
              key={index}
            >

              <button
                type="button"
                onClick={() =>
                  setFaqAbierta(
                    faqAbierta === index ? null : index
                  )
                }
              >

                <span>{item.pregunta}</span>

                <div className="faq-icono">
                  ⌄
                </div>

              </button>

              <div className="faq-contenido">
                <p>{item.respuesta}</p>
              </div>

            </div>

          ))}

        </div>

      </section>

    </main>
  );
}

/* LAYOUT */
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

        <Route
          path="/"
          element={
            localStorage.getItem("usuario")
              ? <Home />
              : <Login />
          }
        />

        <Route
          path="/noticias"
          element={<Noticias />}
        />

        <Route
          path="/noticias/:id"
          element={<DetalleNoticia />}
        />

        <Route
          path="/eventos"
          element={<Eventos />}
        />

        <Route
          path="/eventos/:id"
          element={<DetalleEvento />}
        />

        <Route
          path="/nosotros/historia"
          element={<NuestraHistoria />}
        />

        <Route
          path="/nosotros/conocenos"
          element={<Conocenos />}
        />

        <Route
          path="/autoridades"
          element={<Autoridades />}
        />

        <Route
          path="/contactanos"
          element={<Contacto />}
        />

        <Route
          path="/libro-reclamaciones"
          element={<LibroReclamaciones />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/perfil"
          element={<Perfil />}
        />

      </Routes>

      {!ocultarNavbar && <Footer />}

    </>
  );
}

/* APP */
function App() {

  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const tiempo = setTimeout(() => {
      setLoading(false);
    }, 2500);

    return () => clearTimeout(tiempo);

  }, []);

  if (loading) {
    return <LoadingScreen />;
  }

  return (

    <BrowserRouter>

      <Layout />

    </BrowserRouter>

  );
}

export default App;