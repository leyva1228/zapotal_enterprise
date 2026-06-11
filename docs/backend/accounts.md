# App Accounts

`apps/accounts` — Gestión de usuarios, comuneros y autenticación JWT.

## Modelos

### Usuario (AbstractUser personalizado)

| Campo | Tipo | Detalle |
|-------|------|---------|
| `email` | EmailField | Único, usado para login |
| `username` | CharField | No se usa (heredado por compatibilidad) |
| `tipo_usuario` | CharField | choices: ADMIN, COMUNERO, VISITANTE |
| `estado` | CharField | choices: ACTIVO, INACTIVO, SUSPENDIDO |
| `foto_perfil` | ImageField | Subida a `fotos_perfil/` |
| `telefono` | CharField | Opcional |
| `direccion` | TextField | Opcional |
| `fecha_nacimiento` | DateField | Opcional |
| `USERNAME_FIELD` | - | `email` |
| `REQUIRED_FIELDS` | - | `[]` |

### Comunero

| Campo | Tipo | Detalle |
|-------|------|---------|
| `usuario` | OneToOneField | FK a Usuario |
| `dni` | CharField(8) | Único, validado (8 dígitos) |
| `nombres` | CharField | Nombre completo del comunero |
| `apellido_paterno` | CharField | - |
| `apellido_materno` | CharField | - |

### Modelos de apoyo

- `TokenRestablecer` — Token para restablecimiento de contraseña (email, token, creado, expira)

## Servicios (services.py)

### AuthService
- `registro(datos)`: Crea Usuario (tipo=COMUNERO) + Comunero. Envía email de bienvenida.
- `login(email, password)`: Valida credenciales, verifica estado ACTIVO, retorna tokens JWT.
- `refresh_token(refresh)`: Renueva access token.
- `logout(refresh)`: Blacklist del refresh token.
- `cambiar_password(usuario, old, new)`: Cambio de contraseña.
- `restablecer_password(email)`: Genera token y envía email.
- `confirmar_restablecer(email, token, password)`: Confirma restablecimiento.

### UsuarioService
- `listar_usuarios(filtros)`: Lista paginada con filtros por tipo/estado.
- `obtener_usuario(id)`: Detalle de usuario.
- `actualizar_usuario(id, datos)`: Actualización parcial.
- `cambiar_estado(id, estado)`: Cambia estado (solo admin).
- `cambiar_tipo(id, tipo)`: Cambia tipo (solo admin).
- `eliminar_usuario(id)`: Soft delete (cambia estado a INACTIVO).

### ComuneroService
- `listar_comuneros(filtros)`: Lista paginada.
- `obtener_comunero(id)`: Detalle.
- `actualizar_comunero(id, datos)`: Actualización.
- `existe_dni(dni)`: Verifica unicidad de DNI.

## Vistas (views.py)

| Endpoint | Métodos | Auth | Throttle |
|----------|---------|------|----------|
| `/api/v1/accounts/comuneros/` | GET, POST, PATCH, DELETE | JWT | - |
| `/api/v1/accounts/usuarios/` | GET, POST | JWT | - |
| `/api/v1/accounts/login/` | POST | No | 10/min |
| `/api/v1/accounts/register/` | POST | No | 5/min |
| `/api/v1/accounts/profile/` | GET, PUT, PATCH | JWT | - |
| `/api/v1/accounts/refresh/` | POST | No | 10/min |
| `/api/v1/accounts/logout/` | POST | JWT | - |

### LoginView
- POST: email+password → access+refresh tokens + datos usuario
- Throttle: 10 intentos/minuto
- Rate limit excedido: `429 Too Many Requests`

### RegisterView
- POST: email, password, nombres, apellidos, dni, etc.
- Crea usuario + comunero automáticamente
- Retorna tokens + datos del usuario creado

### ProfileView
- GET: perfil del usuario autenticado
- PUT/PATCH: actualización parcial de perfil

## URLs

```python
router = DefaultRouter()
router.register(r'comuneros', ComuneroViewSet)
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
] + router.urls
```
