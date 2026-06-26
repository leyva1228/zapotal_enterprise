/**
 * AdminPerfil - Pagina de gestion del perfil del usuario admin actual.
 *
 * LOOP 3: Nueva pagina en el sidebar que permite:
 * - Ver y editar datos personales (nombre, telefono, foto).
 * - Cambiar contrasena.
 * - Ver estado de 2FA.
 *
 * Datos del usuario provienen de useAuth (cargados al login).
 * Edicion: PATCH /usuarios/{id}/.
 * Cambio de contrasena: POST /usuarios/{id}/cambiar-password/.
 */
import React, { useState, useEffect } from "react";
import { FaUser, FaLock, FaShieldAlt, FaCamera, FaCheck, FaTimes } from "react-icons/fa";
import { useAuth } from "../../context/AuthContext";
import api from "../../api";

function getRoleLabel(tipo) {
  if (tipo === "ADMIN") return "Administrador";
  if (tipo === "COMUNERO") return "Comunero";
  return tipo || "Usuario";
}

function getStatusLabel(estado) {
  const map = {
    ACTIVO: "Vigente",
    INACTIVO: "Inactivo",
    BLOQUEADO: "Bloqueado",
    RECHAZADO: "Rechazado",
    PENDIENTE_APROBACION: "Pendiente de aprobacion",
    PENDIENTE_OTP: "Pendiente de verificacion",
  };
  return map[estado] || estado;
}

