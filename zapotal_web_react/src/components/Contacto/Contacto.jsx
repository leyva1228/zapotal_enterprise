import React, { useState } from "react";
import axios from "axios";

import {
  FaEnvelope,
  FaPhoneAlt,
  FaMapMarkerAlt,
  FaWhatsapp,
} from "react-icons/fa";

import "./Contacto.css";

function Contacto() {

  const [formulario, setFormulario] = useState({
    nombres: "",
    correo: "",
    telefono: "",
    asunto: "",
    mensaje: "",
  });

  const [enviando, setEnviando] = useState(false);

  const manejarCambio = (e) => {

    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });

  };

  const enviarMensaje = async (e) => {

    e.preventDefault();

    const datos = {
      nombres: formulario.nombres.trim(),
      correo: formulario.correo.trim(),
      telefono: formulario.telefono.trim(),
      asunto: formulario.asunto.trim(),
      mensaje: formulario.mensaje.trim(),
    };

    if (
      !datos.nombres ||
      !datos.correo ||
      !datos.asunto ||
      !datos.mensaje
    ) {

      alert("Completa los campos obligatorios.");

      return;
    }

    if (datos.nombres.length < 3) {

      alert("El nombre debe tener al menos 3 caracteres.");

      return;
    }

    if (datos.asunto.length < 3) {

      alert("El asunto debe tener al menos 3 caracteres.");

      return;
    }

    if (datos.mensaje.length < 10) {

      alert("El mensaje debe tener al menos 10 caracteres.");

      return;
    }

    try {

      setEnviando(true);

      await axios.post(
        "http://127.0.0.1:8000/api/contacto/",
        datos,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      alert("Mensaje enviado correctamente.");

      setFormulario({
        nombres: "",
        correo: "",
        telefono: "",
        asunto: "",
        mensaje: "",
      });

    } catch (error) {

      console.log("ERROR CONTACTO:", error);

      if (error.response) {

        console.log(
          "Respuesta del servidor:",
          error.response.data
        );

        alert(
          "Error del servidor. Revisa que la API esté funcionando."
        );

      } else if (error.request) {

        alert(
          "No hay conexión con Django. Verifica que el servidor esté encendido."
        );

      } else {

        alert(
          "Ocurrió un error inesperado."
        );

      }

    } finally {

      setEnviando(false);

    }
  };

  return (

    <main className="contacto-page">

      {/* HERO */}

      <section className="contacto-hero">

        <div className="contacto-overlay">

          <h1>Contáctanos</h1>

          <p>
            Estamos disponibles para atender consultas,
            sugerencias y mensajes relacionados
            con nuestra comunidad.
          </p>

          {/* ICONOS */}

          <div className="contacto-icons">

            {/* CORREO */}

            <button
              className="icon-circle"
              onClick={() =>
                document
                  .getElementById("correo-section")
                  .scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >
              <FaEnvelope />
            </button>

            {/* TELÉFONO */}

            <button
              className="icon-circle"
              onClick={() =>
                document
                  .getElementById("telefono-section")
                  .scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >
              <FaPhoneAlt />
            </button>

            {/* WHATSAPP */}

            <a
            className="icon-circle"
            href="https://wa.me/921456783"
            target="_blank"
            rel="noreferrer"
            >
            <FaWhatsapp />
            </a>

            {/* MAPA */}

            <button
              className="icon-circle"
              onClick={() =>
                document
                  .getElementById("mapa-zapotal")
                  .scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >
              <FaMapMarkerAlt />
            </button>

          </div>

        </div>

      </section>

      {/* CONTENIDO */}

      <section className="contacto-container">

        {/* INFORMACIÓN */}

        <div className="contacto-info">

          <h2>
            Información de contacto
          </h2>

          <p>
            Puedes comunicarte con nosotros
            mediante los siguientes canales
            oficiales.
          </p>

          {/* UBICACIÓN */}

          <div className="info-box">

            <FaMapMarkerAlt className="info-icon" />

            <div>

              <h3>Ubicación</h3>

              <span>
                Centro Poblado Zapotal,
                Cajamarca - Perú
              </span>

            </div>

          </div>

          {/* CORREO */}

          <div
            className="info-box"
            id="correo-section"
          >

            <FaEnvelope className="info-icon" />

            <div>

              <h3>
                Correo electrónico
              </h3>

              <span>
                contacto@zapotal.com
              </span>

            </div>

          </div>

          {/* TELÉFONO */}

          <div
            className="info-box"
            id="telefono-section"
          >

            <FaPhoneAlt className="info-icon" />

            <div>

              <h3>Teléfono</h3>

              <span>
                +51 987 654 321
              </span>

            </div>

          </div>

        </div>

        {/* FORMULARIO */}

        <div className="contacto-form">

          <h2>
            Enviar mensaje
          </h2>

          <form onSubmit={enviarMensaje}>

            <input
              type="text"
              name="nombres"
              placeholder="Nombres completos"
              value={formulario.nombres}
              onChange={manejarCambio}
            />

            <input
              type="email"
              name="correo"
              placeholder="Correo electrónico"
              value={formulario.correo}
              onChange={manejarCambio}
            />

            <input
              type="text"
              name="telefono"
              placeholder="Teléfono"
              value={formulario.telefono}
              onChange={manejarCambio}
            />

            <input
              type="text"
              name="asunto"
              placeholder="Asunto"
              value={formulario.asunto}
              onChange={manejarCambio}
            />

            <textarea
              name="mensaje"
              placeholder="Escribe tu mensaje..."
              value={formulario.mensaje}
              onChange={manejarCambio}
            />

            <button
              type="submit"
              disabled={enviando}
            >

              {
                enviando
                  ? (
                    <span className="loader-contacto"></span>
                  )
                  : (
                    "Enviar mensaje"
                  )
              }

            </button>

          </form>

        </div>

      </section>

      {/* MAPA */}

      <section
        className="contacto-mapa-section"
        id="mapa-zapotal"
      >

        <div className="contacto-mapa-header">

          <span>
            UBICACIÓN
          </span>

          <h2>
            Encuéntranos en nuestra comunidad
          </h2>

          <p>
            Ubicación referencial del
            Centro Poblado Zapotal,
            Cajamarca - Perú.
          </p>

        </div>

        <div className="contacto-mapa-card">

          <iframe
            title="Plaza de Armas Zapotal"
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1986.0566259555842!2d-78.7048581535762!3d-5.399712120923837!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x91b5091f97fb5759%3A0x8d6949e683cf9c6a!2sPlaza%20Armas%20Zapotal!5e0!3m2!1ses-419!2spe!4v1778180623786!5m2!1ses-419!2spe"
            loading="lazy"
            allowFullScreen
            referrerPolicy="no-referrer-when-downgrade"
          ></iframe>

        </div>

      </section>

    </main>
  );
}

export default Contacto;