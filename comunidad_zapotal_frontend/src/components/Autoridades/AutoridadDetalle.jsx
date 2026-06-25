import React, { useEffect, useState } from "react";
import {
  FaTimes, FaPhone, FaEnvelope, FaFileSignature, FaCalendarAlt,
  FaIdCard, FaUser, FaVenus, FaMars, FaGenderless, FaClock,
  FaShieldAlt, FaUsers, FaUniversity, FaInfoCircle, FaWhatsapp,
  FaLanguage, FaSeedling, FaRedo, FaMapMarkerAlt, FaCheckCircle,
} from "react-icons/fa";
import "./AutoridadDetalle.css";

const SexoIcon = ({ sexo }) => {
  if (sexo === "F") return <FaVenus className="ad-sexo ad-sexo--femenino" />;
  if (sexo === "M") return <FaMars className="ad-sexo ad-sexo--masculino" />;
  return <FaGenderless className="ad-sexo" />;
};

const NivelIcon = ({ nivel }) => {
  if (nivel === "COMUNAL") return <FaUsers />;
  if (nivel === "MUNICIPAL") return <FaUniversity />;
  return <FaShieldAlt />;
};

const Iniciales = ({ nombre, apellido }) => {
  const inicial = (s) => (s && s[0] ? s[0].toUpperCase() : "");
  return (
    <span className="ad-iniciales">
      {inicial(nombre)}{inicial(apellido)}
    </span>
  );
};

function whatsappLink(telefono) {
  if (!telefono) return null;
  const limpio = String(telefono).replace(/[^0-9]/g, '');
  return `https://wa.me/${limpio}`;
}

