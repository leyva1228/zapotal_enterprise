# Post-Implementation Review: Fix pantalla en blanco en detalle noticia/evento

## Estado

- Fecha: 2026-06-28
- Tecnologia: Frontend React (comunidad_zapotal_frontend)
- Tarea: arreglar `TypeError: principales.map is not a function` en `DetalleNoticia` y `DetalleEvento`.

## Resumen

Bug preexistente: dentro de un `useMemo` que destructuraba `principales` se hacia `principales: obtenerComentariosOrdenados` (la funcion) en lugar de `principales: obtenerComentariosOrdenados()` (el array). Cuando la noticia/evento tiene 0 comentarios, el `length` de la funcion (= 0) hacia entrar al branch `sin-comentarios` y no crasheaba; al haber >=1 comentario, `.map` reventaba y la pantalla quedaba en blanco.

## Archivos modificados

- `src/pages/Noticias/DetalleNoticia.jsx`: dentro del `useMemo` que produce `{ multimedia, principales, ... }`, reemplazar `principales: obtenerComentariosOrdenados` por `principales: obtenerComentariosOrdenados()`. Tambien se removio la variable local sin uso `const princ = ...`.
- `src/pages/Eventos/DetalleEvento.jsx`: mismo cambio.

## Verificacion ejecutada

- `npm run build` PASS (frontend).
- Backend endpoints OK: `GET /api/v1/noticias/58/`, `GET /api/v1/noticias/58/relacionadas/`, `GET /api/v1/eventos/34/relacionados/`.

## Resultado

PASS

## Riesgos remanentes

- Ninguno. El fix es de una sola linea en cada archivo y solo afecta el calculo del array de comentarios principales.

## Regresiones observadas

- Ninguna.
