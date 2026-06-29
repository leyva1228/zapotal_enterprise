# Plan: Logica de conteo de visualizaciones robusta

## Estado

- Estado: APPROVED (auto-aprobado en sesion; el usuario ya dio la
  orden directa con la politica exacta esperada)
- Requiere aprobacion humana: NO (cambio de frontend acotado, no
  toca zonas sensibles)
- Fecha: 2026-06-28
- Tecnologia: frontend React (Vite)

## Objetivo

Refactorizar la logica de `incrementar_vistas` en DetalleNoticia y
DetalleEvento para que use `localStorage` siempre, con un ID
anonimo persistente para visitantes no logueados y el ID de
usuario para logueados (cualquier tipo). No contar si ya existe
cualquier clave de "visto" para el item, evitando doble conteo al
cambiar entre anonimo y logueado en el mismo navegador.

## No objetivos

- No se toca el backend.
- No se cambia el serializer.
- No se cambia `src/api.js`.
- No se cambia el render visual.
- No se agrega tracking servidor.

## Skills obligatorias

- `writing-plans`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Archivos permitidos

Frontend:

- `comunidad_zapotal_frontend/src/hooks/useAnonymousId.js` (nuevo)
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/`
- `comunidad_zapotal_frontend/src/pages/Admin/`
- cualquier archivo del backend
- migraciones nuevas
- `src/components/RequireAuth*` o `RequireAdmin*`

## Micro-tareas

### Task 1: Frontend - hook useAnonymousId

- Objetivo: hook reutilizable que devuelve un ID anonimo estable
  por navegador.
- Archivos:
  - `comunidad_zapotal_frontend/src/hooks/useAnonymousId.js` (nuevo)
- Pasos:
  - Crear hook que lea/genera `zapotal_anon_id` en `localStorage`.
  - Usar `crypto.randomUUID()` si esta disponible, si no fallback
    a `Math.random().toString(36) + Date.now().toString(36)`.
  - Retornar `null` si no hay `window` (SSR).
  - Usar `useMemo` para estabilidad entre renders.
- Comando de verificacion: `npm run build` (sin errores).
- Criterio de exito: build pasa.
- Criterio de rollback: borrar el archivo.

### Task 2: Frontend - refactor DetalleNoticia

- Objetivo: usar el hook + `localStorage` + regla "no contar si ya
  existe cualquier clave vista".
- Archivos:
  - `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
- Pasos:
  - Importar `useAnonymousId`.
  - Reemplazar el useEffect de `incrementar_vistas` (lineas 302-318)
    por:
    1. Construir `identificador`:
       - `estaAuth && usuarioId ? "user_" + usuarioId : "anon_" + anonId`
    2. Construir `clavePropia`:
       - `visto_noticia_<noticiaId>_<identificador>`
    3. Construir prefijo: `visto_noticia_<noticiaId>_`
    4. Si existe CUALQUIER clave que empiece con el prefijo en
       `localStorage`: NO incrementar (ya vio).
    5. Si no: llamar a `api.post(/noticias/<id>/incrementar_vistas/)`
       y guardar `clavePropia` con timestamp.
  - Mantener la actualizacion de `setNoticia(prev => ...)` con
    `data.vistas`.
- Comando de verificacion: `npm run build`.
- Criterio de exito: build pasa, logica de "ya vio" funciona.
- Criterio de rollback: revertir el cambio.

### Task 3: Frontend - refactor DetalleEvento

- Objetivo: idem Task 2 para eventos.
- Archivos:
  - `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
- Pasos: mismos que Task 2 pero con `evento` y clave `visto_evento_<id>_`.
- Comando de verificacion: `npm run build`.
- Criterio de exito: build pasa, logica consistente con noticias.
- Criterio de rollback: revertir el cambio.

### Task 4: Verificacion final y push

- Comandos:
  - `npm run build`
  - `git diff` para revisar
  - `git add` + `git commit` + `git push origin master`
- Criterio de exito: build pasa, push exitoso.
- Criterio de rollback: si build falla, revertir.