export default function AutoridadDetalle({ autoridad, onClose }) {
  useEffect(() => {
    const handler = (e) => { if (e.key === "Escape") onClose?.(); };
    document.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  if (!autoridad) return null;

  const a = autoridad;
  const nombre = a.nombre_completo || "Sin nombre";
  const cargo = a.cargo || "";
  const wa = whatsappLink(a.telefono);

  const fmtFecha = (iso) => {
    if (!iso) return null;
    try {
      return new Date(iso).toLocaleDateString("es-PE", { day: "2-digit", month: "long", year: "numeric" });
    } catch { return iso; }
  };

  const fmtDias = (dias) => {
    if (dias == null) return null;
    if (dias < 30)   return `${dias} dias`;
    if (dias < 365)  return `${Math.round(dias / 30)} meses`;
    const anos = Math.floor(dias / 365);
    const meses = Math.round((dias - anos * 365) / 30);
    return meses > 0 ? `${anos} ano${anos > 1 ? 's' : ''} y ${meses} meses` : `${anos} ano${anos > 1 ? 's' : ''}`;
  };

  return (
    <div
      className="ad-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="ad-titulo"
    >
      <div className="ad-modal" onClick={(e) => e.stopPropagation()}>
        <div className="ad-header">
          <button type="button" onClick={onClose} className="ad-close" aria-label="Cerrar">
            <FaTimes />
          </button>
          <div className="ad-header-content">
            <div className="ad-foto-wrap">
              {a.foto_url ? (
                <img src={a.foto_url} alt={nombre} className="ad-foto" />
              ) : (
                <div className="ad-foto-placeholder">
                  <Iniciales nombre={a.nombres} apellido={a.apellidos} />
                </div>
              )}
            </div>
            <div className="ad-header-info">
              <span className="ad-nivel-badge">
                <NivelIcon nivel={a.nivel_gobierno} /> {a.nivel_display}
              </span>
              <h2 id="ad-titulo">{nombre}</h2>
              <p className="ad-cargo">
                {cargo} <SexoIcon sexo={a.sexo} />
              </p>
              {a.es_cargo_tradicional && (
                <p className="ad-tradicional-badge">
                  <FaSeedling /> Cargo tradicional
                  {a.nombre_tradicional && <strong> · {a.nombre_tradicional}</strong>}
                </p>
              )}
              {a.reelegido && (
                <p className="ad-reelegido-badge">
                  <FaRedo /> Reelegido por un segundo periodo consecutivo
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="ad-body">
          {/* DESCRIPCION DEL CARGO */}
          {a.descripcion && (
            <section className="ad-section">
              <h3><FaInfoCircle /> Sobre el cargo</h3>
              <p className="ad-descripcion">{a.descripcion}</p>
            </section>
          )}

          {/* PERIODO */}
          {(a.periodo || a.periodo_inicio || a.tiempo_restante != null) && (
            <section className="ad-section">
              <h3><FaCalendarAlt /> Periodo</h3>
              <div className="ad-grid-2">
                {a.periodo && (
                  <div className="ad-info">
                    <span className="ad-info-label">Periodo declarado</span>
                    <span className="ad-info-value">{a.periodo}</span>
                  </div>
                )}
                {a.duracion_mandato_anos > 0 && (
                  <div className="ad-info">
                    <span className="ad-info-label">Duracion del mandato</span>
                    <span className="ad-info-value">{a.duracion_mandato_anos} {a.duracion_mandato_anos === 1 ? 'ano' : 'anos'}</span>
                  </div>
                )}
                {fmtFecha(a.periodo_inicio) && (
                  <div className="ad-info">
                    <span className="ad-info-label">Inicio</span>
                    <span className="ad-info-value">{fmtFecha(a.periodo_inicio)}</span>
                  </div>
                )}
                {fmtFecha(a.periodo_fin) && (
                  <div className="ad-info">
                    <span className="ad-info-label">Fin</span>
                    <span className="ad-info-value">{fmtFecha(a.periodo_fin)}</span>
                  </div>
                )}
              </div>
              {a.tiempo_restante != null && a.tiempo_restante > 0 && (
                <div className="ad-tiempo-restante">
                  <FaClock />
                  <span>
                    <strong>{fmtDias(a.tiempo_restante)}</strong> restantes
                    del periodo
                  </span>
                </div>
              )}
              {a.proxima_eleccion && (
                <div className="ad-proxima">
                  Proxima renovacion: <strong>{fmtFecha(a.proxima_eleccion)}</strong>
                </div>
              )}
            </section>
          )}

          {/* DATOS PERSONALES */}
          {(a.dni || a.sexo || a.lengua_materna) && (
            <section className="ad-section">
              <h3><FaIdCard /> Datos</h3>
              <div className="ad-grid-2">
                {a.dni && (
                  <div className="ad-info">
                    <span className="ad-info-label"><FaIdCard /> DNI</span>
                    <span className="ad-info-value">{a.dni}</span>
                  </div>
                )}
                {a.sexo && (
                  <div className="ad-info">
                    <span className="ad-info-label"><SexoIcon sexo={a.sexo} /> Sexo</span>
                    <span className="ad-info-value">{a.sexo_display}</span>
                  </div>
                )}
                {a.lengua_materna && (
                  <div className="ad-info">
                    <span className="ad-info-label"><FaLanguage /> Lengua materna</span>
                    <span className="ad-info-value">{a.lengua_display}</span>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* CONTACTO */}
          {(a.telefono || a.email_institucional || wa) && (
            <section className="ad-section">
              <h3><FaPhone /> Contacto</h3>
              <div className="ad-grid-2">
                {a.telefono && (
                  <a href={`tel:${a.telefono}`} className="ad-contacto">
                    <FaPhone /> {a.telefono}
                  </a>
                )}
                {a.email_institucional && (
                  <a href={`mailto:${a.email_institucional}`} className="ad-contacto">
                    <FaEnvelope /> {a.email_institucional}
                  </a>
                )}
                {wa && (
                  <a href={wa} target="_blank" rel="noopener noreferrer" className="ad-contacto ad-whatsapp">
                    <FaWhatsapp /> WhatsApp
                  </a>
                )}
              </div>
            </section>
          )}

          {/* DOCUMENTO LEGAL SUNARP */}
          {(a.nro_partida_sunarp || a.sede_inscripcion || a.resolucion_inscripcion || a.estado_inscripcion) && (
            <section className="ad-section">
              <h3><FaFileSignature /> Documentacion legal (SUNARP)</h3>
              <div className="ad-grid-2">
                {a.nro_partida_sunarp && (
                  <div className="ad-info">
                    <span className="ad-info-label">Partida SUNARP</span>
                    <span className="ad-info-value">{a.nro_partida_sunarp}</span>
                  </div>
                )}
                {a.sede_inscripcion && (
                  <div className="ad-info">
                    <span className="ad-info-label">Oficina registral</span>
                    <span className="ad-info-value">{a.sede_inscripcion}</span>
                  </div>
                )}
                {a.resolucion_inscripcion && (
                  <div className="ad-info">
                    <span className="ad-info-label">Resolucion</span>
                    <span className="ad-info-value">{a.resolucion_inscripcion}</span>
                  </div>
                )}
                {fmtFecha(a.fecha_inscripcion) && (
                  <div className="ad-info">
                    <span className="ad-info-label">Fecha inscripcion</span>
                    <span className="ad-info-value">{fmtFecha(a.fecha_inscripcion)}</span>
                  </div>
                )}
                {a.estado_inscripcion_display && (
                  <div className="ad-info">
                    <span className="ad-info-label">Estado</span>
                    <span className="ad-info-value">
                      {a.estado_inscripcion === 'INSCRITO' ? <FaCheckCircle style={{ color: '#047857' }} /> : null}{' '}
                      {a.estado_inscripcion_display}
                    </span>
                  </div>
                )}
                {fmtFecha(a.fecha_vencimiento_inscripcion) && (
                  <div className="ad-info">
                    <span className="ad-info-label">Vencimiento</span>
                    <span className="ad-info-value">{fmtFecha(a.fecha_vencimiento_inscripcion)}</span>
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