export default function AdminPerfil() {
  const { user } = useAuth();
  const [editMode, setEditMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingPwd, setSavingPwd] = useState(false);
  const [ok, setOk] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    email: "",
    telefono: "",
  });
  const [passwords, setPasswords] = useState({
    password: "",
    password_confirmacion: "",
  });
  const [showPwd, setShowPwd] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        email: user.email || "",
        telefono: user.telefono || "",
      });
    }
  }, [user]);

  if (!user) {
    return <div className="admin-loading">Cargando perfil...</div>;
  }

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true);
    setError("");
    setOk("");
    try {
      const { data } = await api.patch(`/usuarios/${user.id}/`, form);
      setForm({
        email: data.email || "",
        telefono: data.telefono || "",
      });
      setOk("Perfil actualizado correctamente. Recarga la pagina si el sidebar no refleja los cambios.");
      setEditMode(false);
    } catch (err) {
      const d = err.response?.data;
      setError(
        typeof d === "string"
          ? d
          : d?.detail || JSON.stringify(d) || "No se pudo guardar el perfil."
      );
    } finally {
      setSaving(false);
    }
  };

  const cambiarPassword = async (e) => {
    e?.preventDefault?.();
    setError("");
    setOk("");
    if (passwords.password.length < 8) {
      setError("La contrasena debe tener al menos 8 caracteres.");
      return;
    }
    if (passwords.password !== passwords.password_confirmacion) {
      setError("Las contrasenas no coinciden.");
      return;
    }
    setSavingPwd(true);
    try {
      await api.post(`/usuarios/${user.id}/cambiar-password/`, {
        password: passwords.password,
      });
      setOk("Contrasena cambiada. Cierra sesion y vuelve a entrar para usarla.");
      setPasswords({ password: "", password_confirmacion: "" });
      setShowPwd(false);
    } catch (err) {
      const d = err.response?.data;
      setError(
        typeof d === "string"
          ? d
          : d?.detail || JSON.stringify(d) || "No se pudo cambiar la contrasena."
      );
    } finally {
      setSavingPwd(false);
    }
  };

  return (
    <div>
      {ok && <div className="admin-success">{ok}</div>}
      {error && <div className="admin-error">{error}</div>}

      {/* Card: Datos personales */}
      <div className="admin-card">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaUser style={{ marginRight: 8 }} />
            Datos personales
          </h3>
        </div>
        <div className="admin-card__body">
          <form onSubmit={guardar}>
            <div className="admin-form-row" style={{ marginBottom: 16 }}>
              {/* Foto */}
              <div className="admin-form-group" style={{ alignItems: "center", textAlign: "center" }}>
                <label className="admin-form-group__label">Foto de perfil</label>
                <div
                  style={{
                    width: 96,
                    height: 96,
                    borderRadius: "50%",
                    background: "#e5e7eb",
                    margin: "0 auto 8px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    overflow: "hidden",
                    color: "#6b7280",
                    fontSize: 40,
                  }}
                >
                  {user.foto_perfil_url ? (
                    <img
                      src={user.foto_perfil_url}
                      alt="Foto de perfil"
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  ) : (
                    <FaUser />
                  )}
                </div>
                <p className="admin-form-hint">
                  La foto se edita desde la pagina de perfil publica.
                </p>
              </div>

              {/* Info basica */}
              <div>
                <div className="admin-form-group">
                  <label className="admin-form-group__label">Email</label>
                  <input
                    type="email"
                    className="admin-input"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    disabled={!editMode}
                  />
                </div>
                <div className="admin-form-group">
                  <label className="admin-form-group__label">Telefono</label>
                  <input
                    type="tel"
                    className="admin-input"
                    value={form.telefono}
                    onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                    disabled={!editMode}
                    placeholder="+51 999 888 777"
                  />
                </div>
              </div>
            </div>

            <div className="admin-form-row">
              <div className="admin-form-group">
                <label className="admin-form-group__label">Tipo de usuario</label>
                <p className="admin-form-hint" style={{ marginTop: 6 }}>
                  <span
                    className={
                      "admin-badge " +
                      (user.tipo_usuario === "ADMIN"
                        ? "admin-badge--danger"
                        : user.tipo_usuario === "COMUNERO"
                        ? "admin-badge--info"
                        : "admin-badge--gray")
                    }
                  >
                    {getRoleLabel(user.tipo_usuario)}
                  </span>
                </p>
              </div>
              <div className="admin-form-group">
                <label className="admin-form-group__label">Estado de cuenta</label>
                <p className="admin-form-hint" style={{ marginTop: 6 }}>
                  <span
                    className={
                      "admin-badge " +
                      (user.estado === "ACTIVO"
                        ? "admin-badge--success"
                        : user.estado === "BLOQUEADO" || user.estado === "RECHAZADO"
                        ? "admin-badge--danger"
                        : "admin-badge--warning")
                    }
                  >
                    {getStatusLabel(user.estado)}
                  </span>
                </p>
              </div>
            </div>

            <div className="admin-form-actions">
              {editMode ? (
                <>
                  <button
                    type="submit"
                    className="admin-btn admin-btn-primary"
                    disabled={saving}
                  >
                    <FaCheck /> {saving ? "Guardando..." : "Guardar cambios"}
                  </button>
                  <button
                    type="button"
                    className="admin-btn admin-btn-secondary"
                    onClick={() => {
                      setEditMode(false);
                      setError("");
                      setOk("");
                    }}
                    disabled={saving}
                  >
                    <FaTimes /> Cancelar
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  className="admin-btn admin-btn-primary"
                  onClick={() => setEditMode(true)}
                >
                  Editar perfil
                </button>
              )}
            </div>
          </form>
        </div>
      </div>

      {/* Card: Cambiar contrasena */}
      <div className="admin-card">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaLock style={{ marginRight: 8 }} />
            Cambiar contrasena
          </h3>
        </div>
        <div className="admin-card__body">
          <form onSubmit={cambiarPassword}>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Nueva contrasena</label>
              <div style={{ display: "flex", gap: 8 }}>
                <input
                  type={showPwd ? "text" : "password"}
                  className="admin-input"
                  value={passwords.password}
                  onChange={(e) =>
                    setPasswords({ ...passwords, password: e.target.value })
                  }
                  placeholder="Minimo 8 caracteres"
                  autoComplete="new-password"
                  minLength={8}
                />
                <button
                  type="button"
                  className="admin-btn admin-btn-secondary"
                  onClick={() => setShowPwd(!showPwd)}
                >
                  {showPwd ? "Ocultar" : "Mostrar"}
                </button>
              </div>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Confirmar contrasena</label>
              <input
                type={showPwd ? "text" : "password"}
                className="admin-input"
                value={passwords.password_confirmacion}
                onChange={(e) =>
                  setPasswords({ ...passwords, password_confirmacion: e.target.value })
                }
                autoComplete="new-password"
                minLength={8}
              />
            </div>
            <div className="admin-form-actions">
              <button
                type="submit"
                className="admin-btn admin-btn-primary"
                disabled={savingPwd || !passwords.password}
              >
                <FaLock /> {savingPwd ? "Cambiando..." : "Cambiar contrasena"}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Card: Seguridad / 2FA */}
      <div className="admin-card">
        <div className="admin-card__header">
          <h3 className="admin-card__title">
            <FaShieldAlt style={{ marginRight: 8 }} />
            Seguridad
          </h3>
        </div>
        <div className="admin-card__body">
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label">Autenticacion de 2 factores (2FA)</label>
              <p className="admin-form-hint" style={{ marginTop: 6 }}>
                <span
                  className={
                    "admin-badge " +
                    (user.totp_enabled ? "admin-badge--success" : "admin-badge--gray")
                  }
                >
                  {user.totp_enabled ? "Activado" : "Desactivado"}
                </span>
              </p>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Sesiones activas</label>
              <p className="admin-form-hint" style={{ marginTop: 6 }}>
                Gestionadas por JWT. Cierra sesion para revocarlas todas.
              </p>
            </div>
          </div>
          <div className="admin-form-actions">
            <a className="admin-btn admin-btn-secondary" href="/perfil/seguridad">
              Configurar 2FA
            </a>
            <a className="admin-btn admin-btn-secondary" href="/perfil">
              Ir a perfil publico
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
