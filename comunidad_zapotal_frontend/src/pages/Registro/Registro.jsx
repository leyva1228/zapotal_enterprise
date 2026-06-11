import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../api";
import {
  FaUser,
  FaEnvelope,
  FaIdCard,
  FaLock,
  FaEye,
  FaEyeSlash,
  FaUserPlus,
  FaLeaf,
  FaShieldAlt,
  FaArrowRight,
  FaCheckCircle,
} from "react-icons/fa";
import "./Registro.css";

/* ── Sanitiza entradas contra XSS básico ── */
const sanitize = (v) => v.replace(/[<>"'`;]/g, "").trimStart();

/* ── Regex de correo ── */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function Registro() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    nombres: "",
    apellidos: "",
    email: "",
    dni: "",
    password: "",
    confirmar: "",
  });

  const [showPass, setShowPass]         = useState(false);
  const [showConfirm, setShowConfirm]   = useState(false);
  const [loading, setLoading]           = useState(false);
  const [msg, setMsg]                   = useState({ text: "", type: "" });

  /* ── Errores de campo individuales ── */
  const [errors, setErrors] = useState({});

  /* ─────────────── Handlers ─────────────── */

  const setField = (field) => (e) => {
    const val = field === "dni"
      ? e.target.value.replace(/\D/g, "").slice(0, 8) // solo dígitos
      : sanitize(e.target.value);

    setForm((prev) => ({ ...prev, [field]: val }));

    /* Limpia error del campo al editar */
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  /* ── Validación completa antes de enviar ── */
  const validate = () => {
    const newErrors = {};

    if (!form.nombres.trim())
      newErrors.nombres = "Ingresa tus nombres.";

    if (!form.apellidos.trim())
      newErrors.apellidos = "Ingresa tus apellidos.";

    if (!form.email.trim())
      newErrors.email = "Ingresa tu correo electrónico.";
    else if (!EMAIL_REGEX.test(form.email.trim()))
      newErrors.email = "El formato del correo no es válido.";

    if (!form.dni.trim())
      newErrors.dni = "Ingresa tu DNI.";
    else if (!/^\d{8}$/.test(form.dni.trim()))
      newErrors.dni = "El DNI debe tener exactamente 8 dígitos.";

    if (!form.password)
      newErrors.password = "Ingresa una contraseña.";
    else if (form.password.length < 6)
      newErrors.password = "La contraseña debe tener al menos 6 caracteres.";

    if (!form.confirmar)
      newErrors.confirmar = "Confirma tu contraseña.";
    else if (form.password !== form.confirmar)
      newErrors.confirmar = "Las contraseñas no coinciden.";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /* ── Submit ── */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg({ text: "", type: "" });

    if (!validate()) return;

    setLoading(true);

    try {
      const payload = new FormData();
      payload.append("nombres",      form.nombres.trim());
      payload.append("apellidos",    form.apellidos.trim());
      payload.append("email",        form.email.trim());
      payload.append("dni",          form.dni.trim());
      payload.append("password",     form.password);
      payload.append("tipo_usuario", "COMUNERO");

      await api.post(`/usuarios/`, payload, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 10000,
      });

      setMsg({ text: "¡Registro exitoso! Redirigiendo al inicio de sesión…", type: "success" });

      setTimeout(() => navigate("/login"), 1800);

    } catch (err) {
      if (err.code === "ECONNABORTED") {
        setMsg({ text: "El servidor tardó demasiado. Verifica tu conexión.", type: "error" });
      } else if (err.response) {
        const detail = err.response.data?.detail
          || err.response.data?.email?.[0]
          || err.response.data?.dni?.[0]
          || "Error al registrar. Verifica los datos ingresados.";
        setMsg({ text: detail, type: "error" });
      } else if (err.request) {
        setMsg({ text: "No se pudo conectar con el servidor. Verifica tu conexión.", type: "error" });
      } else {
        setMsg({ text: "Ocurrió un error inesperado. Intenta nuevamente.", type: "error" });
      }
    } finally {
      setLoading(false);
    }
  };

  /* ─────────────── JSX ─────────────── */
  return (
    <div className="rg">

      {/* ── Panel izquierdo: hero institucional ── */}
      <section className="rg-hero">
        <div className="rg-overlay" />
        <div className="rg-hero-body">

          <div className="rg-emblem-wrap">
            <img
              src="/img/Logo-comunidad/Logo-principal.png"
              alt="Escudo Comunidad Campesina Zapotal"
              className="rg-emblem"
            />
          </div>

          <h1 className="rg-hero-title">
            Comunidad<br />Campesina<br />Zapotal
          </h1>

          <div className="rg-ornament">
            <span /><FaLeaf /><span />
          </div>

          <p className="rg-hero-desc">
            Únete a nuestra plataforma digital institucional y forma
            parte activa de la comunidad.
          </p>

          <div className="rg-shield">
            <FaShieldAlt />
            <span>Registro seguro y verificado</span>
          </div>

          {/* Pasos del proceso */}
          <div className="rg-steps">
            <div className="rg-step">
              <div className="rg-step-num">1</div>
              <span>Completa tus datos</span>
            </div>
            <div className="rg-step-arrow"><FaArrowRight /></div>
            <div className="rg-step">
              <div className="rg-step-num">2</div>
              <span>Verifica tu correo</span>
            </div>
            <div className="rg-step-arrow"><FaArrowRight /></div>
            <div className="rg-step">
              <div className="rg-step-num">3</div>
              <span>Accede a la plataforma</span>
            </div>
          </div>

        </div>
      </section>

      {/* ── Panel derecho: formulario ── */}
      <section className="rg-panel">
        <form className="rg-card" onSubmit={handleSubmit} noValidate>

          {/* Cabecera */}
          <header className="rg-head">
            <div className="rg-deco"><span /><FaLeaf /><span /></div>
            <p className="rg-eyebrow">Crear cuenta</p>
            <h2 className="rg-card-title">Registro</h2>
            <hr className="rg-rule" />
            <p className="rg-card-sub">
              Completa el formulario para unirte a la plataforma institucional.
            </p>
          </header>

          {/* ── Campos ── */}
          <div className="rg-fields">

            {/* Fila: Nombres + Apellidos */}
            <div className="rg-row">
              <div className="rg-field">
                <label htmlFor="rg-nombres">Nombres</label>
                <div className={`rg-inp ${errors.nombres ? "rg-inp--error" : ""}`}>
                  <FaUser className="rg-ico" aria-hidden="true" />
                  <input
                    id="rg-nombres"
                    type="text"
                    placeholder="Ej. Juan Carlos"
                    value={form.nombres}
                    onChange={setField("nombres")}
                    autoComplete="given-name"
                    maxLength={60}
                  />
                </div>
                {errors.nombres && (
                  <span className="rg-field-error" role="alert">{errors.nombres}</span>
                )}
              </div>

              <div className="rg-field">
                <label htmlFor="rg-apellidos">Apellidos</label>
                <div className={`rg-inp ${errors.apellidos ? "rg-inp--error" : ""}`}>
                  <FaUser className="rg-ico" aria-hidden="true" />
                  <input
                    id="rg-apellidos"
                    type="text"
                    placeholder="Ej. García López"
                    value={form.apellidos}
                    onChange={setField("apellidos")}
                    autoComplete="family-name"
                    maxLength={60}
                  />
                </div>
                {errors.apellidos && (
                  <span className="rg-field-error" role="alert">{errors.apellidos}</span>
                )}
              </div>
            </div>

            {/* Correo */}
            <div className="rg-field">
              <label htmlFor="rg-email">Correo electrónico</label>
              <div className={`rg-inp ${errors.email ? "rg-inp--error" : ""}`}>
                <FaEnvelope className="rg-ico" aria-hidden="true" />
                <input
                  id="rg-email"
                  type="email"
                  placeholder="usuario@ejemplo.com"
                  value={form.email}
                  onChange={setField("email")}
                  autoComplete="email"
                  maxLength={120}
                />
              </div>
              {errors.email && (
                <span className="rg-field-error" role="alert">{errors.email}</span>
              )}
            </div>

            {/* DNI */}
            <div className="rg-field">
              <label htmlFor="rg-dni">
                DNI
                <span className="rg-label-hint">8 dígitos</span>
              </label>
              <div className={`rg-inp ${errors.dni ? "rg-inp--error" : ""}`}>
                <FaIdCard className="rg-ico" aria-hidden="true" />
                <input
                  id="rg-dni"
                  type="text"
                  inputMode="numeric"
                  placeholder="12345678"
                  value={form.dni}
                  onChange={setField("dni")}
                  maxLength={8}
                />
                {form.dni.length === 8 && (
                  <FaCheckCircle className="rg-check" aria-hidden="true" />
                )}
              </div>
              {errors.dni && (
                <span className="rg-field-error" role="alert">{errors.dni}</span>
              )}
            </div>

            {/* Contraseña */}
            <div className="rg-field">
              <label htmlFor="rg-password">Contraseña</label>
              <div className={`rg-inp ${errors.password ? "rg-inp--error" : ""}`}>
                <FaLock className="rg-ico" aria-hidden="true" />
                <input
                  id="rg-password"
                  type={showPass ? "text" : "password"}
                  placeholder="Mínimo 6 caracteres"
                  value={form.password}
                  onChange={setField("password")}
                  autoComplete="new-password"
                  maxLength={64}
                />
                <button
                  type="button"
                  className="rg-eye"
                  onClick={() => setShowPass((v) => !v)}
                  aria-label={showPass ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {showPass ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
              {/* Barra de fortaleza */}
              {form.password.length > 0 && (
                <PasswordStrength password={form.password} />
              )}
              {errors.password && (
                <span className="rg-field-error" role="alert">{errors.password}</span>
              )}
            </div>

            {/* Confirmar contraseña */}
            <div className="rg-field">
              <label htmlFor="rg-confirmar">Confirmar contraseña</label>
              <div className={`rg-inp ${errors.confirmar ? "rg-inp--error" : ""}`}>
                <FaLock className="rg-ico" aria-hidden="true" />
                <input
                  id="rg-confirmar"
                  type={showConfirm ? "text" : "password"}
                  placeholder="Repite tu contraseña"
                  value={form.confirmar}
                  onChange={setField("confirmar")}
                  autoComplete="new-password"
                  maxLength={64}
                />
                <button
                  type="button"
                  className="rg-eye"
                  onClick={() => setShowConfirm((v) => !v)}
                  aria-label={showConfirm ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {showConfirm ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
              {errors.confirmar && (
                <span className="rg-field-error" role="alert">{errors.confirmar}</span>
              )}
            </div>

          </div>{/* /rg-fields */}

          {/* Botón principal */}
          <button
            type="submit"
            className="rg-btn-submit"
            disabled={loading}
          >
            {loading ? (
              <span className="rg-spinner" />
            ) : (
              <>
                <FaUserPlus aria-hidden="true" />
                <span>Crear cuenta</span>
                <FaArrowRight className="rg-arr" aria-hidden="true" />
              </>
            )}
          </button>

          {/* Mensaje global */}
          {msg.text && (
            <div className={`rg-msg rg-msg--${msg.type}`} role="alert">
              {msg.text}
            </div>
          )}

          {/* Link a login */}
          <p className="rg-login">
            ¿Ya tienes una cuenta?{" "}
            <Link to="/login" className="rg-login-link">
              Iniciar sesión
            </Link>
          </p>

          <p className="rg-copy">
            © 2025 Comunidad Campesina Zapotal. Todos los derechos reservados.
          </p>

        </form>
      </section>

    </div>
  );
}

/* ── Subcomponente: barra de fortaleza de contraseña ── */
function PasswordStrength({ password }) {
  const getScore = (p) => {
    let score = 0;
    if (p.length >= 6)  score++;
    if (p.length >= 10) score++;
    if (/[A-Z]/.test(p)) score++;
    if (/[0-9]/.test(p)) score++;
    if (/[^A-Za-z0-9]/.test(p)) score++;
    return score;
  };

  const score = getScore(password);
  const levels = [
    { label: "Muy débil",  color: "#ef4444" },
    { label: "Débil",      color: "#f97316" },
    { label: "Regular",    color: "#eab308" },
    { label: "Buena",      color: "#22c55e" },
    { label: "Excelente",  color: "#16a34a" },
  ];
  const level = levels[Math.min(score - 1, 4)] || levels[0];

  return (
    <div className="rg-strength">
      <div className="rg-strength-bars">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className="rg-strength-bar"
            style={{ background: i <= score ? level.color : undefined }}
          />
        ))}
      </div>
      <span className="rg-strength-label" style={{ color: level.color }}>
        {level.label}
      </span>
    </div>
  );
}

export default Registro;
