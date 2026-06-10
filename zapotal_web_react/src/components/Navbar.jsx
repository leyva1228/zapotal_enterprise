import React, {
  useEffect,
  useRef,
  useState,
} from "react";

import { Link } from "react-router-dom";

import axios from "axios";

import {
  FaChevronDown,
  FaUserCircle,
  FaSignOutAlt,
  FaUser,
  FaCog,
  FaBars,
  FaTimes,
  FaBell,
  FaSearch,
  FaFacebookF,
  FaInstagram,
  FaTiktok,
  FaMapMarkerAlt,
  FaPhone,
} from "react-icons/fa";

import "./Navbar.css";

function Navbar() {

  const [
    perfilAbierto,
    setPerfilAbierto,
  ] = useState(false);

  const [
    menuAbierto,
    setMenuAbierto,
  ] = useState(false);

  const [
    nosotrosAbierto,
    setNosotrosAbierto,
  ] = useState(false);

  const [
    mostrarNotificaciones,
    setMostrarNotificaciones,
  ] = useState(false);

  const [
    notificaciones,
    setNotificaciones,
  ] = useState([]);

  const [
    navVisible,
    setNavVisible,
  ] = useState(true);

  const navbarRef =
    useRef(null);

  const lastScroll =
    useRef(0);

  const usuario = JSON.parse(
    localStorage.getItem("usuario")
  );

  /* ==========================
     SCROLL
  ========================== */

  useEffect(() => {

    const handleScroll =
      () => {

        const current =
          window.scrollY;

        if (
          current >
            lastScroll.current &&
          current > 100
        ) {

          setNavVisible(false);

        } else {

          setNavVisible(true);

        }

        lastScroll.current =
          current;

      };

    window.addEventListener(
      "scroll",
      handleScroll
    );

    return () => {

      window.removeEventListener(
        "scroll",
        handleScroll
      );

    };

  }, []);

  /* ==========================
     CLICK OUTSIDE
  ========================== */

  useEffect(() => {

    const handleClickOutside =
      (e) => {

        if (
          navbarRef.current &&
          !navbarRef.current.contains(
            e.target
          )
        ) {

          setPerfilAbierto(
            false
          );

          setMostrarNotificaciones(
            false
          );

          setNosotrosAbierto(
            false
          );

        }

      };

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () => {

      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );

    };

  }, []);

  /* ==========================
     NOTIFICACIONES
  ========================== */

  useEffect(() => {

    if (!usuario) return;

    axios

      .get(
        `http://127.0.0.1:8000/api/notificaciones/?usuario_id=${usuario.id}`
      )

      .then((res) => {

        setNotificaciones(
          res.data
        );

      })

      .catch((err) => {

        console.log(err);

      });

  }, [usuario]);

  /* ==========================
     LOGOUT
  ========================== */

  const cerrarSesion =
    () => {

      localStorage.removeItem(
        "usuario"
      );

      window.location.href =
        "/login";

    };

  return (

    <>

      {/* TOPBAR */}

      <div className="topbar">

        <div className="topbar-left">

          <button
            className="burger-fixed"
            onClick={() =>
              setMenuAbierto(
                !menuAbierto
              )
            }
          >

            {menuAbierto
              ? <FaTimes />
              : <FaBars />
            }

          </button>

          <div className="topbar-info">

            <span>

              <FaMapMarkerAlt />

              Zapotal, Perú

            </span>

            <span className="separator"></span>

            <span>

              <FaPhone />

              +51 921 456 783

            </span>

          </div>

        </div>

        <div className="topbar-center">

          Bienvenido a la Comunidad Campesina Zapotal

        </div>

        <div className="topbar-social">

          <a
            href="https://facebook.com"
            target="_blank"
            rel="noreferrer"
          >
            <FaFacebookF />
          </a>

          <a
            href="https://instagram.com"
            target="_blank"
            rel="noreferrer"
          >
            <FaInstagram />
          </a>

          <a
            href="https://tiktok.com"
            target="_blank"
            rel="noreferrer"
          >
            <FaTiktok />
          </a>

        </div>

      </div>

      {/* NAVBAR */}

      <header
        ref={navbarRef}
        className={`navbar ${
          !navVisible
            ? "navbar-hidden"
            : ""
        }`}
      >

        {/* LOGO */}

        <Link
          to="/"
          className="navbar-brand"
        >

          <img
            src="/img/Logo-comunidad/Logo-principal.png"
            alt="Logo"
          />

          <div>

            <strong>
              Comunidad Campesina
            </strong>

            <span>
              Zapotal
            </span>

          </div>

        </Link>

        {/* MENU */}

        <nav
          className={`nav-links ${
            menuAbierto
              ? "active"
              : ""
          }`}
        >

          <Link
            to="/"
            onClick={() =>
              setMenuAbierto(false)
            }
          >
            Inicio
          </Link>

          <Link
            to="/noticias"
            onClick={() =>
              setMenuAbierto(false)
            }
          >
            Noticias
          </Link>

          <Link
            to="/eventos"
            onClick={() =>
              setMenuAbierto(false)
            }
          >
            Eventos
          </Link>

          <Link
            to="/autoridades"
            onClick={() =>
              setMenuAbierto(false)
            }
          >
            Autoridades
          </Link>

          <Link
            to="/contactanos"
            onClick={() =>
              setMenuAbierto(false)
            }
          >
            Contacto
          </Link>

          <Link
            to="/donaciones"
            onClick={() =>
              setMenuAbierto(false)
            }
          >
            Donaciones
          </Link>

          {/* DROPDOWN */}

          <div
            className={`dropdown ${
              nosotrosAbierto
                ? "dropdown-open"
                : ""
            }`}
          >

            <button
              className="dropdown-title"
              onClick={() =>
                setNosotrosAbierto(
                  !nosotrosAbierto
                )
              }
            >

              Nosotros

              <FaChevronDown />

            </button>

            <div className="dropdown-menu">

              <Link
                to="/nosotros/historia"
                onClick={() =>
                  setMenuAbierto(false)
                }
              >
                Nuestra historia
              </Link>

              <Link
                to="/nosotros/conocenos"
                onClick={() =>
                  setMenuAbierto(false)
                }
              >
                Conócenos
              </Link>

            </div>

          </div>

        </nav>

        {/* RIGHT */}

        <div className="navbar-user">

          {/* SEARCH */}

          <button
            className="circle-btn"
            onClick={() => {

              alert(
                "Buscador próximamente"
              );

            }}
          >

            <FaSearch />

          </button>

          {/* NOTIFICACIONES */}

          {usuario && (

            <div className="notificacion-box">

              <button
                className="circle-btn"
                onClick={() =>
                  setMostrarNotificaciones(
                    !mostrarNotificaciones
                  )
                }
              >

                <FaBell />

                {notificaciones.length >
                  0 && (

                  <span className="notification-count">

                    {
                      notificaciones.length
                    }

                  </span>

                )}

              </button>

              {mostrarNotificaciones && (

                <div className="notification-dropdown">

                  <h3>
                    Notificaciones
                  </h3>

                  {notificaciones.length === 0 ? (

                    <p className="notification-empty">

                      No hay notificaciones

                    </p>

                  ) : (

                    notificaciones.map(
                      (n) => (

                        <div
                          key={n.id}
                          className="notification-item"
                        >

                          <strong>
                            {n.titulo}
                          </strong>

                          <span>
                            {n.mensaje}
                          </span>

                        </div>

                      )
                    )

                  )}

                </div>

              )}

            </div>

          )}

          {/* PERFIL */}

          {usuario ? (

            <div className="profile-box">

              <button
                className="profile-trigger"
                onClick={() =>
                  setPerfilAbierto(
                    !perfilAbierto
                  )
                }
              >

                {usuario.foto_perfil ? (

                  <img
                    src={
                      usuario.foto_perfil
                    }
                    alt="Perfil"
                    className="profile-img"
                  />

                ) : (

                  <div className="profile-letter">

                    {usuario.nombres?.charAt(
                      0
                    )}

                  </div>

                )}

              </button>

              {perfilAbierto && (

                <div className="profile-dropdown">

                  <Link
                    to="/perfil"
                    className="profile-option"
                  >

                    <FaUser />

                    Ver perfil

                  </Link>

                  <Link
                    to="/configuracion"
                    className="profile-option"
                  >

                    <FaCog />

                    Configuración

                  </Link>

                  <button
                    className="profile-option logout-btn"
                    onClick={
                      cerrarSesion
                    }
                  >

                    <FaSignOutAlt />

                    Cerrar sesión

                  </button>

                </div>

              )}

            </div>

          ) : (

            <Link
              to="/login"
              className="login-btn"
            >

              Ingresar

            </Link>

          )}

        </div>

      </header>

    </>

  );

}

export default Navbar;