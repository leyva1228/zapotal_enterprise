# Frontend — Páginas

`src/pages/`

| Archivo | Ruta | Descripción | Auth |
|---------|------|-------------|------|
| `Login.tsx` | `/login` | Inicio de sesión con email + password | No |
| `Register.tsx` | `/register` | Registro de usuario | No |
| `Home.tsx` | `/` | Landing page con últimas noticias y eventos | No |
| `Noticias.tsx` | `/noticias` | Lista de noticias públicas | No |
| `NoticiaDetalle.tsx` | `/noticias/:id` | Detalle de noticia con comentarios | No |
| `Eventos.tsx` | `/eventos` | Lista de eventos | No |
| `Nosotros.tsx` | `/nosotros` | Página institucional con autoridades | No |
| `Admin.tsx` | `/admin` | Panel de administración | Admin |
| `Perfil.tsx` | `/perfil` | Perfil de usuario autenticado | Sí |
| `Mensajeria.tsx` | `/mensajeria` | Mensajería interna | Sí |
| `Contacto.tsx` | `/contacto` | Formulario de contacto | No |
| `LibroReclamaciones.tsx` | `/libro-reclamaciones` | Libro de reclamaciones | No |
| `Donaciones.tsx` | `/donaciones` | Donaciones (integración Paga.pe) | No |

## Detalle por página

### Login (`Login.tsx`)
- Formulario email + password
- Consume `POST /auth/login/`
- Guarda tokens en localStorage via AuthContext
- Redirige a Home

### Register (`Register.tsx`)
- Formulario: email, password, confirmación, nombres, apellidos, DNI (opcional: tipo_usuario, teléfono, dirección, foto)
- Consume `POST /auth/register/`
- Usa `MultipartFormData` para subir foto
- Redirige a Login

### Home (`Home.tsx`)
- Hero section
- Últimas noticias (Grid de NewsCard)
- Próximos eventos (Grid de EventCard)

### Noticias (`Noticias.tsx`)
- Lista paginada de noticias
- Filtro por categoría

### NoticiaDetalle (`NoticiaDetalle.tsx`)
- Contenido completo de la noticia
- Comentarios anidados
- Formulario para nuevo comentario (requiere auth)
- Botón de like/dislike

### Eventos (`Eventos.tsx`)
- Lista paginada de eventos
- Vista de tarjetas con fecha, lugar, imagen

### Nosotros (`Nosotros.tsx`)
- Descripción institucional
- Lista de autoridades activas (consume `/api/v1/comunidad/autoridades/`)

### Admin (`Admin.tsx`)
- Dashboard con enlaces a gestión de:
  - Noticias, Eventos, Categorías, Multimedia
  - Comentarios, Reacciones
  - Autoridades
  - Mensajes recibidos
  - Contacto y Reclamaciones
- Panel para administradores y usuarios tipo COMUNERO

### Perfil (`Perfil.tsx`)
- Ver y editar perfil propio
- Formulario con foto, teléfono, dirección
- Consume `GET/PUT /auth/profile/`

### Mensajeria (`Mensajeria.tsx`)
- Bandeja de entrada (mensajes recibidos)
- Enviar nuevo mensaje
- Ver detalle y marcar como leído
- Consume `/api/v1/messaging/mensajes/`

### Contacto (`Contacto.tsx`)
- Formulario público: nombre, email, asunto, mensaje
- Consume `POST /api/v1/reports/contacto/`

### LibroReclamaciones (`LibroReclamaciones.tsx`)
- Formulario público: datos personales, tipo, título, descripción, pedido, anexo
- Consume `POST /api/v1/reports/reclamaciones/`

### Donaciones (`Donaciones.tsx`)
- Integración con Paga.pe (API key en `env.js`)
- Formulario de donación voluntaria
