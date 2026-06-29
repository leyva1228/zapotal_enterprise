# Plan: LoadingScreen unificado con duracion real

## Estado

- Estado: APPROVED (auto-aprobado por el usuario al pedir la mejora)
- Requiere aprobacion humana: NO (mejora visual acotada, sin zonas sensibles)
- Fecha: 2026-06-27
- Tecnologia: Frontend React

## Objetivo

Unificar el loader del proyecto al modelo de referencia `_reference/loader/`, exponer un `PageLoader` reutilizable para secciones internas, eliminar los loaders puntuales incoherentes y anclar la duracion del splash al tiempo real de carga (con un minimo para evitar parpadeo).

## No objetivos

- No tocar `src/api.js`, `src/context/`, `RequireAuth*`, `RequireAdmin*`.
- No cambiar contratos API ni backend.
- No rehacer spinners de inputs/botones (rg-spinner, form-btn__loader, mapa-spinner).
- No rehacer el `admin-loading` interno de tablas (solo se reemplaza el splash de App.jsx y los loaders puntuales de pagina completa).

## Skills obligatorias

- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`

## Archivos permitidos

- `src/pages/LoadingScreen/LoadingScreen.jsx`
- `src/pages/LoadingScreen/LoadingScreen.css`
- `src/components/common/PageLoader/PageLoader.jsx` (nuevo)
- `src/components/common/PageLoader/PageLoader.css` (nuevo)
- `src/hooks/useDelayedLoading.js` (nuevo)
- `src/App.jsx`
- `src/pages/Noticias/Noticias.jsx`
- `src/pages/Noticias/Noticias.css` (solo remocion de clases obsoletas del loader)
- `src/pages/Eventos/Eventos.jsx`
- `src/pages/Eventos/Eventos.css` (solo remocion)
- `src/pages/Noticias/DetalleNoticia.jsx`
- `src/pages/Noticias/DetalleNoticia.css` (solo remocion)
- `src/pages/Eventos/DetalleEvento.jsx`
- `src/pages/Eventos/DetalleEvento.css` (solo remocion)
- `src/pages/Autoridades/AutoridadesPage.jsx`
- `src/pages/Autoridades/AutoridadesPage.css` (solo remocion)
- `src/components/Autoridades/Autoridades.jsx`
- `src/components/Autoridades/Autoridades.css` (solo remocion)
- `src/pages/Buscar/Buscar.jsx`
- `src/pages/Buscar/Buscar.css` (solo remocion)

## Archivos prohibidos sin nueva aprobacion

- `src/api.js`
- `src/context/AuthContext.jsx`
- `src/context/*` (cualquier context)
- `src/components/RequireAuth*`
- `src/components/RequireAdmin*`
- `src/pages/Admin/**` (solo se observa `admin-loading` existente; no se modifica Admin en este lote)
- `zapotal_config/**` o cualquier backend

## Micro-tareas

### Task 1: Crear hook `useDelayedLoading`

- Objetivo: hook que devuelve `true` solo si `loading` permanece activo por mas de `delayMs`.
- Archivos: `src/hooks/useDelayedLoading.js` (nuevo).
- Pasos:
  1. Crear archivo con implementacion minima usando `useState` + `useEffect` y `setTimeout`.
  2. Verificar que cuando `loading` cambia a `false` antes del delay, el estado interno vuelve a `false` inmediatamente.
- Comando de verificacion: `npm run build`.
- Criterio de exito: el hook compila sin warnings.
- Criterio de rollback: borrar el archivo.

### Task 2: Reescribir `LoadingScreen` con modelo del reference

- Objetivo: fusionar el diseno actual con sectores + chispas + dots.
- Archivos: `src/pages/LoadingScreen/LoadingScreen.{jsx,css}`.
- Pasos:
  1. Reescribir `LoadingScreen.jsx` con 8 sectores, 6 chispas y dots animados.
  2. Reescribir `LoadingScreen.css` con `@keyframes` del reference + `prefers-reduced-motion`.
  3. Conservar el fondo blanco y logo del proyecto.
- Comando de verificacion: `npm run build`, `npm run lint`.
- Criterio de exito: build y lint limpios.
- Criterio de rollback: `git checkout` del archivo.

### Task 3: Crear `PageLoader` reutilizable

- Objetivo: componente no fullscreen con la misma estetica para usar dentro de paginas.
- Archivos: `src/components/common/PageLoader/{PageLoader.jsx,PageLoader.css}` (nuevo).
- Pasos:
  1. Implementar `PageLoader` que reutilice el mismo logo y animacion reducida.
  2. Variante: prop `variant` (`"section"` centrado, `"page"` que ocupa viewport).
  3. Aceptar prop `mensaje` opcional.
- Comando de verificacion: `npm run build`.
- Criterio de exito: build limpio, componente importable.

### Task 4: Acoplar duracion del splash a carga real

- Objetivo: que `App.jsx` espere al evento `load` real con un minimo visible.
- Archivos: `src/App.jsx`.
- Pasos:
  1. Reemplazar el `setTimeout(1200)` por un hook que escucha `window.load` y aplica `useDelayedLoading` con minimo 400ms.
- Comando de verificacion: `npm run build`.
- Criterio de exito: build limpio, el splash no se cierra antes de que la pagina este lista.

### Task 5: Reemplazar loaders puntuales en paginas publicas

- Objetivo: usar `PageLoader` en lugar de los bloques locales.
- Archivos: `Noticias.jsx`, `Noticias.css`, `Eventos.jsx`, `Eventos.css`, `DetalleNoticia.jsx`, `DetalleNoticia.css`, `DetalleEvento.jsx`, `DetalleEvento.css`, `AutoridadesPage.jsx`, `AutoridadesPage.css`, `Autoridades.jsx`, `Autoridades.css`, `Buscar.jsx`, `Buscar.css`.
- Pasos:
  1. Reemplazar cada bloque de carga por `<PageLoader mensaje="..." />`.
  2. Eliminar de los CSS las clases del loader ya no usadas (mantener cualquier otra regla).
  3. Para `Buscar` (loader inline de busqueda) usar solo el componente pequeno o un spinner minimo.
- Comando de verificacion: `npm run build`, `npm run lint`.
- Criterio de exito: build limpio, las paginas no rompen layout.

### Task 6: Verificacion final

- Objetivo: validar build + lint + smoke test.
- Comandos: `npm run build`, `npm run lint`.
- Reportar resultados.
