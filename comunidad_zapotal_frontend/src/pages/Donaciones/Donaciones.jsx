import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FaHandHoldingHeart, FaLock, FaShieldAlt, FaUsers, FaSeedling,
  FaCheckCircle, FaClock, FaTimesCircle, FaRedo,
  FaUserSecret, FaHome, FaGraduationCap, FaHeartbeat, FaRoad, FaInfoCircle,
  FaCreditCard, FaTimes, FaExclamationCircle, FaIdCard, FaUser, FaEnvelope,
  FaDownload,
  FaSpinner, FaCheck, FaExclamationTriangle,
} from 'react-icons/fa';
import api, { extractList } from '../../api';
import { useAuth } from '../../context/AuthContext';
import './Donaciones.css';

const QUICK_AMOUNTS = [5, 10, 25, 50, 100];
const MIN_AMOUNT = 1;
const MAX_AMOUNT = 5000;

const DESTINATARIOS = [
  { value: 'COMUNIDAD',         label: 'Comunidad general', icon: <FaHome /> },
  { value: 'PROYECTO_OBRAS',    label: 'Obras e infraestructura', icon: <FaRoad /> },
  { value: 'PROYECTO_BECAS',    label: 'Becas educativas', icon: <FaGraduationCap /> },
  { value: 'PROYECTO_SALUD',    label: 'Programas de salud', icon: <FaHeartbeat /> },
  { value: 'PROYECTO_AGRicola', label: 'Desarrollo agricola', icon: <FaSeedling /> },
];

