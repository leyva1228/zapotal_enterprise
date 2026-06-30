# Audit: Modelos Django y consumo desde React

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-29
- Autor/agente: opencode (modelo minimax-m3)
- Tecnologia: Backend Django + Frontend React

## Objetivo

1. Confirmar si el modelo `Comunero` esta siendo usado de verdad en el backend y desde el frontend.
2. Inventariar todos los modelos Django del backend principal.
3. Clasificarlos entre:
   - USADOS (referenciados en views/serializers/admin/services/seeders/management commands o consumidos por React).
   - PARCIALMENTE USADOS (definidos y migrados, pero sin consumidor claro o solo expuestos al admin).
4. Listar los endpoints REST expuestos por el backend y cruzar con los endpoints consumidos por React para detectar modelos sin consumidor o sobre-expuestos.

## Alcance

### Incluye

- Apps: `accounts`, `core`, `comunidad` (incluye `models_institucionales.py`), `content`, `cms`, `donaciones`, `messaging`, `reports`.
- Archivos leidos:
  - `comunidad_zapotal_backend/AGENTS.md`
  - `comunidad_zapotal_frontend/AGENTS.md`
  - `comunidad_zapotal_backend/apps/*/models.py` y `models_institucionales.py`
  - `comunidad_zapotal_backend/apps/*/urls.py`
  - `comunidad_zapotal_backend/apps/*/views*.py` (solo en lo necesario para confirmar uso)
  - `comunidad_zapotal_backend/apps/*/admin.py` (referencia rapida)
  - `comunidad_zapotal_backend/zapotal_config/urls.py`
  - `comunidad_zapotal_backend/apps/accounts/serializers.py`, `services.py`, `admin.py`
  - `comunidad_zapotal_backend/apps/comunidad/views.py`, `serializers.py`, `admin.py`
  - `comunidad_zapotal_frontend/src/api.js`
  - `comunidad_zapotal_frontend/src/hooks/*.js`
  - `comunidad_zapotal_frontend/src/pages/**/*.jsx` (grep por `api.*`)

### No incluye

- No se auditan tests, factories ni management commands como consumidores reales; solo como evidencia de que el modelo existe y se ejercita.
- No se audita el backend legado en `comunidad_zapotal_mobilebff_and_mobile_old/comunidad_zapotal_backend/`.
- No se audita el BFF de Spring Boot ni la app Android.
- No se hace analisis de permisos, performance ni cobertura de tests en este audit.

## Contexto leido

