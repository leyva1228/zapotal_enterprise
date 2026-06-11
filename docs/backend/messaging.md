# App Messaging

`apps/messaging` — Mensajería interna y notificaciones.

## Modelos

### Mensaje

| Campo | Tipo | Detalle |
|-------|------|---------|
| `remitente` | ForeignKey(Usuario) | Quien envía |
| `destinatario` | ForeignKey(Usuario) | Quien recibe |
| `asunto` | CharField(max=200) | - |
| `cuerpo` | TextField | Contenido del mensaje |
| `leido` | BooleanField(default=False) | Estado de lectura |
| `fecha_envio` | DateTimeField(auto_now_add) | - |

### Notificacion

| Campo | Tipo | Detalle |
|-------|------|---------|
| `destinatario` | ForeignKey(Usuario) | Quien recibe la notificación |
| `remitente` | ForeignKey(Usuario, null=True) | Opcional, quien origina |
| `tipo` | CharField(max=50) | Ej: comentario, evento, mensaje, sistema |
| `titulo` | CharField(max=200) | - |
| `mensaje` | TextField | - |
| `leido` | BooleanField(default=False) | - |
| `fecha_creacion` | DateTimeField(auto_now_add) | - |

## Vistas

### MensajeViewSet

| Endpoint | Métodos | Acción |
|----------|---------|--------|
| `/api/v1/messaging/mensajes/` | GET, POST | Lista filtrando por usuario autenticado |
| `/api/v1/messaging/mensajes/{id}/` | GET, PUT, PATCH, DELETE | Propietario o destinatario |

- GET automáticamente filtra por `remitente` o `destinatario` = usuario autenticado
- POST asigna `remitente` automáticamente al usuario autenticado

### NotificacionViewSet

| Endpoint | Métodos | Acción |
|----------|---------|--------|
| `/api/v1/messaging/notificaciones/` | GET, PATCH | Solo destinatario autenticado |
| `/api/v1/messaging/notificaciones/{id}/` | GET, PATCH | Marcar como leída |

## URLs

Router registra ambos ViewSets bajo `/api/v1/messaging/`.
