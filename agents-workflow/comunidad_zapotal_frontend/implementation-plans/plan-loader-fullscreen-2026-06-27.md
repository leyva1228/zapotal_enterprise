# Plan: Loader global fullscreen bajo navbar

## Estado

- Estado: APPROVED (auto-aprobado)
- Requiere aprobacion humana: NO
- Fecha: 2026-06-27
- Tecnologia: Frontend React

## Objetivo

Cubrir TODAS las paginas y secciones con un loader fullscreen que se situa debajo del navbar, bloquea scroll e interacciones, se desbloquea al terminar la carga, y se muestra tambien en cambios de ruta. Mantener el diseno del modelo de referencia.

## No objetivos

- Reescribir loaders de inputs/botones.
- Migrar loaders internos de admin (`admin-loading` con `FaSpinner`).
- Modificar `RequireAuth*`, `RequireAdmin*`, `src/api.js`, contexts existentes.

## Skills obligatorias

- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`

## Archivos permitidos

- `src/context/LoaderContext.jsx` (nuevo)
- `src/components/common/LoaderOverlay/LoaderOverlay.jsx` (nuevo)
- `src/components/common/LoaderOverlay/LoaderOverlay.css` (nuevo)
- `src/components/common/PageLoader/PageLoader.jsx` (variante `overlay`)
- `src/components/common/PageLoader/PageLoader.css`
- `src/hooks/useDelayedLoading.js` (mantener, sin cambios)
- `src/App.jsx`
- `src/index.css` (solo si requiere reglas globales de bloqueo de scroll)
- `src/pages/Noticias/Noticias.jsx`
- `src/pages/Eventos/Eventos.jsx`
- `src/pages/Noticias/DetalleNoticia.jsx`
- `src/pages/Eventos/DetalleEvento.jsx`
- `src/pages/Autoridades/AutoridadesPage.jsx`
- `src/components/Autoridades/Autoridades.jsx`
- `src/pages/Buscar/Buscar.jsx`

## Archivos prohibidos sin nueva aprobacion

- `src/api.js`
- `src/context/AuthContext.jsx`
- `src/components/RequireAuth*`
- `src/components/RequireAdmin*`
- `src/pages/Admin/**`
- Backend Django

## Micro-tareas

### Task 1: Crear `LoaderContext`

- Objetivo: estado global `isLoading` con control por contador de tareas + cambios de ruta.
- Archivos: `src/context/LoaderContext.jsx`.
- Pasos:
  1. Implementar `LoaderProvider` con `useState` + contador (`useRef`).
  2. API: `startTask(id)`, `endTask(id)`, `isLoading`.
  3. `isLoading` se activa cuando hay tareas pendientes o cuando el context fue marcado por un cambio de ruta.
  4. Hook `useLoader()`.
- Criterio de exito: build limpio.

### Task 2: Crear `LoaderOverlay`

- Objetivo: componente fullscreen que se posiciona debajo del navbar.
- Archivos: `src/components/common/LoaderOverlay/{LoaderOverlay.jsx,LoaderOverlay.css}`.
- Pasos:
  1. Estructura: overlay con `position: fixed`, `top: var(--navbar-height, 96px)`, `left: 0`, `right: 0`, `bottom: 0`.
  2. Variante `no-navbar` con `top: 0` para rutas sin navbar.
  3. Z-index entre contenido y navbar.
  4. Bloqueo de scroll del body.
  5. Reutiliza el diseno de `LoadingScreen` con sectores/chispas/dots.
- Criterio de exito: build limpio, layout correcto.

### Task 3: Integrar en `App.jsx`

- Objetivo: splash inicial + route changes activan el context.
- Archivos: `src/App.jsx`.
- Pasos:
  1. Envolver todo con `<LoaderProvider>`.
  2. Mover el control del splash inicial al context.
  3. Crear `RouteChangeListener` que dispara loader en cada cambio de ruta y lo apaga tras un minimo (300ms) usando `useDelayedLoading`.
  4. Renderizar `<LoaderOverlay variant="with-navbar" />` o `variant="no-navbar"` segun la ruta.
- Criterio de exito: build limpio.

### Task 4: Paginas publicas notifican carga

- Objetivo: cada pagina con fetch avisa inicio/fin al context.
- Archivos: `Noticias.jsx`, `Eventos.jsx`, `DetalleNoticia.jsx`, `DetalleEvento.jsx`, `AutoridadesPage.jsx`, `Autoridades.jsx`, `Buscar.jsx`.
- Pasos:
  1. Importar `useLoader`.
  2. En el `useEffect` de carga, llamar `loader.startTask('nombre')` al inicio y `loader.endTask('nombre')` al final.
- Criterio de exito: build limpio, comportamiento correcto.

### Task 5: Verificacion final

- `npm run build` + `npm run dev` (smoke test).
