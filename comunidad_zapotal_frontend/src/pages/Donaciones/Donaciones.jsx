import React, { useState, useEffect, useRef, useMemo } from 'react';
import { initMercadoPago, Payment } from '@mercadopago/sdk-react';
import { useNavigate } from 'react-router-dom';
import {
  FaHandHoldingHeart, FaLock, FaShieldAlt, FaUsers, FaSeedling,
  FaCheckCircle, FaClock, FaTimesCircle, FaArrowLeft, FaRedo,
  FaUserSecret, FaHome, FaGraduationCap, FaHeartbeat, FaRoad, FaInfoCircle,
} from 'react-icons/fa';
import api, { extractList } from '../../api';
import { useAuth } from '../../context/AuthContext';
import './Donaciones.css';

const MP_PUBLIC_KEY = import.meta.env.VITE_MP_PUBLIC_KEY || '';

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
  const brickRef = useRef(null);

  const [step, setStep] = useState('form');
  const [stats, setStats] = useState(null);
  const [amount, setAmount] = useState(25);
  const [customAmount, setCustomAmount] = useState('');
  const [message, setMessage] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [donorName, setDonorName] = useState(user?.nombre_completo || '');
  const [donorEmail, setDonorEmail] = useState(user?.email || '');
  const [destinatario, setDestinatario] = useState('COMUNIDAD');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [donationId, setDonationId] = useState(null);
  const [publicKey, setPublicKey] = useState(MP_PUBLIC_KEY);

  useEffect(() => {
    if (MP_PUBLIC_KEY) {
      try {
        initMercadoPago(MP_PUBLIC_KEY, { locale: 'es-PE' });
      } catch (e) {
        console.error('Error inicializando MercadoPago SDK:', e);
      }
    }
    api.get('/donaciones/estadisticas/').then((r) => setStats(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    return () => {
      if (brickRef.current && typeof brickRef.current.unmount === 'function') {
        try { brickRef.current.unmount(); } catch (e) { /* ignore */ }
      }
    };
  }, [step]);

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
    if (!isAnonymous && !isAuthenticated && !donorEmail) {
      setError('Ingresa tu email para enviarte el comprobante, o marca "Donar anonimamente".');
      return false;
    }
    if (isAnonymous && !donorEmail) {
      setError('Para donar anonimamente necesitamos un email para enviarte el comprobante.');
      return false;
    }
    return true;
  };

  const handleContinueToPayment = async () => {
    if (!validateForm()) return;
    if (!publicKey) {
      setError('La pasarela de pagos no esta configurada. Contacta al administrador.');
      return;
    }
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
      setPublicKey(data.public_key);
      if (data.public_key && data.public_key !== MP_PUBLIC_KEY) {
        try { initMercadoPago(data.public_key, { locale: 'es-PE' }); } catch (e) { /* ignore */ }
      }
      setStep('brick');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e) {
      const detail = e.response?.data?.detail || e.message || 'Error desconocido';
      setError(`No se pudo iniciar la donacion: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const onPaymentSubmit = ({ selectedPaymentMethod, formData }) => {
    return new Promise((resolve, reject) => {
      api.post('/donaciones/procesar/', {
        donation_id: donationId,
        token: formData.token,
        payment_method_id: formData.payment_method_id,
        issuer_id: formData.issuer_id,
        installments: formData.installments,
        payer: formData.payer,
      })
        .then((response) => {
          setResult(response.data);
          setStep('result');
          window.scrollTo({ top: 0, behavior: 'smooth' });
          resolve();
        })
        .catch((error) => {
          const errData = error.response?.data;
          setResult({
            status: 'rejected',
            detail: errData?.detail || error.message || 'El pago fue rechazado',
          });
          setStep('result');
          window.scrollTo({ top: 0, behavior: 'smooth' });
          reject();
        });
    });
  };

  const onPaymentError = (error) => {
    console.error('Error en Payment Brick:', error);
    setError('Hubo un error al cargar el formulario de pago. Recarga la pagina e intenta de nuevo.');
  };

  const resetFlow = () => {
    setStep('form');
    setResult(null);
    setDonationId(null);
    setError('');
    setMessage('');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const formatStat = (n) => {
    if (n === null || n === undefined) return '0';
    return new Intl.NumberFormat('es-PE').format(n);
  };

  return (
    <div className="don-page">
      {/* ====== HERO ====== */}
      <section className="don-hero">
        <div className="don-hero__overlay" />
        <div className="don-hero__content">
          <FaHandHoldingHeart className="don-hero__icon" />
          <h1 className="don-hero__title">Tu donacion construye futuro</h1>
          <p className="don-hero__subtitle">
            Tus aportes permiten a la Comunidad Campesina Zapotal financiar proyectos de
            infraestructura, becas educativas, programas de salud y desarrollo agricola
            que benefician a las familias de nuestra comunidad.
          </p>

          <div className="don-stats">
            <div className="don-stat">
              <FaUsers className="don-stat__icon" />
              <div>
                <strong>250+</strong>
                <span>Familias beneficiadas</span>
              </div>
            </div>
            <div className="don-stat">
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
                <span>Donaciones recibidas</span>
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
            <p>Apoyo a familias en situacion vulnerable, campañas de salud preventiva.</p>
          </div>
          <div className="don-impact__card">
            <FaSeedling className="don-impact__card-icon" />
            <h3>Desarrollo agricola</h3>
            <p>Programas de capacitacion tecnica para jovenes, insumos para pequenos productores.</p>
          </div>
        </div>
      </section>

      {/* ====== FORMULARIO DE DONACION ====== */}
      {step === 'form' && !isAuthenticated && (
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

      {step === 'form' && isAuthenticated && (
        <section className="don-form-section">
          <div className="don-form-card">
            <h2 className="don-form-title">Cuanto quieres donar?</h2>
            <p className="don-form-subtitle">Elige un monto o escribe el que desees. Lo que aportas transforma.</p>

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

            {/* Destino */}
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

            {/* Mensaje */}
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
                rows={3}
                className="don-textarea"
              />
              <span className="don-counter">{message.length} / 500</span>
            </div>

            {/* Anonimato */}
            <label className="don-checkbox">
              <input
                type="checkbox"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
              />
              <FaUserSecret />
              <span>Donar anonimamente (no se mostrara mi nombre publicamente)</span>
            </label>

            {/* Datos del donante: opcionales (se usan los del usuario si esta vacio) */}
            {isAnonymous && (
              <div className="don-donor-info">
                <p className="don-help">
                  <FaInfoCircle /> Tu donacion sera anonima. Usaremos los datos de tu cuenta solo para enviarte el comprobante.
                </p>
              </div>
            )}

            {error && (
              <div className="don-error" role="alert">
                {error}
              </div>
            )}

            <button
              type="button"
              className="don-cta"
              onClick={handleContinueToPayment}
              disabled={loading || !publicKey}
            >
              {loading ? (
                <>Procesando...</>
              ) : (
                <>
                  <FaLock /> Continuar al pago - {formatPEN(finalAmount)}
                </>
              )}
            </button>

            {!publicKey && (
              <p className="don-warning">
                La pasarela de pagos no esta configurada. Contacta al administrador del sitio.
              </p>
            )}
          </div>
        </section>
      )}

      {/* ====== BRICK DE PAGO ====== */}
      {step === 'brick' && donationId && (
        <section className="don-brick-section">
          <div className="don-brick-card">
            <button
              type="button"
              className="don-back"
              onClick={() => setStep('form')}
            >
              <FaArrowLeft /> Volver y modificar el monto
            </button>

            <h2 className="don-form-title">Completa tu donacion de {formatPEN(finalAmount)}</h2>

            <div className="don-summary">
              <div className="don-summary__row">
                <span>Monto:</span>
                <strong>{formatPEN(finalAmount)}</strong>
              </div>
              {DESTINATARIOS.find((d) => d.value === destinatario) && (
                <div className="don-summary__row">
                  <span>Destino:</span>
                  <strong>{DESTINATARIOS.find((d) => d.value === destinatario).label}</strong>
                </div>
              )}
              {!isAnonymous && donorName && (
                <div className="don-summary__row">
                  <span>De:</span>
                  <strong>{donorName}</strong>
                </div>
              )}
              {isAnonymous && (
                <div className="don-summary__row">
                  <span>De:</span>
                  <strong>Anonimo</strong>
                </div>
              )}
            </div>

            <div className="don-trust-banner">
              <FaShieldAlt />
              <p>
                <strong>Pago 100% seguro.</strong> Tus datos de tarjeta nunca llegan a nuestros
                servidores. El procesamiento lo hace Mercado Pago directamente.
              </p>
            </div>

            <div className="don-brick-container">
              {publicKey ? (
                <Payment
                  initialization={{ amount: Number(finalAmount.toFixed(2)) }}
                  customization={{
                    paymentMethods: {
                      creditCard: 'all',
                      debitCard: 'all',
                    },
                    visual: {
                      style: {
                        theme: 'default',
                      },
                    },
                  }}
                  onSubmit={onPaymentSubmit}
                  onReady={() => {}}
                  onError={onPaymentError}
                />
              ) : (
                <div className="don-error">No se pudo cargar el formulario de pago.</div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ====== RESULTADO ====== */}
      {step === 'result' && result && (
        <section className="don-result-section">
          <div className={`don-result-card don-result-card--${result.status}`}>
            {result.status === 'approved' && (
              <>
                <FaCheckCircle className="don-result-icon" />
                <h2>Gracias por tu donacion!</h2>
                <p>Tu aporte de <strong>{formatPEN(finalAmount)}</strong> ha sido recibido exitosamente.</p>
                {result.mp_payment_id && (
                  <p className="don-result-detail">
                    ID de transaccion: <code>#{result.mp_payment_id}</code>
                  </p>
                )}
                <p className="don-result-detail">
                  El comprobante fue enviado a <strong>{donorEmail || user?.email}</strong>.
                </p>
                <p className="don-result-message">
                  Tu aporte se traduce en obras concretas para la comunidad. Mil gracias!
                </p>
                <div className="don-result-actions">
                  <button className="don-cta don-cta--secondary" onClick={resetFlow}>
                    <FaRedo /> Hacer otra donacion
                  </button>
                  <button className="don-cta don-cta--ghost" onClick={() => navigate('/')}>
                    <FaHome /> Volver al inicio
                  </button>
                </div>
              </>
            )}

            {result.status === 'in_process' && (
              <>
                <FaClock className="don-result-icon" />
                <h2>Estamos procesando tu pago</h2>
                <p>Tu donacion esta en revision. Te notificaremos por email cuando se confirme.</p>
                {result.mp_payment_id && (
                  <p className="don-result-detail">ID: <code>#{result.mp_payment_id}</code></p>
                )}
                <div className="don-result-actions">
                  <button className="don-cta don-cta--secondary" onClick={() => navigate('/')}>
                    <FaHome /> Volver al inicio
                  </button>
                </div>
              </>
            )}

            {result.status === 'rejected' && (
              <>
                <FaTimesCircle className="don-result-icon" />
                <h2>El pago fue rechazado</h2>
                <p>{result.detail || 'Por favor intenta con otro metodo de pago o contacta a tu banco.'}</p>
                <div className="don-result-actions">
                  <button className="don-cta don-cta--secondary" onClick={resetFlow}>
                    <FaRedo /> Intentar de nuevo
                  </button>
                  <button className="don-cta don-cta--ghost" onClick={() => navigate('/')}>
                    <FaHome /> Volver al inicio
                  </button>
                </div>
              </>
            )}
          </div>
        </section>
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
