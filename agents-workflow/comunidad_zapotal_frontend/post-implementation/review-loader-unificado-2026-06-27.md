# Post-Implementation Review: LoadingScreen unificado con duracion real

## Estado

- Fecha: 2026-06-27
- Tecnologia: Frontend React (comunidad_zapotal_frontend)
- Plan relacionado: `agents-workflow/comunidad_zapotal_frontend/implementation-plans/plan-loader-unificado-2026-06-27.md`
- Audit relacionado: `agents-workflow/comunidad_zapotal_frontend/audits/active/audit-loader-unificado-2026-06-27.md`
- Task o lote relacionado: Task 1-6 (loader unificado)

## Resumen

Se unifico el loader del proyecto al modelo de referencia `_reference/loader/` (sectores del logo + chispas + dots) y se ancla la duracion del splash al evento real `window.load` con un minimo visible para evitar parpadeo. Se creo un `PageLoader` reutilizable para secciones internas y se reemplazo el loader puntual de paginas publicas (Noticias, Eventos, Detalles, Autoridades, Buscar).

## Archivos creados

- `src/hooks/useDelayedLoading.js` — hook para mostrar loader solo si la carga supera N ms.
- `src/components/common/PageLoader/PageLoader.jsx` — componente in-page con anillo, logo central, chispas y dots.
- `src/components/common/PageLoader/PageLoader.css` — estilos con soporte `prefers-reduced-motion`.

## Archivos modificados

- `src/pages/LoadingScreen/LoadingScreen.jsx` — reescrito segun el modelo de referencia.
- `src/pages/LoadingScreen/LoadingScreen.css` — reescrito con 8 sectores + 6 chispas + dots.
- `src/App.jsx` — splash anclado a `window.load` con minimo de 400ms y fallback 8s.
- `src/pages/Noticias/Noticias.jsx` — usa `PageLoader`.
- `src/pages/Noticias/Noticias.css` — clases `.loader-*` removidas.
- `src/pages/Eventos/Eventos.jsx` — usa `PageLoader`; bug de import `mdicons/react` corregido a `react-icons/md`.
- `src/pages/Eventos/Eventos.css` — clases de carga removidas.
- `src/pages/Noticias/DetalleNoticia.jsx` — usa `PageLoader`.
- `src/pages/Noticias/DetalleNoticia.css` — `.loading-container`/`.loading-spinner` removidos.
- `src/pages/Eventos/DetalleEvento.jsx` — usa `PageLoader`.
- `src/pages/Autoridades/AutoridadesPage.jsx` — usa `PageLoader`.
- `src/pages/Autoridades/AutoridadesPage.css` — `.au-loading-spinner` removido.
- `src/components/Autoridades/Autoridades.jsx` — usa `PageLoader`.
- `src/components/Autoridades/Autoridades.css` — `.loading-spinner` removido.
- `src/pages/Buscar/Buscar.jsx` — usa `PageLoader`; import `FaRedo` sin uso removido.
- `src/pages/Buscar/Buscar.css` — `.buscar-loading` y `.spin` removidos.

## Verificacion ejecutada

- `npm run build` — PASS (248 modulos, ~16s, sin errores).
- `npm run dev` — Vite arranca limpio en http://localhost:5173.
- `npm run lint` — no ejecutable: eslint no esta instalado en `node_modules` (problema preexistente del repo, no introducido por esta tarea).

## Resultado

PASS

## Riesgos remanentes

- El `useDelayedLoading` no se utilizo dentro de `App.jsx` (se opto por un setTimeout con minimo 400ms directo) por simplicidad y para evitar doble render. Queda disponible para futuros loaders in-page que necesiten anti-parpadeo.
- Los loaders del admin (`admin-loading` con `FaSpinner`) no se migraron en este lote para mantener el alcance acotado. Quedan como mejora futura.
- El `LoadingScreen` y `PageLoader` son componentes independientes; si se requiere una sola fuente de diseno, se puede refactorizar `PageLoader` para reutilizar los sectores del reference. Se decidio no hacerlo para evitar acoplamiento.

## Regresiones observadas

- Ninguna en build/dev server.
- Se corrigio una regresion preexistente en `Eventos.jsx`: import roto `import { MdLocationOn } from "mdicons/react"` → `react-icons/md`.

## Proximos pasos

- Migrar loaders de `pages/Admin/*` a un spinner consistente (lote futuro).
- Configurar ESLint en el repo (problema operativo, no de codigo).
- Considerar throttling 3G real en Playwright para verificar la duracion del splash.
