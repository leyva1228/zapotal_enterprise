# Reporte de Análisis: frontend-architecture

**Proyecto:** Comunidad Campesina Zapotal — Portal Web
**Fecha:** 2026-06-10

## Resumen Ejecutivo

La arquitectura del frontend sigue el patrón tradicional de CRA con React Router. La separación entre componentes y páginas es clara, pero la gestión de estado, el manejo de datos asíncronos, y la organización de servicios presentan oportunidades de mejora. No hay abstracciones de servicio, la lógica de fetching está acoplada a los componentes, y el manejo de autenticación es manual.

## Puntos Fuertes

- Separación clara entre `components/` (reutilizables) y `pages/` (vistas de ruta)
- React Router con rutas bien definidas y layout compartido
- AuthProvider como contexto global para estado de sesión
- Scroll restoration manejado con ScrollToTop
- Componente LoadingScreen global durante carga inicial

## Áreas de Mejora

### 1. Sin Capa de Servicio
Todas las llamadas API están escritas directamente en los componentes con `axios.get/post`. No hay un archivo `api.js` o `services/` que abstraiga la URL base, headers, manejo de errores, interceptors, o tipado de respuestas.

Ocurre en:
- `Autoridades.jsx:14-35` — `axios.get` directo en useEffect
- `Eventos.jsx:20-60` — `axios.get` directo en useEffect
- `Noticias.js` — `axios.get` directo
- `DetalleEvento.jsx` — múltiples axios calls para comentarios
- `DetalleNoticia.js` — múltiples axios calls
- `Contacto.jsx` — `axios.post` para envío de formulario
- `LibroReclamaciones.jsx` — `axios.post`
- `Login.jsx` — `axios.post` para autenticación
- `Registro.jsx` — `axios.post` para registro

### 2. URLs de API Inconsistentes
- Algunas llamadas usan `http://127.0.0.1:8000/api`
- Otras usan `http://localhost:8000/api`
- Deberían centralizarse en una variable de entorno (`.env`)

### 3. Estado Global Manual
- Autenticación manejada con AuthContext + sessionStorage
- Sin librería de estado global (Zustand, Redux, Jotai)
- Sin persistencia automática de datos de sesión

### 4. Sin Manejo de Errores Global
- No hay interceptor de Axios para errores HTTP (401, 500)
- No hay sistema de notificaciones para errores
- Cada componente maneja errores individualmente con `catch` y estado local

### 5. Sin Layout Anidado
- React Router no usa layout routes (Outlet)
- App.js contiene el hero de Home + Router, acoplando layout a página específica
- No hay layout separado para rutas autenticadas vs públicas

### 6. Sin Lazy Loading de Rutas
Todas las rutas se importan estáticamente en App.js:
```jsx
import Home from './pages/Home';
import Eventos from './pages/Eventos/Eventos';
import Noticias from './pages/Noticias/Noticias';
// etc.
```

### 7. Estructura de Archivos
```
src/
  components/       → Navbar.jsx (plano), Footer.jsx (plano),
                      Contacto/ (carpeta), Autoridades/ (carpeta),
                      LibroReclamaciones/ (carpeta), ScrollToTop.jsx (plano),
                      LoadingScreen.jsx (plano)
  pages/            → Home/, Login/, Eventos/, Noticias/, Perfil/, Registro/
  App.js            → Router + Layout + Hero de Home
```

Falta consistencia: algunos componentes tienen carpeta (con sus CSS colocalizados), otros son archivos planos.

### 8. Sin TypeScript ni Tipos Compartidos
No hay carpetas `types/` o `interfaces/`. Las props se pasan sin validación de tipos.

## Recomendaciones

1. **Crear capa de servicios** (`src/services/api.js`) con Axios instance, base URL de `.env`, interceptors para auth token y errores globales
2. **Centralizar URLs de API** en `.env` con `REACT_APP_API_URL`
3. **Implementar React.lazy + Suspense** para todas las rutas
4. **Usar layout routes** de React Router: Layout principal con Navbar + Footer + `<Outlet/>`
5. **Separar hero de Home** del layout global en App.js
6. **Agregar interceptors de Axios** para manejo global de errores 401 (redirect a login)
7. **Implementar sistema de notificaciones** con contexto + toasts
8. **Estandarizar estructura**: todos los componentes en carpetas propias
9. **Agregar TypeScript** gradualmente, empezando por `services/api.ts` y props de componentes
10. **Considerar Zustand** si el estado global crece más allá de auth

## Prioridad de Acción

| Acción | Prioridad | Esfuerzo |
|--------|-----------|----------|
| Capa de servicio API | Alta | Bajo |
| Centralizar URL en .env | Alta | Bajo |
| Axios interceptors | Alta | Bajo |
| React.lazy + Suspense | Alta | Bajo |
| Layout routes (Outlet) | Alta | Medio |
| Separar hero de layout | Alta | Medio |
| Sistema de notificaciones | Media | Medio |
| Estandarizar estructura | Media | Bajo |
| TypeScript | Media | Alto |
| Zustand | Baja | Medio |
