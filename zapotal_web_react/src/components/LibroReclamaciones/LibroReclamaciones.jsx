import React, { useState } from "react";
import {
  FaCommentDots,
  FaExclamationCircle,
  FaLightbulb,
} from "react-icons/fa";
import axios from "axios";

import "./LibroReclamaciones.css";

function LibroReclamaciones() {
  const [formulario, setFormulario] = useState({
    nombres: "",
    apellidos: "",
    dni: "",
    correo: "",
    telefono: "",
    tipo_solicitud: "",
    asunto: "",
    descripcion: "",
    pedido: "",
  });

  const [cargando, setCargando] = useState(false);
  const [estadoEnvio, setEstadoEnvio] = useState("");

  const cambiarValor = (e) => {
    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });
  };

  const enviarSolicitud = async (e) => {
    e.preventDefault();

    setCargando(true);
    setEstadoEnvio("");

    try {
      await axios.post(
        "http://localhost:8000/api/libro-reclamaciones/",
        formulario
      );

      setEstadoEnvio("exito");

      setFormulario({
        nombres: "",
        apellidos: "",
        dni: "",
        correo: "",
        telefono: "",
        tipo_solicitud: "",
        asunto: "",
        descripcion: "",
        pedido: "",
      });

      setTimeout(() => {
        setEstadoEnvio("");
      }, 4000);
    } catch (error) {
      console.log("ERROR:", error.response?.data || error);
      setEstadoEnvio("error");
    } finally {
      setCargando(false);
    }
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
            Campesina Zapotal. Nuestro compromiso es garantizar una atención
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
                name="nombres"
                placeholder="Nombres"
                value={formulario.nombres}
                onChange={cambiarValor}
                required
              />

              <input
                type="text"
                name="apellidos"
                placeholder="Apellidos"
                value={formulario.apellidos}
                onChange={cambiarValor}
                required
              />
            </div>

            <div className="grupo-form">
              <input
                type="text"
                name="dni"
                placeholder="DNI"
                value={formulario.dni}
                onChange={cambiarValor}
                maxLength="8"
                required
              />

              <input
                type="email"
                name="correo"
                placeholder="Correo electrónico"
                value={formulario.correo}
                onChange={cambiarValor}
                required
              />
            </div>

            <div className="grupo-form">
              <input
                type="text"
                name="telefono"
                placeholder="Teléfono"
                value={formulario.telefono}
                onChange={cambiarValor}
              />

              <select
                name="tipo_solicitud"
                value={formulario.tipo_solicitud}
                onChange={cambiarValor}
                required
              >
                <option value="">Seleccione el tipo de solicitud</option>
                <option value="RECLAMO">Reclamo</option>
                <option value="QUEJA">Queja</option>
                <option value="SUGERENCIA">Sugerencia</option>
              </select>
            </div>

            <input
              type="text"
              name="asunto"
              placeholder="Asunto"
              value={formulario.asunto}
              onChange={cambiarValor}
              required
            />

            <textarea
              rows="7"
              name="descripcion"
              placeholder="Describa detalladamente su solicitud..."
              value={formulario.descripcion}
              onChange={cambiarValor}
              required
            ></textarea>

            <textarea
              rows="4"
              name="pedido"
              placeholder="Pedido del usuario (opcional)"
              value={formulario.pedido}
              onChange={cambiarValor}
            ></textarea>

            <button
              type="submit"
              disabled={cargando}
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

            {estadoEnvio === "exito" && (
              <div className="alerta-exito">
                <div className="check-container">
                  <div className="check-icon"></div>
                </div>

                <h3>Solicitud enviada</h3>

                <p>Su reclamo fue registrado correctamente.</p>
              </div>
            )}

            {estadoEnvio === "error" && (
              <div className="alerta-error">
                <h3>Error al enviar</h3>

                <p>Verifique los datos e intente nuevamente.</p>
              </div>
            )}
          </form>
        </div>
      </section>
    </main>
  );
}

export default LibroReclamaciones;