# Auditoría: Subsistema de Notificaciones

> Reporte generado: 2026-06-30

---

## 1. Modelo de datos

**Archivo:** `comunidad_zapotal_backend/apps/messaging/models.py`

### `Notificacion`

| Campo | Tipo | Detalle |
|---|---|---|
| `id` | AutoField | PK |
| `destinatario` | FK → User | null=True, on_delete=CASCADE |
| `tipo` | CharField(choices) | 33 tipos enum (ver abajo) |
| `titulo` | CharField(255) | Título de la notificación |
| `mensaje` | TextField | Cuerpo |
| `url_destino` | CharField(255) | blank=True |
| `fecha_creacion` | DateTimeField | auto_now_add |
| `leido` | BooleanField | default=False |
| `content_type` | FK → ContentType | null=True, referencia polimórfica |
| `object_id` | PositiveIntegerField | null=True |
| `contenido_relacionado` | GenericForeignKey | (content_type, object_id) |

### Tipos de notificación (33)

```
mensaje_nuevo, comentario_nuevo, comentario_respuesta, like_comentario,
reporte_resuelto, reporte_rechazado, donacion_recibida, donacion_confirmada,
meta_alcanzada, agradecimiento_donante, bienvenida, bienvenida_admin,
noticia_publicada, evento_creado, cuenta_activada, cuenta_desactivada,
cuenta_suspendida, cuenta_reactivada, cambio_rol, contenido_reportado,
solicitud_contacto, baja_confirmada, baja_rechazada, recordatorio_evento,
nuevo_miembro, publicacion_aprobada, publicacion_rechazada,
notificacion_admin, notificacion_sistema, recordatorio,
alerta_seguridad, felicitacion, personalizado
```

### `Mensaje` (misma app)

Mensajes privados entre usuarios con `remitente`, `destinatario`, `asunto`, `cuerpo`, `leido`, `fecha_envio`, `fecha_lectura`.

---

## 2. API Endpoints

### 2.1 ViewSet principal

**Archivo:** `comunidad_zapotal_backend/apps/messaging/views.py`

| Método | URL | Acción |
|---|---|---|
| GET | `/api/notificaciones/` | Lista paginada (filtra por `destinatario=request.user`, soporta `?leido=bool`) |
| GET | `/api/notificaciones/{id}/` | Detalle |
| PATCH | `/api/notificaciones/{id}/mark_read/` | Marca como leída |
| PATCH | `/api/notificaciones/{id}/mark_unread/` | Marca como no leída |
| POST | `/api/notificaciones/mark_all_read/` | Marca todas como leídas |

**Router:** `comunidad_zapotal_backend/apps/messaging/urls.py` — `router.register(r'notificaciones', NotificacionViewSet)`

### 2.2 Endpoints duplicados en content

**Archivo:** `comunidad_zapotal_backend/apps/content/views_user.py`

| Método | URL | Función |
|---|---|---|
| GET | `/api/contador-no-leidas/` | Retorna `{ "contador": N }` |
| POST | `/api/marcar-todas-leidas/` | Marca todas como leídas para `request.user` |

**Rutas:** `comunidad_zapotal_backend/apps/content/urls.py`

**Hallazgo ⚠️:** `marcar_todas_leidas` existe en dos lugares:
1. Como action del ViewSet en `messaging/views.py`
2. Como función independiente en `content/views_user.py`

Ambos hacen `Notificacion.objects.filter(...).update(leido=True)`. Esto duplica lógica y puede causar confusión.

### 2.3 Permisos

- El ViewSet usa `IsAuthenticated`.
- Los helpers en content no tienen decorador de permiso explícito (heredan de `@api_view` con `IsAuthenticatedOrReadOnly` o similar — verificar).
- `list` filtra por `request.user` siempre → no hay riesgo de ver notificaciones ajenas.

---

## 3. Backend: productores de notificaciones

### 3.1 Vía signals (content/signals.py)

