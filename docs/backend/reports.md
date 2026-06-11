# App Reports

`apps/reports` — Contacto y libro de reclamaciones.

## Modelos

### ContactoMensaje

| Campo | Tipo | Detalle |
|-------|------|---------|
| `nombre` | CharField(max=100) | Nombre del remitente |
| `email` | EmailField | - |
| `asunto` | CharField(max=200) | - |
| `mensaje` | TextField | - |
| `leido` | BooleanField(default=False) | Estado interno |
| `fecha_envio` | DateTimeField(auto_now_add) | - |

### LibroReclamacion

| Campo | Tipo | Detalle |
|-------|------|---------|
| `nombres` | CharField(max=100) | Nombres del reclamante |
| `apellidos` | CharField(max=100) | Apellidos |
| `dni` | CharField(max=8) | Documento nacional |
| `email` | EmailField | - |
| `telefono` | CharField(max=15) | Opcional |
| `direccion` | CharField(max=255) | Opcional |
| `tipo` | CharField(choices) | QUEJA, RECLAMO, SUGERENCIA |
| `titulo` | CharField(max=200) | - |
| `descripcion` | TextField | - |
| `pedido` | TextField | Opcional, qué solicita |
| `estado` | CharField(choices) | PENDIENTE, EN_REVISION, RESUELTO, RECHAZADO |
| `anexo` | FileField | Opcional, subida a `reclamaciones/` |
| `fecha_creacion` | DateTimeField(auto_now_add) | - |
| `fecha_resolucion` | DateTimeField(null=True) | - |

## Vistas

### ContactoViewSet

| Endpoint | Métodos | Permisos |
|----------|---------|----------|
| `/api/v1/reports/contacto/` | POST | AllowAny (público) |
| `/api/v1/reports/contacto/{id}/` | GET, PATCH, DELETE | IsAdminUser |

- Create público sin autenticación
- Lectura/gestión solo administradores

### LibroReclamacionViewSet

| Endpoint | Métodos | Permisos |
|----------|---------|----------|
| `/api/v1/reports/reclamaciones/` | POST | AllowAny (público) |
| `/api/v1/reports/reclamaciones/{id}/` | GET, PATCH, DELETE | IsAdminUser |

- Create público sin autenticación
- Lectura/gestión solo administradores

## URLs

Router registra ambos ViewSets bajo `/api/v1/reports/`.
