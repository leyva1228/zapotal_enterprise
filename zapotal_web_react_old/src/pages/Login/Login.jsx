import React, { useState } from "react";
import axios from "axios";

import {
  FaEnvelope,
  FaLock,
  FaUser,
  FaShieldAlt,
  FaLeaf,
} from "react-icons/fa";

import "./Login.css";

function Login() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const [mensaje, setMensaje] = useState("");

  const handleLogin = async (e) => {

    e.preventDefault();

    setLoading(true);

    setMensaje("");

    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/api/login/",
        {
          email,
          password,
        }
      );

      localStorage.setItem(
        "usuario",
        JSON.stringify(response.data.usuario)
      );

      setMensaje("Inicio de sesión correcto.");

      setTimeout(() => {

        window.location.href = "/";

      }, 900);

    } catch (error) {

      if (error.response) {

        setMensaje(
          error.response.data.mensaje ||
          "Correo o contraseña incorrectos."
        );

      } else {

        setMensaje(
          "No se pudo conectar con el servidor."
        );
      }

    } finally {

      setLoading(false);
    }
  };

  return (

    <div className="login-page">

      {/* PANEL IZQUIERDO */}
      <section className="login-hero">

        <div className="login-hero-overlay"></div>

        <div className="login-hero-content">

          <img
            src="/img/Logo-comunidad/Logo-principal.png"
            alt="Logo Comunidad Campesina Zapotal"
            className="login-logo"
          />

          <h1>
            Comunidad <br />
            Campesina <br />
            Zapotal
          </h1>

          <div className="decor-line">

            <span></span>

            <FaLeaf className="decor-icon" />

            <span></span>

          </div>

          <p>
            Plataforma digital institucional para la gestión,
            comunicación y participación de los comuneros.
          </p>

          <div className="secure-box">

            <span>
              <FaShieldAlt />
            </span>

            Acceso seguro y autorizado

          </div>

        </div>

      </section>

      {/* PANEL DERECHO */}
      <section className="login-panel">

        <form
          className="login-card"
          onSubmit={handleLogin}
        >

          <div className="login-card-header">

            <div className="small-decor">

              <span></span>

              <FaLeaf className="small-leaf" />

              <span></span>

            </div>

            <h4>
              Bienvenido
            </h4>

            <h2>
              Iniciar Sesión
            </h2>

            <div className="title-line"></div>

            <p>
              Ingresa tus credenciales para acceder
              a la plataforma institucional.
            </p>

          </div>

          {/* EMAIL */}
          <div className="form-group">

            <label>
              Correo electrónico
            </label>

            <div className="input-box">

              <span className="input-icon">
                <FaEnvelope />
              </span>

              <input
                type="email"
                placeholder="Ingresa tu correo electrónico"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                required
              />

            </div>

          </div>

          {/* PASSWORD */}
          <div className="form-group">

            <label>
              Contraseña
            </label>

            <div className="input-box">

              <span className="input-icon">
                <FaLock />
              </span>

              <input
                type="password"
                placeholder="Ingresa tu contraseña"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                required
              />

            </div>

          </div>

          {/* OPCIONES */}
          <div className="login-options">

            <label>

              <input type="checkbox" />

              Recordarme

            </label>

            <a href="/">
              ¿Olvidaste tu contraseña?
            </a>

          </div>

          {/* BOTÓN LOGIN */}
          <button
            type="submit"
            disabled={loading}
          >

            <FaLock className="btn-icon" />

            {loading
              ? "Ingresando..."
              : "Ingresar"}

          </button>

          {/* MENSAJE */}
          {mensaje && (

            <div className="mensaje-login">
              {mensaje}
            </div>

          )}

          {/* DIVISOR */}
          <div className="login-divider">

            <span></span>

            <p>
              o continúa con
            </p>

            <span></span>

          </div>

          {/* INVITADO */}
          <button
            type="button"
            className="guest-button"
            onClick={() => {
                localStorage.setItem(
                "usuario",
                JSON.stringify({
                    nombres: "Invitado",
                    tipo_usuario: "USUARIO",
                    email: "Sin cuenta",
                    foto_perfil: ""
                })
                );

                window.location.href = "/";
            }}
            >
            Acceso como invitado
            </button>

          <p className="copyright">

            © 2025 Comunidad Campesina Zapotal.
            Todos los derechos reservados.

          </p>

        </form>

      </section>

    </div>
  );
}

export default Login;