| Evento | Señal | Notificación creada |
|---|---|---|
| Noticia publicada | `post_save` en News | `noticia_publicada` |
| Evento creado | `post_save` en Event | `evento_creado` (suscriptores) |
| Comentario nuevo | Señal post-save | `comentario_nuevo` (autor contenido) |
| Respuesta a comentario | Señal post-save | `comentario_respuesta` |

### 3.2 Vía services

`NotificacionService.crear_notificacion()` es el método central usado por todos los productores.

**Caso: Donaciones** (`donaciones/views.py:1309`)
- `_crear_notificaciones()` → `donacion_recibida/confirmada/meta_alcanzada/agradecimiento`

**Caso: Reports** (`reports/views.py`)
- `_crear_notificaciones_admin()` → `reporte_resuelto/rechazado`

**Caso: Contacto** (`comunidad/views_institucionales.py`)
- `_crear_notificaciones_admin()` en flujo de formulario de contacto

**Caso: Bajas** (no encontrado aún — probablemente en accounts)
- `baja_confirmada`, `baja_rechazada`

**Caso: Cuentas** (accounts)
- `cuenta_activada/desactivada/suspendida/reactivada`, `cambio_rol`, `bienvenida`

**Caso: Mensajes privados**
- `mensaje_nuevo` — creada desde vista de mensajería

### 3.3 Comando de purga

**Archivo:** `messaging/management/commands/purge_old_notifications.py`

Elimina notificaciones leídas con más de N días (configurable). Debe correr como cron.

**Recomendación:** Programar cron semanal (domingo 03:00).

---

## 4. Frontend

### 4.1 NotificationBell (contador + dropdown)

**Archivo:** `src/components/common/NotificationBell/NotificationBell.jsx`

- Polling cada **60s** a `/api/contador-no-leidas/`
- Dropdown con últimas **5** no leídas
- Cada ítem: enlace a `url_destino` + botón "Marcar leída"
- Botón "Marcar todas leídas" al pie
- Contador visible en badge rojo del ícono campana

### 4.2 Navbar

**Archivo:** `src/components/common/Navbar/Navbar.jsx`

- Renderiza `<NotificationBell />` solo si hay sesión activa
- Posición: extremo derecho del header

### 4.3 AdminNotificaciones (panel admin)

**Archivo:** `src/pages/Admin/AdminNotificaciones.jsx`

- Ruta: `/admin/notificaciones`
- Tabla paginada con columnas: Tipo, Título, Mensaje, Fecha, Leído
- Filtros: por estado (leído/no leído), por tipo, por fecha
- Acciones: marcar leída, marcar no leída, marcar todas leídas
- Usa `useUrlFilters` para mantener filtros en query params
- Redirige según `url_destino` o tipo al hacer clic
- Carga desde `/api/notificaciones/`

### 4.4 Perfil (tab Notificaciones)

**Archivo:** `src/pages/Perfil/Perfil.jsx`

- Tab "Notificaciones" con lista paginada
- Mismo endpoint `/api/notificaciones/`
- Filtros básicos (leído/no leído)
- Vista para usuario logueado (no admin)

### 4.5 AdminDashboard

**Archivo:** `src/pages/Admin/AdminDashboard.jsx`

- Contiene enlace a `/admin/notificaciones`

### 4.6 Rutas

**Archivo:** `src/App.jsx`

- `<Route path="/admin/notificaciones" element={<AdminNotificaciones />} />`

---

## 5. Flujo completo

```
[Evento externo]
    ↓
[Productor] (signal / vista / servicio)
    ↓
NotificacionService.crear_notificacion()
    ↓
[DB] Notificacion creada (leido=False)
    ↓
[Frontend] NotificationBell poll cada 60s → GET /api/contador-no-leidas/
    ↓
[Frontend] Badge actualizado con contador
    ↓
[Usuario] Abre dropdown → últimas 5 no leídas
    ↓
[Usuario] Click en ítem → redirige a url_destino
    ↓
[Usuario] Click "Marcar leída" → PATCH /api/notificaciones/{id}/mark_read/
    ↓
[Usuario] "Marcar todas" → POST /api/notificaciones/mark_all_read/
```

