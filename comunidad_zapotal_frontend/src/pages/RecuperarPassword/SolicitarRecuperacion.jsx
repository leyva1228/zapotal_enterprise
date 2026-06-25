import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api';
import {
  FaEnvelope, FaArrowRight, FaShieldAlt, FaLeaf,
  FaSpinner, FaCheckCircle, FaTimes, FaExclamationTriangle,
} from 'react-icons/fa';
import Turnstile from '../../components/Turnstile';
import './RecuperarPassword.css';

const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function SolicitarRecuperacion() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: '' });
  const [turnstileToken, setTurnstileToken] = useState('');
  const [validacionEmail, setValidacionEmail] = useState({ estado: 'idle', sugerencia: null });
  const debounceEmailRef = useRef(null);
  const turnstileRef = useRef(null);

  const onEmailChange = (val) => {
    setEmail(val);
    if (debounceEmailRef.current) clearTimeout(debounceEmailRef.current);
    if (!val || !EMAIL_REGEX.test(val.trim())) {
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setMsg({ text: 'Ingresa tu correo electronico.', type: 'error' });
      return;
    }
    if (TURNSTILE_SITE_KEY && !turnstileToken) {
      setMsg({ text: 'Completa la verificacion antibot.', type: 'error' });
      return;
    }
    setLoading(true);
    setMsg({ text: '', type: '' });
    try {
      await api.post('/password-reset/request/', {
        email: email.trim(),
        turnstile_token: turnstileToken || '',
      });
      setMsg({
        text: 'Si el email existe, recibiras un codigo para restablecer tu contrasena.',
        type: 'success',
      });
      setTimeout(() => {
        navigate('/recuperar-password/confirmar', { state: { email: email.trim() } });
      }, 1200);
    } catch (err) {
      setMsg({
        text: 'Si el email existe, recibiras un codigo para restablecer tu contrasena.',
        type: 'success',
      });
      setTimeout(() => {
        navigate('/recuperar-password/confirmar', { state: { email: email.trim() } });
      }, 1200);
      if (turnstileRef.current) turnstileRef.current.reset();
      setTurnstileToken('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rp">
      <section className="rp-panel">
        <form className="rp-card" onSubmit={handleSubmit}>
          <div className="rp-deco"><span /><FaLeaf /><span /></div>
          <h1 className="rp-title">Recuperar contrasena</h1>
          <p className="rp-sub">Te enviaremos un codigo de verificacion a tu correo.</p>
          <div className="rp-field">
            <label htmlFor="rp-email">Correo electronico</label>
            <div className={`rp-inp ${
              validacionEmail.estado === 'valido' ? 'rp-inp--ok' :
              validacionEmail.estado === 'invalido' ? 'rp-inp--warn' : ''
            }`}>
              <FaEnvelope className="rp-ico" />
              <input
                id="rp-email" type="email" placeholder="usuario@ejemplo.com"
                value={email} onChange={(e) => onEmailChange(e.target.value)}
                required maxLength={120}
              />
              <span className="rp-inp__status" aria-live="polite">
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
            {validacionEmail.sugerencia && (
              <span className="rp-email-sugerencia">
                ¿Quizás quisiste decir:{' '}
                <button
                  type="button"
                  onClick={() => onEmailChange(validacionEmail.sugerencia)}
                >
                  {validacionEmail.sugerencia}
                </button>?
              </span>
            )}
          </div>
          {TURNSTILE_SITE_KEY && (
            <div className="rp-turnstile">
              <Turnstile
                ref={turnstileRef}
                siteKey={TURNSTILE_SITE_KEY}
                onVerify={(token) => setTurnstileToken(token)}
                onExpire={() => setTurnstileToken('')}
                onError={() => setTurnstileToken('')}
              />
            </div>
          )}
          <button type="submit" className="rp-btn-submit" disabled={loading}>
            {loading ? <span className="rp-spinner" /> : (
              <><span>Enviar codigo</span><FaArrowRight className="rp-arr" /></>
            )}
          </button>
          {msg.text && <div className={`rp-msg rp-msg--${msg.type}`} role="alert">{msg.text}</div>}
          <p className="rp-login">
            <Link to="/login" className="rp-login-link">Volver a iniciar sesion</Link>
          </p>
          <div className="rp-shield">
            <FaShieldAlt /><span>Acceso seguro y autorizado</span>
          </div>
        </form>
      </section>
    </div>
  );
}
