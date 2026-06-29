# Audit: Mejora del LoadingScreen unificado

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-27
- Autor/agente: opencode (Minimax-M3)
- Tecnologia: Frontend React (comunidad_zapotal_frontend)

## Objetivo

Mejorar el `LoadingScreen` actual (`src/pages/LoadingScreen/`) fusionando el diseno del modelo de referencia (`_reference/loader/LoadingScreen.{jsx,css}`), sin reemplazar el componente, y reemplazar todos los loaders puntuales de paginas y componentes con una version compartida del mismo diseno. La duracion del loader debe acoplarse al tiempo real de carga segun la calidad de internet (no un timeout fijo).

## Alcance

### Incluye

- `src/pages/LoadingScreen/LoadingScreen.jsx` y `LoadingScreen.css`: integrar el modelo de sectores + chispas + dots del reference.
- `src/components/common/PageLoader/`: nuevo componente reutilizable para loaders in-page (variante sin fullscreen).
- `src/hooks/useDelayedLoading.js`: nuevo hook para mostrar el loader solo si la carga supera N ms (evita parpadeo) y mantenerlo hasta que termine.
- Integrar en: `src/pages/Noticias/Noticias.jsx`, `src/pages/Noticias/DetalleNoticia.jsx`, `src/pages/Eventos/Eventos.jsx`, `src/pages/Eventos/DetalleEvento.jsx`, `src/pages/Autoridades/AutoridadesPage.jsx`, `src/pages/Buscar/Buscar.jsx`, `src/components/Autoridades/Autoridades.jsx`, `src/pages/Admin/*` (solo donde ya hay `admin-loading`).
- `src/App.jsx`: reemplazar el `setTimeout` fijo de 1200ms por la espera real al evento `load` + `useDelayedLoading` (minimo visible).
- CSS global minimo: importar estilos del loader en `src/index.css` o mantenerlos locales en `LoadingScreen.css` + `PageLoader.css`.

### No incluye

- Cambios en el backend.
- Cambios en `src/api.js`, `src/context/`, `RequireAuth*`, `RequireAdmin*` (zonas sensibles — sin cambios).
- Reescribir loaders internos de inputs/botones (`rg-spinner`, `form-btn__loader`, `mapa-spinner`).
- Cambiar contratos de API.

## Contexto leido

- `comunidad_zapotal_frontend/AGENTS.md`
- `comunidad_zapotal_frontend/graphify/GRAPH_REPORT.md` (referencia)
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `comunidad_zapotal_frontend/_reference/loader/LoadingScreen.jsx`
- `comunidad_zapotal_frontend/_reference/loader/LoadingScreen.css`
- `comunidad_zapotal_frontend/src/pages/LoadingScreen/LoadingScreen.jsx`
- `comunidad_zapotal_frontend/src/pages/LoadingScreen/LoadingScreen.css`
- `comunidad_zapotal_frontend/src/App.jsx`
- `comunidad_zapotal_frontend/src/index.css`

## Estado actual

El `LoadingScreen` actual muestra un fondo gris, un circulo blanco con sombra, cuatro piezas que vuelan y el logo final escalado. Texto "Cargando... Preparando la plataforma comunitaria". El `App.jsx` lo cierra con un `setTimeout` fijo de 1200ms, no esperando a que termine la carga real.

En paginas internas hay multiples loaders inconsistentes:
- `Noticias`: `<div className="loader-container">` con anillos y titulo "Cargando publicaciones".
- `Eventos`: bloque `.loader-container` / `.loader-wrapper` con anillos y mensaje.
- `DetalleNoticia` / `DetalleEvento`: `<div className="loading-container">` con `loading-spinner` y parrafo.
- `Autoridades`: `au-loading-spinner`.
- `Admin*`: `admin-loading` con `FaSpinner fa-spin`.
- `RequireAuth` / `RequireAdmin`: `admin-loading` con texto "Cargando...".

Todos visualmente diferentes y sin conexion con el tiempo real de carga.

## Diseno de referencia (`_reference/loader/`)

- Sector circular: 8 gajos del logo (clip-path) que vuelan desde fuera hacia el centro y se ensamblan.
- Chispas doradas (`#d4a017`) en 6 posiciones absolutas que se alejan al final.
- Texto "Cargando sistema" + tres puntos animados en bucle.
- Soporte `prefers-reduced-motion`.
- Sin fondo: solo blanco (`#ffffff`).

## Riesgos

- UX: el loader aparece solo si la carga es >300ms para evitar parpadeo. Para demoras largas se mantiene visible todo el tiempo real.
- Performance: el logo se clona 8 veces por el sector. Verificar que `clip-path` no degrade en navegadores antiguos (aceptable: el target es Vite + navegadores modernos).
- Branding: respetar logo del proyecto (`/img/Logo-comunidad/Logo-principal.png`).
- Accesibilidad: `role="status"`, `aria-label`, `prefers-reduced-motion`.

## Skills recomendadas

- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`

## Recomendacion

1. Crear un componente base `LoadingScreen` mejorado que combine lo mejor de ambos (fondo blanco limpio, sectores del logo, chispas, dots, texto).
2. Crear un `PageLoader` in-page que reutilice la misma estetica con un wrapper no fullscreen.
3. Crear `useDelayedLoading(loading, delayMs)` que devuelva `true` cuando `loading` lleva mas de `delayMs` activo, para no parpadear.
4. Reemplazar loaders puntuales en paginas publicas y admin, conservando el `admin-loading` solo en zonas donde el `FaSpinner` se usa por consistencia minima.
5. En `App.jsx`, esperar a `window.load` + un minimo de 400ms para que el splash no parpadee.

## Verificacion sugerida

- `npm run build` en `comunidad_zapotal_frontend/`.
- `npm run lint`.
- Smoke test: abrir `/`, `/noticias`, `/eventos`, `/noticias/:id`, `/eventos/:id`, `/autoridades`, `/admin` con throttling 3G y observar el loader.
