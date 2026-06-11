import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import {
  FaEnvelope, FaLock, FaUser, FaShieldAlt,
  FaLeaf, FaUserPlus, FaEye, FaEyeSlash,
  FaArrowRight, FaExclamationTriangle,
} from "react-icons/fa";
import "./Login.css";

const API_URL      = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1"; 
const MAX_INTENTOS = 10;
const BLOQUEO_MS   = 5 * 60 * 1000;
const STORAGE_KEY  = "lp_intentos";

const sanitize = (v) => v.replace(/[<>"'`;]/g, "").trimStart();

const leerContador = () => {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return { intentos: 0, bloqueadoHasta: null };
    return JSON.parse(raw);
  } catch {
    return { intentos: 0, bloqueadoHasta: null };
  }
};

const guardarContador = (data) => {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
};

const resetContador = () => {
  sessionStorage.removeItem(STORAGE_KEY);
};

function Login() {
  const [form, setForm]         = useState({ email: "", password: "" });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [msg, setMsg]           = useState({ text: "", type: "" });
  const [intentos, setIntentos] = useState(0);
  const [bloqueado, setBloqueado]           = useState(false);
  const [tiempoRestante, setTiempoRestante] = useState(0);

  useEffect(() => {
    const { intentos: i, bloqueadoHasta } = leerContador();
    if (bloqueadoHasta && Date.now() < bloqueadoHasta) {
      setBloqueado(true);
      setIntentos(i);
      iniciarCuentaRegresiva(bloqueadoHasta);
    } else if (bloqueadoHasta && Date.now() >= bloqueadoHasta) {
      resetContador();
    } else {
      setIntentos(i);
    }
  }, []);

  const iniciarCuentaRegresiva = (hasta) => {
    const tick = () => {
      const restante = Math.max(0, hasta - Date.now());
      setTiempoRestante(Math.ceil(restante / 1000));
      if (restante <= 0) {
        setBloqueado(false);
        setIntentos(0);
        setMsg({ text: "", type: "" });
        resetContador();
      } else {
        setTimeout(tick, 1000);
      }
    };
    tick();
  };

  const formatTiempo = (seg) => {
    const m = Math.floor(seg / 60);
    const s = seg % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  };

  const setField = (f) => (e) => {
    const val = sanitize(e.target.value);
    setForm((p) => ({ ...p, [f]: val }));
  };

  const showMsg = (text, type = "error") => setMsg({ text, type });

  const limpiarCampos = () => setForm({ email: "", password: "" });

  const registrarFallo = () => {
    const { intentos: prev } = leerContador();
    const nuevos = prev + 1;
    setIntentos(nuevos);

    if (nuevos >= MAX_INTENTOS) {
      const hasta = Date.now() + BLOQUEO_MS;
      guardarContador({ intentos: nuevos, bloqueadoHasta: hasta });
      setBloqueado(true);
      limpiarCampos();
      showMsg("Límite de intentos excedido. Inténtelo nuevamente más tarde.", "blocked");
      iniciarCuentaRegresiva(hasta);
    } else {
      guardarContador({ intentos: nuevos, bloqueadoHasta: null });
      limpiarCampos();
      showMsg("Correo o contraseña incorrectos.", "error");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    if (bloqueado) return;

    const emailVal = form.email.trim();
    const passVal  = form.password.trim();

    if (!emailVal) return showMsg("Ingresa tu correo electrónico.");
    if (!passVal)  return showMsg("Ingresa tu contraseña.");

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailVal)) {
      return registrarFallo();
    }

    if (passVal.length < 6) {
      return registrarFallo();
    }

    setLoading(true);
    setMsg({ text: "", type: "" });

    try {
      const { data } = await axios.post(
        `${API_URL}/login/`,
        { email: emailVal, password: passVal },
        { timeout: 10000 }
      );

      // Verificar si el backend indica éxito
      if (!data.ok) {
        registrarFallo();
        return;
      }

      const ud = data.usuario;
      if (!ud) {
        limpiarCampos();
        return showMsg("Respuesta inesperada del servidor.");
      }

      // Construir objeto usuario con los campos que vienen del backend
      const usuario = {
        id:           ud.id,
        email:        ud.email,
        nombres:      ud.nombres      || "",
        apellidos:    ud.apellidos    || "",
        tipo_usuario: ud.tipo_usuario || "COMUNERO",
        foto_perfil:  ud.foto_perfil_url || ud.foto_perfil || "",
        dni:          ud.dni          || null,
        token:        data.token      || null,
      };

      localStorage.setItem("usuario", JSON.stringify(usuario));
      if (data.token) localStorage.setItem("token", data.token);

      if (!localStorage.getItem("usuario")) {
        limpiarCampos();
        return showMsg("No se pudo guardar la sesión. Intenta nuevamente.");
      }

      resetContador();
      showMsg("¡Bienvenido! Ingreso correcto.", "success");

      // Redirección según rol (mejora)
      setTimeout(() => {
        const accionPendiente = localStorage.getItem("accionPendiente");
        if (accionPendiente) {
          try {
            const a = JSON.parse(accionPendiente);
            window.location.href = a.noticiaId ? `/noticias/${a.noticiaId}` : "/";
            localStorage.removeItem("accionPendiente");
          } catch {
            window.location.href = "/";
          }
        } else if (usuario.tipo_usuario === "ADMIN") {
          window.location.href = "/admin";
        } else {
          window.location.href = "/";
        }
      }, 1200);

    } catch (err) {
      if (err.code === "ECONNABORTED") {
        limpiarCampos();
        showMsg("El servidor tardó demasiado. Verifica tu conexión.");
      } else if (err.response) {
        const status = err.response.status;
        if (status === 401 || status === 400) {
          registrarFallo();
        } else if (status === 403) {
          limpiarCampos();
          showMsg("Tu cuenta ha sido suspendida. Contacta al administrador.", "blocked");
        } else if (status >= 500) {
          limpiarCampos();
          showMsg("Error en el servidor. Intenta más tarde.");
        } else {
          registrarFallo();
        }
      } else if (err.request) {
        limpiarCampos();
        showMsg("No se pudo conectar con el servidor. Verifica tu conexión.");
      } else {
        limpiarCampos();
        showMsg("Ocurrió un error inesperado. Intenta nuevamente.");
      }
    } finally {
      setLoading(false);
    }
  };

  const accesoInvitado = () => {
    localStorage.setItem("usuario", JSON.stringify({
      id: null, nombres: "Invitado", apellidos: "",
      email: "invitado@temporal.com", tipo_usuario: "INVITADO",
      foto_perfil: "", esInvitado: true,
    }));
    localStorage.removeItem("token");
    showMsg("Accediendo como invitado. No podrás comentar ni reaccionar.", "info");
    setTimeout(() => { window.location.href = "/"; }, 1000);
  };

  return (
    <div className="lp">

      <section className="lp-hero">
        <div className="lp-overlay" />
        <div className="lp-hero-body">
          <div className="lp-emblem-wrap">
            <img
              src="/img/Logo-comunidad/Logo-principal.png"
              alt="Escudo Comunidad Campesina Zapotal"
              className="lp-emblem"
            />
          </div>
          <h1 className="lp-hero-title">
            Comunidad<br />Campesina<br />Zapotal
          </h1>
          <div className="lp-ornament">
            <span /><FaLeaf /><span />
          </div>
          <p className="lp-hero-desc">
            Plataforma digital institucional diseñada para la gestión eficiente, la comunicación transparente y la participación activa de los comuneros.  
            Un espacio seguro que fortalece la identidad comunitaria y facilita el acceso a información relevante y servicios en línea.  
          </p>
          <div className="lp-shield">
            <FaShieldAlt /><span>Acceso seguro y autorizado</span>
          </div>
        </div>
      </section>

      <section className="lp-panel">
        <form className="lp-card" onSubmit={handleLogin} noValidate>

          <header className="lp-head">
            <div className="lp-deco"><span /><FaLeaf /><span /></div>
            <p className="lp-eyebrow">Bienvenido</p>
            <h2 className="lp-card-title">Iniciar Sesión</h2>
            <hr className="lp-rule" />
            <p className="lp-card-sub">
              Ingresa tus credenciales para acceder a la plataforma institucional.
            </p>
          </header>

          {bloqueado && (
            <div className="lp-bloqueo-banner">
              <FaExclamationTriangle />
              <div>
                <strong>Acceso bloqueado temporalmente</strong>
                <p>Podrás intentarlo nuevamente en <strong>{formatTiempo(tiempoRestante)}</strong>.</p>
              </div>
            </div>
          )}

          <div className="lp-fields">
            <div className="lp-field">
              <label htmlFor="lp-email">Correo electrónico</label>
              <div className={`lp-inp ${bloqueado ? "lp-inp--disabled" : ""}`}>
                <FaEnvelope className="lp-ico" aria-hidden="true" />
                <input
                  id="lp-email"
                  type="email"
                  placeholder="usuario@ejemplo.com"
                  value={form.email}
                  onChange={setField("email")}
                  autoComplete="email"
                  disabled={bloqueado}
                  maxLength={120}
                  required
                />
              </div>
            </div>

            <div className="lp-field">
              <label htmlFor="lp-pass">Contraseña</label>
              <div className={`lp-inp ${bloqueado ? "lp-inp--disabled" : ""}`}>
                <FaLock className="lp-ico" aria-hidden="true" />
                <input
                  id="lp-pass"
                  type={showPass ? "text" : "password"}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={setField("password")}
                  autoComplete="current-password"
                  disabled={bloqueado}
                  maxLength={64}
                  required
                />
                {!bloqueado && (
                  <button
                    type="button"
                    className="lp-eye"
                    onClick={() => setShowPass((v) => !v)}
                    aria-label={showPass ? "Ocultar contraseña" : "Mostrar contraseña"}
                  >
                    {showPass ? <FaEyeSlash /> : <FaEye />}
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="lp-opts">
            <label className="lp-remember">
              <input type="checkbox" disabled={bloqueado} /><span>Recordarme</span>
            </label>
            <Link to="/recuperar-password" className="lp-forgot">¿Olvidaste tu contraseña?</Link>
          </div>

          <button
            type="submit"
            className={`lp-btn-submit ${bloqueado ? "lp-btn-submit--blocked" : ""}`}
            disabled={loading || bloqueado}
          >
            {loading
              ? <span className="lp-spinner" />
              : bloqueado
                ? <><FaLock aria-hidden="true" /><span>Bloqueado {formatTiempo(tiempoRestante)}</span></>
                : <><FaLock aria-hidden="true" /><span>Ingresar</span><FaArrowRight className="lp-arr" aria-hidden="true" /></>
            }
          </button>

          {msg.text && (
            <div className={`lp-msg lp-msg--${msg.type}`} role="alert">
              {msg.text}
            </div>
          )}

          <div className="lp-sep"><span /><em>o continúa como</em><span /></div>

          <button
            type="button"
            className="lp-btn-guest"
            onClick={accesoInvitado}
            disabled={loading}
          >
            <FaUser aria-hidden="true" /><span>Acceso como invitado</span>
          </button>

          <p className="lp-reg">
            ¿No tienes una cuenta?{" "}
            <Link to="/registro" className="lp-reg-link">
              <FaUserPlus aria-hidden="true" /> Regístrate aquí
            </Link>
          </p>

          <p className="lp-copy">
            © 2025 Comunidad Campesina Zapotal. Todos los derechos reservados.
          </p>

        </form>
      </section>

    </div>
  );
}

export default Login;
