import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api';
import { FaEnvelope, FaArrowRight, FaShieldAlt, FaLeaf } from 'react-icons/fa';
import Turnstile from '../../components/Turnstile';
import './RecuperarPassword.css';

const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY;

export default function SolicitarRecuperacion() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: '' });
  const [turnstileToken, setTurnstileToken] = useState('');
  const turnstileRef = useRef(null);

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
            <div className="rp-inp">
              <FaEnvelope className="rp-ico" />
              <input
                id="rp-email" type="email" placeholder="usuario@ejemplo.com"
                value={email} onChange={(e) => setEmail(e.target.value)}
                required maxLength={120}
              />
            </div>
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
