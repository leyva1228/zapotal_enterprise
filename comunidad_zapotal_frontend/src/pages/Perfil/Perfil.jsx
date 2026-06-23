import React, { useState, useEffect, useRef, useCallback } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  FaUser, FaShieldAlt, FaBell, FaFire, FaStar, FaSignOutAlt,
  FaCamera, FaUserCircle, FaKey, FaMobileAlt, FaTrashAlt,
  FaCheckCircle, FaCalendarAlt, FaIdCard, FaEnvelope, FaCheck,
  FaHandHoldingHeart, FaExternalLinkAlt, FaHourglassHalf, FaTimesCircle,
} from "react-icons/fa";
import api, { extractList } from "../../api";
import { useAuth } from "../../context/AuthContext";
import BotonFavorito from "../../components/BotonFavorito";
import "./Perfil.css";

const TABS = [
  { id: "info", label: "Informacion Personal", icon: <FaUser /> },
  { id: "seguridad", label: "Seguridad", icon: <FaShieldAlt /> },
  { id: "notificaciones", label: "Notificaciones", icon: <FaBell /> },
  { id: "favoritos", label: "Favoritos", icon: <FaStar /> },
  { id: "donaciones", label: "Mis Donaciones", icon: <FaHandHoldingHeart /> },
  { id: "baja", label: "Baja de Cuenta", icon: <FaTrashAlt /> },
];

const ESTADO_DONACION = {
  APROBADO: { label: "Aprobada", color: "emerald", icon: <FaCheckCircle /> },
  EN_PROCESO: { label: "En proceso", color: "amber", icon: <FaHourglassHalf /> },
  PENDIENTE: { label: "Pendiente", color: "amber", icon: <FaHourglassHalf /> },
  RECHAZADO: { label: "Rechazada", color: "rose", icon: <FaTimesCircle /> },
  CANCELADO: { label: "Cancelada", color: "gray", icon: <FaTimesCircle /> },
  REEMBOLSADO: { label: "Reembolsada", color: "sky", icon: <FaTimesCircle /> },
};

const ESTILO_ESTADO = {
  emerald: "bg-emerald-100 text-emerald-800 border-emerald-300",
  amber: "bg-amber-100 text-amber-800 border-amber-300",
  rose: "bg-rose-100 text-rose-800 border-rose-300",
  gray: "bg-gray-100 text-gray-800 border-gray-300",
  sky: "bg-sky-100 text-sky-800 border-sky-300",
};

const DESTINATARIO_LABELS = {
  GENERAL: "Apoyo general a la comunidad",
  INFRAESTRUCTURA: "Mejoras de infraestructura",
  EVENTOS: "Eventos y actividades",
  BECAS: "Becas y capacitacion",
  EMERGENCIA: "Fondo de emergencia",
};

