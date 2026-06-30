import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  FaShieldAlt, FaArrowLeft, FaKey, FaTimes,
} from 'react-icons/fa';
import api from '../../../api';
import { useAuth } from '../../../context/AuthContext';
import { useToast } from '../../common/ToastCenter/ToastCenter';
import OTPInput from '../OTPInput/OTPInput';
import './TwoFactorVerify.css';

export default function TwoFactorVerify() {
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const { setAuth } = useAuth();
  const state = location.state || {};
  const [tokenTemp, setTokenTemp] = useState(state.tokenTemp || '');
  const [usuarioId, setUsuarioId] = useState(state.usuarioId || null);
  const [email, setEmail] = useState(state.email || '');
  const [codigo, setCodigo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokenTemp || !usuarioId) {
      navigate('/login', { replace: true });
    }
  }, [tokenTemp, usuarioId, navigate]);

  const onComplete = async (c) => {
    if (loading) return;
    setCodigo(c);
    setError('');
    setLoading(true);
    try {
      const { data } = await api.post('/auth/2fa/verify-login/', {
        token_temp: tokenTemp,
        codigo: c,
      });
      const ud = data.usuario;
      setAuth({
        user: {
          id: ud.id,
          email: ud.email,
          nombres: ud.nombres || '',
          apellidos: ud.apellidos || '',
          tipo_usuario: ud.tipo_usuario || 'COMUNERO',
          estado: ud.estado,
          es_admin: ud.es_admin === true,
          es_autoridad: ud.es_autoridad === true,
          autoridad_cargo: ud.autoridad_cargo || null,
          foto_perfil: ud.foto_perfil || ud.foto_perfil_url || '',
        },
        access: data.access,
        refresh: data.refresh,
      });
      toast.push({ type: 'success', text: 'Codigo verificado. Bienvenido.', duration: 3500 });
      const isAdmin = ud.es_admin || ud.tipo_usuario === 'ADMIN';
      navigate(isAdmin ? '/admin' : '/', { replace: true });
    } catch (err) {
      const d = err.response?.data;
      const detail = (d && (d.detail || d.error?.code)) || 'Codigo incorrecto.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const onCancel = () => {
    navigate('/login', { replace: true });
  };

  return (
    <div className="twofa-page">
      <div className="twofa-card">
        <header className="twofa-head">
          <div className="twofa-icon"><FaShieldAlt /></div>
          <h1>Verificacion en dos pasos</h1>
          <p className="twofa-sub">
            Hola {email || 'usuario'}, abre Google Authenticator e ingresa el codigo de 6 digitos.
          </p>
        </header>
        <OTPInput value={codigo} onChange={setCodigo} onComplete={onComplete} disabled={loading} />
        {error && <div className="twofa-error">{error}</div>}
        <div className="twofa-actions">
          <button type="button" className="twofa-btn twofa-btn--ghost" onClick={onCancel} disabled={loading}>
            <FaTimes /> Cancelar
          </button>
          <button
            type="button"
            className="twofa-btn twofa-btn--primary"
            onClick={() => codigo && onComplete(codigo)}
            disabled={loading || codigo.length !== 6}
          >
            <FaKey /> {loading ? 'Verificando...' : 'Verificar'}
          </button>
        </div>
        <p className="twofa-hint">
          Tambien puedes usar uno de los 10 codigos de respaldo si no tienes tu dispositivo.
        </p>
        <button type="button" className="twofa-back" onClick={onCancel}>
          <FaArrowLeft /> Volver al inicio de sesion
        </button>
      </div>
    </div>
  );
}
