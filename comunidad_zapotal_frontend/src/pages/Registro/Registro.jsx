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
  const [msg, setMsg] = useState({ text: '', type: '' });
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
    <div className="min-h-screen flex flex-col md:flex-row bg-white">
      {/* Hero / Branding — mismo layout, imagen y paleta que Login */}
      <aside
        className="relative md:w-1/2 flex items-center justify-center py-16 md:py-0 bg-cover bg-center"
        style={{ backgroundImage: "url('/img/login/Union-fondo login.jpg')" }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary-950/80 via-primary-900/70 to-primary-800/60" />
        <div className="relative z-10 text-center px-6 max-w-md">
          <div className="mx-auto mb-6 h-28 w-28 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border-2 border-white/30">
            <img src="/img/Logo-comunidad/Logo-principal.png" alt="Escudo" className="h-20 w-20" />
          </div>
          <h1 className="font-display text-3xl md:text-4xl font-bold text-white leading-tight">
            Comunidad Campesina<br />Zapotal
          </h1>
          {/* Adorno con el oro del navbar (mismo que Login) */}
          <div className="my-5 flex items-center justify-center gap-3 text-white/80">
            <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
            <FaLeaf style={{ color: "var(--nb-dorado)" }} />
            <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
          </div>
          <p className="text-white/85 text-base leading-relaxed">
            Unite a nuestra plataforma digital institucional.
          </p>
          <div className="mt-8 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm text-white/90 text-sm border border-white/20">
            <FaShieldAlt className="text-primary-300" />
            <span>Registro seguro y verificado</span>
          </div>
        </div>
      </aside>

      {/* Form — mismo estilo limpio que Login: SIN card con sombra,
          SIN eyebrow "PASO 1 DE 2", SIN shield ni steps. Solo el
          form directo sobre el panel derecho, igual que Login. */}
      <section className="md:w-1/2 flex items-center justify-center p-6 md:p-10 bg-gradient-to-br from-white via-white to-primary-50/30">
        {step === 1 && (
          <form onSubmit={handleSubmit} noValidate className="w-full max-w-md">
            <header className="text-center mb-6">
              {/* Adorno con el oro del navbar (mismo que el hero) */}
              <div className="my-3 flex items-center justify-center gap-3" style={{ color: "var(--nb-dorado)" }}>
                <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
                <FaLeaf />
                <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
              </div>
              <p className="text-sm text-primary-700 uppercase tracking-wider font-semibold">Crear cuenta</p>
              <h2 className="font-display text-3xl font-bold text-primary-800 mt-1">Registrate</h2>
              <hr className="my-3 border-t" style={{ borderColor: "var(--nb-dorado-light)" }} />
              <p className="text-mute text-sm">
                Completa el formulario. Te enviaremos un codigo de verificacion a tu correo.
              </p>
            </header>

            {msg.text && (
              <div role="alert" className={`mb-4 p-3 rounded-lg border text-sm ${
                msg.type === 'success'
                  ? 'bg-primary-50 border-primary-300 text-primary-800'
                  : 'bg-red-50 border-red-300 text-red-800'
              }`}>
                {msg.text}
              </div>
            )}

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="rg-nombres" className="label">Nombres</label>
                  <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                    errors.nombres ? 'border-red-300 bg-red-50' : 'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
                  }`}>
                    <FaUser className="text-secondary-400" />
                    <input id="rg-nombres" type="text" placeholder="Ej. Juan Carlos"
                      value={form.nombres} onChange={setField('nombres')}
                      autoComplete="given-name" maxLength={60}
                      className="flex-1 bg-transparent outline-none text-sm" />
                  </div>
                  {errors.nombres && <span className="block mt-1 text-xs text-red-600 font-medium">{errors.nombres}</span>}
                </div>
                <div>
                  <label htmlFor="rg-apellidos" className="label">Apellidos</label>
                  <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                    errors.apellidos ? 'border-red-300 bg-red-50' : 'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
                  }`}>
                    <FaUser className="text-secondary-400" />
                    <input id="rg-apellidos" type="text" placeholder="Ej. Perez Gomez"
                      value={form.apellidos} onChange={setField('apellidos')}
                      autoComplete="family-name" maxLength={60}
                      className="flex-1 bg-transparent outline-none text-sm" />
                  </div>
                  {errors.apellidos && <span className="block mt-1 text-xs text-red-600 font-medium">{errors.apellidos}</span>}
                </div>
              </div>

              <div>
                <label htmlFor="rg-email" className="label">Correo electronico</label>
                <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                  errors.email ? 'border-red-300 bg-red-50' :
                  validacionEmail.estado === 'valido' ? 'border-green-500 bg-green-50' :
                  validacionEmail.estado === 'invalido' ? 'border-amber-500 bg-amber-50' :
                  'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
                }`}>
                  <FaEnvelope className="text-secondary-400" />
                  <input id="rg-email" type="email" placeholder="usuario@ejemplo.com"
                    value={form.email} onChange={setField('email')}
                    autoComplete="email" maxLength={120}
                    className="flex-1 bg-transparent outline-none text-sm" />
                  <span className="flex items-center" aria-live="polite">
                    {validacionEmail.estado === 'validando' && <FaSpinner className="fa-spin text-gray-500" />}
                    {validacionEmail.estado === 'valido' && <FaCheckCircle className="text-green-600" />}
                    {validacionEmail.estado === 'invalido' && validacionEmail.motivo === 'catch-all' && (
                      <FaExclamationTriangle className="text-amber-500" />
                    )}
                    {validacionEmail.estado === 'invalido' && validacionEmail.motivo !== 'catch-all' && (
                      <FaTimes className="text-red-600" />
                    )}
                  </span>
                </div>
                {errors.email && <span className="block mt-1 text-xs text-red-600 font-medium">{errors.email}</span>}
                {validacionEmail.sugerencia && (
                  <span className="block mt-1 text-xs text-amber-700">
                    ¿Quizás quisiste decir:{' '}
                    <button
                      type="button"
                      onClick={() => {
                        setForm((prev) => ({ ...prev, email: validacionEmail.sugerencia }));
                        onEmailChangeValidacion(validacionEmail.sugerencia);
                      }}
                      className="underline text-primary-800"
                    >
                      {validacionEmail.sugerencia}
                    </button>?
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="rg-dni" className="label">DNI</label>
                  <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                    errors.dni ? 'border-red-300 bg-red-50' : 'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
                  }`}>
                    <FaIdCard className="text-secondary-400" />
                    <input id="rg-dni" type="text" inputMode="numeric" placeholder="8 digitos"
                      value={form.dni} onChange={setField('dni')}
                      maxLength={8}
                      className="flex-1 bg-transparent outline-none text-sm" />
                  </div>
                  {errors.dni && <span className="block mt-1 text-xs text-red-600 font-medium">{errors.dni}</span>}
                </div>
                <div>
                  <label htmlFor="rg-telefono" className="label">Telefono <span className="text-mute normal-case tracking-normal font-normal text-xs">(opcional)</span></label>
                  <div className="flex items-center gap-2 px-3 py-2 border border-secondary-300 rounded-md transition-colors bg-white focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200">
                    <FaUser className="text-secondary-400" />
                    <input id="rg-telefono" type="tel" placeholder="+51 999 999 999"
                      value={form.telefono} onChange={setField('telefono')}
                      autoComplete="tel" maxLength={15}
                      className="flex-1 bg-transparent outline-none text-sm" />
                  </div>
                </div>
              </div>

              <div>
                <label htmlFor="rg-pass" className="label">Contrasena</label>
                <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                  errors.password ? 'border-red-300 bg-red-50' : 'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
                }`}>
                  <FaLock className="text-secondary-400" />
                  <input id="rg-pass" type={showPass ? 'text' : 'password'} placeholder="Minimo 8, 1 mayuscula, 1 numero"
                    value={form.password} onChange={setField('password')}
                    autoComplete="new-password" maxLength={64}
                    className="flex-1 bg-transparent outline-none text-sm" />
                  <button type="button" onClick={() => setShowPass((v) => !v)}
                    className="text-xs text-primary-700 hover:text-primary-900 font-medium px-2"
                    aria-label={showPass ? 'Ocultar contrasena' : 'Mostrar contrasena'}>
                    {showPass ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                {errors.password && <span className="block mt-1 text-xs text-red-600 font-medium">{errors.password}</span>}
              </div>

              <div>
                <label htmlFor="rg-confirmar" className="label">Confirmar contrasena</label>
                <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                  errors.confirmar ? 'border-red-300 bg-red-50' : 'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
                }`}>
                  <FaLock className="text-secondary-400" />
                  <input id="rg-confirmar" type={showConfirm ? 'text' : 'password'} placeholder="Repite la contrasena"
                    value={form.confirmar} onChange={setField('confirmar')}
                    autoComplete="new-password" maxLength={64}
                    className="flex-1 bg-transparent outline-none text-sm" />
                  <button type="button" onClick={() => setShowConfirm((v) => !v)}
                    className="text-xs text-primary-700 hover:text-primary-900 font-medium px-2"
                    aria-label={showConfirm ? 'Ocultar contrasena' : 'Mostrar contrasena'}>
                    {showConfirm ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                {errors.confirmar && <span className="block mt-1 text-xs text-red-600 font-medium">{errors.confirmar}</span>}
              </div>

              {TURNSTILE_SITE_KEY && (
                <div className="mt-2 flex justify-center">
                  <Turnstile
                    ref={turnstileRef}
                    siteKey={TURNSTILE_SITE_KEY}
                    onVerify={(token) => setTurnstileToken(token)}
                    onExpire={() => setTurnstileToken('')}
                    onError={() => setTurnstileToken('')}
                  />
                  {errors.turnstile && <span className="block mt-1 text-xs text-red-600 font-medium">{errors.turnstile}</span>}
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`mt-6 w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-md font-semibold text-sm transition-colors ${
                loading
                  ? 'bg-primary-300 text-white cursor-not-allowed'
                  : 'bg-primary-700 text-white hover:bg-primary-800 active:bg-primary-900'
              }`}
            >
              {loading ? <span className="inline-block w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> : (
                <>
                  <FaUserPlus />
                  <span>Registrarme y enviar codigo</span>
                  <FaArrowRight />
                </>
              )}
            </button>

            <p className="text-center mt-5 text-sm text-mute">
              ¿Ya tienes una cuenta?{' '}
              <Link to="/login" className="text-primary-700 hover:text-primary-900 font-semibold inline-flex items-center gap-1">
                Inicia sesion
              </Link>
            </p>

            <p className="text-center mt-4 text-xs text-soft">
              © 2026 Comunidad Campesina Zapotal. Todos los derechos reservados.
            </p>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={(e) => { e.preventDefault(); handleVerificarOtp(otp); }} noValidate className="w-full max-w-md">
            <header className="text-center mb-6">
              <div className="my-3 flex items-center justify-center gap-3" style={{ color: "var(--nb-dorado)" }}>
                <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
                <FaLeaf />
                <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
              </div>
              <p className="text-sm text-primary-700 uppercase tracking-wider font-semibold">Verificacion</p>
              <h2 className="font-display text-3xl font-bold text-primary-800 mt-1">Confirma tu correo</h2>
              <hr className="my-3 border-t" style={{ borderColor: "var(--nb-dorado-light)" }} />
              <p className="text-mute text-sm">
                Hemos enviado un codigo de 6 digitos a <strong>{form.email}</strong>.
                Ingresalo a continuacion para activar tu cuenta.
              </p>
            </header>

            <div className="space-y-4">
              <div>
                <label htmlFor="rg-otp" className="label">Codigo de verificacion</label>
                <div className="flex justify-center mt-1">
                  <OTPInput value={otp} onChange={setOtp} onComplete={handleVerificarOtp} disabled={loading} />
                </div>
                {devOtpCode && (
                  <p className="mt-2 text-xs text-center text-mute">
                    <FaKey className="inline-block mr-1" /> Codigo (modo dev): <code className="px-1 py-0.5 bg-secondary-100 rounded">{devOtpCode}</code>
                  </p>
                )}
                {errors.otp && <span className="block mt-1 text-xs text-red-600 font-medium text-center">{errors.otp}</span>}
              </div>

              <div className="text-center">
                <button
                  type="button"
                  onClick={handleReenviar}
                  disabled={loading || cooldown > 0}
                  className="text-sm text-primary-700 hover:text-primary-900 font-medium disabled:text-mute disabled:cursor-not-allowed inline-flex items-center gap-1"
                >
                  <FaRedo /> {cooldown > 0 ? `Reenviar en ${formatTiempo(cooldown)}` : 'Reenviar codigo'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || otp.length !== 6}
              className={`mt-6 w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-md font-semibold text-sm transition-colors ${
                loading || otp.length !== 6
                  ? 'bg-primary-300 text-white cursor-not-allowed'
                  : 'bg-primary-700 text-white hover:bg-primary-800 active:bg-primary-900'
              }`}
            >
              {loading ? <span className="inline-block w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> : (
                <>
                  <FaCheckCircle />
                  <span>Verificar y continuar</span>
                  <FaArrowRight />
                </>
              )}
            </button>

            <p className="text-center mt-4 text-xs text-mute">
              Si no recibes el codigo, revisa tu bandeja de spam.
            </p>

            <p className="text-center mt-5 text-sm text-mute">
              ¿Ya tienes una cuenta?{' '}
              <Link to="/login" className="text-primary-700 hover:text-primary-900 font-semibold inline-flex items-center gap-1">
                Inicia sesion
              </Link>
            </p>

            <p className="text-center mt-4 text-xs text-soft">
              © 2026 Comunidad Campesina Zapotal. Todos los derechos reservados.
            </p>
          </form>
        )}
      </section>
    </div>
  );
}
