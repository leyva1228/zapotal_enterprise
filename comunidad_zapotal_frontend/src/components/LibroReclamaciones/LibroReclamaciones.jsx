import React, { useState, useRef } from "react";
import {
  FaCommentDots,
  FaExclamationCircle,
  FaLightbulb,
  FaEnvelope, FaSpinner, FaCheckCircle, FaTimes, FaExclamationTriangle,
  FaBalanceScale, FaPrint, FaRedo,
} from "react-icons/fa";
import api from "../../api";
import useEmailDestino from "../../hooks/useEmailDestino";

import "./LibroReclamaciones.css";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function LibroReclamaciones() {
  const { email_contacto: emailDestino, fallback: emailFallback } = useEmailDestino();
  const [formulario, setFormulario] = useState({
    nombre: "",
    email: "",
    telefono: "",
    direccion: "",
    tipo: "",
    descripcion: "",
  });

  const [cargando, setCargando] = useState(false);
  const [estadoEnvio, setEstadoEnvio] = useState("");
  const [errorDetalle, setErrorDetalle] = useState("");
  const [reclamoEnviado, setReclamoEnviado] = useState(null);
  const [validacionEmail, setValidacionEmail] = useState({ estado: 'idle', sugerencia: null });
  const debounceEmailRef = useRef(null);

  const emailBloqueado = validacionEmail.estado === 'invalido'
    && validacionEmail.motivo !== 'catch-all'
    && !validacionEmail.mensaje?.toLowerCase().includes('sospechoso');

  const cambiarValor = (e) => {
    const { name, value } = e.target;
    setFormulario({ ...formulario, [name]: value });
    if (name === 'email') onEmailChangeValidacion(value);
  };

  const onEmailChangeValidacion = (val) => {
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

  const enviarSolicitud = async (e) => {
    e.preventDefault();
    setCargando(true);
    setEstadoEnvio("");
    setErrorDetalle("");

    try {
      const r = await api.post("/libro-reclamaciones/", formulario);
      setReclamoEnviado(r.data);
      setEstadoEnvio("exito");
      setFormulario({
        nombre: "", email: "", telefono: "", direccion: "", tipo: "", descripcion: "",
      });
    } catch (error) {
      console.error("[LibroReclamaciones] error al enviar:", error);
      const data = error.response?.data;
      const detalles = data?.error?.details || data?.details || data;
      if (detalles && typeof detalles === "object" && Object.keys(detalles).length) {
        const msg = Object.entries(detalles)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v[0] : v}`)
          .join(" · ");
        setErrorDetalle(msg);
      } else if (data?.error?.message) {
        setErrorDetalle(data.error.message);
      } else if (data?.detail) {
        setErrorDetalle(data.detail);
      }
      setEstadoEnvio("error");
    } finally {
      setCargando(false);
    }
  };

  const formatFechaCorta = (str) => {
    if (!str) return '-';
    try {
      return new Date(str).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch { return '-'; }
  };

  return (
    <main className="libro-page">
      <section className="libro-hero">
        <div className="libro-overlay"></div>

        <div className="libro-contenido">
          <div className="libro-etiquetas">
            <span className="libro-etiqueta">
              <FaCommentDots />
              Reclamos
            </span>

            <span className="libro-etiqueta">
              <FaExclamationCircle />
              Quejas
            </span>

            <span className="libro-etiqueta">
              <FaLightbulb />
              Sugerencias
            </span>
          </div>

          <h1>
            Libro de <br />
            Reclamaciones
          </h1>

          <p>
            Este espacio permite registrar reclamos, quejas o sugerencias
            relacionadas con la atención y servicios brindados por la Comunidad
            Campesina Niño Dios de Zapotal. Nuestro compromiso es garantizar una atención
            transparente, responsable y orientada al bienestar de todos los
            comuneros y visitantes.
          </p>
        </div>
      </section>

      <section className="formulario-section">
        <div className="formulario-container">
          <h2>Registrar solicitud</h2>

          <form className="libro-formulario" onSubmit={enviarSolicitud}>
            <div className="grupo-form">
              <input
                type="text"
                name="nombre"
                placeholder="Nombres y apellidos completos"
                value={formulario.nombre}
                onChange={cambiarValor}
                minLength={3}
                required
              />
            </div>

            <div className="grupo-form">
              <div className={`libro-input-with-icon ${
                validacionEmail.estado === 'valido' ? 'libro-input--ok' :
                validacionEmail.estado === 'invalido' ? 'libro-input--warn' : ''
              }`}>
                <input
                  type="email"
                  name="email"
                  placeholder="Correo electrónico"
                  value={formulario.email}
                  onChange={cambiarValor}
                  required
                />
                <span className="libro-input__status" aria-live="polite">
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
                <small className="libro-email-sugerencia">
                  ¿Quizás quisiste decir:{' '}
                  <button
                    type="button"
                    onClick={(e) => {
                      setFormulario({ ...formulario, email: validacionEmail.sugerencia });
                      onEmailChangeValidacion(validacionEmail.sugerencia);
                      e.preventDefault();
                    }}
                  >
                    {validacionEmail.sugerencia}
                  </button>?
                </small>
              )}

              <input
                type="tel"
                name="telefono"
                placeholder="Teléfono (opcional)"
                value={formulario.telefono}
                onChange={cambiarValor}
              />
            </div>

            <input
              type="text"
              name="direccion"
              placeholder="Dirección (opcional)"
              value={formulario.direccion}
              onChange={cambiarValor}
            />

            <select
              name="tipo"
              value={formulario.tipo}
              onChange={cambiarValor}
              required
            >
              <option value="">Seleccione el tipo de solicitud</option>
              <option value="RECLAMO">Reclamo</option>
              <option value="QUEJA">Queja</option>
              <option value="SUGERENCIA">Sugerencia</option>
            </select>

            <textarea
              rows="7"
              name="descripcion"
              placeholder="Describa detalladamente su solicitud (mínimo 10 caracteres)..."
              value={formulario.descripcion}
              onChange={cambiarValor}
              minLength={10}
              required
            ></textarea>

            <button
              type="submit"
              disabled={cargando || emailBloqueado}
              className={cargando ? "boton-cargando" : ""}
            >
              {cargando ? (
                <>
                  <span className="spinner"></span>
                  Enviando...
                </>
              ) : (
                "Enviar solicitud"
              )}
            </button>

            {emailBloqueado && (
              <p className="libro-error-email" role="alert">
                Corrige el correo electronico antes de enviar.
              </p>
            )}

            {estadoEnvio === "exito" && reclamoEnviado && (
              <div className="libro-constancia" role="status">
                <FaCheckCircle className="libro-constancia__icono" />
                <h3>¡Reclamo registrado!</h3>
                <p>Tu mensaje fue recibido. Te notificaremos por correo electronico
                cualquier actualizacion del estado.</p>
                <p className="libro-constancia__linea">
                  <strong>Codigo de seguimiento:</strong>{" "}
                  <code>{reclamoEnviado.numero_reclamo || `LIB-${reclamoEnviado.id}`}</code>
                </p>
                <p className="libro-constancia__linea">
                  <strong>Fecha de recepcion:</strong>{" "}
                  {formatFechaCorta(reclamoEnviado.fecha)}
                </p>
                <p className="libro-constancia__linea">
                  <strong>Plazo maximo de respuesta:</strong>{" "}
                  {formatFechaCorta(reclamoEnviado.plazo_respuesta)} (30 dias habiles)
                </p>
                <div className="libro-constancia__botones">
                  <button
                    type="button"
                    className="libro-constancia__btn"
                    onClick={() => window.print()}
                  >
                    <FaPrint /> Imprimir constancia
                  </button>
                  <button
                    type="button"
                    className="libro-constancia__btn libro-constancia__btn--secundario"
                    onClick={() => {
                      setEstadoEnvio("");
                      setReclamoEnviado(null);
                    }}
                  >
                    <FaRedo /> Enviar otro reclamo
                  </button>
                </div>
              </div>
            )}

            {estadoEnvio === "error" && (
              <div className="alerta-error">
                <h3>Error al enviar</h3>
                <p>
                  {errorDetalle ||
                    "Verifique los datos e intente nuevamente."}
                </p>
              </div>
            )}
          </form>

          <p className="libro-texto-legal" role="note">
            <FaBalanceScale /> Conforme a la <strong>Ley N° 29571</strong>,
            Codigo de Proteccion y Defensa del Consumidor, tu reclamo sera
            atendido en un plazo maximo de <strong>30 dias habiles</strong>.
            Si no recibimos respuesta, se aplicara silencio administrativo
            positivo a tu favor.
          </p>
          <p className="libro-contacto-nota" aria-live="polite">
            <FaEnvelope />
            Su reclamo sera enviado a{" "}
            <a href={`mailto:${emailDestino}`}>{emailDestino}</a>{" "}
            y atendido conforme a la Ley N° 29571.
          </p>
        </div>
      </section>
    </main>
  );
}

export default LibroReclamaciones;
