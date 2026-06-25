import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api';
import {
  FaUser, FaEnvelope, FaIdCard, FaLock, FaEye, FaEyeSlash,
  FaUserPlus, FaLeaf, FaShieldAlt, FaCheckCircle, FaRedo,
  FaArrowRight, FaCheck, FaTimes, FaKey, FaSpinner, FaExclamationTriangle,
} from 'react-icons/fa';
import Turnstile from '../../components/Turnstile';
import OTPInput from '../../components/OTPInput';
import { useToast } from '../../components/ToastCenter';
import './Registro.css';

const sanitize = (v) => v.replace(/[<>"'`;]/g, '').trimStart();
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const COOLDOWN_REENVIO = 60;

export default function Registro() {
  const navigate = useNavigate();
  const toast = useToast();

  const [form, setForm] = useState({
    nombres: '', apellidos: '', email: '', dni: '',
    password: '', confirmar: '', telefono: '',
  });
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // OTP state
  const [step, setStep] = useState(1); // 1 = form, 2 = otp
  const [usuarioId, setUsuarioId] = useState(null);
  const [otp, setOtp] = useState('');
  const [devOtpCode, setDevOtpCode] = useState('');
  const [cooldown, setCooldown] = useState(0);

  // Turnstile
  const [turnstileToken, setTurnstileToken] = useState('');
  const turnstileRef = useRef(null);

  // ZeroBounce live validation
  const [validacionEmail, setValidacionEmail] = useState({ estado: 'idle', sugerencia: null });
  const debounceEmailRef = useRef(null);

  const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY;

  const setField = (field) => (e) => {
    const val = field === 'dni'
      ? e.target.value.replace(/\D/g, '').slice(0, 8)
      : sanitize(e.target.value);
    setForm((prev) => ({ ...prev, [field]: val }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: '' }));
    if (field === 'email') onEmailChangeValidacion(val);
  };

  const onEmailChangeValidacion = (val) => {
    if (debounceEmailRef.current) clearTimeout(debounceEmailRef.current);
    if (!val || !val.includes('@') || !EMAIL_REGEX.test(val.trim())) {
      setValidacionEmail({ estado: 'idle', sugerencia: null });
      return;
    }
    setValidacionEmail({ estado: 'validando' });
    debounceEmailRef.current = setTimeout(async () => {
      try {
        const { data } = await api.get('/validar-email/', { params: { email: val.trim() } });
        setValidacionEmail({
          estado: data.es_valido ? 'valido' : 'invalido',
          sugerencia: data.did_you_mean || null,
          motivo: data.motivo || null,
        });
      } catch {
        setValidacionEmail({ estado: 'idle' });
      }
    }, 800);
  };

  const validate = () => {
    const e = {};
    if (!form.nombres.trim()) e.nombres = 'Ingresa tus nombres.';
    if (!form.apellidos.trim()) e.apellidos = 'Ingresa tus apellidos.';
    if (!form.email.trim()) e.email = 'Ingresa tu correo electronico.';
    else if (!EMAIL_REGEX.test(form.email.trim())) e.email = 'El formato del correo no es valido.';
    if (!form.dni.trim()) e.dni = 'Ingresa tu DNI.';
    else if (!/^\d{8}$/.test(form.dni.trim())) e.dni = 'El DNI debe tener exactamente 8 digitos.';
    if (!form.password) e.password = 'Ingresa una contrasena.';
    else if (form.password.length < 8) e.password = 'La contrasena debe tener al menos 8 caracteres.';
    else if (!/[A-Z]/.test(form.password)) e.password = 'La contrasena debe incluir una mayuscula.';
    else if (!/\d/.test(form.password)) e.password = 'La contrasena debe incluir un numero.';
    if (!form.confirmar) e.confirmar = 'Confirma tu contrasena.';
    else if (form.password !== form.confirmar) e.confirmar = 'Las contrasenas no coinciden.';
    if (TURNSTILE_SITE_KEY && !turnstileToken) {
      e.turnstile = 'Completa la verificacion antibot antes de continuar.';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const payload = {
        email: form.email.trim(),
        password: form.password,
        dni: form.dni.trim(),
        nombres: form.nombres.trim(),
        apellidos: form.apellidos.trim(),
        telefono: form.telefono || undefined,
        tipo_usuario: 'COMUNERO',
        turnstile_token: turnstileToken || '',
      };
      const { data } = await api.post('/registro/iniciar/', payload, { timeout: 10000 });
      setUsuarioId(data.usuario_id);
      if (data.dev_otp_code) {
        setDevOtpCode(data.dev_otp_code);
        setOtp(data.dev_otp_code);
      }
      if (data.resend) {
        toast.push({
          type: 'info',
          title: 'Tu cuenta ya existe',
          text: data.mensaje || 'Te enviamos un nuevo codigo a tu correo para completar la verificacion.',
          duration: 5000,
        });
      } else {
        toast.push({
          type: 'success',
          text: 'Te enviamos un codigo de verificacion a tu correo.',
          duration: 4000,
        });
      }
      setStep(2);
      setCooldown(COOLDOWN_REENVIO);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Error al registrar. Verifica los datos.';
      toast.push({ type: 'error', text: detail, duration: 5000 });
      if (turnstileRef.current) turnstileRef.current.reset();
      setTurnstileToken('');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const handleVerificarOtp = useCallback(async (codigo) => {
    if (loading) return;
    if (!codigo || codigo.length !== 6) {
      toast.push({ type: 'warning', text: 'Ingresa los 6 digitos del codigo.', duration: 3500 });
      return;
    }
    setLoading(true);
    try {
      await api.post('/registro/verificar-otp/', {
        usuario_id: usuarioId,
        codigo,
      });
      // Guardar en sessionStorage para que App.jsx muestre el toast
      sessionStorage.setItem('pending_approval', JSON.stringify({
        email: form.email.trim(),
        ts: Date.now(),
      }));
      toast.push({
        type: 'success',
        title: 'Cuenta verificada',
        text: 'Tu correo fue confirmado. Tu cuenta esta pendiente de aprobacion.',
        duration: 4000,
      });
      setTimeout(() => navigate('/'), 700);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Codigo incorrecto o expirado.';
      toast.push({ type: 'error', text: detail, duration: 5000 });
      setOtp('');
    } finally {
      setLoading(false);
    }
  }, [loading, usuarioId, form.email, navigate, toast]);

  const handleReenviar = async () => {
    if (cooldown > 0) return;
    if (!usuarioId) return;
    setLoading(true);
    try {
      const { data } = await api.post('/registro/reenviar-otp/', { usuario_id: usuarioId });
      if (data.dev_otp_code) {
        setDevOtpCode(data.dev_otp_code);
        setOtp(data.dev_otp_code);
      }
      toast.push({ type: 'info', text: 'Nuevo codigo enviado a tu correo.', duration: 3500 });
      setCooldown(COOLDOWN_REENVIO);
    } catch (err) {
      const detail = err.response?.data?.detail || 'No se pudo reenviar el codigo.';
      toast.push({ type: 'error', text: detail, duration: 5000 });
    } finally {
      setLoading(false);
    }
  };

  const formatTiempo = (s) => `0:${String(s).padStart(2, '0')}`;

  return (
    <div className="rg">
      <section className="rg-hero">
        <div className="rg-overlay" />
        <div className="rg-hero-body">
          <div className="rg-emblem-wrap">
            <img src="/img/Logo-comunidad/Logo-principal.png" alt="Escudo" className="rg-emblem" />
          </div>
          <h1 className="rg-hero-title">Comunidad<br />Campesina<br />Zapotal</h1>
          <div className="rg-ornament"><span /><FaLeaf /><span /></div>
          <p className="rg-hero-desc">
            Unite a nuestra plataforma digital institucional.
          </p>
          <div className="rg-shield">
            <FaShieldAlt />
            <span>Registro seguro y verificado</span>
          </div>
          <div className="rg-steps">
            <div className={`rg-step ${step >= 1 ? 'rg-step--active' : ''}`}>
              <div className="rg-step-num">1</div><span>Datos</span>
            </div>
            <div className="rg-step-arrow"><FaArrowRight /></div>
            <div className={`rg-step ${step >= 2 ? 'rg-step--active' : ''}`}>
              <div className="rg-step-num">2</div><span>Codigo</span>
            </div>
          </div>
        </div>
      </section>

      <section className="rg-panel">
        {step === 1 && (
          <form className="rg-card" onSubmit={handleSubmit} noValidate>
            <header className="rg-head">
              <div className="rg-deco"><span /><FaLeaf /><span /></div>
              <p className="rg-eyebrow">Paso 1 de 2</p>
              <h2 className="rg-card-title">Tus datos</h2>
              <hr className="rg-rule" />
              <p className="rg-card-sub">
                Completa el formulario. Te enviaremos un codigo de verificacion a tu correo.
              </p>
            </header>

            <div className="rg-fields">
              <div className="rg-row">
                <div className="rg-field">
                  <label htmlFor="rg-nombres">Nombres</label>
                  <div className={`rg-inp ${errors.nombres ? 'rg-inp--error' : ''}`}>
                    <FaUser className="rg-ico" />
                    <input id="rg-nombres" type="text" placeholder="Ej. Juan Carlos"
                      value={form.nombres} onChange={setField('nombres')}
                      autoComplete="given-name" maxLength={60} />
                  </div>
                  {errors.nombres && <span className="rg-field-error" role="alert">{errors.nombres}</span>}
                </div>
                <div className="rg-field">
                  <label htmlFor="rg-apellidos">Apellidos</label>
                  <div className={`rg-inp ${errors.apellidos ? 'rg-inp--error' : ''}`}>
                    <FaUser className="rg-ico" />
                    <input id="rg-apellidos" type="text" placeholder="Ej. Perez Gomez"
                      value={form.apellidos} onChange={setField('apellidos')}
                      autoComplete="family-name" maxLength={60} />
                  </div>
                  {errors.apellidos && <span className="rg-field-error" role="alert">{errors.apellidos}</span>}
                </div>
              </div>

              <div className="rg-field">
                <label htmlFor="rg-email">Correo electronico</label>
                <div className={`rg-inp ${errors.email ? 'rg-inp--error' : ''} ${
                  validacionEmail.estado === 'valido' ? 'rg-inp--ok' :
                  validacionEmail.estado === 'invalido' ? 'rg-inp--warn' : ''
                }`}>
                  <FaEnvelope className="rg-ico" />
                  <input id="rg-email" type="email" placeholder="usuario@ejemplo.com"
                    value={form.email} onChange={setField('email')}
                    autoComplete="email" maxLength={120} />
                  <span className="rg-inp__status" aria-live="polite">
                    {validacionEmail.estado === 'validando' && <FaSpinner className="fa-spin" color="#6b7280" />}
                    {validacionEmail.estado === 'valido' && <FaCheckCircle color="#16a34a" />}
                    {validacionEmail.estado === 'invalido' && validacionEmail.motivo === 'catch-all' && (
                      <FaExclamationTriangle color="#f59e0b" />
                    )}
                    {validacionEmail.estado === 'invalido' && validacionEmail.motivo !== 'catch-all' && (
                      <FaTimes color="#dc2626" />
                    )}
                  </span>
                </div>
                {errors.email && <span className="rg-field-error" role="alert">{errors.email}</span>}
                {validacionEmail.sugerencia && (
                  <span className="rg-email-sugerencia">
                    ¿Quizás quisiste decir:{' '}
                    <button
                      type="button"
                      onClick={() => {
                        setForm((prev) => ({ ...prev, email: validacionEmail.sugerencia }));
                        onEmailChangeValidacion(validacionEmail.sugerencia);
                      }}
                    >
                      {validacionEmail.sugerencia}
                    </button>?
                  </span>
                )}
              </div>

              <div className="rg-row">
                <div className="rg-field">
                  <label htmlFor="rg-dni">DNI</label>
                  <div className={`rg-inp ${errors.dni ? 'rg-inp--error' : ''}`}>
                    <FaIdCard className="rg-ico" />
                    <input id="rg-dni" type="text" inputMode="numeric" placeholder="8 digitos"
                      value={form.dni} onChange={setField('dni')}
                      maxLength={8} />
                  </div>
                  {errors.dni && <span className="rg-field-error" role="alert">{errors.dni}</span>}
                </div>
                <div className="rg-field">
                  <label htmlFor="rg-telefono">Telefono (opcional)</label>
                  <div className="rg-inp">
                    <FaUser className="rg-ico" />
                    <input id="rg-telefono" type="tel" placeholder="+51 999 999 999"
                      value={form.telefono} onChange={setField('telefono')}
                      autoComplete="tel" maxLength={15} />
                  </div>
                </div>
              </div>

              <div className="rg-field">
                <label htmlFor="rg-pass">Contrasena</label>
                <div className={`rg-inp ${errors.password ? 'rg-inp--error' : ''}`}>
                  <FaLock className="rg-ico" />
                  <input id="rg-pass" type={showPass ? 'text' : 'password'} placeholder="Minimo 8, 1 mayuscula, 1 numero"
                    value={form.password} onChange={setField('password')}
                    autoComplete="new-password" maxLength={64} />
                  <button type="button" className="rg-eye" onClick={() => setShowPass((v) => !v)}>
                    {showPass ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                {errors.password && <span className="rg-field-error" role="alert">{errors.password}</span>}
              </div>

              <div className="rg-field">
                <label htmlFor="rg-confirmar">Confirmar contrasena</label>
                <div className={`rg-inp ${errors.confirmar ? 'rg-inp--error' : ''}`}>
                  <FaLock className="rg-ico" />
                  <input id="rg-confirmar" type={showConfirm ? 'text' : 'password'} placeholder="Repite la contrasena"
                    value={form.confirmar} onChange={setField('confirmar')}
                    autoComplete="new-password" maxLength={64} />
                  <button type="button" className="rg-eye" onClick={() => setShowConfirm((v) => !v)}>
                    {showConfirm ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                {errors.confirmar && <span className="rg-field-error" role="alert">{errors.confirmar}</span>}
              </div>

              {TURNSTILE_SITE_KEY && (
                <div className="rg-field">
                  <Turnstile
                    ref={turnstileRef}
                    siteKey={TURNSTILE_SITE_KEY}
                    onVerify={(token) => setTurnstileToken(token)}
                    onExpire={() => setTurnstileToken('')}
                    onError={() => setTurnstileToken('')}
                  />
                  {errors.turnstile && <span className="rg-field-error" role="alert">{errors.turnstile}</span>}
                </div>
              )}
            </div>

            <button type="submit" className="rg-btn-submit" disabled={loading}>
              {loading ? <span className="rg-spinner" /> : <><FaUserPlus /> Registrarme y enviar codigo <FaArrowRight /></>}
            </button>

            <p className="rg-login">
              ¿Ya tienes cuenta? <Link to="/login" className="rg-login-link">Inicia sesion</Link>
            </p>

            <p className="rg-copy">
              © 2026 Comunidad Campesina Zapotal. Todos los derechos reservados.
            </p>
          </form>
        )}

        {step === 2 && (
          <div className="rg-card">
            <header className="rg-head">
              <div className="rg-deco"><span /><FaLeaf /><span /></div>
              <p className="rg-eyebrow">Paso 2 de 2</p>
              <h2 className="rg-card-title">Verifica tu correo</h2>
              <hr className="rg-rule" />
              <p className="rg-card-sub">
                Hemos enviado un codigo de 6 digitos a <strong>{form.email}</strong>.
                Ingresalo a continuacion para activar tu cuenta.
              </p>
            </header>

            <div className="rg-otp-wrap">
              <OTPInput value={otp} onChange={setOtp} onComplete={handleVerificarOtp} disabled={loading} />
              {devOtpCode && (
                <div className="rg-dev-otp">
                  <FaKey /> Codigo (modo dev): <code>{devOtpCode}</code>
                </div>
              )}
            </div>

            <div className="rg-resend">
              <button
                type="button"
                className="rg-btn-resend"
                onClick={handleReenviar}
                disabled={loading || cooldown > 0}
              >
                <FaRedo /> {cooldown > 0 ? `Reenviar en ${formatTiempo(cooldown)}` : 'Reenviar codigo'}
              </button>
            </div>

            <button
              type="button"
              className="rg-btn-submit"
              onClick={() => handleVerificarOtp(otp)}
              disabled={loading || otp.length !== 6}
            >
              {loading ? <span className="rg-spinner" /> : <><FaCheckCircle /> Verificar y continuar <FaArrowRight /></>}
            </button>

            <p className="rg-help">
              Si no recibes el codigo, revisa tu bandeja de spam o espera unos minutos.
            </p>
            <p className="rg-login">
              ¿Ya tienes cuenta? <Link to="/login" className="rg-login-link">Inicia sesion</Link>
            </p>
            <p className="rg-copy">
              © 2026 Comunidad Campesina Zapotal. Todos los derechos reservados.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
