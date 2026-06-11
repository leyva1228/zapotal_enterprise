import React, { useState } from "react";
import api from "../../api";
import { FaEnvelope } from "react-icons/fa";
import "./Contacto.css";

const ESTADO_INICIAL = {
  nombres:  "",
  correo:   "",
  telefono: "",
  asunto:   "",
  mensaje:  "",
};

// Validación con reglas exactas del backend
function validar(d) {
  if (!d.nombres || !d.correo || !d.asunto || !d.mensaje)
    return "Completa todos los campos obligatorios.";
  if (d.nombres.length < 3)
    return "El nombre debe tener al menos 3 caracteres.";
  if (d.asunto.length < 3)
    return "El asunto debe tener al menos 3 caracteres.";
  if (d.mensaje.length < 10)
    return "El mensaje debe tener al menos 10 caracteres.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.correo))
    return "Ingresa un correo electrónico válido.";
  if (d.telefono) {
    const soloDigitos = d.telefono.replace(/\D/g, "");
    if (soloDigitos.length < 6 || soloDigitos.length > 15)
      return "El teléfono debe tener entre 6 y 15 dígitos (solo números).";
  }
  return null;
}

const sanitizarTelefono = (tel) => (tel ? tel.replace(/\D/g, "") : "");

const MAPA_NORMAL =
  "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1587.436215433498!2d-78.70441609140151!3d-5.398991904143531!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x91b5091f97fb5759%3A0x8d6949e683cf9c6a!2sPlaza%20Armas%20Zapotal!5e0!3m2!1ses!2spe!4v1780170316874!5m2!1ses!2spe";

const MAPA_SATELITE =
  "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1587.436215433498!2d-78.70441609140151!3d-5.398991904143531!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x91b5091f97fb5759%3A0x8d6949e683cf9c6a!2sPlaza%20Armas%20Zapotal!5e1!3m2!1ses!2spe!4v1780170316874!5m2!1ses!2spe";