function fuerzaPassword(pwd) {
  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[a-z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  return score; // 0-5
}

function labelFuerza(score) {
  if (score <= 1) return { label: 'Debil', color: '#ef4444' };
  if (score === 2) return { label: 'Regular', color: '#f59e0b' };
  if (score === 3) return { label: 'Buena', color: '#10b981' };
  if (score === 4) return { label: 'Fuerte', color: '#059669' };
  return { label: 'Muy fuerte', color: '#047857' };
}

function timeAgo(str) {
  if (!str) return "";
  const d = new Date(str);
  if (isNaN(d.getTime())) return "";
  const diff = Date.now() - d.getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "ahora";
  if (min < 60) return `hace ${min} min`;
  const h = Math.floor(min / 60);
  if (h < 24) return `hace ${h} h`;
  return `hace ${Math.floor(h / 24)} d`;
}

export default function Perfil() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { user: authUser, isAuthenticated, setAuth, clearAuth } = useAuth();
  const [tab, setTab] = useState(() => {
    const t = searchParams.get('tab');
    return TABS.some((x) => x.id === t) ? t : 'info';
  });

  const [usuario, setUsuario] = useState(authUser);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: '' });

  const [form, setForm] = useState({ nombres: '', email: '', telefono: '' });
  const [pwdForm, setPwdForm] = useState({ actual: '', nueva: '', confirmar: '' });
  const [pwdError, setPwdError] = useState('');
  const [showPwd, setShowPwd] = useState({ actual: false, nueva: false, confirmar: false });
  const [pwdCooldown, setPwdCooldown] = useState(false);

  const [modalFoto, setModalFoto] = useState(false);
  const [opcionFoto, setOpcionFoto] = useState('imagen');
  const [vistaPrevia, setVistaPrevia] = useState(null);
  const [archivoFoto, setArchivoFoto] = useState(null);
  const inputFotoRef = useRef(null);

  const [notificaciones, setNotificaciones] = useState([]);
  const [notifFiltro, setNotifFiltro] = useState('');
  const [favoritosNoticias, setFavoritosNoticias] = useState([]);
  const [favoritosEventos, setFavoritosEventos] = useState([]);
  const [subFav, setSubFav] = useState('NOTICIA');

  const [bajaForm, setBajaForm] = useState({ motivo: '', confirma: false });
  const [bajaEnviada, setBajaEnviada] = useState(false);
  const [bajaEstado, setBajaEstado] = useState(null); // null | PENDIENTE | APROBADA | RECHAZADA | CANCELADA

  // Donaciones
  const [donaciones, setDonaciones] = useState([]);
  const [donacionesLoading, setDonacionesLoading] = useState(false);
  const [donacionesError, setDonacionesError] = useState('');
  const [donacionDetalle, setDonacionDetalle] = useState(null);

  const cargarDonaciones = useCallback(async () => {
    setDonacionesLoading(true);
    setDonacionesError('');
    try {
      const res = await api.get('/donaciones/mis-donaciones/');
      const data = Array.isArray(res.data) ? res.data : (res.data?.results || []);
      setDonaciones(data);
    } catch (err) {
      setDonacionesError('No se pudieron cargar tus donaciones.');
      setDonaciones([]);
    } finally {
      setDonacionesLoading(false);
    }
  }, []);

  const cargarDetalleDonacion = async (id) => {
    try {
      const res = await api.get(`/donaciones/${id}/`);
      setDonacionDetalle(res.data);
    } catch (err) {
      setDonacionError?.('No se pudo cargar el detalle de la donacion.');
    }
  };

  // 2FA
  const [twofaFlow, setTwofaFlow] = useState(null); // null | 'setup' | 'enabled' | 'disable'
  const [twofaSetup, setTwofaSetup] = useState(null); // {secret, otpauth_url, qr_code_base64, backup_codes}
  const [twofaCode, setTwofaCode] = useState('');
  const [twofaPassword, setTwofaPassword] = useState('');
  const [twofaLoading, setTwofaLoading] = useState(false);
  const [twofaError, setTwofaError] = useState('');

  const mostrarMensaje = (texto, tipo = 'exito') => {
    setMsg({ text: texto, type: tipo });
    setTimeout(() => setMsg({ text: '', type: '' }), 4000);
  };

  // Cargar datos del usuario al montar
  useEffect(() => {
    if (!isAuthenticated) return;
    setUsuario(authUser);
    if (authUser) {
      setForm({
        nombres: authUser.nombre_completo || `${authUser.nombres || ''} ${authUser.apellidos || ''}`.trim(),
        email: authUser.email || '',
        telefono: authUser.telefono || '',
      });
    }
    // Carga detalles del usuario. Si falla (403 por permisos, 404, etc),
    // seguimos mostrando la pagina con los datos basicos del auth context.
    api.get(`/usuarios/${authUser.id}/`).then(({ data }) => {
      const actualizado = { ...authUser, ...data };
      setUsuario(actualizado);
      // Solo actualizamos el user (no access/refresh tokens aca).
      try {
        const currentToken = sessionStorage.getItem('token');
        const currentRefresh = sessionStorage.getItem('refresh');
        setAuth({ user: actualizado, access: currentToken, refresh: currentRefresh });
      } catch (e) {
        setAuth({ user: actualizado });
      }
      setForm({
        nombres: actualizado.nombre_completo || `${actualizado.nombres || ''} ${actualizado.apellidos || ''}`.trim(),
        email: actualizado.email || '',
        telefono: actualizado.telefono || '',
      });
    }).catch((err) => {
      // 401 ya lo maneja el interceptor. Para 403/404/sin red, seguimos
      // con los datos que ya tenemos del auth context.
      if (err?.response?.status !== 401) {
        // Silencioso: el usuario sigue viendo su perfil basico.
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cambiar tab via URL
  const cambiarTab = (nuevoTab) => {
    setTab(nuevoTab);
    setSearchParams({ tab: nuevoTab });
  };

  // Cargar contenido por tab
  useEffect(() => {
    if (tab === 'notificaciones') cargarNotificaciones();
    if (tab === 'favoritos') cargarFavoritos();
    if (tab === 'donaciones') cargarDonaciones();
    if (tab === 'baja') cargarEstadoBaja();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  const cargarNotificaciones = async () => {
    try {
      const params = {};
      if (notifFiltro === 'no_leidas') params.leido = false;
      if (notifFiltro === 'leidas') params.leido = true;
      const { data } = await api.get('/notificaciones/', { params });
      const list = Array.isArray(data) ? data : (data?.results || []);
      setNotificaciones(list);
    } catch (e) { setNotificaciones([]); }
  };

  const cargarFavoritos = async () => {
    try {
      const [n, e] = await Promise.all([
        api.get('/favoritos/?tipo=NOTICIA'),
        api.get('/favoritos/?tipo=EVENTO'),
      ]);
      setFavoritosNoticias(Array.isArray(n.data) ? n.data : (n.data?.results || []));
      setFavoritosEventos(Array.isArray(e.data) ? e.data : (e.data?.results || []));
    } catch (e) { setFavoritosNoticias([]); setFavoritosEventos([]); }
  };

  const cargarEstadoBaja = async () => {
    try {
      const { data } = await api.get('/solicitudes-baja/?estado=PENDIENTE');
      const list = Array.isArray(data) ? data : (data?.results || []);
      if (list.length > 0) {
        setBajaEstado('PENDIENTE');
        setBajaEnviada(true);
      } else {
        const { data: r } = await api.get('/solicitudes-baja/');
        const all = Array.isArray(r) ? r : (r?.results || []);
        if (all.length > 0) setBajaEstado(all[0].estado);
        else setBajaEstado(null);
        setBajaEnviada(all.length > 0);
      }
    } catch (e) { setBajaEstado(null); }
  };

  const guardarInfo = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.patch(`/usuarios/${authUser.id}/`, {
        telefono: form.telefono,
      });
      setUsuario((u) => ({ ...u, ...data, telefono: form.telefono }));
      setAuth({ user: { ...authUser, ...data, telefono: form.telefono }, access: null, refresh: null });
      mostrarMensaje('Informacion actualizada.');
    } catch (e) {
      mostrarMensaje('No se pudo actualizar la informacion.', 'error');
    } finally { setLoading(false); }
  };

  const cambiarPassword = async (e) => {
    e.preventDefault();
    setPwdError('');
    if (pwdForm.nueva !== pwdForm.confirmar) {
      setPwdError('Las contrasenas no coinciden.');
      return;
    }
    if (fuerzaPassword(pwdForm.nueva) < 3) {
      setPwdError('La contrasena debe tener al menos 8 caracteres, 1 mayuscula y 1 numero.');
      return;
    }
    setLoading(true);
    try {
      await api.post(`/usuarios/${authUser.id}/cambiar-password/`, {
        password_actual: pwdForm.actual,
        password_nueva: pwdForm.nueva,
      });
      mostrarMensaje('Contrasena actualizada. Cierra sesion y vuelve a iniciar.');
      setPwdForm({ actual: '', nueva: '', confirmar: '' });
    } catch (err) {
      const d = err.response?.data;
      setPwdError(typeof d === 'string' ? d : (d?.detail || d?.password_actual?.[0] || 'No se pudo cambiar la contrasena.'));
    } finally {
      setLoading(false);
      setPwdCooldown(true);
      setTimeout(() => setPwdCooldown(false), 5000);
    }
  };

  const toggle2FA = async () => {
    try {
      if (usuario?.two_factor_enabled) {
        setTwofaFlow('disable');
        setTwofaError('');
        setTwofaPassword('');
      } else {
        setTwofaFlow('setup');
        setTwofaError('');
        setTwofaCode('');
        setTwofaLoading(true);
        try {
          const { data } = await api.post('/auth/2fa/setup/');
          setTwofaSetup(data);
        } catch (e) {
          const d = e.response?.data;
          setTwofaError(typeof d === 'string' ? d : d?.detail || 'No se pudo iniciar el setup de 2FA.');
          setTwofaFlow(null);
        } finally {
          setTwofaLoading(false);
        }
      }
    } catch (e) {
      mostrarMensaje('No se pudo cambiar el estado de 2FA.', 'error');
    }
  };

  const confirmar2FA = async () => {
    if (!twofaCode || twofaCode.length !== 6) {
      setTwofaError('Ingresa el codigo de 6 digitos de tu app autenticadora.');
      return;
    }
    if (!twofaSetup?.secret) {
      setTwofaError('Inicia el setup nuevamente.');
      return;
    }
    setTwofaLoading(true);
    setTwofaError('');
    try {
      const { data } = await api.post('/auth/2fa/confirm/', {
        secret: twofaSetup.secret,
        codigo: twofaCode,
      });
      setUsuario((u) => ({ ...u, two_factor_enabled: true }));
      setTwofaSetup((s) => ({ ...s, backup_codes: data.backup_codes || s?.backup_codes || [] }));
      setTwofaFlow('enabled');
      setTwofaCode('');
      mostrarMensaje('2FA activado correctamente. Guarda tus codigos de respaldo.');
    } catch (e) {
      const d = e.response?.data;
      setTwofaError(typeof d === 'string' ? d : d?.detail || 'Codigo incorrecto.');
    } finally {
      setTwofaLoading(false);
    }
  };

  const desactivar2FA = async () => {
    if (!twofaPassword) {
      setTwofaError('Ingresa tu contrasena para confirmar.');
      return;
    }
    setTwofaLoading(true);
    setTwofaError('');
    try {
      await api.post('/auth/2fa/disable/', { password: twofaPassword });
      setUsuario((u) => ({ ...u, two_factor_enabled: false }));
      setTwofaFlow(null);
      setTwofaSetup(null);
      setTwofaCode('');
      setTwofaPassword('');
      mostrarMensaje('2FA desactivado.');
    } catch (e) {
      const d = e.response?.data;
      setTwofaError(typeof d === 'string' ? d : d?.detail || 'No se pudo desactivar 2FA.');
    } finally {
      setTwofaLoading(false);
    }
  };

  const cancelar2FA = () => {
    setTwofaFlow(null);
    setTwofaSetup(null);
    setTwofaCode('');
    setTwofaPassword('');
    setTwofaError('');
  };

  const verNotificacion = async (n) => {
    if (!n.leido) {
      try { await api.patch(`/notificaciones/${n.id}/`, { leido: true }); } catch (e) {}
      setNotificaciones((prev) => prev.map((x) => x.id === n.id ? { ...x, leido: true } : x));
    }
    if (n.url_destino && (n.url_destino.startsWith('/') || (!n.url_destino.startsWith('http')))) {
      navigate(n.url_destino);
    }
  };

  const marcarNotifLeida = async (id) => {
    try {
      await api.patch(`/notificaciones/${id}/`, { leido: true });
      setNotificaciones((prev) => prev.map((n) => n.id === id ? { ...n, leido: true } : n));
    } catch (e) {}
  };

  const marcarTodasLeidas = async () => {
    try {
      await api.post('/notificaciones/marcar-todas-leidas/');
      setNotificaciones((prev) => prev.map((n) => ({ ...n, leido: true })));
      mostrarMensaje('Todas marcadas como leidas.');
    } catch (e) {}
  };

  const eliminarNotif = async (id) => {
    try {
      await api.delete(`/notificaciones/${id}/`);
      setNotificaciones((prev) => prev.filter((n) => n.id !== id));
    } catch (e) {}
  };

  const quitarFavorito = async (fav) => {
    try {
      await api.delete(`/favoritos/${fav.id}/`);
      cargarFavoritos();
    } catch (e) {}
  };

  // Foto
  const seleccionarArchivo = (e) => {
    const archivo = e.target.files[0];
    if (!archivo) return;
    setOpcionFoto('imagen');
    setArchivoFoto(archivo);
    setVistaPrevia(URL.createObjectURL(archivo));
  };
  const guardarFoto = async () => {
    if (opcionFoto === 'avatar') {
      try {
        await api.patch(`/usuarios/${authUser.id}/`, { foto_perfil: null });
        setUsuario((u) => ({ ...u, foto_perfil: '' }));
        setAuth({ user: { ...authUser, foto_perfil: '' }, access: null, refresh: null });
        mostrarMensaje('Avatar predeterminado aplicado.');
        setModalFoto(false);
      } catch (e) {
        mostrarMensaje('No se pudo actualizar.', 'error');
      }
      return;
    }
    if (!archivoFoto) {
      mostrarMensaje('Selecciona una imagen.', 'error');
      return;
    }
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append('foto_perfil', archivoFoto);
      const { data } = await api.patch(`/usuarios/${authUser.id}/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const fotoUrl = data.foto_perfil_url || data.foto_perfil || usuario.foto_perfil;
      setUsuario((u) => ({ ...u, foto_perfil: fotoUrl }));
      setAuth({ user: { ...authUser, foto_perfil: fotoUrl }, access: null, refresh: null });
      mostrarMensaje('Foto de perfil actualizada.');
      setModalFoto(false);
    } catch (e) {
      mostrarMensaje('No se pudo actualizar la imagen.', 'error');
    } finally { setLoading(false); }
  };

  // Baja
  const enviarBaja = async (e) => {
    e.preventDefault();
    if (bajaForm.motivo.trim().length < 20) {
      mostrarMensaje('El motivo debe tener al menos 20 caracteres.', 'error');
      return;
    }
    if (!bajaForm.confirma) {
      mostrarMensaje('Debes confirmar que entiendes la baja.', 'error');
      return;
    }
    setLoading(true);
    try {
      await api.post('/mi-cuenta/solicitar-baja/', { motivo: bajaForm.motivo });
      setBajaEnviada(true);
      setBajaEstado('PENDIENTE');
      mostrarMensaje('Tu solicitud ha sido enviada y esta en revision.');
    } catch (e) {
      const d = e.response?.data;
      mostrarMensaje(typeof d === 'string' ? d : (d?.detail || 'No se pudo enviar la solicitud.'), 'error');
    } finally { setLoading(false); }
  };

  const cancelarBaja = async () => {
    try {
      await api.post('/mi-cuenta/cancelar-baja/');
      setBajaEnviada(false);
      setBajaEstado(null);
      setBajaForm({ motivo: '', confirma: false });
      mostrarMensaje('Solicitud cancelada.');
    } catch (e) {
      mostrarMensaje('No se pudo cancelar.', 'error');
    }
  };

  const cerrarSesion = async () => {
    await clearAuth();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  const f = labelFuerza(fuerzaPassword(pwdForm.nueva));
  const nombreCompleto = usuario?.nombre_completo || `${usuario?.nombres || ''} ${usuario?.apellidos || ''}`.trim() || 'Usuario';
  const fechaRegistro = usuario?.fecha_registro
    ? new Date(usuario.fecha_registro).toLocaleDateString('es-PE', { day: '2-digit', month: 'long', year: 'numeric' })
    : 'No disponible';

  return (
    <div className="perfil-page">
      <section className="perfil-hero">
        <div className="perfil-hero-overlay" />
        <div className="perfil-hero-content">
          <h1>Mi Perfil</h1>
          <div className="perfil-breadcrumb">
            <Link to="/">Inicio</Link>
            <span>/</span>
            <p>Mi Perfil</p>
          </div>
        </div>
      </section>

      <main className="perfil-container">
        <section className="perfil-card-user">
          <div className="perfil-card-top" />
          <div className="perfil-avatar-box">
            {usuario?.foto_perfil ? (
              <img src={usuario.foto_perfil} alt="Foto de perfil" className="perfil-avatar" />
            ) : (
              <div className="perfil-avatar-icon"><FaUserCircle /></div>
            )}
            <button type="button" className="perfil-camera-btn" onClick={() => setModalFoto(true)} title="Cambiar foto">
              <FaCamera />
            </button>
          </div>
          <h2>{nombreCompleto}</h2>
          <span className="perfil-rol">{usuario?.tipo_usuario || 'Usuario'}</span>
          <div className="perfil-line" />
          <p className="perfil-meta">Miembro desde {fechaRegistro}</p>
          {msg.text && (
            <div className={`perfil-mensaje perfil-mensaje--${msg.type}`}>{msg.text}</div>
          )}
        </section>

        <div className="perfil-layout">
          <aside className="perfil-sidebar">
            <nav>
              {TABS.map((t) => (
                <button
                  key={t.id}
                  className={`perfil-sidebar__link ${tab === t.id ? 'perfil-sidebar__link--active' : ''}`}
                  onClick={() => cambiarTab(t.id)}
                >
                  <span className="perfil-sidebar__icon">{t.icon}</span>
                  <span>{t.label}</span>
                </button>
              ))}
            </nav>
            <div className="perfil-sidebar__bottom">
              <button
                className="perfil-sidebar__logout"
                onClick={cerrarSesion}
                type="button"
              >
                <FaSignOutAlt /> Cerrar sesion
              </button>
            </div>
          </aside>

          <section className="perfil-content">
            {tab === 'info' && (
              <div>
                <h2 className="perfil-section-title">Informacion Personal</h2>
                <form onSubmit={guardarInfo} className="perfil-form">
                  <div className="perfil-form-row">
                    <div className="admin-form-group">
                      <label className="admin-form-group__label">Nombre completo</label>
                      <input className="admin-input" type="text" value={form.nombres} disabled />
                      <div className="admin-form-hint">Para cambiar tu nombre, contacta al administrador.</div>
                    </div>
                    <div className="admin-form-group">
                      <label className="admin-form-group__label">DNI</label>
                      <input className="admin-input" type="text" value={usuario?.dni || 'No registrado'} disabled />
                    </div>
                  </div>
                  <div className="admin-form-group">
                    <label className="admin-form-group__label">Correo electronico</label>
                    <input className="admin-input" type="email" value={form.email} disabled />
                    <div className="admin-form-hint">Para cambiar tu email, contacta al administrador.</div>
                  </div>
                  <div className="admin-form-group">
                    <label className="admin-form-group__label">Telefono</label>
                    <input
                      className="admin-input"
                      type="tel"
                      value={form.telefono}
                      onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                      placeholder="+51 999 999 999"
                    />
                  </div>
                  <div className="admin-form-group">
                    <label className="admin-form-group__label">Tipo de usuario</label>
                    <input className="admin-input" type="text" value={usuario?.tipo_usuario || ''} disabled />
                  </div>
                  <div className="admin-form-group">
                    <label className="admin-form-group__label">Estado de cuenta</label>
                    <input className="admin-input" type="text" value={usuario?.estado || 'ACTIVO'} disabled />
                  </div>
                  <button type="submit" className="perfil-btn-primary" disabled={loading}>
                    {loading ? 'Guardando...' : 'Guardar cambios'}
                  </button>
                </form>
              </div>
            )}

            {tab === 'seguridad' && (
              <div>
                <h2 className="perfil-section-title">Seguridad de la cuenta</h2>
                <form onSubmit={cambiarPassword} className="perfil-form">
                  <div className="admin-form-group">
                    <label className="admin-form-group__label">Contrasena actual</label>
                    <div className="perfil-pwd-input">
                      <input
                        className="admin-input"
                        type={showPwd.actual ? 'text' : 'password'}
                        value={pwdForm.actual}
                        onChange={(e) => setPwdForm({ ...pwdForm, actual: e.target.value })}
                        required
                      />
                      <button
                        type="button"
                        className="perfil-eye"
                        onClick={() => setShowPwd((p) => ({ ...p, actual: !p.actual }))}
                      >
                        {showPwd.actual ? 'Ocultar' : 'Mostrar'}
                      </button>
                    </div>
                  </div>
                  <div className="admin-form-group">
                    <label className="admin-form-group__label">Nueva contrasena</label>
                    <div className="perfil-pwd-input">
                      <input
                        className="admin-input"
                        type={showPwd.nueva ? 'text' : 'password'}
                        value={pwdForm.nueva}
                        onChange={(e) => setPwdForm({ ...pwdForm, nueva: e.target.value })}
                        required
                      />
                      <button
                        type="button"
                        className="perfil-eye"
                        onClick={() => setShowPwd((p) => ({ ...p, nueva: !p.nueva }))}
                      >
                        {showPwd.nueva ? 'Ocultar' : 'Mostrar'}
                      </button>
                    </div>
                    {pwdForm.nueva && (
                      <div className="perfil-pwd-strength">
                        <div className="perfil-pwd-strength__bar">
                          {[1, 2, 3, 4, 5].map((i) => (
                            <span
                              key={i}
                              className="perfil-pwd-strength__seg"
                              style={{
                                background: i <= fuerzaPassword(pwdForm.nueva) ? f.color : '#e5e7eb',
                              }}
                            />
                          ))}
                        </div>
                        <span style={{ color: f.color }} className="text-xs">{f.label}</span>
                      </div>
                    )}
                    <div className="admin-form-hint">Minimo 8 caracteres, 1 mayuscula, 1 numero.</div>
                  </div>
                  <div className="admin-form-group">
                    <label className="admin-form-group__label">Confirmar nueva contrasena</label>
                    <div className="perfil-pwd-input">
                      <input
                        className="admin-input"
                        type={showPwd.confirmar ? 'text' : 'password'}
                        value={pwdForm.confirmar}
                        onChange={(e) => setPwdForm({ ...pwdForm, confirmar: e.target.value })}
                        required
                      />
                      <button
                        type="button"
                        className="perfil-eye"
                        onClick={() => setShowPwd((p) => ({ ...p, confirmar: !p.confirmar }))}
                      >
                        {showPwd.confirmar ? 'Ocultar' : 'Mostrar'}
                      </button>
                    </div>
                  </div>
                  {pwdError && <div className="perfil-error">{pwdError}</div>}
                  <button type="submit" className="perfil-btn-primary" disabled={loading || pwdCooldown}>
                    <FaKey /> {loading ? 'Guardando...' : 'Actualizar contrasena'}
                  </button>
                </form>

                <hr className="perfil-divider" />

                <h3 className="perfil-subtitle">Verificacion en dos pasos (2FA)</h3>
                <p className="perfil-help">
                  Anade una capa extra de seguridad requiriendo un codigo de tu app autenticadora (Google Authenticator, Authy, etc.) al iniciar sesion.
                </p>

                {usuario?.two_factor_enabled && twofaFlow === null && (
                  <div className="perfil-2fa-status perfil-2fa-status--active">
                    <FaShieldAlt />
                    <div>
                      <strong>2FA esta activado.</strong>
                      <p>Tus ingresos requieren un codigo de 6 digitos de tu app autenticadora.</p>
                    </div>
                    <button
                      type="button"
                      className="perfil-btn-danger"
                      onClick={() => { setTwofaFlow('disable'); setTwofaError(''); setTwofaPassword(''); }}
                    >
                      Desactivar 2FA
                    </button>
                  </div>
                )}

                {!usuario?.two_factor_enabled && twofaFlow === null && (
                  <button
                    type="button"
                    className="perfil-btn-primary"
                    onClick={toggle2FA}
                    disabled={twofaLoading}
                  >
                    <FaShieldAlt /> {twofaLoading ? 'Iniciando...' : 'Activar 2FA'}
                  </button>
                )}

                {twofaFlow === 'setup' && twofaSetup && (
                  <div className="perfil-2fa-setup">
                    <p className="perfil-help">
                      1. Abre Google Authenticator (o cualquier app TOTP).<br />
                      2. Escanea el codigo QR o ingresa la clave manualmente.<br />
                      3. Ingresa el codigo de 6 digitos que muestra la app para confirmar.
                    </p>
                    <div className="perfil-2fa-qr-box">
                      <img
                        src={twofaSetup.qr_code_base64}
                        alt="Codigo QR para 2FA"
                        className="perfil-2fa-qr"
                      />
                    </div>
                    <div className="admin-form-group">
                      <label className="admin-form-group__label">Clave secreta</label>
                      <input
                        className="admin-input"
                        type="text"
                        readOnly
                        value={twofaSetup.secret || ''}
                        onClick={(e) => e.target.select()}
                      />
                    </div>
                    <div className="admin-form-group">
                      <label className="admin-form-group__label">Codigo de verificacion (6 digitos)</label>
                      <input
                        className="admin-input"
                        type="text"
                        inputMode="numeric"
                        maxLength={6}
                        value={twofaCode}
                        onChange={(e) => setTwofaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        placeholder="000000"
                        autoComplete="one-time-code"
                      />
                    </div>
                    {twofaError && <div className="perfil-error">{twofaError}</div>}
                    <div className="perfil-2fa-actions">
                      <button
                        type="button"
                        className="perfil-btn-primary"
                        onClick={confirmar2FA}
                        disabled={twofaLoading || twofaCode.length !== 6}
                      >
                        {twofaLoading ? 'Verificando...' : 'Confirmar y activar'}
                      </button>
                      <button
                        type="button"
                        className="perfil-btn-secondary"
                        onClick={cancelar2FA}
                        disabled={twofaLoading}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                )}

                {twofaFlow === 'enabled' && twofaSetup?.backup_codes?.length > 0 && (
                  <div className="perfil-2fa-backup">
                    <h4 className="perfil-subtitle">Codigos de respaldo</h4>
                    <p className="perfil-help">
                      Guarda estos 10 codigos en un lugar seguro. Puedes usarlos para iniciar sesion si pierdes tu dispositivo. Cada codigo solo se puede usar una vez.
                    </p>
                    <ul className="perfil-2fa-codes">
                      {twofaSetup.backup_codes.map((c, i) => (
                        <li key={i}><code>{c}</code></li>
                      ))}
                    </ul>
                    <button
                      type="button"
                      className="perfil-btn-secondary"
                      onClick={cancelar2FA}
                    >
                      Ya los guarde
                    </button>
                  </div>
                )}

                {twofaFlow === 'disable' && (
                  <div className="perfil-2fa-disable">
                    <p className="perfil-help">
                      Para desactivar 2FA, ingresa tu contrasena actual.
                    </p>
                    <div className="admin-form-group">
                      <label className="admin-form-group__label">Contrasena</label>
                      <input
                        className="admin-input"
                        type="password"
                        value={twofaPassword}
                        onChange={(e) => setTwofaPassword(e.target.value)}
                        autoComplete="current-password"
                      />
                    </div>
                    {twofaError && <div className="perfil-error">{twofaError}</div>}
                    <div className="perfil-2fa-actions">
                      <button
                        type="button"
                        className="perfil-btn-danger"
                        onClick={desactivar2FA}
                        disabled={twofaLoading || !twofaPassword}
                      >
                        {twofaLoading ? 'Desactivando...' : 'Confirmar desactivacion'}
                      </button>
                      <button
                        type="button"
                        className="perfil-btn-secondary"
                        onClick={cancelar2FA}
                        disabled={twofaLoading}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {tab === 'notificaciones' && (
              <div>
                <h2 className="perfil-section-title">Notificaciones</h2>
                <div className="perfil-notif-filters">
                  <button
                    className={`perfil-pill ${notifFiltro === '' ? 'perfil-pill--active' : ''}`}
                    onClick={() => { setNotifFiltro(''); setTimeout(cargarNotificaciones, 0); }}
                  >Todas</button>
                  <button
                    className={`perfil-pill ${notifFiltro === 'no_leidas' ? 'perfil-pill--active' : ''}`}
                    onClick={() => { setNotifFiltro('no_leidas'); setTimeout(cargarNotificaciones, 0); }}
                  >No leidas</button>
                  <button
                    className={`perfil-pill ${notifFiltro === 'leidas' ? 'perfil-pill--active' : ''}`}
                    onClick={() => { setNotifFiltro('leidas'); setTimeout(cargarNotificaciones, 0); }}
                  >Leidas</button>
                  <div className="flex-1" />
                  <button className="perfil-link" onClick={marcarTodasLeidas}>
                    Marcar todas como leidas
                  </button>
                </div>
                {notificaciones.length === 0 ? (
                  <p className="perfil-help">No tienes notificaciones.</p>
                ) : (
                  <ul className="perfil-notif-list">
                    {notificaciones.map((n) => (
                      <li
                        key={n.id}
                        className={`perfil-notif-item ${n.leido ? 'perfil-notif-item--leido' : ''}`}
                        onClick={() => verNotificacion(n)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => { if (e.key === 'Enter') verNotificacion(n); }}
                      >
                        <div className="perfil-notif-item__icon"><FaBell /></div>
                        <div className="perfil-notif-item__body">
                          <div className="perfil-notif-item__title">{n.titulo}</div>
                          <div className="perfil-notif-item__msg">{n.mensaje}</div>
                          <div className="perfil-notif-item__time">
                            {timeAgo(n.fecha)}
                            {n.tipo_display && n.tipo_display !== 'Informacion' && <span className="perfil-notif-tipo"> &middot; {n.tipo_display}</span>}
                          </div>
                        </div>
                        <div className="perfil-notif-item__actions">
                          {!n.leido && (
                            <button className="perfil-link" onClick={(e) => { e.stopPropagation(); marcarNotifLeida(n.id); }}>
                              <FaCheck /> Marcar leida
                            </button>
                          )}
                          <button className="perfil-link perfil-link--danger" onClick={(e) => { e.stopPropagation(); eliminarNotif(n.id); }}>
                            Eliminar
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {tab === 'favoritos' && (
              <div>
                <h2 className="perfil-section-title">Favoritos</h2>
                <div className="perfil-fav-tabs">
                  <button
                    className={`perfil-pill ${subFav === 'NOTICIA' ? 'perfil-pill--active' : ''}`}
                    onClick={() => setSubFav('NOTICIA')}
                  >
                    Noticias ({favoritosNoticias.length})
                  </button>
                  <button
                    className={`perfil-pill ${subFav === 'EVENTO' ? 'perfil-pill--active' : ''}`}
                    onClick={() => setSubFav('EVENTO')}
                  >
                    Eventos ({favoritosEventos.length})
                  </button>
                </div>
                {subFav === 'NOTICIA' ? (
                  favoritosNoticias.length === 0 ? (
                    <p className="perfil-help">No tienes noticias favoritas.</p>
                  ) : (
                    <ul className="perfil-fav-list">
                      {favoritosNoticias.map((fav) => (
                        <li key={fav.id} className="perfil-fav-item">
                          <Link to={`/noticias/${fav.noticia}`} className="perfil-fav-item__title">
                            {fav.noticia_titulo || 'Noticia'}
                          </Link>
                          <button
                            className="perfil-link perfil-link--danger"
                            onClick={() => quitarFavorito(fav)}
                          >
                            <FaTrashAlt /> Quitar
                          </button>
                        </li>
                      ))}
                    </ul>
                  )
                ) : (
                  favoritosEventos.length === 0 ? (
                    <p className="perfil-help">No tienes eventos favoritos.</p>
                  ) : (
                    <ul className="perfil-fav-list">
                      {favoritosEventos.map((fav) => (
                        <li key={fav.id} className="perfil-fav-item">
                          <Link to={`/eventos/${fav.evento}`} className="perfil-fav-item__title">
                            {fav.evento_titulo || 'Evento'}
                          </Link>
                          <button
                            className="perfil-link perfil-link--danger"
                            onClick={() => quitarFavorito(fav)}
                          >
                            <FaTrashAlt /> Quitar
                          </button>
                        </li>
                      ))}
                    </ul>
                  )
                )}
              </div>
            )}

            {tab === 'donaciones' && (
              <div>
                <h2 className="perfil-section-title">Mis Donaciones</h2>
                <p className="perfil-help">
                  Aqui puedes ver el historial de todas las donaciones que has realizado a la comunidad Zapotal.
                  Tu apoyo hace posible que sigamos creciendo juntos.
                </p>

                <div className="donaciones-actions">
                  <Link to="/donaciones" className="donaciones-btn-donar">
                    <FaHandHoldingHeart /> Hacer una nueva donacion
                    <FaExternalLinkAlt className="donaciones-btn-icon-out" />
                  </Link>
                </div>

                {donacionesLoading && (
                  <p className="perfil-help">Cargando tus donaciones...</p>
                )}

                {donacionesError && (
                  <p className="perfil-error">{donacionesError}</p>
                )}

                {!donacionesLoading && !donacionesError && donaciones.length === 0 && (
                  <div className="donaciones-empty">
                    <FaHandHoldingHeart className="donaciones-empty-icon" />
                    <p>Aun no has realizado ninguna donacion.</p>
                    <Link to="/donaciones" className="donaciones-btn-donar">
                      Ser el primero en donar
                    </Link>
                  </div>
                )}

                {!donacionesLoading && donaciones.length > 0 && (
                  <div className="donaciones-list">
                    {donaciones.map((d) => {
                      const estado = ESTADO_DONACION[d.estado] || ESTADO_DONACION.PENDIENTE;
                      const estiloEstado = ESTILO_ESTADO[estado.color] || ESTILO_ESTADO.gray;
                      const destinatario = DESTINATARIO_LABELS[d.destinatario] || d.destinatario;
                      const fecha = d.fecha_creacion
                        ? new Date(d.fecha_creacion).toLocaleString('es-PE', { dateStyle: 'medium', timeStyle: 'short' })
                        : '';
                      return (
                        <div key={d.id} className="donaciones-card">
                          <div className="donaciones-card-head">
                            <div>
                              <p className="donaciones-card-monto">
                                S/ {Number(d.monto).toFixed(2)} <span className="donaciones-card-moneda">{d.moneda}</span>
                              </p>
                              <p className="donaciones-card-dest">{destinatario}</p>
                            </div>
                            <span className={`donaciones-estado-badge ${estiloEstado}`}>
                              {estado.icon} {estado.label}
                            </span>
                          </div>
                          {d.mensaje && (
                            <p className="donaciones-card-msg">"{d.mensaje}"</p>
                          )}
                          <div className="donaciones-card-foot">
                            <span className="donaciones-card-fecha">{fecha}</span>
                            {d.mp_payment_id && (
                              <span className="donaciones-card-ref">
                                Ref: {String(d.mp_payment_id).slice(-8)}
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {tab === 'baja' && (
              <div>
                <h2 className="perfil-section-title">Solicitud de Baja de Cuenta</h2>
                <p className="perfil-help">
                  Si deseas dejar de usar la plataforma, puedes solicitar la baja de tu cuenta.
                  Un administrador revisara tu solicitud y la cuenta sera desactivada.
                </p>

                {bajaEnviada && bajaEstado === 'PENDIENTE' && (
                  <div className="perfil-baja-info perfil-baja-info--warning">
                    <strong>Tu solicitud de baja esta en revision.</strong>
                    <p>Un administrador la procesara pronto. Puedes cancelarla en cualquier momento.</p>
                    <button className="perfil-btn-secondary" onClick={cancelarBaja}>
                      Cancelar solicitud
                    </button>
                  </div>
                )}
                {bajaEnviada && bajaEstado === 'APROBADA' && (
                  <div className="perfil-baja-info perfil-baja-info--danger">
                    <strong>Tu cuenta ha sido desactivada.</strong>
                    <p>No puedes iniciar sesion. Contacta al administrador para reactivarla.</p>
                  </div>
                )}
                {bajaEnviada && bajaEstado === 'RECHAZADA' && (
                  <div className="perfil-baja-info perfil-baja-info--info">
                    <strong>Tu solicitud de baja fue rechazada.</strong>
                    <p>Tu cuenta sigue activa. Contacta al administrador para mas informacion.</p>
                  </div>
                )}
                {bajaEnviada && bajaEstado === 'CANCELADA' && (
                  <div className="perfil-baja-info perfil-baja-info--info">
                    <strong>Cancelaste tu solicitud.</strong>
                    <p>Tu cuenta sigue activa. Si vuelves a solicitar, tendras que llenar el formulario de nuevo.</p>
                  </div>
                )}

                {!bajaEnviada && (
                  <form onSubmit={enviarBaja} className="perfil-form">
                    <div className="admin-form-group">
                      <label className="admin-form-group__label admin-form-group__label--required">Motivo de la baja</label>
                      <textarea
                        className="admin-textarea"
                        value={bajaForm.motivo}
                        onChange={(e) => setBajaForm({ ...bajaForm, motivo: e.target.value })}
                        rows={5}
                        placeholder="Explica brevemente por que deseas darte de baja..."
                        required
                        minLength={20}
                      />
                      <div className="admin-form-hint">Minimo 20 caracteres.</div>
                    </div>
                    <div className="admin-form-group">
                      <label className="perfil-checkbox">
                        <input
                          type="checkbox"
                          checked={bajaForm.confirma}
                          onChange={(e) => setBajaForm({ ...bajaForm, confirma: e.target.checked })}
                          required
                        />
                        <span>Entiendo que mi cuenta sera desactivada y no podre iniciar sesion.</span>
                      </label>
                    </div>
                    <button
                      type="submit"
                      className="perfil-btn-danger"
                      disabled={loading || !bajaForm.confirma}
                    >
                      <FaTrashAlt /> {loading ? 'Enviando...' : 'Solicitar baja de cuenta'}
                    </button>
                  </form>
                )}
              </div>
            )}
          </section>
        </div>
      </main>

      {modalFoto && (
        <div className="perfil-modal-overlay" onClick={() => setModalFoto(false)}>
          <div className="perfil-modal" onClick={(e) => e.stopPropagation()}>
            <div className="perfil-modal-header">
              <h2>Cambiar foto de perfil</h2>
              <button type="button" onClick={() => setModalFoto(false)}><FaTrashAlt /></button>
            </div>
            <div className="perfil-modal-body">
              <label className="admin-form-group__label">Opcion</label>
              <select
                className="admin-select"
                value={opcionFoto}
                onChange={(e) => {
                  if (e.target.value === 'avatar') {
                    setOpcionFoto('avatar');
                    setArchivoFoto(null);
                    setVistaPrevia(null);
                  } else {
                    setOpcionFoto('imagen');
                    inputFotoRef.current?.click();
                  }
                }}
              >
                <option value="imagen">Cargar una imagen</option>
                <option value="avatar">Usar avatar predeterminado</option>
              </select>
              <input
                ref={inputFotoRef}
                type="file"
                accept="image/*"
                onChange={seleccionarArchivo}
                hidden
              />
              <div className="perfil-modal-preview">
                {vistaPrevia ? (
                  <img src={vistaPrevia} alt="Vista previa" />
                ) : opcionFoto === 'avatar' ? (
                  <FaUserCircle className="perfil-modal-avatar" />
                ) : (
                  <div className="perfil-modal-placeholder">
                    <FaCamera />
                    <span>Haz clic en "Cargar una imagen"</span>
                  </div>
                )}
              </div>
            </div>
            <div className="perfil-modal-footer">
              <button type="button" className="perfil-btn-primary" onClick={guardarFoto} disabled={loading}>
                {loading ? 'Guardando...' : 'Guardar'}
              </button>
              <button type="button" className="perfil-btn-secondary" onClick={() => setModalFoto(false)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