- `AGENTS.md` raiz
- `graphify.md`
- `comunidad_zapotal_backend/AGENTS.md`
- `comunidad_zapotal_frontend/AGENTS.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `comunidad_zapotal_backend/graphify/` y `comunidad_zapotal_frontend/graphify/` (estructura, no leidos a detalle en este audit)

## Inventario de modelos Django

Total: 30 modelos distribuidos en 8 apps.

### accounts (5)

| Modelo | db_table | Definido en | Notas |
|---|---|---|---|
| `Comunero` | `comunero` | `apps/accounts/models.py:10` | DNI unico, estado ACTIVO/INACTIVO |
| `Usuario` | `usuario` | `apps/accounts/models.py:152` | User custom (auth), referencia opcional a `Comunero` |
| `OTPVerification` | `otp_verification` | `apps/accounts/models.py:78` | Codigos OTP (registro, reset, 2FA) |
| `PendingApproval` | `pending_approval` | `apps/accounts/models.py:124` | Snapshot usuario pendiente de aprobacion admin |
| `UsuarioManager` (no es modelo) | - | `apps/accounts/models.py:54` | Manager de `Usuario` |

### core (1)

| Modelo | db_table | Definido en | Notas |
|---|---|---|---|
| `AuditLog` | `audit_log` | `apps/core/models.py:5` | Bitacora centralizada |

### comunidad (2 + 7 institucionales)

| Modelo | Definido en | Notas |
|---|---|---|
| `ComiteComunal` | `apps/comunidad/models.py:6` | Comites (Electoral, Revisor, Rondas, Gestion, Obras, Educacion) |
| `Autoridad` | `apps/comunidad/models.py:108` | Cargos Directiva Comunal + Municipalidad + Autoridad Politica |
| `ConfiguracionComunidad` | `apps/comunidad/models_institucionales.py:13` | Singleton (pk=1) con toda la identidad + textos editables |
| `MarcoLegalItem` | `apps/comunidad/models_institucionales.py:213` | Items del Marco Legal |
| `PaginaLegal` | `apps/comunidad/models_institucionales.py:235` | Terminos, Privacidad, Cookies |
| `HitoHistorico` | `apps/comunidad/models_institucionales.py:263` | Timeline historica |
| `GaleriaImagen` | `apps/comunidad/models_institucionales.py:292` | Galeria publica (vinculable a Noticia/Evento) |
| `MensajeContacto` | `apps/comunidad/models_institucionales.py:339` | Formulario de contacto publico |
| `CategoriaGaleria` | `apps/comunidad/models_institucionales.py:388` | Categorias editables de galeria |
| `TextoSeccionInterna` | `apps/comunidad/models_institucionales.py:409` | Textos editables por seccion + idioma |

### content (9)

| Modelo | db_table | Definido en |
|---|---|---|
| `Categoria` | `categoria` | `apps/content/models.py:6` |
| `Noticia` | `noticia` | `apps/content/models.py:21` |
| `Evento` | `evento` | `apps/content/models.py:60` |
| `Multimedia` | `multimedia` | `apps/content/models.py:87` |
| `Comentario` | `comentario` | `apps/content/models.py:126` |
| `Reaccion` | `reaccion` | `apps/content/models.py:207` |
| `Favorito` | `favorito` | `apps/content/models.py:285` |
| `SolicitudBaja` | `solicitud_baja` | `apps/content/models.py:347` |
| `NovedadVista` | `novedad_vista` | `apps/content/models.py:393` |

### cms (1)

| Modelo | db_table | Definido en |
|---|---|---|
| `ContenidoEstatico` | `contenido_estatico` | `apps/cms/models.py:4` |

### donaciones (1)

| Modelo | Definido en |
|---|---|
| `Donacion` | `apps/donaciones/models.py:6` |

### messaging (2)

| Modelo | Definido en |
|---|---|
| `Mensaje` | `apps/messaging/models.py:5` |
| `Notificacion` | `apps/messaging/models.py:33` |

### reports (1)

| Modelo | Definido en |
|---|---|
| `LibroReclamacion` | `apps/reports/models.py:6` |

## Pregunta 1: ¿Se esta usando el modelo `Comunero`?

**Si, esta en uso activo en backend y parcialmente en frontend.** Detalle:

### Backend - evidencia de uso real

- Definido en `apps/accounts/models.py:10` (DNI, nombres, apellidos, estado).
- Registrado en admin: `apps/accounts/admin.py:82` (`@admin.register(Comunero)`).
- ViewSet CRUD admin-only: `apps/accounts/views.py:37-49` (`ComuneroViewSet`, ruta `/api/v1/comuneros/`).
- Serializer: `apps/accounts/serializers.py:11` (`ComuneroSerializer`).
- Service: `apps/accounts/services.py:156-163` (`ComuneroService.create_comunero`).
- Factory de tests: `apps/accounts/factories/__init__.py:39-46` (`ComuneroFactory`).
- Creacion automatica en registro publico:
  - `apps/accounts/views_auth.py:143-152` valida DNI duplicado y crea `Comunero`.
  - `apps/accounts/services.py:117` crea `Comunero` como parte del alta de usuario tipo `COMUNERO`.
- Seeders:
  - `apps/accounts/management/commands/seed_comuneros.py` (seed basico).
  - `apps/comunidad/management/commands/seed_autoridades.py:86` usa `Comunero.get_or_create` para autoridades.
  - `apps/comunidad/management/commands/seed_jerarquia.py:19` crea `Comunero` ficticio de presidente.
- FKs que dependen de el:
  - `Usuario.comunero` (OneToOne, opcional).
  - `Autoridad.comunero` (OneToOne, requerido).
  - `Autoridad.comunero_info` (snapshot textual legacy, ver migracion 0002).

### Frontend - uso parcial

`Comunero` se consume solo en pantallas admin, no en UI publica:

- `src/pages/Admin/AdminAutoridades.jsx:70`: `api.get("/comuneros/")` con `.catch(() => ({ data: { data: [] } }))` (fallback silencioso).
- `src/pages/Admin/AdminUsuarios.jsx:65`: `api.get("/comuneros/")` con mismo fallback silencioso.

**Observacion importante:** en ambos casos el endpoint falla silenciosamente y se renderiza lista vacia. Esto indica que la llamada funciona, pero que su exito no es critico para la pantalla (las dos paginas ya tienen fallback a `usuarios` y `autoridades`). El DNI/nombre del comunero en el detalle de usuarios se obtiene indirectamente via `/usuarios/?search=` y el join `comunero__nombres` que ya hace el backend en `UsuarioViewSet.filter_queryset` (ver `apps/accounts/views.py:122-131`).

**Conclusion Comunero:** modelo vivo, con seeders, admin, API, factories y dependencias. Consumido por frontend solo como lookup auxiliar en admin. **No es candidato a eliminacion**, pero su endpoint REST esta sub-utilizado fuera de admin.

## Pregunta 2: ¿Que modelos estan en uso?

### Modelos USADOS (consumidos o expuestos activamente)

| Modelo | Donde se usa | Endpoint REST | Consumido por React |
|---|---|---|---|
| `Usuario` | accounts | `/api/v1/usuarios/`, `/api/v1/auth/login/`, `/api/v1/auth/2fa/*`, `/api/v1/registro/*`, `/api/v1/password-reset/*` | Si (Perfil, Admin, AuthContext, Login, Registro) |
| `Comunero` | accounts | `/api/v1/comuneros/` | Si (solo AdminAutoridades, AdminUsuarios, fallback silencioso) |
| `OTPVerification` | accounts | interno (no es CRUD), usado por views_auth | no directo (transparente al frontend) |
| `PendingApproval` | accounts | interno + usado en serializadores admin | no directo |
| `AuditLog` | core | `/api/v1/audit-log/` | Si (AdminAuditoria, AdminDashboard) |
| `Autoridad` | comunidad | `/api/v1/autoridades/`, `/api/v1/autoridades/agrupadas/`, `/api/v1/autoridades/estadisticas/` | Si (AdminAutoridades, AutoridadesPage, AdminDashboard) |
| `ComiteComunal` | comunidad | `/api/v1/comites-comunales/` | Si (AdminComitesComunales, AutoridadesPage) |
| `ConfiguracionComunidad` | comunidad | `/api/v1/configuracion/` | Si (useConfiguracion, AdminConfiguracion, AdminInstitucional) |
| `MarcoLegalItem` | comunidad | `/api/v1/marco-legal/` | Si (useMarcoLegal, AdminInstitucional) |
| `PaginaLegal` | comunidad | `/api/v1/paginas-legales/`, `/api/v1/paginas-legales/<slug>/` | Si (usePaginaLegal, AdminInstitucional, TerminosPage, PrivacidadPage, CookiesPage, LegalPage) |
| `HitoHistorico` | comunidad | `/api/v1/hitos-historicos/` | Si (useHitosHistoricos, AdminInstitucional, NuestraHistoria) |
| `GaleriaImagen` | comunidad | `/api/v1/galeria/` | Si (useGaleria, AdminGaleria, AdminInstitucional, Galeria) |
| `MensajeContacto` | comunidad | `/api/v1/contacto/` (POST publico), `/api/v1/mensajes-contacto/` (admin) | Si (Contacto.jsx publico, AdminMensajes admin) |
| `CategoriaGaleria` | comunidad | `/api/v1/galerias/categorias/` (publico), `/api/v1/galerias/categorias-admin/` (admin) | Si (useTextosSeccion, Galeria) |
| `TextoSeccionInterna` | comunidad | `/api/v1/textos-seccion/` (publico), `/api/v1/textos-seccion-admin/` (admin) | Si (useTextosSeccion, AdminInstitucional) |
| `Categoria` | content | `/api/v1/categorias/` | Si (AdminCategorias, AdminNoticias, AdminDashboard) |
| `Noticia` | content | `/api/v1/noticias/`, `/api/v1/noticia/detalle/<id>/`, `/api/v1/noticia/detalle/<id>/relacionadas/`, `/api/v1/noticia/detalle/<id>/comentarios/`, `/api/v1/noticia/detalle/<id>/incrementar_vistas/` | Si (Noticias, DetalleNoticia, AdminNoticias, AdminDashboard, AdminGaleria) |
| `Evento` | content | `/api/v1/eventos/` + variantes singulares | Si (Eventos, DetalleEvento, AdminEventos, AdminDashboard, AdminGaleria) |
| `Multimedia` | content | `/api/v1/multimedias/` | Si (SubirMultimedia) |
| `Comentario` | content | `/api/v1/comentarios/`, `/api/v1/comentarios/<id>/cambiar_estado/` | Si (DetalleNoticia, DetalleEvento, AdminComentarios) |
| `Reaccion` | content | `/api/v1/reacciones/` | Si (DetalleNoticia, DetalleEvento, AdminDashboard) |
| `Favorito` | content | `/api/v1/favoritos/` | Si (BotonFavorito, Perfil) |
| `SolicitudBaja` | content | `/api/v1/solicitudes-baja/`, `/api/v1/solicitudes-baja/<id>/aprobar/`, `/api/v1/solicitudes-baja/<id>/rechazar/`, `/api/v1/mi-cuenta/solicitar-baja/`, `/api/v1/mi-cuenta/cancelar-baja/` | Si (Perfil, AdminBajas) |
| `NovedadVista` | content | `/api/v1/novedades/`, `/api/v1/novedades/<tipo>/<id>/marcar-vista/` | NO consumido por React (frontend consume `Notificacion` en su lugar) |
| `ContenidoEstatico` | cms | `/api/v1/cms/contenido/` | Si (AdminCms). NO consumido por UI publica (Frontend lee desde `ConfiguracionComunidad` y `PaginaLegal`). |
| `Donacion` | donaciones | `/api/v1/donaciones/iniciar/`, `/procesar/`, `/procesar-simulado/`, `/webhook/`, `/mis-donaciones/`, `/<id>/`, `/<id>/boleta-pdf/`, `/estadisticas/`, `/admin/lista/`, `/admin/<id>/reembolsar/`, `/admin/<id>/cancelar/` | Si (Donaciones publico, Perfil, AdminDonaciones, AdminDashboard) |
| `Mensaje` | messaging | `/api/v1/mensajes/` (ModelViewSet completo) | **NO consumido por React** |
| `Notificacion` | messaging | `/api/v1/notificaciones/`, `/api/v1/notificaciones/no-leidas/count`, `/api/v1/notificaciones/marcar-todas-leidas/`, `/api/v1/notificaciones/contador-no-leidas/` | Si (Perfil, AdminNotificaciones, NotificationBell) |
| `LibroReclamacion` | reports | `/api/v1/libro-reclamaciones/`, `/api/v1/libro-reclamaciones/<id>/cambiar_estado/`, `/<id>/plantillas-respuesta/`, `/<id>/responder/` | Si (LibroReclamacion publico, AdminReclamaciones, AdminDashboard) |

### Modelos PARCIALMENTE USADOS o sin consumidor React claro

| Modelo | Riesgo |
|---|---|
| `Mensaje` (messaging) | ViewSet completo registrado, tests, admin, services y factory. **El frontend React no lo consume** (busqueda en `src/` sin matches para `/mensajes/`). Usado solo por los tests del backend. Posible candidato a UI de chat entre usuarios aun no implementada, o a deprecacion. |
| `NovedadVista` (content) | Endpoints `/novedades/` y `/novedades/<tipo>/<id>/marcar-vista/` no son consumidos por React. El frontend usa `Notificacion` para badges. Es tracking interno del backend para "novedades vistas", pero no tiene UI asociada. |
| `ContenidoEstatico` (cms) | CRUD `/api/v1/cms/contenido/` consumido solo por `AdminCms.jsx`. El sitio publico lee textos desde `ConfiguracionComunidad` y `PaginaLegal`, no desde `ContenidoEstatico`. La tabla `contenido_estatico` puede tener registros duplicados/no usados. |

### Modelos NO USADOS (modelos definidos que no parecen tener consumidor)

**Ninguno**. Todos los 30 modelos tienen al menos un consumidor backend (admin, viewset, signals, seeders, management commands o factories). La pregunta correcta es **"¿cuales estan sobre-expuestos o sub-utilizados?"**, no "cuales no se usan".

## Pregunta 3: ¿Que modelos consume el frontend React?

### Endpoints consumidos (path -> modelo -> archivo)

| Endpoint React | Modelo backend | Archivos React |
|---|---|---|
| `/usuarios/` | Usuario | AdminUsuarios, AdminDashboard, Perfil, AdminAutoridades |
| `/comuneros/` | Comunero | AdminUsuarios, AdminAutoridades (fallback silencioso) |
| `/autoridades/`, `/autoridades/agrupadas/`, `/autoridades/estadisticas/`, `/autoridades/<id>/` | Autoridad | AdminAutoridades, AutoridadesPage, AdminDashboard |
| `/comites-comunales/`, `/comites-comunales/<id>/` | ComiteComunal | AdminComitesComunales, AutoridadesPage |
| `/categorias/`, `/categorias/<id>/` | Categoria | AdminCategorias, AdminNoticias, AdminDashboard |
| `/noticias/`, `/noticias/<id>/`, `/noticia/detalle/<id>/*` | Noticia | Noticias, DetalleNoticia, AdminNoticias, AdminDashboard, AdminGaleria, Eventos (relacionadas) |
| `/eventos/`, `/eventos/<id>/`, `/evento/detalle/<id>/*` | Evento | Eventos, DetalleEvento, AdminEventos, AdminDashboard, AdminGaleria |
| `/multimedias/`, `/multimedias/<id>/` | Multimedia | SubirMultimedia |
| `/comentarios/`, `/comentarios/<id>/*` | Comentario | DetalleNoticia, DetalleEvento, AdminComentarios |
| `/reacciones/`, `/reacciones/<id>/` | Reaccion | DetalleNoticia, DetalleEvento, AdminDashboard |
| `/favoritos/`, `/favoritos/<id>/` | Favorito | BotonFavorito, Perfil |
| `/solicitudes-baja/`, `/solicitudes-baja/<id>/aprobar/`, `/solicitudes-baja/<id>/rechazar/` | SolicitudBaja | Perfil, AdminBajas |
| `/mi-cuenta/solicitar-baja/`, `/mi-cuenta/cancelar-baja/` | SolicitudBaja | Perfil |
| `/novedades/`, `/novedades/<tipo>/<id>/marcar-vista/` | NovedadVista | **No consumido** |
| `/configuracion/` | ConfiguracionComunidad | useConfiguracion, AdminConfiguracion, AdminInstitucional |
| `/marco-legal/`, `/marco-legal/<id>/` | MarcoLegalItem | useMarcoLegal, AdminInstitucional, MarcoLegal |
| `/paginas-legales/`, `/paginas-legales/<slug>/` | PaginaLegal | usePaginaLegal, AdminInstitucional, Terminos/Privacidad/Cookies/Legal |
| `/hitos-historicos/`, `/hitos-historicos/<id>/` | HitoHistorico | useHitosHistoricos, AdminInstitucional, NuestraHistoria |
| `/galeria/`, `/galeria/<id>/` | GaleriaImagen | useGaleria, AdminGaleria, AdminInstitucional, Galeria |
| `/galerias/categorias/` (publico) | CategoriaGaleria | useTextosSeccion, Galeria |
| `/galerias/categorias-admin/` | CategoriaGaleria | (admin) |
| `/textos-seccion/` (publico) | TextoSeccionInterna | useTextosSeccion |
| `/textos-seccion-admin/` | TextoSeccionInterna | (admin) |
| `/mensajes-contacto/`, `/mensajes-contacto/<id>/marcar_leido/`, `/marcar_respondido/` | MensajeContacto | AdminMensajes |
| `/contacto/` (POST publico) | MensajeContacto | Contacto (componente publico) |
| `/cms/contenido/`, `/cms/contenido/<id>/` | ContenidoEstatico | AdminCms (no en UI publica) |
| `/public/email-contacto/` | ConfiguracionComunidad (campo email_contacto + override) | useEmailDestino |
| `/validar-email/` | apps.comunidad (ZeroBounce wrapper) | Registro, Donaciones, SolicitarRecuperacion |
| `/registro/iniciar/`, `/registro/verificar-otp/`, `/registro/reenviar-otp/` | Usuario + OTPVerification | Registro |
| `/auth/login/`, `/auth/logout/`, `/auth/2fa/*` | Usuario + OTPVerification | Login, Perfil, TwoFactorVerify |
| `/password-reset/request/`, `/password-reset/confirm/` | Usuario | SolicitarRecuperacion, ConfirmarRecuperacion |
| `/usuarios/<id>/cambiar-password/` | Usuario | Perfil |
| `/token/refresh/`, `/token/blacklist/` | SimpleJWT | api.js (interceptor) |
| `/buscar/` | varios (helper) | Buscar |
| `/audit-log/` | AuditLog | AdminAuditoria, AdminDashboard |
| `/notificaciones/`, `/notificaciones/<id>/`, `/notificaciones/marcar-todas-leidas/`, `/notificaciones/contador-no-leidas/` | Notificacion | Perfil, AdminNotificaciones, NotificationBell, NotificationBell (?) |
| `/mensajes/`, `/mensajes/<id>/` | Mensaje | **No consumido** |
| `/libro-reclamaciones/`, `/libro-reclamaciones/<id>/*` | LibroReclamacion | LibroReclamacion (publico), AdminReclamaciones, AdminDashboard |
| `/donaciones/iniciar/`, `/donaciones/procesar-simulado/`, `/donaciones/estadisticas/` | Donacion | Donaciones, AdminDashboard |
| `/donaciones/mis-donaciones/`, `/donaciones/<id>/`, `/donaciones/<id>/boleta-pdf/` | Donacion | Perfil |
| `/donaciones/admin/lista/`, `/donaciones/admin/<id>/reembolsar/`, `/donaciones/admin/<id>/cancelar/` | Donacion | AdminDonaciones |
| `/solicitudes-baja/` | SolicitudBaja | Perfil, AdminBajas |
| `/admin/zerobounce/creditos/` | apps.comunidad.zerobounce | (admin) |
| `/health/`, `/health/live/`, `/health/ready/` | apps.core.health | (no UI; usado por infra) |

## Estado actual

1. **`Comunero` esta vivo** pero con exposicion REST admin-only. El frontend lo consume como lookup auxiliar y tolera fallos silenciosos.
2. Todos los 30 modelos tienen al menos un consumidor backend. **No hay modelos "zombie" puros** (definidos sin ninguna referencia).
3. Hay **3 modelos con exposicion REST sin consumidor React claro**:
   - `Mensaje` (messaging) - ViewSet completo, sin UI.
   - `NovedadVista` (content) - Endpoints, sin UI.
   - `ContenidoEstatico` (cms) - consumido solo por admin.
4. El frontend **si consume** los modelos de `accounts` (Usuario, Comunero), `comunidad` (Autoridad, ComiteComunal, Configuracion, MarcoLegal, PaginaLegal, HitoHistorico, Galeria, MensajeContacto, CategoriaGaleria, TextoSeccionInterna), `content` (Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion, Favorito, SolicitudBaja), `donaciones` (Donacion), `messaging` (Notificacion), `reports` (LibroReclamacion) y `core` (AuditLog).
5. El frontend **NO consume** `Mensaje`, `NovedadVista`, y `ContenidoEstatico` (este ultimo solo en admin).

## Riesgos

- **Baja prioridad:** eliminar modelos sin uso. No hay modelo sin uso. Cualquier depuracion apunta a quitar endpoints, no modelos.
- **Riesgo de superficie publica:** `ComuneroViewSet` es ModelViewSet con permiso `IsAdminUser` (correcto), pero expone `search_fields` con DNI/nombres/apellidos. Revisar que efectivamente requiera admin en produccion.
- **Riesgo de inconsistencia:** `Autoridad` tiene campo `dni` desnormalizado para casos sin `Comunero` (Gobernador). Si los seeders crean autoridades sin comunero, los admin pueden no poder asignarles un Comunero real despues.
- **Riesgo de duplicidad:** `ContenidoEstatico` (cms) vs `ConfiguracionComunidad` (comunidad). El sitio publico lee del segundo; el primero solo se usa en admin. Riesgo de drift: si alguien edita `contenido_estatico` creyendo que afecta al sitio publico, no pasara nada.
- **Riesgo de "fantasma":** `NovedadVista` y `Mensaje` son modelos con CRUD completo + admin + tests pero sin UI React. Si se decide que no se usaran, su eliminacion requiere:
  - Backup y migracion de datos (si aplica).
  - Decision sobre UI futura de chat/mensajes o tracking de lecturas.
- **Riesgo de busqueda global:** React consume `/buscar/`. El endpoint es una funcion (`buscar_global`) que internamente consulta Noticia, Evento, Autoridad, etc. Cualquier modelo nuevo debe agregarse explicitamente en esa vista.

## Skills recomendadas

- `django-expert`: para analisis profundo de modelos, signals y migraciones.
- `api-and-interface-design`: para evaluar contratos REST y deprecacion controlada.
- `api-contract-testing`: para validar el corte React <-> backend antes de cualquier cambio.
- `code-review-and-quality`: para revisar la limpieza eventual de modelos sub-utilizados.

## Recomendacion

### Que hacer

1. **Mantener `Comunero` como esta.** Es pieza central de la identidad (DNI) y base de `Autoridad` y `Usuario.tipo_usuario=COMUNERO`.
2. **Mantener todos los 30 modelos.** No hay ninguno claramente muerto.
3. **Decidir y documentar el destino de los 3 modelos "sub-utilizados"**:
   - `Mensaje` (messaging): si hay plan de chat entre usuarios, mantener y construir UI; si no, deprecar endpoints y dejar el modelo solo como "futuro".
   - `NovedadVista` (content): si no se usara, eliminar el modelo y los endpoints `/novedades/*`. El frontend ya no los usa.
   - `ContenidoEstatico` (cms): decidir si se migra todo a `ConfiguracionComunidad` y se elimina la tabla, o se mantiene solo para textos administrativos.
4. **Documentar el contrato actual** de los endpoints con consumidor React limitado:
   - `/api/v1/comuneros/` (solo admin, contrato: ComuneroSerializer).
   - `/api/v1/novedades/` (sin consumidor React).
   - `/api/v1/mensajes/` (sin consumidor React).
   - `/api/v1/cms/contenido/` (solo admin, sin reflejo en sitio publico).
5. **Si se decide eliminar `NovedadVista`**: crear plan de migracion, backup, eliminar endpoint y modelo en micro-tareas, actualizar tests.

### Que NO hacer

- No eliminar `Comunero` (es base del modelo de identidad).
- No eliminar `Autoridad` (es la pieza del dominio institucional).
- No romper `ComuneroViewSet` ni cambiar el serializador sin migrar el frontend.
- No tocar `apps/accounts/` ni `apps/core/` sin tests aprobados (ver AGENTS.md backend).
- No cambiar `zapotal_config/settings.py` en este audit (no aplica).
- No hacer refactor masivo: este audit solo describe y propone; cualquier cambio debe pasar por plan + aprobacion.

## Verificacion sugerida

Comandos minimos si en el futuro se decide tocar alguno de los modelos:

```bash
# Desde comunidad_zapotal_backend/
python manage.py check
python -m pytest apps -q
ruff check .

# Buscar referencias antes de cualquier cambio
grep -r "NovedadVista" apps/
grep -r "Mensaje" apps/messaging/
grep -r "ContenidoEstatico" apps/cms/
```

Ademas, antes de cualquier deprecacion, ejecutar el frontend para confirmar que ningun componente de React usa el endpoint:

```bash
# Desde comunidad_zapotal_frontend/
grep -r "novedad" src/
grep -r "/mensajes/" src/
grep -r "cms/contenido" src/
npm run build
```

## Entregable

- Este archivo: `agents-workflow/comunidad_zapotal_backend/audits/active/audit-modelos-django-2026-06-29.md`
- Estado: DRAFT -> actualizado a READY_FOR_PLAN.
- Proximo paso sugerido: si se decide actuar sobre `NovedadVista`, `Mensaje` o `ContenidoEstatico`, crear plan en `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/`.