function Contacto() {
  const [formulario, setFormulario] = useState(ESTADO_INICIAL);
  const [enviando,   setEnviando  ] = useState(false);
  const [feedback,   setFeedback  ] = useState({ tipo: "", msg: "" });
  const [mapaListo,  setMapaListo ] = useState(false);
  const [vistaMap,   setVistaMap  ] = useState("satelite");

  const manejarCambio = ({ target: { name, value } }) =>
    setFormulario((prev) => ({ ...prev, [name]: value }));

  const enviarMensaje = async (e) => {
    e.preventDefault();

    const datos = Object.fromEntries(
      Object.entries(formulario).map(([k, v]) => [k, v.trim()])
    );

    const error = validar(datos);
    if (error) {
      setFeedback({ tipo: "error", msg: error });
      return;
    }

    const telefonoLimpio = sanitizarTelefono(datos.telefono);
    const datosFinales = { ...datos, telefono: telefonoLimpio };

    try {
      setEnviando(true);
      setFeedback({ tipo: "", msg: "" });

      // Guardamos el tiempo de inicio para forzar un mínimo de 800ms de carga
      const inicio = Date.now();

      const respuesta = await api.post("/contacto/", datosFinales, {
        headers: { "Content-Type": "application/json" },
      });

      // Calculamos cuánto tiempo ha pasado
      const transcurrido = Date.now() - inicio;
      const tiempoRestante = Math.max(0, 800 - transcurrido);

      // Esperamos lo necesario para que el loader se vea al menos 0.8 segundos
      await new Promise(resolve => setTimeout(resolve, tiempoRestante));

      setFeedback({ tipo: "exito", msg: "¡Mensaje enviado! Te responderemos pronto." });
      setFormulario(ESTADO_INICIAL);

      // Limpiar el mensaje de éxito después de 3 segundos
      setTimeout(() => {
        if (feedback.tipo === "exito") {
          setFeedback({ tipo: "", msg: "" });
        }
      }, 3000);

    } catch (err) {
      // Aseguramos que el loader también se muestre al menos un poco
      const transcurrido = Date.now() - (window._inicioEnvio || Date.now());
      const tiempoRestante = Math.max(0, 500 - transcurrido);
      await new Promise(resolve => setTimeout(resolve, tiempoRestante));

      if (err.response && err.response.data && err.response.data.telefono) {
        setFeedback({ tipo: "error", msg: "El teléfono debe tener entre 6 y 15 dígitos (solo números)." });
      } else {
        setFeedback({ tipo: "error", msg: "No se pudo enviar el mensaje. Revisa los datos e intenta nuevamente." });
      }
    } finally {
      setEnviando(false);
    }
  };

  return (
    <main className="contacto-page">

      <section className="contacto-seccion">
        <div className="contacto-bg" aria-hidden="true" />

        <div className="contacto-card">
          <div className="contacto-card__encabezado">
            <h2>Enviar mensaje</h2>
            <p>Los campos marcados con <span className="req">*</span> son obligatorios.</p>
          </div>

          {feedback.msg && (
            <div className={`form-feedback form-feedback--${feedback.tipo}`} role="alert">
              {feedback.msg}
            </div>
          )}

          <form className="contacto-form" onSubmit={enviarMensaje} noValidate>
            <div className="form-fila">
              <div className="form-grupo">
                <label htmlFor="nombres" className="form-label">
                  Nombres completos <span className="req">*</span>
                </label>
                <input id="nombres" type="text" name="nombres" className="form-input"
                  placeholder="Ej. María Torres Vega"
                  value={formulario.nombres} onChange={manejarCambio} autoComplete="name" />
              </div>
              <div className="form-grupo">
                <label htmlFor="telefono" className="form-label">
                  Teléfono <span className="form-label--opcional">(opcional)</span>
                </label>
                <input id="telefono" type="tel" name="telefono" className="form-input"
                  placeholder="Ej. 987654321"
                  value={formulario.telefono} onChange={manejarCambio} autoComplete="tel" />
              </div>
            </div>

            <div className="form-grupo">
              <label htmlFor="correo" className="form-label">
                Correo electrónico <span className="req">*</span>
              </label>
              <input id="correo" type="email" name="correo" className="form-input"
                placeholder="Ej. nombre@correo.com"
                value={formulario.correo} onChange={manejarCambio} autoComplete="email" />
            </div>

            <div className="form-grupo">
              <label htmlFor="asunto" className="form-label">
                Asunto <span className="req">*</span>
              </label>
              <input id="asunto" type="text" name="asunto" className="form-input"
                placeholder="¿En qué podemos ayudarte?"
                value={formulario.asunto} onChange={manejarCambio} />
            </div>

            <div className="form-grupo">
              <label htmlFor="mensaje" className="form-label">
                Mensaje <span className="req">*</span>
              </label>
              <textarea id="mensaje" name="mensaje"
                className="form-input form-input--textarea"
                placeholder="Escribe tu mensaje con detalle..."
                value={formulario.mensaje} onChange={manejarCambio} />
            </div>

            <button type="submit" className="form-btn" disabled={enviando}>
              {enviando
                ? <><span className="form-btn__loader" aria-hidden="true" /> Enviando…</>
                : <><FaEnvelope aria-hidden="true" /> Enviar mensaje</>
              }
            </button>
          </form>
        </div>
      </section>

      <div className="contenedor-separador">
        <div className="onda-svg">
          <svg viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true">
            <path fill="#ffffff" fillOpacity="1" d="M0,32L60,42.7C120,53,240,75,360,74.7C480,75,600,53,720,48C840,43,960,53,1080,64C1200,75,1320,85,1380,90.7L1440,96L1440,120L1380,120C1320,120,1200,120,1080,120C960,120,840,120,720,120C600,120,480,120,360,120C240,120,120,120,60,120L0,120Z"></path>
          </svg>
        </div>

        <div className="contenido-separador">
          <svg className="icono-brujula" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z"/>
          </svg>

          <h2 className="texto-separador">VISÍTANOS EN ZAPOTAL, Huranago</h2>

          <svg className="icono-brujula" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z"/>
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
