import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import api from "../../api";
import {
  FaEnvelope, FaPhone, FaMapMarkerAlt, FaHome, FaExclamationTriangle,
  FaShieldAlt, FaClock, FaWhatsapp, FaCheckCircle, FaSpinner,
  FaTimesCircle, FaExclamationCircle, FaPrint, FaRedo,
} from "react-icons/fa";
import useConfiguracion from "../../hooks/useConfiguracion";
import useEmailDestino from "../../hooks/useEmailDestino";
import "./Contacto.css";

const ESTADO_INICIAL = {
  nombre:   "",
  email:    "",
  telefono: "",
  asunto:   "",
  mensaje:  "",
  website:  "",  // honeypot: debe quedar vacio
};

function validar(d) {
  if (!d.nombre || !d.email || !d.asunto || !d.mensaje)
    return "Completa todos los campos obligatorios.";
  if (d.nombre.length < 3)
    return "El nombre debe tener al menos 3 caracteres.";
  if (d.asunto.length < 3)
    return "El asunto debe tener al menos 3 caracteres.";
  if (d.mensaje.length < 10)
    return "El mensaje debe tener al menos 10 caracteres.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email))
    return "Ingresa un correo electrónico válido.";
  if (d.telefono) {
    const soloDigitos = d.telefono.replace(/\D/g, "");
    if (soloDigitos.length < 6 || soloDigitos.length > 15)
      return "El teléfono debe tener entre 6 y 15 dígitos (solo números).";
  }
  return null;
}

// Traduce un objeto de errores del backend a un string legible
function formatearErrores(errores) {
  if (!errores || typeof errores !== "object") return null;
  // DRF plano: { field: [msg] }  /  envuelto: error.details
  const entries = Object.entries(errores);
  if (entries.length === 0) return null;
  return entries
    .map(([campo, msgs]) => {
      const mensaje = Array.isArray(msgs) ? msgs[0] : msgs;
      const etiqueta = ({
        nombre:  "Nombre",
        email:   "Correo",
        telefono:"Teléfono",
        asunto:  "Asunto",
        mensaje: "Mensaje",
        non_field_errors: "Formulario",
      })[campo] || campo;
      return `${etiqueta}: ${mensaje}`;
    })
    .join(" · ");
}

const sanitizarTelefono = (tel) => (tel ? tel.replace(/\D/g, "") : "");

const MAPA_NORMAL =
  "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1587.436215433498!2d-78.70441609140151!3d-5.398991904143531!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x91b5091f97fb5759%3A0x8d6949e683cf9c6a!2sPlaza%20Armas%20Zapotal!5e0!3m2!1ses!2spe!4v1780170316874!5m2!1ses!2spe";

const MAPA_SATELITE =
  "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1587.436215433498!2d-78.70441609140151!3d-5.398991904143531!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x91b5091f97fb5759%3A0x8d6949e683cf9c6a!2sPlaza%20Armas%20Zapotal!5e1!3m2!1ses!2spe!4v1780170316874!5m2!1ses!2spe";

