import React, { useRef, useState } from "react";
import axios from "axios";
import { Link, Navigate } from "react-router-dom";

import {
  FaUser,
  FaEnvelope,
  FaIdCard,
  FaShieldAlt,
  FaCalendarAlt,
  FaCheckCircle,
  FaLock,
  FaCamera,
  FaUserCircle,
  FaUpload,
  FaTimes,
} from "react-icons/fa";

import "./Perfil.css";

function Perfil() {
  const usuarioGuardado = JSON.parse(localStorage.getItem("usuario"));

  const [usuario, setUsuario] = useState(usuarioGuardado);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);

  const [modalAbierto, setModalAbierto] = useState(false);
  const [opcionImagen, setOpcionImagen] = useState("imagen");
  const [vistaPrevia, setVistaPrevia] = useState(null);
  const [archivoSeleccionado, setArchivoSeleccionado] = useState(null);
  const [usarAvatarDefault, setUsarAvatarDefault] = useState(false);

  const inputFotoRef = useRef(null);

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  const nombreCompleto = `${usuario?.nombres || ""} ${usuario?.apellidos || ""}`.trim();

  const fechaRegistro = usuario?.fecha_registro
    ? new Date(usuario.fecha_registro).toLocaleDateString("es-PE", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      })
    : "No disponible";

  const limpiarSeleccion = () => {
    setVistaPrevia(null);
    setArchivoSeleccionado(null);
    setUsarAvatarDefault(false);

    if (inputFotoRef.current) {
      inputFotoRef.current.value = "";
    }
  };

  const abrirModal = () => {
    setModalAbierto(true);
    setOpcionImagen("imagen");
    limpiarSeleccion();
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setOpcionImagen("imagen");
    limpiarSeleccion();
  };

  const abrirSelectorArchivo = () => {
    setOpcionImagen("imagen");
    setUsarAvatarDefault(false);
    setVistaPrevia(null);
    setArchivoSeleccionado(null);

    if (inputFotoRef.current) {
      inputFotoRef.current.value = "";
      inputFotoRef.current.click();
    }
  };

  const seleccionarArchivo = (e) => {
    const archivo = e.target.files[0];

    if (!archivo) return;

    setOpcionImagen("imagen");
    setArchivoSeleccionado(archivo);
    setUsarAvatarDefault(false);
    setVistaPrevia(URL.createObjectURL(archivo));
  };

  const activarAvatar = () => {
    setOpcionImagen("avatar");
    setArchivoSeleccionado(null);
    setVistaPrevia(null);
    setUsarAvatarDefault(true);

    if (inputFotoRef.current) {
      inputFotoRef.current.value = "";
    }
  };

  const cambiarOpcion = (e) => {
    const valor = e.target.value;

    if (valor === "avatar") {
      activarAvatar();
      return;
    }

    abrirSelectorArchivo();
  };

  const guardarImagen = async () => {
    try {
      setCargando(true);
      setMensaje("");

      if (usarAvatarDefault) {
        const usuarioActualizado = {
          ...usuario,
          foto_perfil: "",
        };

        localStorage.setItem("usuario", JSON.stringify(usuarioActualizado));
        setUsuario(usuarioActualizado);
        setMensaje("Avatar actualizado correctamente.");
        cerrarModal();
        return;
      }

      if (!archivoSeleccionado) {
        setMensaje("Selecciona una imagen o un avatar.");
        setCargando(false);
        return;
      }

      const formData = new FormData();
      formData.append("foto_perfil", archivoSeleccionado);

      const response = await axios.patch(
        `http://127.0.0.1:8000/api/usuarios/${usuario.id}/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const usuarioActualizado = {
        ...usuario,
        foto_perfil:
          response.data.foto_perfil_url ||
          response.data.foto_perfil ||
          usuario.foto_perfil,
      };

      localStorage.setItem("usuario", JSON.stringify(usuarioActualizado));
      setUsuario(usuarioActualizado);
      setMensaje("Foto de perfil actualizada correctamente.");
      cerrarModal();

    } catch (error) {
      setMensaje("No se pudo actualizar la imagen.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="perfil-page">

      <section className="perfil-hero">
        <div className="perfil-hero-overlay"></div>

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
          <div className="perfil-card-top"></div>

          <div className="perfil-avatar-box">
            {usuario?.foto_perfil ? (
              <img
                src={usuario.foto_perfil}
                alt="Foto de perfil"
                className="perfil-avatar"
              />
            ) : (
              <div className="perfil-avatar-icon">
                <FaUserCircle />
              </div>
            )}

            <button
              type="button"
              className="perfil-camera-btn"
              onClick={abrirModal}
            >
              <FaCamera />
            </button>
          </div>

          <h2>{nombreCompleto || "Usuario"}</h2>

          <span className="perfil-rol">
            {usuario?.tipo_usuario || "Usuario"}
          </span>

          <div className="perfil-line"></div>

          <p className="perfil-frase">
            “Unidos trabajamos por el desarrollo de nuestra comunidad.”
          </p>

          <button
            type="button"
            className="perfil-upload-btn"
            onClick={abrirModal}
            disabled={cargando}
          >
            <FaUpload />
            {cargando ? "Guardando..." : "Subir imagen"}
          </button>

          {mensaje && (
            <div className="perfil-mensaje">
              {mensaje}
            </div>
          )}
        </section>

        <section className="perfil-info-card">
          <div className="perfil-section-title">
            <h2>Información Personal</h2>
            <span></span>
          </div>

          <div className="perfil-info-list">

            <div className="perfil-info-row">
              <div className="perfil-info-icon"><FaUser /></div>
              <strong>Nombres y Apellidos</strong>
              <p>{nombreCompleto || "No registrado"}</p>
            </div>

            <div className="perfil-info-row">
              <div className="perfil-info-icon"><FaEnvelope /></div>
              <strong>Correo electrónico</strong>
              <p>{usuario?.email || "No registrado"}</p>
            </div>

            <div className="perfil-info-row">
              <div className="perfil-info-icon"><FaIdCard /></div>
              <strong>DNI</strong>
              <p>{usuario?.dni || "No registrado"}</p>
            </div>

            <div className="perfil-info-row">
              <div className="perfil-info-icon"><FaShieldAlt /></div>
              <strong>Tipo de usuario</strong>
              <p>{usuario?.tipo_usuario || "No registrado"}</p>
            </div>

            <div className="perfil-info-row">
              <div className="perfil-info-icon"><FaCalendarAlt /></div>
              <strong>Fecha de registro</strong>
              <p>{fechaRegistro}</p>
            </div>

            <div className="perfil-info-row">
              <div className="perfil-info-icon"><FaCheckCircle /></div>
              <strong>Estado</strong>
              <p className="estado-activo">
                {usuario?.estado || "Activo"}
              </p>
            </div>

          </div>
        </section>

        <section className="perfil-security-card">
          <div>
            <div className="perfil-section-title">
              <h2>Seguridad de la cuenta</h2>
              <span></span>
            </div>

            <p>
              Mantén tu cuenta segura actualizando tu contraseña periódicamente.
            </p>
          </div>

          <button className="perfil-password-btn" type="button">
            <FaLock />
            Cambiar contraseña
          </button>
        </section>

      </main>

      {modalAbierto && (
        <div className="perfil-modal-overlay">
          <div className="perfil-modal">

            <div className="perfil-modal-header">
              <h2>Seleccionar imagen de perfil</h2>

              <button type="button" onClick={cerrarModal}>
                <FaTimes />
              </button>
            </div>

            <div className="perfil-modal-body">
              <label className="perfil-modal-label">
                Opciones de imagen
              </label>

              <select
                className="perfil-modal-select"
                value={opcionImagen}
                onChange={cambiarOpcion}
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
                ) : usarAvatarDefault ? (
                  <FaUserCircle className="perfil-modal-avatar" />
                ) : (
                  <div
                    className="perfil-modal-placeholder"
                    onClick={abrirSelectorArchivo}
                  >
                    <FaUpload />
                  </div>
                )}

                <button
                  type="button"
                  className="perfil-modal-link"
                  onClick={abrirSelectorArchivo}
                >
                  elegir una imagen
                </button>
              </div>
            </div>

            <div className="perfil-modal-footer">
              <button
                type="button"
                className="btn-guardar-modal"
                onClick={guardarImagen}
                disabled={cargando}
              >
                {cargando ? "Guardando..." : "Guardar"}
              </button>

              <button
                type="button"
                className="btn-cancelar-modal"
                onClick={cerrarModal}
              >
                Cancelar
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default Perfil;