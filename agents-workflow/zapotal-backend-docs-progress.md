# Zapotal Backend Documentation Progress

**Ultima actualizacion:** 2026-06-27

## Estado actual

| App | Archivos fuente | Docs | Estado |
|-----|----------------|------|--------|
| accounts | 16 | 16 | ✅ Completo |
| cms | 4 | 4 | ✅ Completo |
| comunidad | 10 | 10 | ✅ Completo |
| content | 9 | 9 | ✅ Completo |
| core | 19 | 19 | ✅ Completo |
| donaciones | 7 | 7 | ✅ Completo |
| messaging | ~9 | ~9 | ✅ Completo |
| **reports** | **11** | **11** | **✅ Completo** |
| **root (manage, conftest)** | **2** | **2** | **✅ Completo** |
| **zapotal_config** | **5** | **5** | **✅ Completo** |

**Total apps/buckets documentados:** 10/10

**Total source files documentados:** 92 source files + 80 boilerplate = ~172 archivos Python documentados

## Progreso

Backend source files documentados: 92/92 (~100%)
Boilerplate files: 80/80 (100%)

## Loops y features documentados por app

### content
- Noticia, Evento, LibroReclamacion, Comentario, MensajeContacto
- Filtros por estado, tipo_evento, categoria
- Comentarios con moderacion (PUBLICADO/OCULTO)
- Adjuntos (imagen, pdf)
- Signals: notificacion automatica en post_save
- Servicios para publicar, adjuntar, notificar

### core
- PlantillaCorreo, LogActividad, ConfiguracionSitio, Image, PDFFile
- Admin DUAL (Django admin + AdminPersonalizado)
- Audit logging en CREATE/UPDATE/DELETE
- Cache de configuracion
- 12 vistas/viewsets, 7 sets de tests
- Middleware: AuditMiddleware, ContentSecurityPolicyMiddleware

### donaciones
- CampaniaDonacion, Donacion con Mercado Pago
- CRUD de campanias, procesamiento de donaciones
- Vista publica de campanias activas + total recaudado
- Validacion de monto minimo y campania activa

### messaging
- Mensaje (privado), Notificacion (20+ tipos, 10+ referencia_tipo)
- Mensajeria privada, conteo de no leidas
- Notificaciones automaticas en eventos del sistema
- 6 signals en post_save de Noticia, Evento, Usuario, etc.
- Management command: purge_old_notifications
- 3 archivos de tests, 30+ tests

### accounts
- Custom user con roles ADMIN/COMUNERO/USUARIO
- JWT (SimpleJWT), registro con OTP, login 2-pasos
- Password reset, admin personalizado con acciones
- Invitaciones con expiracion y limite de usos
- Perfil de comunero completo
- 7 conjuntos de tests

### cms
- Banner, Testimonios, Novedades con service layer

### comunidad
- Galeria, Documentos, Directorio, ContactosEmergencia, ServiciosPublicos
- ZeroBounce integration, helpers de email

### reports (✅ nuevo)
- LibroReclamacion con compliance Ley 29571 (INDECOPI)
- Estados: PENDIENTE, EN_PROCESO, RESUELTO, VENCIDO
- Prioridad, numero_reclamo (LIB-YYYY-NNNNNN), plazo_respuesta (30d habiles)
- 12 feriados nacionales peruanos excluidos del calculo
- Silencio administrativo positivo (management command cron)
- ZeroBounce validacion, alias legacy frontend
- 3 plantillas de respuesta (aceptar, rechazar, informacion)
- Rate limit por IP+email (2/hora)
- Admin actions: marcar en proceso, resuelto, exportar CSV
- 3 archivos de tests (~30 tests): basicos, email, exhaustivos

### zapotal_config (✅ nuevo)
- 18 apps instaladas (8 propias)
- JWT, drf-spectacular, CORS, CSP, throttle scopes
- MySQL + R2 condicional
- Email via Resend/SMTP/console
- ZeroBounce, Mercado Pago, Turnstile config
- 13 rutas principales + health checks

## Resumen de endpoints documentados

| App | Endpoints |
|-----|-----------|
| accounts/auth | /auth/register/, /auth/verify-otp/, /auth/login/, /auth/token/refresh/, /auth/password-reset/, /auth/password-reset/confirm/ |
| accounts/users | /users/me/, /users/register-admin/ |
| accounts/invitaciones | /invitaciones/ |
| cms | /banners/, /testimonios/, /novedades/ |
| comunidad | /galeria/, /documentos/, /directorio/, /contactos-emergencia/, /servicios-publicos/ |
| content | /noticias/, /eventos/, /libro-reclamaciones/, /comentarios/, /mensajes-contacto/ |
| core | /logs-actividad/, /configuracion/, /admins/, /admins/actividad-reciente/, /admins/estadisticas/ |
| donaciones | /campanias-donacion/, /donaciones/, /mis-donaciones/ |
| messaging | /mensajes/, /notificaciones/, /notificaciones/no-leidas/count/ |
| reports | /libro-reclamaciones/, /libro-reclamaciones/{id}/cambiar_estado/, /plantillas-respuesta/, /responder/ |
| admin | /backend/ (custom admin) |
| docs | /api/schema/, /api/docs/ |
| health | /health/, /health/live/, /health/ready/ |

## Notas finales
- Documentacion completa del backend Django: 92 source files + 80 boilerplate
- Backend Django 6.0 con python-decouple, RESEND, drf-spectacular
- Proximo paso: frontend React + Vite, mobile BFF Spring Boot, Android app