function Contacto() {
  const { data: cfg } = useConfiguracion();
  const { email_contacto: emailDestino, fallback: emailFallback } = useEmailDestino();
  const [formulario, setFormulario] = useState(ESTADO_INICIAL);
  const [errores,    setErrores   ] = useState({});
  const [enviando,   setEnviando  ] = useState(false);
  const [feedback,   setFeedback  ] = useState({ tipo: "", msg: "" });
  const [codigoEnviado, setCodigoEnviado] = useState(null);
  const [mapaListo,  setMapaListo ] = useState(false);
  // V2.1: AbortController para cancelar envio + countdown de espera.
  const abortRef = useRef(null);
  const [cuentaAtras, setCuentaAtras] = useState(0);
  const [vistaMap,   setVistaMap  ] = useState("satelite");
  // Estado de la validacion live de ZeroBounce.
  // estado: idle | verificando | valido | invalido | sospechoso | error
  const [emailEstado, setEmailEstado] = useState({ estado: "idle", mensaje: "" });
  const debounceRef = useRef(null);

  const wa = cfg?.whatsapp_numero
    ? `https://wa.me/${cfg.whatsapp_numero.replace(/[^0-9]/g, "")}`
    : null;

  const emailBloqueado =
    emailEstado.estado === "invalido" &&
    emailEstado.mensaje &&
    !emailEstado.mensaje.toLowerCase().includes("catch-all") &&
    !emailEstado.mensaje.toLowerCase().includes("sospechoso");

  const manejarCambio = ({ target: { name, value } }) => {
    setFormulario((prev) => ({ ...prev, [name]: value }));
    // Limpiar error del campo cuando el usuario empieza a corregir
    if (errores[name]) {
      setErrores((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  // Live validation del email contra ZeroBounce (debounce 800ms).
  // No bloquea el envio: el backend tambien valida, esta llamada
  // es solo feedback UX.
  useEffect(() => {
    const email = (formulario.email || "").trim();
    const formatoValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!formatoValido) {
      setEmailEstado({ estado: "idle", mensaje: "" });
      if (debounceRef.current) clearTimeout(debounceRef.current);
      return undefined;
    }
    setEmailEstado({ estado: "verificando", mensaje: "Verificando..." });
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        const { data } = await api.get("/validar-email/", {
          params: { email },
        });
        if (data.es_valido) {
          if (data.es_sospechoso) {
            setEmailEstado({
              estado: "sospechoso",
              mensaje: data.motivo || "El dominio acepta cualquier direccion (catch-all)",
            });
          } else {
            setEmailEstado({ estado: "valido", mensaje: "Correo verificado" });
          }
        } else {
          const base = data.motivo || "El correo no es valido";
          const sugerencia = data.did_you_mean
            ? ` Qusite decir: ${data.did_you_mean}?`
            : "";
          setEmailEstado({
            estado: "invalido",
            mensaje: base + sugerencia,
          });
          setErrores((prev) => ({ ...prev, email: base + sugerencia }));
        }
      } catch (e) {
        // Si el endpoint falla (red, 5xx, etc.) no bloqueamos al usuario.
        setEmailEstado({ estado: "idle", mensaje: "" });
      }
    }, 800);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [formulario.email]);

  const enviarMensaje = async (e) => {
    e.preventDefault();
    setErrores({});

    const datos = Object.fromEntries(
      Object.entries(formulario).map(([k, v]) => [k, (v || "").trim()])
    );

    const error = validar(datos);
    if (error) {
      setFeedback({ tipo: "error", msg: error });
      return;
    }

    const telefonoLimpio = sanitizarTelefono(datos.telefono);
    const datosFinales = { ...datos, telefono: telefonoLimpio };

    // V2.1: AbortController para que el usuario pueda cancelar.
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    // V2.1: countdown regresivo mientras espera respuesta del backend.
    // El usuario ve cuanto tiempo le queda antes del timeout (15s).
    const DEADLINE_MS = 15000;
    setCuentaAtras(Math.ceil(DEADLINE_MS / 1000));
    const tickInterval = setInterval(() => {
      setCuentaAtras((s) => (s > 0 ? s - 1 : 0));
    }, 1000);
    const timeoutId = setTimeout(() => {
      controller.abort();
      setFeedback({ tipo: "error", msg: "La solicitud tardo demasiado. Intenta de nuevo." });
      setEnviando(false);
    }, DEADLINE_MS);

    try {
      setEnviando(true);
      setFeedback({ tipo: "", msg: "" });

      const inicio = Date.now();
      await api.post("/contacto/", datosFinales, {
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
      });
      const transcurrido = Date.now() - inicio;
      const tiempoRestante = Math.max(0, 800 - transcurrido);
      await new Promise((resolve) => setTimeout(resolve, tiempoRestante));

      setFeedback({
        tipo: "exito",
        msg: "¡Mensaje enviado! Te responderemos pronto al correo proporcionado.",
      });
      setCodigoEnviado(r.data?.id || new Date().getTime());
      setFormulario(ESTADO_INICIAL);
    } catch (err) {
      clearInterval(tickInterval);
      clearTimeout(timeoutId);
      abortRef.current = null;
      // Log tecnico para debugging
      // eslint-disable-next-line no-console
      console.error("[Contacto] error al enviar:", err);

      const status = err.response?.status;
      const data   = err.response?.data;

      // Cancelado por el usuario (AbortController) o por timeout
      if (err.name === "CanceledError" || err.name === "AbortError" ||
          err.code === "ERR_CANCELED") {
        return; // no mostrar feedback negativo
      }

      // Throttling (429) - respetar retry-after si viene
      if (status === 429) {
        const retryAfter = parseInt(
          err.response.headers?.["retry-after"] || "60", 10,
        );
        setFeedback({
          tipo: "error",
          msg: `Has enviado muchos mensajes. Vuelve a intentarlo en ${retryAfter} segundos.`,
        });
      // Honeypot / spam (400 con detail)
      } else if (status === 400 && data?.detail) {
        setFeedback({ tipo: "error", msg: data.detail });
      // 400 con detalles por campo (validacion)
      } else if (status === 400) {
        const detalles = data?.error?.details || data?.details || data;
        const msg = formatearErrores(detalles) || data?.error?.message ||
          "Hay errores en el formulario. Revisa los datos e intenta nuevamente.";
        setFeedback({ tipo: "error", msg });
      // CSRF o sesion expirada (403)
      } else if (status === 403) {
        setFeedback({
          tipo: "error",
          msg: "Tu sesión expiró. Recarga la página e intenta de nuevo.",
        });
      // 5xx - servidor
      } else if (status >= 500) {
        setFeedback({
          tipo: "error",
          msg: "El servidor tuvo un problema. Intenta de nuevo en unos minutos.",
        });
      // Sin respuesta (red, CORS, offline)
      } else if (!err.response) {
        setFeedback({
          tipo: "error",
          msg: "No se pudo conectar con el servidor. Verifica tu conexión a internet.",
        });
      // Cualquier otro caso
      } else {
        setFeedback({
          tipo: "error",
          msg: "No se pudo enviar el mensaje. Intenta de nuevo en unos minutos.",
        });
      }
      } finally {
      clearInterval(tickInterval);
      clearTimeout(timeoutId);
      abortRef.current = null;
      setEnviando(false);
      setCuentaAtras(0);
    }
  };

  const cancelarEnvio = () => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  };

  return (
    <main className="contacto-page">

      {/* HERO compacto */}
      <section className="contacto-hero">
        <div className="contacto-hero__bg" aria-hidden="true" />
        <div className="contacto-hero__contenido">
          <span className="contacto-hero__label">Estamos para escucharte</span>
          <h1>Contacto</h1>
          <p>
            Escríbenos por el formulario, visítanos en la Casa Comunal o
            contáctanos por los canales oficiales. Te responderemos a la
            brevedad.
          </p>
        </div>
      </section>

      {/* LAYOUT 2 COLUMNAS: info izquierda + form derecho */}
      <section className="contacto-grid">
        {/* ============ COLUMNA IZQUIERDA: info de contacto ============ */}
        <aside className="contacto-info" aria-label="Información de contacto">

          <div className="contacto-info__cabecera">
            <span className="contacto-info__eyebrow">Comunidad Zapotal</span>
            <h2>Información de contacto</h2>
            <p>
              {cfg?.descripcion_corta ||
                "Comunidad Campesina organizada, con sede institucional en la Casa Comunal."}
            </p>
          </div>

          {/* Tarjeta Casa Comunal */}
          {cfg && (
            <div className="contacto-info__tarjeta">
              <div className="contacto-info__tarjeta-encabezado">
                <FaHome className="contacto-info__icono" />
                <h3>Casa Comunal</h3>
              </div>
              <p className="contacto-info__tarjeta-descripcion">
                Sede institucional. Aquí sesiona la Asamblea General y la
                Directiva Comunal.
              </p>
              <ul className="contacto-info__lista">
                {cfg.direccion_casa_comunal && (
                  <li>
                    <FaMapMarkerAlt className="contacto-info__li-icono" />
                    <div>
                      <strong>Dirección</strong>
                      <span>{cfg.direccion_casa_comunal}</span>
                    </div>
                  </li>
                )}
                {cfg.telefono_fijo && (
                  <li>
                    <FaPhone className="contacto-info__li-icono" />
                    <div>
                      <strong>Teléfono</strong>
                      <a href={`tel:${cfg.telefono_fijo.replace(/\s/g, "")}`}>
                        {cfg.telefono_fijo}
                      </a>
                    </div>
                  </li>
                )}
                {cfg.email_contacto && (
                  <li>
                    <FaEnvelope className="contacto-info__li-icono" />
                    <div>
                      <strong>Email</strong>
                      <a href={`mailto:${emailDestino}`}>
                        {emailDestino}
                      </a>
                    </div>
                  </li>
                )}
                {cfg.horario_atencion && (
                  <li>
                    <FaClock className="contacto-info__li-icono" />
                    <div>
                      <strong>Horario</strong>
                      <span>{cfg.horario_atencion}</span>
                    </div>
                  </li>
                )}
              </ul>
              {wa && (
                <a
                  href={wa}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="contacto-info__btn contacto-info__btn--wa"
                >
                  <FaWhatsapp /> Escríbenos por WhatsApp
                </a>
              )}
            </div>
          )}

          {/* Tarjeta Canal de Denuncias */}
          {cfg && (
            <div className="contacto-info__tarjeta contacto-info__tarjeta--denuncias">
              <div className="contacto-info__tarjeta-encabezado">
                <FaExclamationTriangle className="contacto-info__icono" />
                <h3>Canal de Denuncias</h3>
              </div>
              <p className="contacto-info__tarjeta-descripcion">
                Tu identidad será protegida conforme a la Ley 29733. Puedes
                reportar irregularidades de forma segura y confidencial.
              </p>
              <a
                href={`mailto:${emailDestino}?subject=Denuncia%20anonima`}
                className="contacto-info__btn contacto-info__btn--denuncia"
              >
                <FaShieldAlt /> {emailDestino}
              </a>
            </div>
          )}

          {/* Enlace al Marco Legal */}
          <Link to="/nosotros/marco-legal" className="contacto-info__link-marco-legal">
            <FaShieldAlt /> Conoce nuestro Marco Legal
          </Link>
        </aside>

        {/* ============ COLUMNA DERECHA: formulario ============ */}
        <div className="contacto-formulario">
          <div className="contacto-formulario__encabezado">
            <h2>Enviar mensaje</h2>
            <p>
              Los campos con <span className="req">*</span> son obligatorios.
              Te respondemos por correo electrónico.
            </p>
          </div>

          {feedback.msg && (
            <div
              className={`form-feedback form-feedback--${feedback.tipo}`}
              role="alert"
            >
              {feedback.tipo === "exito" && <FaCheckCircle aria-hidden="true" />}
              {feedback.msg}
            </div>
          )}

          <form className="contacto-form" onSubmit={enviarMensaje} noValidate>
            {/* Honeypot anti-spam: los bots autocompletan este campo, los humanos no. */}
            <div className="form-honeypot" aria-hidden="true">
              <label htmlFor="website-hp">Sitio web</label>
              <input
                id="website-hp"
                type="text"
                name="website"
                tabIndex={-1}
                autoComplete="off"
                value={formulario.website || ""}
                onChange={manejarCambio}
              />
            </div>

            <div className="form-fila">
              <div className="form-grupo">
                <label htmlFor="nombre" className="form-label">
                  Nombres completos <span className="req">*</span>
                </label>
                <input
                  id="nombre"
                  type="text"
                  name="nombre"
                  className={`form-input ${errores.nombre ? "form-input--error" : ""}`}
                  placeholder="Ej. María Torres Vega"
                  value={formulario.nombre}
                  onChange={manejarCambio}
                  autoComplete="name"
                  autoFocus
                  minLength={3}
                  maxLength={200}
                  aria-invalid={!!errores.nombre}
                  aria-describedby={errores.nombre ? "err-nombre" : undefined}
                  required
                />
                {errores.nombre && (
                  <span id="err-nombre" className="form-grupo__error" role="alert">
                    {errores.nombre}
                  </span>
                )}
              </div>
              <div className="form-grupo">
                <label htmlFor="telefono" className="form-label">
                  Teléfono <span className="form-label--opcional">(opcional)</span>
                </label>
                <input
                  id="telefono"
                  type="tel"
                  name="telefono"
                  className={`form-input ${errores.telefono ? "form-input--error" : ""}`}
                  placeholder="Ej. 987654321"
                  value={formulario.telefono}
                  onChange={manejarCambio}
                  autoComplete="tel"
                  maxLength={15}
                  inputMode="tel"
                  aria-invalid={!!errores.telefono}
                  aria-describedby={errores.telefono ? "err-telefono" : undefined}
                />
                {errores.telefono && (
                  <span id="err-telefono" className="form-grupo__error" role="alert">
                    {errores.telefono}
                  </span>
                )}
              </div>
            </div>

            <div className="form-grupo">
              <label htmlFor="email" className="form-label">
                Correo electrónico <span className="req">*</span>
              </label>
              <div className="form-grupo__input-con-icono">
                <input
                  id="email"
                  type="email"
                  name="email"
                  className={`form-input ${errores.email ? "form-input--error" : ""} ${emailEstado.estado === "valido" ? "form-input--valido" : ""}`}
                  placeholder="Ej. nombre@correo.com"
                  value={formulario.email}
                  onChange={manejarCambio}
                  autoComplete="email"
                  maxLength={254}
                  aria-invalid={!!errores.email || emailEstado.estado === "invalido"}
                  aria-describedby={
                    errores.email
                      ? "err-email"
                      : emailEstado.mensaje
                      ? "estado-email"
                      : undefined
                  }
                  required
                />
                {emailEstado.estado === "verificando" && (
                  <FaSpinner
                    className="form-grupo__icono form-grupo__icono--verificando"
                    aria-label="Verificando"
                  />
                )}
                {emailEstado.estado === "valido" && (
                  <FaCheckCircle
                    className="form-grupo__icono form-grupo__icono--valido"
                    aria-label="Verificado"
                  />
                )}
                {emailEstado.estado === "sospechoso" && (
                  <FaExclamationCircle
                    className="form-grupo__icono form-grupo__icono--sospechoso"
                    aria-label="Sospechoso"
                  />
                )}
                {emailEstado.estado === "invalido" && (
                  <FaTimesCircle
                    className="form-grupo__icono form-grupo__icono--invalido"
                    aria-label="Invalido"
                  />
                )}
              </div>
              {errores.email && (
                <span id="err-email" className="form-grupo__error" role="alert">
                  {errores.email}
                </span>
              )}
              {!errores.email && emailEstado.mensaje && (
                <span
                  id="estado-email"
                  className={`form-grupo__ayuda form-grupo__ayuda--${emailEstado.estado}`}
                  role="status"
                >
                  {emailEstado.mensaje}
                </span>
              )}
            </div>

            <div className="form-grupo">
              <label htmlFor="asunto" className="form-label">
                Asunto <span className="req">*</span>
              </label>
              <input
                id="asunto"
                type="text"
                name="asunto"
                className={`form-input ${errores.asunto ? "form-input--error" : ""}`}
                placeholder="¿En qué podemos ayudarte?"
                value={formulario.asunto}
                onChange={manejarCambio}
                aria-invalid={!!errores.asunto}
                aria-describedby={errores.asunto ? "err-asunto" : undefined}
                required
              />
              {errores.asunto && (
                <span id="err-asunto" className="form-grupo__error" role="alert">
                  {errores.asunto}
                </span>
              )}
            </div>

            <div className="form-grupo">
              <label htmlFor="mensaje" className="form-label">
                Mensaje <span className="req">*</span>
              </label>
              <textarea
                id="mensaje"
                name="mensaje"
                className={`form-input form-input--textarea ${errores.mensaje ? "form-input--error" : ""}`}
                placeholder="Escribe tu mensaje con detalle (mínimo 10 caracteres)..."
                value={formulario.mensaje}
                onChange={manejarCambio}
                rows={6}
                maxLength={1000}
                aria-invalid={!!errores.mensaje}
                aria-describedby={errores.mensaje ? "err-mensaje" : undefined}
                required
              />
              <div className="form-grupo__contador">
                {formulario.mensaje.length} / 1000 caracteres
              </div>
              {errores.mensaje && (
                <span id="err-mensaje" className="form-grupo__error" role="alert">
                  {errores.mensaje}
                </span>
              )}
            </div>

            <button
              type="submit"
              className="form-btn"
              disabled={enviando || emailBloqueado}
            >
              {enviando ? (
                <>
                  <span className="form-btn__loader" aria-hidden="true" />
                  Enviando…{cuentaAtras > 0 && ` (${cuentaAtras}s)`}
                </>
              ) : (
                <>
                  <FaEnvelope aria-hidden="true" /> Enviar mensaje
                </>
              )}
            </button>

            {enviando && (
              <button
                type="button"
                className="form-btn form-btn--secondary"
                onClick={cancelarEnvio}
              >
                Cancelar envio
              </button>
            )}

            <p className="form-aviso">
              Al enviar este formulario aceptas que la Comunidad te contacte
              por los medios proporcionados. Más información en nuestra{" "}
              <Link to="/privacidad">Política de Privacidad</Link>.
            </p>
          </form>

          {/* Panel de confirmacion post-envio (solo si hubo exito). */}
          {feedback.tipo === "exito" && codigoEnviado && (
            <div className="form-confirmacion" role="status">
              <FaCheckCircle className="form-confirmacion__icono" />
              <h3>Mensaje enviado correctamente</h3>
              <p>
                Tu mensaje fue recibido. Te responderemos por correo electronico
                a la direccion proporcionada en un plazo maximo de 48 horas.
              </p>
              <p className="form-confirmacion__codigo">
                <strong>Codigo de seguimiento:</strong> ZAP-{String(codigoEnviado).padStart(6, '0')}
              </p>
              <div className="form-confirmacion__botones">
                <button
                  type="button"
                  className="form-confirmacion__btn"
                  onClick={() => window.print()}
                >
                  <FaPrint /> Imprimir constancia
                </button>
                <button
                  type="button"
                  className="form-confirmacion__btn form-confirmacion__btn--secundario"
                  onClick={() => {
                    setFeedback({ tipo: "", msg: "" });
                    setCodigoEnviado(null);
                  }}
                >
                  <FaRedo /> Enviar otro mensaje
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* SEPARADOR + MAPA */}
      <div className="contenedor-separador">
        <div className="onda-svg">
          <svg viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true">
            <path
              fill="#ffffff"
              fillOpacity="1"
              d="M0,32L60,42.7C120,53,240,75,360,74.7C480,75,600,53,720,48C840,43,960,53,1080,64C1200,75,1320,85,1380,90.7L1440,96L1440,120L1380,120C1320,120,1200,120,1080,120C960,120,840,120,720,120C600,120,480,120,360,120C240,120,120,120,60,120L0,120Z"
            />
          </svg>
        </div>

        <div className="contenido-separador">
          <svg className="icono-brujula" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z" />
          </svg>
          <h2 className="texto-separador">VISÍTANOS EN ZAPOTAL, Huarango</h2>
          <svg className="icono-brujula" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z" />
          </svg>
        </div>
      </div>

      <section className="contacto-mapa" id="mapa-zapotal">
        <div className={`mapa-wrapper ${mapaListo ? "mapa-wrapper--listo" : ""}`}>
          {!mapaListo && (
            <div className="mapa-loader" aria-label="Cargando mapa">
              <span className="mapa-spinner" aria-hidden="true" />
              <p>Cargando mapa…</p>
            </div>
          )}
          <iframe
            key={vistaMap}
            title="Plaza de Armas Zapotal"
            src={vistaMap === "satelite" ? MAPA_SATELITE : MAPA_NORMAL}
            loading="lazy"
            allowFullScreen
            referrerPolicy="no-referrer-when-downgrade"
            onLoad={() => setMapaListo(true)}
            className={mapaListo ? "mapa-iframe--visible" : ""}
          />
        </div>
      </section>
    </main>
  );
}

export default Contacto;