---

## 6. Hallazgos y observaciones

### 🔴 Críticos

1. **Duplicación de `marcar_todas_leidas`** — existe en `NotificacionViewSet` (action POST) y como endpoint independiente en `content/views_user.py`. Ambas implementaciones hacen `update(leido=True)` sin transacción ni logging. Unificar.

2. **`contador_no_leidas` fuera del ViewSet** — El endpoint vive en `content/views_user.py` en vez de ser una action del ViewSet (`/api/notificaciones/contador-no-leidas/`). Inconsistencia de ruteo.

### 🟡 Moderados

3. **Sin WebSockets / SSE** — El polling de 60s es adecuado para el volumen actual pero no escala. Considerar SSE para notificaciones en tiempo real cuando la base de usuarios crezca.

4. **Sin paginación en NotificationBell** — El dropdown solo muestra 5. Si hay más de 5 no leídas, el usuario no lo sabe sin ir al panel. Agregar indicador tipo "y N más".

5. **Referencia polimórfica infrautilizada** — `content_type`/`object_id` existen pero no se usan consistentemente en el frontend para generar enlaces contextuales.

### 🟢 Leves

6. **Sin tests específicos** — No se encontraron tests unitarios para `NotificacionService` ni `NotificacionViewSet`.

7. **`purge_old_notifications` sin cron configurado** — El comando existe pero no hay entry en crontab ni schedule documentado.

8. **Email transaccional opcional sin trazabilidad** — `EmailService.enviar_notificacion()` existe pero no hay registro de qué notificaciones generan email y cuáles no.

---

## 7. Recomendaciones

| Prioridad | Acción |
|---|---|
| Alta | Unificar `marcar_todas_leidas` en un solo endpoint dentro del ViewSet |
| Alta | Mover `contador-no-leidas` como action del ViewSet |
| Media | Agregar indicador de cantidad total no leída en NotificationBell |
| Media | Agregar tests unitarios para modelo, viewset y service |
| Media | Configurar cron para `purge_old_notifications` |
| Baja | Evaluar SSE para reemplazar polling cuando sea necesario |
| Baja | Documentar el envío de email transaccional por tipo de notificación |

---

## 8. Archivos relevantes

| Archivo | Rol |
|---|---|
| `messaging/models.py` | Modelo `Notificacion` + `Mensaje` |
| `messaging/views.py` | `NotificacionViewSet` |
| `messaging/serializers.py` | `NotificacionSerializer` |
| `messaging/services.py` | `NotificacionService` |
| `messaging/urls.py` | Router |
| `messaging/management/commands/purge_old_notifications.py` | Purga |
| `content/signals.py` | Señales productoras |
| `content/views_user.py` | Helpers duplicados |
| `content/urls.py` | Rutas de content |
| `donaciones/views.py` | Notificaciones de donaciones |
| `reports/views.py` | Notificaciones de reports |
| `comunidad/views_institucionales.py` | Notificaciones de contacto |
| `accounts/services.py` | Email transaccional |
| `zapotal_config/settings.py` | Config (`FRONTEND_ADMIN_URL`, `EMAIL_DESTINO_TEMPORAL`) |
| `fr/AdminNotificaciones.jsx` | Panel admin |
| `fr/Perfil.jsx` | Tab de notificaciones en perfil |
| `fr/NotificationBell.jsx` | Campana + contador + dropdown |
| `fr/Navbar.jsx` | Renderiza campana |
| `fr/AdminDashboard.jsx` | Link a admin notificaciones |
| `fr/App.jsx` | Ruta `/admin/notificaciones` |
| `fr/api.js` | Axios base |
