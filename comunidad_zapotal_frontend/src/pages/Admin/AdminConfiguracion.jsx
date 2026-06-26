/**
 * AdminConfiguracion - Pagina "Perfil" del panel admin.
 *
 * Configuracion administrativa del sistema (modulos on/off, parametros globales).
 * Esta pagina SI es accesible desde el menu "Perfil" del sidebar.
 * NO duplica acciones personales (foto, contrasena, 2FA) que viven en /perfil del sitio publico.
 *
 * Endpoints:
 * - GET   /api/v1/configuracion/   (publico, lectura)
 * - PATCH /api/v1/configuracion/   (solo admin, escritura)
 *
 * Backend: ConfiguracionComunidadView en apps/comunidad/views_institucionales.py
 * Registra quien modifico (actualizado_por) en backend.
 */
import React, { useEffect, useState } from "react";
import {
  FaCog, FaSave, FaCheckCircle, FaExclamationTriangle,
  FaUsers, FaHandHoldingHeart, FaStar, FaUserPlus, FaCommentDots,
  FaEnvelope, FaClock, FaUserShield, FaShieldAlt, FaInfoCircle,
} from "react-icons/fa";
import api from "../../api";
import useAdminRefresh from "../../hooks/useAdminRefresh";

const FLAG_KEYS = [
  {
    key: "modulo_donaciones_activo",
    icon: <FaHandHoldingHeart />,
    label: "Modulo Donaciones",
    desc: "Permite mostrar/ocultar la seccion de donaciones en el sitio publico.",
    color: "emerald",
  },
  {
    key: "modulo_favoritos_activo",
    icon: <FaStar />,
    label: "Modulo Favoritos",
    desc: "Permite mostrar/ocultar el boton de favoritos en noticias y eventos.",
    color: "amber",
  },
  {
    key: "modulo_registro_abierto",
    icon: <FaUserPlus />,
    label: "Registro publico",
    desc: "Permite bloquear el registro de nuevos usuarios.",
    color: "sky",
  },
  {
    key: "modulo_comentarios_activo",
    icon: <FaCommentDots />,
    label: "Modulo Comentarios",
    desc: "Permite deshabilitar comentarios en noticias y eventos.",
    color: "indigo",
  },
  {
    key: "moderacion_comentarios_previa",
    icon: <FaUsers />,
    label: "Moderacion previa",
    desc: "Los comentarios quedan PENDIENTES hasta aprobacion del admin.",
    color: "violet",
  },
  {
    key: "notificaciones_email_activas",
    icon: <FaEnvelope />,
    label: "Notificaciones por email",
    desc: "Envia emails automaticos al admin (bienvenida, alertas).",
    color: "rose",
  },
];

const COLOR_CLASSES = {
  emerald: { bg: "bg-emerald-100", text: "text-emerald-700", border: "border-emerald-300" },
  amber:   { bg: "bg-amber-100",   text: "text-amber-700",   border: "border-amber-300" },
  sky:     { bg: "bg-sky-100",     text: "text-sky-700",     border: "border-sky-300" },
  indigo:  { bg: "bg-indigo-100",  text: "text-indigo-700",  border: "border-indigo-300" },
  violet:  { bg: "bg-violet-100",  text: "text-violet-700",  border: "border-violet-300" },
  rose:    { bg: "bg-rose-100",    text: "text-rose-700",    border: "border-rose-300" },
};

function Toggle({ checked, onChange, label, color }) {
  const colors = COLOR_CLASSES[color] || COLOR_CLASSES.emerald;
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={
        "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 " +
        (checked ? colors.bg : "bg-gray-300")
      }
    >
      <span
        className={
          "inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform " +
          (checked ? "translate-x-6" : "translate-x-1")
        }
      />
    </button>
  );
}

export default function AdminConfiguracion() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [ok, setOk] = useState("");
  const [error, setError] = useState("");

  const cargar = async () => {
    setLoading(true);
    setError("");
    setOk("");
    try {
      const { data } = await api.get("/configuracion/");
      setConfig(data);
    } catch (e) {
      setError("No se pudo cargar la configuracion.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargar(); }, []);
  useAdminRefresh(cargar);

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true);
    setError("");
    setOk("");
    try {
      const payload = { ...config };
      delete payload.id;
      delete payload.actualizado_en;
      delete payload.actualizado_por;
      delete payload.actualizado_por_email;
      const { data } = await api.patch("/configuracion/", payload);
      setConfig(data);
      setOk("Configuracion guardada correctamente.");
    } catch (err) {
      const d = err.response?.data;
      setError(typeof d === "string" ? d : (d?.detail || JSON.stringify(d) || "Error al guardar."));
    } finally {
      setSaving(false);
    }
  };

  const toggle = (key) => setConfig({ ...config, [key]: !config[key] });

  if (loading && !config) {
    return (
      <div className="admin-loading">
        <FaCog className="fa-spin mr-2" /> Cargando configuracion del sistema...
      </div>
    );
  }

  if (!config) {
    return (
      <div className="admin-error">
        <FaExclamationTriangle className="inline mr-1" />
        {error || "No se pudo cargar la configuracion del sistema."}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success"><FaCheckCircle className="inline mr-1" /> {ok}</div>}

      <form onSubmit={guardar} className="space-y-4">
        <div className="admin-card">
          <div className="admin-card__header">
            <div>
              <h3 className="admin-card__title">
                <FaShieldAlt className="text-emerald-700" />
                Modulos del sistema
              </h3>
              <p className="text-xs text-gray-500 mt-1">
                Activa o desactiva funcionalidades globales de la plataforma.
              </p>
            </div>
            <button
              type="submit"
              className="admin-btn admin-btn-primary"
              disabled={saving}
            >
              <FaSave /> {saving ? "Guardando..." : "Guardar cambios"}
            </button>
          </div>
          <div className="admin-card__body space-y-3">
            {FLAG_KEYS.map((f) => {
              const colors = COLOR_CLASSES[f.color] || COLOR_CLASSES.emerald;
              return (
                <div
                  key={f.key}
                  className="flex items-start gap-4 p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:bg-gray-50 transition-colors"
                >
                  <div className={`w-10 h-10 rounded-lg ${colors.bg} ${colors.text} flex items-center justify-center text-lg flex-shrink-0`}>
                    {f.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-gray-900">
                      {f.label}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {f.desc}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={`text-xs font-semibold ${config[f.key] ? colors.text : "text-gray-400"}`}>
                      {config[f.key] ? "Activo" : "Inactivo"}
                    </span>
                    <Toggle
                      checked={!!config[f.key]}
                      onChange={() => toggle(f.key)}
                      label={f.label}
                      color={f.color}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="admin-card">
          <div className="admin-card__header">
            <h3 className="admin-card__title">
              <FaInfoCircle className="text-sky-700" />
              Informacion del sistema
            </h3>
          </div>
          <div className="admin-card__body">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                <FaClock className="text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">Ultima actualizacion</div>
                  <div className="font-semibold text-gray-900">
                    {config.actualizado_en
                      ? new Date(config.actualizado_en).toLocaleString("es-PE")
                      : "Nunca"}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                <FaUserShield className="text-gray-500" />
                <div>
                  <div className="text-xs text-gray-500">Modificado por</div>
                  <div className="font-semibold text-gray-900">
                    {config.actualizado_por_email || "Sistema"}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
