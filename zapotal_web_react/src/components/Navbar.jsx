import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

import {
  FaHome,
  FaNewspaper,
  FaCalendarAlt,
  FaUserTie,
  FaPhoneAlt,
  FaHandsHelping,
  FaChevronDown,
  FaUserCircle,
  FaSignOutAlt,
  FaUser,
  FaCog,
  FaShieldAlt,
  FaBars,
  FaTimes,
  FaBell,
} from "react-icons/fa";

import "./Navbar.css";

function Navbar() {

  const [perfilAbierto, setPerfilAbierto] =
    useState(false);

  const [menuAbierto, setMenuAbierto] =
    useState(false);

  const [notificaciones, setNotificaciones] =
    useState([]);

  const [
    mostrarNotificaciones,
    setMostrarNotificaciones
  ] = useState(false);

  const usuario = JSON.parse(
    localStorage.getItem("usuario")
  );

  /* =========================
     CARGAR NOTIFICACIONES
  ========================= */

  useEffect(() => {

    if (!usuario) return;

    axios
      .get(
        `http://127.0.0.1:8000/api/notificaciones/?usuario_id=${usuario.id}`
      )

      .then((res) => {

        setNotificaciones(res.data);

      })

      .catch((err) => {

        console.log(err);

      });

  }, [usuario]);

  /* =========================
     CERRAR SESIÓN
  ========================= */

  const cerrarSesion = () => {

    localStorage.removeItem("usuario");

    window.location.href = "/login";

  };

  return (

    <header className="navbar">

      {/* LOGO */}

      <Link
        to="/"
        className="navbar-brand"
      >

        <img
          src="/img/Logo-comunidad/Logo-principal.png"
          alt="Logo Comunidad Campesina Zapotal"
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

      {/* HAMBURGUESA */}

      <button
        className="menu-toggle"
        onClick={() =>
          setMenuAbierto(!menuAbierto)
        }
      >

        {menuAbierto
          ? <FaTimes />
          : <FaBars />
        }

      </button>

      {/* MENÚ */}

      <nav
        className={`nav-links ${
          menuAbierto ? "active" : ""
        }`}
      >

        <Link
          to="/"
          onClick={() =>
            setMenuAbierto(false)
          }
        >

          <FaHome />

          Inicio

        </Link>

        <Link
          to="/noticias"
          onClick={() =>
            setMenuAbierto(false)
          }
        >

          <FaNewspaper />

          Noticias

        </Link>

        <Link
          to="/eventos"
          onClick={() =>
            setMenuAbierto(false)
          }
        >

          <FaCalendarAlt />

          Eventos

        </Link>

        <Link
          to="/autoridades"
          onClick={() =>
            setMenuAbierto(false)
          }
        >

          <FaUserTie />

          Autoridades

        </Link>

        <Link
          to="/contactanos"
          onClick={() =>
            setMenuAbierto(false)
          }
        >

          <FaPhoneAlt />

          Contáctanos

        </Link>

        {/* DROPDOWN */}

        <div className="dropdown">

          <span className="dropdown-title">

            <FaHandsHelping />

            Sobre Nosotros

            <FaChevronDown className="dropdown-arrow" />

          </span>

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

      {/* USUARIO */}

      {usuario ? (

        <div className="navbar-user">

          {/* NOTIFICACIONES */}

          <div className="notificacion-box">

            <button
              className="btn-notificacion"
              onClick={() =>
                setMostrarNotificaciones(
                  !mostrarNotificaciones
                )
              }
            >

              <FaBell />

              {notificaciones.length > 0 && (

                <span className="notificacion-count">

                  {notificaciones.length}

                </span>

              )}

            </button>

            {mostrarNotificaciones && (

              <div className="notificacion-dropdown">

                <h3>
                  Notificaciones
                </h3>

                {notificaciones.length === 0 ? (

                  <p className="sin-notificaciones">

                    No hay notificaciones

                  </p>

                ) : (

                  notificaciones.map((n) => (

                    <div
                      key={n.id}
                      className="notificacion-item"
                    >

                      <strong>
                        {n.titulo}
                      </strong>

                      <span>
                        {n.mensaje}
                      </span>

                    </div>

                  ))

                )}

              </div>

            )}

          </div>

          {/* PERFIL */}

          <button
            className="profile-trigger"
            onClick={() =>
              setPerfilAbierto(!perfilAbierto)
            }
          >

            {usuario.foto_perfil ? (

              <img
                src={usuario.foto_perfil}
                alt="Perfil"
                className="profile-img"
              />

            ) : (

              <FaUserCircle className="profile-icon" />

            )}

            <div className="profile-text">

              <strong>
                {usuario.nombres || "Usuario"}
              </strong>

              <span>
                Ver perfil
              </span>

            </div>

            <FaChevronDown className="profile-arrow" />

          </button>

          {perfilAbierto && (

            <div className="profile-dropdown">

              <div className="profile-dropdown-header">

                {usuario.foto_perfil ? (

                  <img
                    src={usuario.foto_perfil}
                    alt="Perfil"
                    className="profile-dropdown-img"
                  />

                ) : (

                  <FaUserCircle className="profile-dropdown-icon" />

                )}

                <div>

                  <h3>
                    {usuario.nombres || "Usuario"}
                  </h3>

                  <p>
                    {usuario.email || "Correo no registrado"}
                  </p>

                  <span className="profile-role">

                    <FaShieldAlt />

                    {usuario.tipo_usuario || "USUARIO"}

                  </span>

                </div>

              </div>

              <div className="profile-dropdown-line"></div>

              <Link
                to="/perfil"
                className="profile-option"
                onClick={() =>
                  setPerfilAbierto(false)
                }
              >

                <FaUser className="option-icon green" />

                <div>

                  <strong>
                    Ver perfil
                  </strong>

                  <span>
                    Administra tu información personal
                  </span>

                </div>

              </Link>

              <Link
                to="/perfil"
                className="profile-option"
                onClick={() =>
                  setPerfilAbierto(false)
                }
              >

                <FaCog className="option-icon gray" />

                <div>

                  <strong>
                    Configuración
                  </strong>

                  <span>
                    Preferencias de cuenta
                  </span>

                </div>

              </Link>

              <div className="profile-dropdown-line"></div>

              <button
                className="profile-option logout-option"
                onClick={cerrarSesion}
              >

                <FaSignOutAlt className="option-icon red" />

                <div>

                  <strong>
                    Cerrar sesión
                  </strong>

                  <span>
                    Salir de tu cuenta
                  </span>

                </div>

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

    </header>

  );
}

export default Navbar;