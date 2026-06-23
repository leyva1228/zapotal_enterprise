import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import api from '../../api';
import { FaLock, FaArrowRight, FaShieldAlt, FaLeaf } from 'react-icons/fa';
import './RecuperarPassword.css';

export default function ConfirmarRecuperacion() {
  const navigate = useNavigate();
  const location = useLocation();
  const emailInicial = location.state?.email || '';
  const [email] = useState(emailInicial);
  const [codigo, setCodigo] = useState('');
  const [nueva, setNueva] = useState('');
  const [confirmar, setConfirmar] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !codigo || !nueva) {
      setMsg({ text: 'Completa todos los campos.', type: 'error' });
      return;
    }
    if (nueva.length < 6) {
      setMsg({ text: 'La contrasena debe tener minimo 6 caracteres.', type: 'error' });
      return;
    }
    if (nueva !== confirmar) {
      setMsg({ text: 'Las contrasenas no coinciden.', type: 'error' });
      return;
    }
    setLoading(true);
    setMsg({ text: '', type: '' });
    try {
      await api.post('/password-reset/confirm/', {
        email,
        codigo,
        nueva_password: nueva,
      });
      setMsg({ text: 'Contrasena actualizada. Inicia sesion.', type: 'success' });
      setTimeout(() => navigate('/login'), 1200);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Codigo incorrecto o expirado.';
      setMsg({ text: detail, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rp">
      <section className="rp-panel">
        <form className="rp-card" onSubmit={handleSubmit}>
          <div className="rp-deco"><span /><FaLeaf /><span /></div>
          <h1 className="rp-title">Restablecer contrasena</h1>
          <p className="rp-sub">Ingresa el codigo que recibiste por correo.</p>
          <div className="rp-field">
            <label>Codigo de verificacion</label>
            <div className="rp-inp">
              <input
                type="text" inputMode="numeric" maxLength={6}
                value={codigo} onChange={(e) => setCodigo(e.target.value.replace(/\D/g, ''))}
                placeholder="000000" required
              />
            </div>
          </div>
          <div className="rp-field">
            <label>Nueva contrasena</label>
            <div className="rp-inp">
              <FaLock className="rp-ico" />
              <input
                type="password" placeholder="Minimo 6 caracteres"
                value={nueva} onChange={(e) => setNueva(e.target.value)}
                required minLength={6}
              />
            </div>
          </div>
          <div className="rp-field">
            <label>Confirmar contrasena</label>
            <div className="rp-inp">
              <FaLock className="rp-ico" />
              <input
                type="password" placeholder="Repite la contrasena"
                value={confirmar} onChange={(e) => setConfirmar(e.target.value)}
                required
              />
            </div>
          </div>
          <button type="submit" className="rp-btn-submit" disabled={loading}>
            {loading ? <span className="rp-spinner" /> : (
              <><span>Cambiar contrasena</span><FaArrowRight className="rp-arr" /></>
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
