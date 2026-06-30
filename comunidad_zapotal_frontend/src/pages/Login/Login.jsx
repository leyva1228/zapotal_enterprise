import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import api from '../../api';
import { useAuth } from '../../context/AuthContext';
import {
  FaEnvelope, FaLock, FaShieldAlt, FaLeaf, FaUserPlus,
  FaEye, FaEyeSlash, FaArrowRight, FaExclamationTriangle,
} from 'react-icons/fa';
import Turnstile from '../../components/auth/Turnstile/Turnstile';

const MAX_INTENTOS = 10;
const BLOQUEO_MS = 5 * 60 * 1000;
const STORAGE_KEY = 'lp_intentos';
const ANTIBOT_KEY = 'lp_antibot_count';
const ANTIBOT_EVERY = 5;

const sanitize = (v) => v.replace(/[<>"'`;]/g, '').trimStart();

function leerContador() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return { intentos: 0, bloqueadoHasta: null };
    return JSON.parse(raw);
  } catch (e) {
    return { intentos: 0, bloqueadoHasta: null };
  }
}
function guardarContador(data) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}
function resetContador() {
  sessionStorage.removeItem(STORAGE_KEY);
}

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setAuth, setLoading } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLocalLoading] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: '' });
  const [intentos, setIntentos] = useState(0);
  const [bloqueado, setBloqueado] = useState(false);
  const [tiempoRestante, setTiempoRestante] = useState(0);
  const [antibotCount, setAntibotCount] = useState(0);
  const [mostrarAntibot, setMostrarAntibot] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState('');

  React.useEffect(() => {
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
    try {
      const raw = localStorage.getItem(ANTIBOT_KEY);
      const c = raw ? parseInt(raw, 10) : 0;
      setAntibotCount(Number.isFinite(c) ? c : 0);
      setMostrarAntibot((Number.isFinite(c) ? c : 0) > 0 && (Number.isFinite(c) ? c : 0) % ANTIBOT_EVERY === 0);
    } catch (e) { /* noop */ }
  }, []);

  const iniciarCuentaRegresiva = (hasta) => {
    const tick = () => {
      const restante = Math.max(0, hasta - Date.now());
      setTiempoRestante(Math.ceil(restante / 1000));
      if (restante <= 0) {
        setBloqueado(false);
        setIntentos(0);
        setMsg({ text: '', type: '' });
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
    return `${m}:${String(s).padStart(2, '0')}`;
  };

  const setField = (f) => (e) => {
    const val = sanitize(e.target.value);
    setForm((p) => ({ ...p, [f]: val }));
  };

  const showMsg = (text, type = 'error') => setMsg({ text, type });

  const limpiarCampos = () => setForm({ email: '', password: '' });

  const registrarFallo = () => {
    const { intentos: prev } = leerContador();
    const nuevos = prev + 1;
    setIntentos(nuevos);
    if (nuevos >= MAX_INTENTOS) {
      const hasta = Date.now() + BLOQUEO_MS;
      guardarContador({ intentos: nuevos, bloqueadoHasta: hasta });
      setBloqueado(true);
      limpiarCampos();
      showMsg('Limite de intentos excedido. Intentelo nuevamente mas tarde.', 'blocked');
      iniciarCuentaRegresiva(hasta);
    } else {
      guardarContador({ intentos: nuevos, bloqueadoHasta: null });
      limpiarCampos();
      showMsg('Correo o contrasena incorrectos.', 'error');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (bloqueado) return;
    const emailVal = form.email.trim();
    const passVal = form.password.trim();
    if (!emailVal) return showMsg('Ingresa tu correo electronico.');
    if (!passVal) return showMsg('Ingresa tu contrasena.');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailVal)) return registrarFallo();
    if (passVal.length < 6) return registrarFallo();

    setLocalLoading(true);
    setMsg({ text: '', type: '' });
    setLoading(true);

    try {
      let data;
      try {
        const resp = await api.post('/auth/login/', { email: emailVal, password: passVal }, { timeout: 10000 });
        data = resp.data;
      } catch (e) {
        if (e.response?.status === 202 && e.response?.data?.requires_2fa) {
          navigate('/2fa', { state: { tokenTemp: e.response.data.token_temp, usuarioId: e.response.data.usuario_id, email: emailVal } });
          return;
        }
        if (e.response?.status === 202) {
          navigate('/2fa', { state: { tokenTemp: e.response.data.token_temp, usuarioId: e.response.data.usuario_id, email: emailVal } });
          return;
        }
        if (e.response?.status === 401) { registrarFallo(); return; }
        if (e.response?.status === 403) {
          const data = e.response?.data || {};
          const code = data.code || data.error?.code;
          if (code === 'USER_BLOCKED') { navigate('/cuenta/bloqueada'); return; }
          if (code === 'USER_REJECTED') { navigate('/cuenta/rechazada'); return; }
          if (code === 'USER_PENDING_OTP') {
            showMsg('Tu cuenta esta esperando verificacion de codigo. Ve a Registro para reenviar.', 'warning');
            setTimeout(() => navigate('/registro'), 2500);
            return;
          }
          if (code === 'USER_INACTIVE') {
            showMsg('Tu cuenta esta inactiva. Contacta al administrador.', 'blocked');
            return;
          }
          showMsg('Tu cuenta ha sido suspendida. Contacta al administrador.', 'blocked');
          return;
        }
        throw e;
      }

      if (data?.requires_2fa) {
        navigate('/2fa', { state: { tokenTemp: data.token_temp, usuarioId: data.usuario_id, email: emailVal } });
        return;
      }

      const ud = data.usuario;
      if (!ud) { registrarFallo(); return; }
      const usuario = {
        id: ud.id, email: ud.email,
        nombres: ud.nombres || '', apellidos: ud.apellidos || '',
        tipo_usuario: ud.tipo_usuario || 'COMUNERO',
        estado: ud.estado,
        es_admin: ud.es_admin === true,
        es_autoridad: ud.es_autoridad === true,
        autoridad_cargo: ud.autoridad_cargo || null,
        foto_perfil: ud.foto_perfil || ud.foto_perfil_url || '',
        dni: ud.dni || null,
      };
      setAuth({ user: usuario, access: data.access, refresh: data.refresh });
      resetContador();
      showMsg('Bienvenido. Ingreso correcto.', 'success');
      const from = location.state?.from;
      setTimeout(() => {
        if (from && !from.startsWith('/admin') && !ud.es_admin) {
          navigate(from);
        } else if (ud.tipo_usuario === 'ADMIN' || ud.es_admin) {
          navigate('/admin');
        } else {
          navigate('/');
        }
      }, 600);
    } catch (err) {
      showMsg('No se pudo conectar con el servidor. Verifica tu conexion.');
    } finally {
      setLocalLoading(false);
      setLoading(false);
      setTurnstileToken('');
    }
  };

  // Antibot counter effect: show Turnstile every N failed attempts
  React.useEffect(() => {
    if (antibotCount > 0 && antibotCount % ANTIBOT_EVERY === 0) {
      setMostrarAntibot(true);
    }
  }, [antibotCount]);

  const msgClass = msg.type === 'success'
    ? 'bg-primary-50 border-primary-300 text-primary-800'
    : msg.type === 'warning'
      ? 'bg-accent-50 border-accent-300 text-accent-800'
      : msg.type === 'blocked'
        ? 'bg-red-50 border-red-300 text-red-800'
        : 'bg-red-50 border-red-300 text-red-800';

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-white">
      {/* Hero / Branding — mismo layout y paleta que Registro */}
      <aside
        className="relative md:w-1/2 flex items-center justify-center py-16 md:py-0 bg-cover bg-center"
        style={{ backgroundImage: "url('/img/login/Union-fondo login.jpg')" }}
      >
        <div className="absolute inset-0 bg-black/30" />
          <div className="relative z-10 text-center px-6 max-w-md">
            <div className="mx-auto mb-6 h-28 w-28 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border-2 border-white/30">
              <img src="/img/Logo-comunidad/Logo-principal.png" alt="Escudo" className="h-20 w-20" />
            </div>
            <h1
              className="font-display text-3xl md:text-4xl font-bold text-white leading-tight"
              style={{ textShadow: "0 0 8px rgba(184, 150, 62, 0.85), 0 1px 3px rgba(0, 0, 0, 0.15)" }}
            >
              Comunidad Campesina<br />Niño Dios de Zapotal
            </h1>
            {/* Adorno con el oro del navbar (--nb-dorado / --nb-dorado-light) */}
            <div className="my-5 flex items-center justify-center gap-3 text-white/80">
              <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
              <FaLeaf style={{ color: "var(--nb-dorado)" }} />
              <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
            </div>
            <p className="text-white/85 text-base leading-relaxed">
              Plataforma digital institucional para la gestion eficiente y transparente.
            </p>
            <div className="mt-8 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm text-white/90 text-sm border border-white/20">
              <FaShieldAlt className="text-primary-300" />
              <span>Acceso seguro y autorizado</span>
            </div>
          </div>
      </aside>

      {/* Form */}
      <section className="md:w-1/2 flex items-center justify-center p-6 md:p-10 bg-gradient-to-br from-white via-white to-primary-50/30">
        <form onSubmit={handleLogin} noValidate className="w-full max-w-md">
          <header className="text-center mb-6">
            {/* Adorno con el oro del navbar (mismo que el hero) */}
            <div className="my-3 flex items-center justify-center gap-3" style={{ color: "var(--nb-dorado)" }}>
              <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
              <FaLeaf />
              <span className="h-px w-12" style={{ background: "var(--nb-dorado-light)" }} />
            </div>
            <p
              className="text-sm uppercase tracking-wider font-semibold"
              style={{ color: "var(--nb-dorado, #b8963e)" }}
            >
              Bienvenido
            </p>
            <h2
              className="font-display text-3xl font-bold mt-1"
              style={{ color: "var(--nb-verde, #1a3209)" }}
            >
              Iniciar Sesion
            </h2>
            <hr className="my-3 border-t" style={{ borderColor: "var(--nb-dorado-light)" }} />
            <p className="text-mute text-sm">
              Ingresa tus credenciales para acceder a la plataforma institucional.
            </p>
          </header>

          {bloqueado && (
            <div className="flex items-start gap-3 p-4 mb-4 rounded-lg bg-red-50 border border-red-300 text-red-800">
              <FaExclamationTriangle className="text-xl mt-0.5 flex-shrink-0" />
              <div>
                <strong>Acceso bloqueado temporalmente</strong>
                <p className="text-sm">Podras intentarlo nuevamente en <strong>{formatTiempo(tiempoRestante)}</strong>.</p>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="lp-email" className="label">Correo electronico</label>
              <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                bloqueado ? 'opacity-50' : 'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
              }`}>
                <FaEnvelope className="text-secondary-400" />
                <input
                  id="lp-email" type="email" placeholder="usuario@ejemplo.com"
                  value={form.email} onChange={setField('email')}
                  autoComplete="email" disabled={bloqueado} maxLength={120} required
                  className="flex-1 bg-transparent outline-none text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="lp-pass" className="label">Contrasena</label>
              <div className={`flex items-center gap-2 px-3 py-2 border rounded-md transition-colors bg-white ${
                bloqueado ? 'opacity-50' : 'border-secondary-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-200'
              }`}>
                <FaLock className="text-secondary-400" />
                <input
                  id="lp-pass" type={showPass ? 'text' : 'password'} placeholder="********"
                  value={form.password} onChange={setField('password')}
                  autoComplete="current-password" disabled={bloqueado} maxLength={64} required
                  className="flex-1 bg-transparent outline-none text-sm"
                />
                {!bloqueado && (
                  <button type="button" onClick={() => setShowPass((v) => !v)}
                    className="text-xs text-primary-700 hover:text-primary-900 font-medium px-2"
                    aria-label={showPass ? 'Ocultar contrasena' : 'Mostrar contrasena'}>
                    {showPass ? <FaEyeSlash /> : <FaEye />}
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="mt-3">
            <Link to="/recuperar-password" className="text-sm text-primary-700 hover:text-primary-900 font-medium">
              ¿Olvidaste tu contrasena?
            </Link>
          </div>

          {mostrarAntibot && (
            <div className="mt-4 p-3 rounded-lg bg-accent-50 border border-accent-300">
              <div className="text-sm text-accent-800 mb-2">
                Verificacion de seguridad requerida. Marca la casilla para continuar.
              </div>
              <Turnstile
                siteKey={import.meta.env.VITE_TURNSTILE_SITE_KEY || ''}
                onVerify={(token) => { setTurnstileToken(token); showMsg('Verificacion completada.', 'success'); }}
                onExpire={() => setTurnstileToken('')}
                onError={() => { setTurnstileToken(''); showMsg('Error en la verificacion. Intenta de nuevo.', 'error'); }}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading || bloqueado}
            className={`mt-6 w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-md font-semibold text-sm border-2 transition-all duration-300 shadow-md ${
              loading || bloqueado
                ? 'cursor-not-allowed opacity-60 border-[var(--nb-dorado)] bg-[var(--nb-verde)] text-white'
                : 'border-[var(--nb-dorado)] bg-gradient-to-br from-[var(--nb-verde)] to-[var(--nb-verde-claro)] text-white hover:from-[var(--nb-dorado)] hover:to-[var(--nb-dorado-light)] hover:text-[var(--nb-verde)] hover:border-[var(--nb-verde)] hover:-translate-y-0.5 hover:shadow-lg active:translate-y-0 active:shadow-md focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-[var(--nb-dorado-light)] focus-visible:ring-offset-2'
            }`}
            style={{
              boxShadow: loading || bloqueado
                ? undefined
                : '0 10px 24px rgba(26, 50, 9, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.12)',
            }}
          >
            {loading ? <span className="inline-block w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> : (
              <>
                <FaLock />
                <span>{bloqueado ? `Bloqueado ${formatTiempo(tiempoRestante)}` : 'Ingresar'}</span>
                {!bloqueado && <FaArrowRight />}
              </>
            )}
          </button>

          {msg.text && (
            <div role="alert" className={`mt-3 p-3 rounded-lg border text-sm ${msgClass}`}>
              {msg.text}
            </div>
          )}

          <p className="text-center mt-5 text-sm text-mute">
            ¿No tienes una cuenta?{' '}
            <Link
              to="/registro"
              className="font-semibold inline-flex items-center gap-1 transition-colors"
              style={{ color: "var(--nb-verde, #1a3209)" }}
            >
              <FaUserPlus /> Registrate aqui
            </Link>
          </p>

          <p className="text-center mt-4 text-xs text-soft">
            © 2026 Comunidad Campesina Niño Dios de Zapotal. Todos los derechos reservados.
          </p>
        </form>
      </section>
    </div>
  );
}