export default function Donaciones() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const dialogRef = useRef(null);

  const [stats, setStats] = useState(null);
  const [amount, setAmount] = useState(25);
  const [customAmount, setCustomAmount] = useState('');
  const [message, setMessage] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [donorName, setDonorName] = useState(user?.nombre_completo || '');
  const [donorEmail, setDonorEmail] = useState(user?.email || '');
  const [destinatario, setDestinatario] = useState('COMUNIDAD');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [donationId, setDonationId] = useState(null);
  const [statsUpdating, setStatsUpdating] = useState(false);

  // ZeroBounce live validation del email (solo si el usuario NO esta logueado,
  // porque si esta logueado el email ya fue validado al registrarse).
  const [emailEstado, setEmailEstado] = useState({ estado: 'idle', sugerencia: null });
  const emailDebounceRef = useRef(null);

  // Si el usuario esta logueado, marcamos el email como verificado de inmediato
  // y NO lanzamos la validacion contra ZeroBounce.
  useEffect(() => {
    if (isAuthenticated && user?.email) {
      setEmailEstado({ estado: 'valido', sugerencia: null });
    } else if (!isAuthenticated) {
      setEmailEstado({ estado: 'idle', sugerencia: null });
    }
  }, [isAuthenticated, user]);

  // Live validation ZeroBounce (debounce 800ms) solo si NO esta logueado
  // y el email difiere del del usuario (que ya esta validado).
  useEffect(() => {
    if (isAuthenticated) return undefined;
    const email = (donorEmail || '').trim();
    const formatoValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!formatoValido) {
      setEmailEstado({ estado: 'idle', sugerencia: null });
      if (emailDebounceRef.current) clearTimeout(emailDebounceRef.current);
      return undefined;
    }
    setEmailEstado({ estado: 'verificando', sugerencia: null });
    if (emailDebounceRef.current) clearTimeout(emailDebounceRef.current);
    emailDebounceRef.current = setTimeout(async () => {
      try {
        const { data } = await api.get('/validar-email/', { params: { email } });
        if (data.es_valido) {
          if (data.es_sospechoso) {
            setEmailEstado({
              estado: 'sospechoso',
              sugerencia: data.did_you_mean || null,
              motivo: data.motivo || 'El dominio acepta cualquier direccion',
            });
          } else {
            setEmailEstado({ estado: 'valido', sugerencia: null });
          }
        } else {
          setEmailEstado({
            estado: 'invalido',
            sugerencia: data.did_you_mean || null,
            motivo: data.motivo || 'Correo no valido',
          });
        }
      } catch {
        setEmailEstado({ estado: 'idle', sugerencia: null });
      }
    }, 800);
    return () => {
      if (emailDebounceRef.current) clearTimeout(emailDebounceRef.current);
    };
  }, [donorEmail, isAuthenticated]);

  // Helper: indica si el email actual bloquea el envio del form.
  // Solo se bloquea en estado 'invalido' confirmado por ZeroBounce
  // (no 'sospechoso' tipo catch-all, que igual permite enviar).
  const emailBloqueado =
    !isAuthenticated &&
    emailEstado.estado === 'invalido' &&
    emailEstado.motivo &&
    !emailEstado.motivo.toLowerCase().includes('catch-all') &&
    !emailEstado.motivo.toLowerCase().includes('sospechoso');

  // Modal de pago
  const [modalOpen, setModalOpen] = useState(false);
  const [tipoTarjeta, setTipoTarjeta] = useState('debito');
  const [cardNumber, setCardNumber] = useState('');
  const [cardName, setCardName] = useState(user?.nombre_completo || '');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvv, setCardCvv] = useState('');
  const [modalError, setModalError] = useState('');
  const [paying, setPaying] = useState(false);

  // Modal de resultado
  const [resultModal, setResultModal] = useState(null);

  const cargarStats = () => {
    api.get('/donaciones/estadisticas/').then((r) => setStats(r.data)).catch(() => {});
  };

  useEffect(() => {
    cargarStats();
  }, []);

  const finalAmount = useMemo(() => {
    if (customAmount && customAmount !== '') {
      const n = parseFloat(customAmount);
      return isNaN(n) ? 0 : n;
    }
    return amount;
  }, [amount, customAmount]);

  const formatPEN = (n) => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency', currency: 'PEN', minimumFractionDigits: 2,
    }).format(n || 0);
  };

  const formatStat = (n) => {
    if (n === null || n === undefined) return '0';
    return new Intl.NumberFormat('es-PE').format(n);
  };

  const validateForm = () => {
    setError('');
    if (finalAmount < MIN_AMOUNT) {
      setError(`El monto minimo es ${formatPEN(MIN_AMOUNT)}.`);
      return false;
    }
    if (finalAmount > MAX_AMOUNT) {
      setError(`El monto maximo es ${formatPEN(MAX_AMOUNT)}.`);
      return false;
    }
    if (!donorEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(donorEmail.trim())) {
      setError('Ingresa un correo electronico valido para enviarte la boleta de pago.');
      return false;
    }
    // Si es invitado y ZeroBounce ya determino que el email es invalido, bloqueamos.
    if (emailBloqueado) {
      setError('El correo electronico no es valido. Usa otro para continuar.');
      return false;
    }
    return true;
  };

  const handleContinuar = async () => {
    if (!validateForm()) return;
    setLoading(true);
    try {
      const { data } = await api.post('/donaciones/iniciar/', {
        monto: Number(finalAmount.toFixed(2)),
        mensaje: message.trim(),
        anonima: isAnonymous,
        destinatario,
        nombre_donante: isAnonymous ? donorName : (user?.nombre_completo || ''),
        email_donante: donorEmail,
        documento_donante: user?.dni || '',
      });
      setDonationId(data.donation_id);
      setCardName(user?.nombre_completo || '');
      setModalOpen(true);
    } catch (e) {
      const detail = e.response?.data?.detail || e.message || 'Error desconocido';
      setError(`No se pudo iniciar la donacion: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const validateCard = () => {
    setModalError('');
    const digits = cardNumber.replace(/\s/g, '');
    if (digits.length < 13 || digits.length > 19) {
      setModalError('Numero de tarjeta invalido. Verifica e intenta de nuevo.');
      return false;
    }
    if (!/^\d{2}\/\d{2}$/.test(cardExpiry)) {
      setModalError('Fecha de expiracion invalida. Usa el formato MM/AA.');
      return false;
    }
    if (!/^\d{3,4}$/.test(cardCvv)) {
      setModalError('CVV invalido. Debe tener 3 o 4 digitos.');
      return false;
    }
    if (cardName.trim().length < 3) {
      setModalError('Ingresa el nombre tal como aparece en la tarjeta.');
      return false;
    }
    return true;
  };

  const handleDonar = async () => {
    if (!validateCard()) return;
    setPaying(true);
    const ultimos_4 = cardNumber.replace(/\s/g, '').slice(-4);
    try {
      const { data } = await api.post('/donaciones/procesar-simulado/', {
        donation_id: donationId,
        ultimos_4,
        tipo_tarjeta: tipoTarjeta,
      });
      // data.status puede ser 'aprobado', 'en_proceso' o 'rechazado'
      const statusNormalizado = data.status.replace('en_proceso', 'in_process');
      setResultModal({
        status: statusNormalizado,
        detail: data.status_detail,
        donation_id: data.donation_id,
        sim_payment_id: data.sim_payment_id,
        monto: finalAmount,
        destinatario,
        ultimos_4,
        tipo_tarjeta: tipoTarjeta,
      });
      setModalOpen(false);
      // Si fue aprobado, refrescar stats del hero con animacion
      if (statusNormalizado === 'aprobado') {
        setStatsUpdating(true);
        cargarStats();
        setTimeout(() => setStatsUpdating(false), 1500);
      }
    } catch (e) {
      const detail = e.response?.data?.detail || e.message || 'Error desconocido';
      setModalError(`No se pudo procesar el pago: ${detail}`);
    } finally {
      setPaying(false);
    }
  };

  const cerrarModalPago = () => {
    if (paying) return;
    setModalOpen(false);
    setModalError('');
    setCardNumber('');
    setCardExpiry('');
    setCardCvv('');
  };

  const cerrarModalResultado = () => {
    setResultModal(null);
    if (resultModal?.status === 'aprobado') {
      // Resetear todo para una nueva donacion
      setDonationId(null);
      setMessage('');
      setError('');
      setCardNumber('');
      setCardExpiry('');
      setCardCvv('');
    }
  };

  const descargarBoleta = async (donationIdValue) => {
    try {
      const response = await api.get(
        `/donaciones/${donationIdValue}/boleta-pdf/`,
        { responseType: 'blob' },
      );
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      // Extraer nombre del header Content-Disposition si viene del backend
      const cd = response.headers['content-disposition'] || '';
      const match = cd.match(/filename="?([^"]+)"?/);
      link.download = match ? match[1] : `boleta-donacion-${donationIdValue}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Error descargando boleta:', e);
      setError('No se pudo descargar la boleta. Intenta nuevamente.');
    }
  };

  const formatCardNumber = (v) => {
    const digits = v.replace(/\D/g, '').slice(0, 19);
    return digits.replace(/(.{4})/g, '$1 ').trim();
  };

  const formatExpiry = (v) => {
    const digits = v.replace(/\D/g, '').slice(0, 4);
    if (digits.length <= 2) return digits;
    return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  };

  return (
    <div className="don-page">
      {/* ====== HERO ====== */}
      <section className="don-hero">
        <div className="don-hero__bg" aria-hidden="true" />
        <div className="don-hero__overlay" aria-hidden="true" />
        <div className="don-hero__content">
          <h1 className="don-hero__title">Tu donacion construye futuro</h1>
          <p className="don-hero__subtitle">
            Tus aportes permiten a la Comunidad Campesina Niño Dios de Zapotal financiar proyectos de
            infraestructura, becas educativas, programas de salud y desarrollo agricola
            que benefician a las familias de nuestra comunidad.
          </p>

          <div className={`don-stats ${statsUpdating ? 'don-stats--pulse' : ''}`}>
            <div className="don-stat">
              <FaUsers className="don-stat__icon" />
              <div>
                <strong>250+</strong>
                <span>Familias beneficiadas</span>
              </div>
            </div>
            <div className="don-stat don-stat--featured">
              <FaHandHoldingHeart className="don-stat__icon" />
              <div>
                <strong>{formatPEN(stats?.total_recaudado || 0)}</strong>
                <span>Recaudado en total</span>
              </div>
            </div>
            <div className="don-stat">
              <FaSeedling className="don-stat__icon" />
              <div>
                <strong>{formatStat(stats?.cantidad_donaciones || 0)}</strong>
                <span>Donaciones aprobadas</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ====== A DONDE VA TU DONACION ====== */}
      <section className="don-impact">
        <h2 className="don-impact__title">A donde va tu donacion</h2>
        <p className="don-impact__intro">Cada sol que donas se traduce en obras concretas para la comunidad.</p>
        <div className="don-impact__grid">
          <div className="don-impact__card">
            <FaGraduationCap className="don-impact__card-icon" />
            <h3>Educacion</h3>
            <p>Materiales y mejoras para la escuela primaria local. Becas para jovenes destacados.</p>
          </div>
          <div className="don-impact__card">
            <FaRoad className="don-impact__card-icon" />
            <h3>Infraestructura</h3>
            <p>Mejoramiento de los caminos vecinales, mantenimiento de locales comunales.</p>
          </div>
          <div className="don-impact__card">
            <FaHeartbeat className="don-impact__card-icon" />
            <h3>Salud</h3>
            <p>Apoyo a familias en situacion vulnerable, campanas de salud preventiva.</p>
          </div>
          <div className="don-impact__card">
            <FaSeedling className="don-impact__card-icon" />
            <h3>Desarrollo agricola</h3>
            <p>Programas de capacitacion tecnica para jovenes, insumos para pequenos productores.</p>
          </div>
        </div>
      </section>

      {/* ====== AUTH GATE (no logueado) ====== */}
      {!isAuthenticated && !resultModal && (
        <section className="don-form-section">
          <div className="don-form-card don-auth-required">
            <FaHandHoldingHeart className="don-auth-icon" />
            <h2 className="don-form-title">Inicia sesion para donar</h2>
            <p className="don-form-subtitle">
              Las donaciones estan disponibles solo para comuneros y autoridades registradas en la plataforma.
              Es rapido, seguro y tu apoyo queda registrado en tu perfil.
            </p>
            <div className="don-auth-actions">
              <button
                type="button"
                className="don-btn-primary"
                onClick={() => navigate('/login', { state: { from: '/donaciones' } })}
              >
                Iniciar sesion
              </button>
              <button
                type="button"
                className="don-btn-secondary"
                onClick={() => navigate('/registro')}
              >
                Registrarme
              </button>
            </div>
            <p className="don-help">
              <FaInfoCircle /> Si ya tienes cuenta, te llevamos de regreso a esta pagina despues del login.
            </p>
          </div>
        </section>
      )}

      {/* ====== FORMULARIO DE DONACION (2 COLUMNAS) ====== */}
      {isAuthenticated && (
        <section className="don-form-section">
          <div className="don-form-card">
            <h2 className="don-form-title">Cuanto quieres donar?</h2>
            <p className="don-form-subtitle">Elige un monto o escribe el que desees. Lo que aportas transforma.</p>

            <div className="don-form-grid">
              {/* COLUMNA IZQUIERDA: monto + destino */}
              <div className="don-form-col">
                <div className="don-quick-amounts">
                  {QUICK_AMOUNTS.map((amt) => (
                    <button
                      key={amt}
                      type="button"
                      className={`don-amount-chip ${amount === amt && !customAmount ? 'is-active' : ''}`}
                      onClick={() => { setAmount(amt); setCustomAmount(''); }}
                    >
                      S/ {amt}
                    </button>
                  ))}
                  <button
                    type="button"
                    className={`don-amount-chip ${customAmount !== '' ? 'is-active' : ''}`}
                    onClick={() => { setCustomAmount(' '); setAmount(0); }}
                  >
                    Otro monto
                  </button>
                </div>

                {(customAmount !== '' || amount === 0) ? (
                  <div className="don-custom-amount">
                    <span className="don-currency">S/</span>
                    <input
                      type="number"
                      min={MIN_AMOUNT}
                      max={MAX_AMOUNT}
                      step="0.01"
                      value={customAmount}
                      onChange={(e) => setCustomAmount(e.target.value)}
                      placeholder="0.00"
                      autoFocus
                      className="don-custom-amount-input"
                    />
                  </div>
                ) : (
                  <div className="don-amount-display">
                    <span className="don-currency">S/</span>
                    <span className="don-amount-number">{amount.toFixed(2)}</span>
                  </div>
                )}

                <p className="don-amount-range">
                  Rango permitido: {formatPEN(MIN_AMOUNT)} - {formatPEN(MAX_AMOUNT)}
                </p>

                <div className="don-field">
                  <label className="don-field__label">Destino de tu donacion</label>
                  <div className="don-destinatarios">
                    {DESTINATARIOS.map((d) => (
                      <button
                        key={d.value}
                        type="button"
                        className={`don-destinatario ${destinatario === d.value ? 'is-active' : ''}`}
                        onClick={() => setDestinatario(d.value)}
                      >
                        <span className="don-destinatario__icon">{d.icon}</span>
                        <span>{d.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* COLUMNA DERECHA: mensaje + email + anonimato + CTA */}
              <div className="don-form-col">
                <div className="don-field">
                  <label htmlFor="don-message" className="don-field__label">
                    Mensaje (opcional)
                  </label>
                  <textarea
                    id="don-message"
                    maxLength={500}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Un mensaje de aliento para la comunidad..."
                    rows={4}
                    className="don-textarea"
                  />
                  <span className="don-counter">{message.length} / 500</span>
                </div>

                {/* Campo de correo electronico: se autorrellena si esta logueado,
                    y se valida con ZeroBounce si es invitado. */}
                <div className="don-field">
                  <label htmlFor="don-email" className="don-field__label">
                    <FaEnvelope /> Correo electronico
                    {isAuthenticated && (
                      <span className="don-field__readonly-badge" title="Verificado de tu cuenta">
                        <FaCheck /> verificado
                      </span>
                    )}
                  </label>
                  <div className={`don-email-input ${emailEstado.estado === 'valido' ? 'is-valid' : ''} ${emailEstado.estado === 'invalido' ? 'is-invalid' : ''} ${emailEstado.estado === 'sospechoso' ? 'is-warning' : ''}`}>
                    <input
                      id="don-email"
                      type="email"
                      value={donorEmail}
                      onChange={(e) => setDonorEmail(e.target.value)}
                      placeholder="tunombre@correo.com"
                      maxLength={120}
                      readOnly={isAuthenticated}
                      className="don-form-field__input"
                      autoComplete="email"
                    />
                    <span className="don-email-status" aria-live="polite">
                      {emailEstado.estado === 'verificando' && <FaSpinner className="fa-spin" />}
                      {emailEstado.estado === 'valido' && isAuthenticated && <FaCheck />}
                      {emailEstado.estado === 'valido' && !isAuthenticated && <FaCheck />}
                      {emailEstado.estado === 'sospechoso' && <FaExclamationTriangle />}
                      {emailEstado.estado === 'invalido' && <FaTimesCircle />}
                    </span>
                  </div>
                  {emailEstado.motivo && emailEstado.estado === 'invalido' && !isAuthenticated && (
                    <span className="don-field__error" role="alert">
                      {emailEstado.motivo}
                    </span>
                  )}
                  {emailEstado.motivo && emailEstado.estado === 'sospechoso' && !isAuthenticated && (
                    <span className="don-field__warning" role="status">
                      {emailEstado.motivo}
                    </span>
                  )}
                  {isAuthenticated && (
                    <span className="don-field__helper">
                      Tu correo ya fue verificado al registrarte. Se usara para enviarte la boleta de pago.
                    </span>
                  )}
                </div>

                <label className="don-checkbox">
                  <input
                    type="checkbox"
                    checked={isAnonymous}
                    onChange={(e) => setIsAnonymous(e.target.checked)}
                  />
                  <FaUserSecret />
                  <span>Donar anonimamente (no se mostrara mi nombre publicamente)</span>
                </label>

                {isAnonymous && (
                  <div className="don-donor-info">
                    <p className="don-help">
                      <FaInfoCircle /> Tu donacion sera anonima. Usaremos los datos de tu cuenta solo para enviarte el comprobante.
                    </p>
                  </div>
                )}

                {error && (
                  <div className="don-error" role="alert">
                    <FaExclamationCircle /> {error}
                  </div>
                )}

                <button
                  type="button"
                  className="don-cta"
                  onClick={handleContinuar}
                  disabled={loading}
                >
                  {loading ? (
                    <>Procesando...</>
                  ) : (
                    <>
                      <FaHandHoldingHeart /> Continuar Donando
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ====== MODAL: METODO DE PAGO ====== */}
      {modalOpen && (
        <div className="don-modal-backdrop" onClick={cerrarModalPago}>
          <div
            className="don-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="don-modal-title"
          >
            <button
              type="button"
              className="don-modal__close"
              onClick={cerrarModalPago}
              aria-label="Cerrar"
            >
              <FaTimes />
            </button>

            <header className="don-modal__header">
              <div className="don-modal__icon">
                <FaLock />
              </div>
              <div>
                <h3 id="don-modal-title">Metodo de pago</h3>
                <p className="don-modal__subtitle">
                  Donacion de <strong>{formatPEN(finalAmount)}</strong> a la Comunidad Zapotal
                </p>
              </div>
            </header>

            <div className="don-summary">
              <div className="don-summary__row">
                <span>Monto:</span>
                <strong>{formatPEN(finalAmount)}</strong>
              </div>
              <div className="don-summary__row">
                <span>Destino:</span>
                <strong>{DESTINATARIOS.find((d) => d.value === destinatario)?.label}</strong>
              </div>
            </div>

            <div className="don-trust-banner">
              <FaShieldAlt />
              <p>
                <strong>Pago 100% seguro.</strong> Tus datos de tarjeta se procesan
                directamente. Nunca almacenamos los digitos completos.
              </p>
            </div>

            <div className="don-card-type">
              <label className={`don-card-type__opt ${tipoTarjeta === 'debito' ? 'is-active' : ''}`}>
                <input
                  type="radio"
                  name="tipo_tarjeta"
                  value="debito"
                  checked={tipoTarjeta === 'debito'}
                  onChange={() => setTipoTarjeta('debito')}
                />
                <FaCreditCard />
                <div>
                  <strong>Tarjeta de debito</strong>
                  <span>Debito directo de tu cuenta</span>
                </div>
              </label>
              <label className={`don-card-type__opt ${tipoTarjeta === 'credito' ? 'is-active' : ''}`}>
                <input
                  type="radio"
                  name="tipo_tarjeta"
                  value="credito"
                  checked={tipoTarjeta === 'credito'}
                  onChange={() => setTipoTarjeta('credito')}
                />
                <FaCreditCard />
                <div>
                  <strong>Tarjeta de credito</strong>
                  <span>Visa, Mastercard, American Express</span>
                </div>
              </label>
            </div>

            <div className="don-form-field">
              <label htmlFor="don-card-numero" className="don-form-field__label">
                <FaCreditCard /> Numero de tarjeta
              </label>
              <input
                id="don-card-numero"
                type="text"
                inputMode="numeric"
                value={cardNumber}
                onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                placeholder="0000 0000 0000 0000"
                maxLength={23}
                className="don-form-field__input"
                autoComplete="cc-number"
              />
            </div>

            <div className="don-form-field">
              <label htmlFor="don-card-nombre" className="don-form-field__label">
                <FaUser /> Nombre del titular
              </label>
              <input
                id="don-card-nombre"
                type="text"
                value={cardName}
                onChange={(e) => setCardName(e.target.value)}
                placeholder="Como aparece en la tarjeta"
                className="don-form-field__input"
                autoComplete="cc-name"
              />
            </div>

            <div className="don-form-row-2">
              <div className="don-form-field">
                <label htmlFor="don-card-expiry" className="don-form-field__label">
                  <FaIdCard /> Vencimiento
                </label>
                <input
                  id="don-card-expiry"
                  type="text"
                  inputMode="numeric"
                  value={cardExpiry}
                  onChange={(e) => setCardExpiry(formatExpiry(e.target.value))}
                  placeholder="MM/AA"
                  maxLength={5}
                  className="don-form-field__input"
                  autoComplete="cc-exp"
                />
              </div>
              <div className="don-form-field">
                <label htmlFor="don-card-cvv" className="don-form-field__label">
                  <FaLock /> CVV
                </label>
                <input
                  id="don-card-cvv"
                  type="password"
                  inputMode="numeric"
                  value={cardCvv}
                  onChange={(e) => setCardCvv(e.target.value.replace(/\D/g, '').slice(0, 4))}
                  placeholder="123"
                  maxLength={4}
                  className="don-form-field__input"
                  autoComplete="cc-csc"
                />
              </div>
            </div>

            {modalError && (
              <div className="don-error" role="alert">
                <FaExclamationCircle /> {modalError}
              </div>
            )}

            <button
              type="button"
              className="don-cta don-modal__cta"
              onClick={handleDonar}
              disabled={paying}
            >
              {paying ? (
                <>Procesando pago...</>
              ) : (
                <>
                  <FaHandHoldingHeart /> Donar {formatPEN(finalAmount)}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* ====== MODAL: RESULTADO ====== */}
      {resultModal && (
        <div className="don-modal-backdrop" onClick={cerrarModalResultado}>
          <div
            className={`don-modal don-modal--result don-result--${resultModal.status}`}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <button
              type="button"
              className="don-modal__close"
              onClick={cerrarModalResultado}
              aria-label="Cerrar"
            >
              <FaTimes />
            </button>

            {resultModal.status === 'aprobado' && (
              <>
                <div className="don-modal__icon don-modal__icon--success">
                  <FaCheckCircle />
                </div>
                <h3>Gracias por tu donacion!</h3>
                <p className="don-modal__subtitle">
                  Tu aporte de <strong>{formatPEN(resultModal.monto)}</strong> fue recibido exitosamente.
                </p>
                <div className="don-summary">
                  <div className="don-summary__row">
                    <span>ID de transaccion:</span>
                    <strong><code>#{resultModal.sim_payment_id}</code></strong>
                  </div>
                  <div className="don-summary__row">
                    <span>Tarjeta:</span>
                    <strong>**** {resultModal.ultimos_4} ({resultModal.tipo_tarjeta})</strong>
                  </div>
                  <div className="don-summary__row">
                    <span>Comprobante:</span>
                    <strong>{user?.email || donorEmail}</strong>
                  </div>
                </div>
                <p className="don-modal__message">
                  Tu aporte se traduce en obras concretas para la comunidad. Mil gracias!
                </p>
                <div className="don-modal__actions">
                  <button
                    className="don-cta don-cta--secondary"
                    onClick={() => descargarBoleta(resultModal.donation_id)}
                  >
                    <FaDownload /> Descargar boleta PDF
                  </button>
                  <button className="don-cta" onClick={cerrarModalResultado}>
                    <FaHandHoldingHeart /> Hacer otra donacion
                  </button>
                  <button className="don-cta don-cta--ghost" onClick={() => navigate('/')}>
                    <FaHome /> Volver al inicio
                  </button>
                </div>
              </>
            )}

            {resultModal.status === 'in_process' && (
              <>
                <div className="don-modal__icon don-modal__icon--warning">
                  <FaClock />
                </div>
                <h3>Pago en verificacion</h3>
                <p className="don-modal__subtitle">
                  Estamos verificando tu donacion con el emisor de tu tarjeta.
                </p>
                <div className="don-summary">
                  <div className="don-summary__row">
                    <span>ID de transaccion:</span>
                    <strong><code>#{resultModal.sim_payment_id}</code></strong>
                  </div>
                  <div className="don-summary__row">
                    <span>Tarjeta:</span>
                    <strong>**** {resultModal.ultimos_4} ({resultModal.tipo_tarjeta})</strong>
                  </div>
                </div>
                <p className="don-modal__message">
                  Te notificaremos por correo electronico cuando el pago se confirme.
                </p>
                <div className="don-modal__actions">
                  <button className="don-cta don-cta--ghost" onClick={() => navigate('/')}>
                    <FaHome /> Volver al inicio
                  </button>
                </div>
              </>
            )}

            {resultModal.status === 'rechazado' && (
              <>
                <div className="don-modal__icon don-modal__icon--error">
                  <FaTimesCircle />
                </div>
                <h3>Pago rechazado</h3>
                <p className="don-modal__subtitle">{resultModal.detail}</p>
                <div className="don-summary">
                  <div className="don-summary__row">
                    <span>ID de transaccion:</span>
                    <strong><code>#{resultModal.sim_payment_id}</code></strong>
                  </div>
                  <div className="don-summary__row">
                    <span>Tarjeta:</span>
                    <strong>**** {resultModal.ultimos_4} ({resultModal.tipo_tarjeta})</strong>
                  </div>
                </div>
                <p className="don-modal__message">
                  Puedes intentar nuevamente con otra tarjeta o contactar a tu banco.
                </p>
                <div className="don-modal__actions">
                  <button
                    className="don-cta"
                    onClick={() => { setResultModal(null); setModalOpen(true); }}
                  >
                    <FaRedo /> Intentar de nuevo
                  </button>
                  <button className="don-cta don-cta--ghost" onClick={() => navigate('/')}>
                    <FaHome /> Volver al inicio
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ====== TRUST FOOTER ====== */}
      <section className="don-trust-footer">
        <div className="don-trust-item">
          <FaLock />
          <strong>Pago 100% seguro</strong>
          <span>Encriptacion SSL y procesado por Mercado Pago</span>
        </div>
        <div className="don-trust-item">
          <FaShieldAlt />
          <strong>Tus datos estan protegidos</strong>
          <span>Los datos de tu tarjeta nunca llegan a nuestros servidores</span>
        </div>
        <div className="don-trust-item">
          <FaHandHoldingHeart />
          <strong>100% a la comunidad</strong>
          <span>Cada sol donado se traduce en obras para Zapotal</span>
        </div>
      </section>
    </div>
  );
}
