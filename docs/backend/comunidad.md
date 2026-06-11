# App Comunidad

`apps/comunidad` — Autoridades de la comunidad campesina.

## Modelos

### Autoridad

| Campo | Tipo | Detalle |
|-------|------|---------|
| `comunero` | ForeignKey(Comunero) | FK a comunero |
| `usuario` | ForeignKey(Usuario) | FK a usuario (para foto_perfil) |
| `cargo` | CharField(max=100) | Ej: Presidente, Vicepresidente, Secretario |
| `descripcion` | TextField | Opcional |
| `fecha_inicio` | DateField | Inicio del período |
| `fecha_fin` | DateField | Opcional, fin del período |
| `activo` | BooleanField(default=True) | Si está en funciones |

## Vistas

### AutoridadViewSet

| Endpoint | Métodos | Permisos |
|----------|---------|----------|
| `/api/v1/comunidad/autoridades/` | GET, POST, PUT, PATCH, DELETE | IsAdminOrReadOnly |

- GET público: lista autoridades activas con datos del comunero + foto del usuario
- POST/PUT/PATCH/DELETE: solo administradores

## Serializador

`AutoridadSerializer` incluye:
- `comunero_nombre` (read only): nombre completo del comunero
- `foto_url` (read only): URL de la foto del usuario asociado
