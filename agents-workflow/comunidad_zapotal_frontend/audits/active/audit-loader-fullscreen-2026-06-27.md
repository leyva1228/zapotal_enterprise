# Audit: Loader global fullscreen bajo navbar con cobertura de paginas y secciones

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-27
- Autor/agente: opencode (Minimax-M3)
- Tecnologia: Frontend React (comunidad_zapotal_frontend)

## Objetivo

Hacer que el loader unificado:
1. Aparezca en TODAS las paginas y secciones, no solo en la carga inicial.
2. Ocupe toda la pantalla DESPUES del navbar (no cubra el navbar).
3. Bloquee la interaccion y el scroll mientras carga.
4. Se desbloquee automaticamente cuando la pagina termine de cargar.
5. Ancle su duracion al tiempo real de carga (no a un timeout fijo).

## Alcance

### Incluye

- Nuevo `LoaderContext` con `useLoader()` para que paginas/secciones avisen inicio/fin de carga.
- Nuevo `RouteChangeLoader` que detecta cambios de ruta y muestra el loader hasta el siguiente tick (cubre navegacion instantanea).
- Refactor del `App.jsx`:
  - Mover el splash inicial a un overlay DENTRO del provider de rutas, debajo del navbar.
  - Listener de `window.load` + minimo visible 400ms.
  - Bloqueo de scroll global mientras `isLoading`.
- `PageLoader` actualizado: nueva variante `overlay` que cubre el area debajo del navbar y bloquea interacciones.
- Aplicar `useLoader` en paginas publicas con fetch: `Noticias`, `Eventos`, `DetalleNoticia`, `DetalleEvento`, `AutoridadesPage`, `Autoridades`, `Buscar`, `Home` (si tiene fetch futuro), y admin pages.
- CSS: capa fullscreen bajo navbar (z-index mayor que contenido, menor que navbar). Posicionar via `top: var(--navbar-height, 96px)` o `bottom: 0` con `top: 0` solo si no hay navbar.
- `useDelayedLoading` ya creado en el lote anterior queda como base; se reemplaza por el context.

### No incluye

- Reescribir loaders internos de inputs/botones.
- Modificar contratos API.
- Modificar `RequireAuth*` / `RequireAdmin*` (zonas sensibles — solo se observan).
- Modificar `src/api.js` o contexts existentes.

## Contexto leido

- `comunidad_zapotal_frontend/AGENTS.md`
- `graphify.md`
- `comunidad_zapotal_frontend/src/components/Navbar.css` (navbar `position: fixed`, `var(--navbar-height)`)
- `comunidad_zapotal_frontend/src/App.jsx`
- `comunidad_zapotal_frontend/src/pages/LoadingScreen/LoadingScreen.{jsx,css}`
- `comunidad_zapotal_frontend/src/components/common/PageLoader/{PageLoader.jsx,PageLoader.css}`
- `comunidad_zapotal_frontend/src/hooks/useDelayedLoading.js`
- Auditoria previa: `audits/active/audit-loader-unificado-2026-06-27.md`
- Plan previo: `implementation-plans/plan-loader-unificado-2026-06-27.md`

## Estado actual

- Splash inicial en `App.jsx` con `LoadingScreen` fullscreen (cubre navbar).
- `PageLoader` se usa como reemplazo puntual en paginas (variante `section` centrada, no fullscreen).
- No hay coordinacion entre paginas: cada una tiene su propio `loading` local.
- No hay bloqueo de scroll.
- No hay cobertura en cambios de ruta (al ir de `/` a `/noticias` no aparece loader).
- Admin pages usan `admin-loading` con `FaSpinner` (no migrado).

## Riesgos

- UX: un loader que parpadea en cada cambio de ruta es molesto. Mitigacion: `delayMs` minimo 250-300ms (anti-parpadeo) y duracion maxima por cambio (ej. 8s fallback).
- Performance: el context se monta en el nivel mas alto para que toda la app pueda leer/escribir.
- Compatibilidad: `var(--navbar-height)` ya esta en `:root`. Si en algunas rutas no hay navbar (login, admin), el overlay debe ignorar la altura.
- Z-index: navbar es `position: fixed` con z-index propio. Verificar que el overlay queda por debajo.

## Skills recomendadas

- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`

## Recomendacion

1. Crear `LoaderContext` + `useLoader()` + `<LoaderProvider>` con estado `isLoading` y un `delayMs` configurable.
2. Crear `RouteChangeLoader` que use `useLocation` y muestre el loader brevemente en cada cambio de ruta (con minimo 300ms y maximo 2500ms, con override por pagina si la pagina llama `useLoader().start()` / `stop()`).
3. Refactor de `App.jsx`:
   - Mover el splash inicial al provider.
   - Mostrar el loader global si `isLoading` es true, con `top: var(--navbar-height, 96px)`.
   - En rutas sin navbar, usar `top: 0`.
   - `body { overflow: hidden }` mientras carga.
4. Integrar `useLoader` en paginas publicas (envolver `setLoading(true)` y `setLoading(false)`).
5. Verificar build, dev server, smoke test manual.

## Verificacion sugerida

- `npm run build`
- `npm run dev` (arranque sin errores)
- Smoke test: abrir `/`, navegar a `/noticias`, `/eventos`, `/eventos/:id`, `/autoridades`, `/contactanos`, `/buscar`, `/admin` y observar el loader en cada transicion.
- Verificar con throttling 3G en DevTools que el loader no se cierra prematuramente.
