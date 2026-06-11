# Frontend — Componentes

`src/components/`

## Navegación y Layout

### Navbar
- Barra de navegación superior responsiva
- Enlaces públicas: Inicio, Noticias, Eventos, Nosotros, Contacto
- Enlaces autenticados: Perfil, Mensajería, Admin (si es admin/comunero)
- Botón Login/Logout según estado de AuthContext

### Footer
- Pie de página con enlaces e información institucional

## Protección de Rutas

### ProtectedRoute
- Envuelve rutas que requieren autenticación
- Redirige a `/login` si no hay token en AuthContext

### AdminRoute
- Envuelve rutas de administración
- Verifica que `tipo_usuario` sea ADMINISTRADOR o COMUNERO
- Redirige a Home si no tiene permisos

## Display

### NewsCard
- Tarjeta de noticia: imagen, categoría, título, resumen, fecha, vistas
- Usada en grid de Home y Noticias

### EventCard
- Tarjeta de evento: imagen, título, fecha, ubicación
- Usada en grid de Home y Eventos

## Feedback

### Loading
- Spinner de carga mientras se ejecutan peticiones

### ErrorMessage
- Mensaje de error con opción de reintentar

## AuthContext

`src/context/AuthContext.tsx` — Estado global de autenticación.

### Funcionalidad
- `login(email, password)`: llama a `POST /auth/login/`, guarda tokens en localStorage, decodifica JWT
- `register(data)`: llama a `POST /auth/register/` con FormData
- `logout()`: limpia tokens, redirige a login
- `user`: objeto decodificado del JWT (id, email, tipo_usuario, nombre, apellido)
- Refresca token automáticamente si expiró (vía api.ts interceptor)
