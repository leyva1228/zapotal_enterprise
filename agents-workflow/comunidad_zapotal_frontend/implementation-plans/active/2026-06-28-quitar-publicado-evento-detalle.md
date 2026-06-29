# Plan: Quitar "Publicado:" del meta-row del detalle de evento

## Estado

- Estado: APPROVED (auto-aprobado en sesion; el usuario ya dio la
  orden directa con el ejemplo exacto del formato esperado)
- Requiere aprobacion humana: NO (cambio cosmético de una linea,
  sin tocar zonas sensibles)
- Fecha: 2026-06-28
- Tecnologia: frontend React (Vite)

## Objetivo

Igualar el meta-row inferior del detalle de evento al patron del
detalle de noticia: "👁 N visualizaciones  dd mmm yyyy" (sin
"Publicado:").

## No objetivos

- No se toca el backend.
- No se cambia el detalle de noticia (ya esta correcto).
- No se cambian CSS, iconos ni helpers.
- No se cambia el bloque verde superior con Fecha/Ubicacion.

## Skills obligatorias

- `writing-plans`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Archivos permitidos

- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/`
- cualquier archivo del backend
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  (referencia, no se modifica)

## Micro-tareas

### Task 1: Frontend - quitar prefijo "Publicado:"

- Objetivo: igualar el meta-row inferior del detalle de evento al
  patron del detalle de noticia.
- Archivos:
  - `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
- Pasos:
  - Linea 781: cambiar
    `<span className="yt-desc-fecha">Publicado: {formatFecha(evento.fecha)}</span>`
    por
    `<span className="yt-desc-fecha">{formatFecha(evento.fecha)}</span>`.
  - Verificacion visual: el render queda igual que el de noticias
    (ojo + visualizaciones + fecha).
- Comando de verificacion: `npm run build`.
- Criterio de exito: build pasa sin errores.
- Criterio de rollback: revertir el cambio en `DetalleEvento.jsx`.

### Task 2: Verificacion final y push

- Objetivo: confirmar que el cambio compila y subir a GitHub.
- Comandos:
  - `npm run build`
  - `git diff` para revisar el diff
  - `git add` + `git commit` + `git push origin master`
- Criterio de exito: build pasa, commit y push exitosos.
- Criterio de rollback: si el build falla, revertir el cambio.
