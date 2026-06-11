# Frontend — Servicios API

`src/services/`

## api.ts (Axios Instance)

- Base URL desde `window.VITE_API_URL` o `http://localhost:8000/api/v1/`
- Interceptor de request: agrega `Authorization: Bearer <token>` desde localStorage
- Interceptor de response: en 401 intenta refresh token (`/auth/refresh/`), si falla redirige a login
- Refresh token almacenado en `localStorage.getItem('refresh_token')`

## Módulos

| Archivo | Funciones principales | Endpoints |
|---------|----------------------|-----------|
| `auth.ts` | `login`, `register`, `refreshToken` | `/auth/login/`, `/auth/register/`, `/auth/refresh/` |
| `noticias.ts` | `getNoticias`, `getNoticia`, `createNoticia`, `updateNoticia`, `deleteNoticia`, `getRelacionadas`, `incrementarVistas` | `/content/noticias/` |
| `eventos.ts` | `getEventos`, `getEvento`, `createEvento`, `updateEvento`, `deleteEvento` | `/content/eventos/` |
| `categorias.ts` | `getCategorias`, `createCategoria`, `updateCategoria`, `deleteCategoria` | `/content/categorias/` |
| `autoridades.ts` | `getAutoridades` | `/comunidad/autoridades/` |
| `mensajes.ts` | `getMensajes`, `getMensaje`, `sendMensaje`, `deleteMensaje` | `/messaging/mensajes/` |
| `reports.ts` | `sendContacto`, `sendReclamacion` | `/reports/contacto/`, `/reports/reclamaciones/` |
| `profile.ts` | `getProfile`, `updateProfile` | `/auth/profile/` |

## Configuración

`public/env.js` — Variables de entorno runtime:

```js
window.VITE_API_URL = "http://localhost:8000/api/v1/"
window.VITE_PAGAPE_KEY = "pg_test_..."
```

`vite.config.ts` — Proxy de desarrollo:

```ts
proxy: {
  "/api": {
    target: "http://localhost:8000",
    changeOrigin: true,
  },
}
```
