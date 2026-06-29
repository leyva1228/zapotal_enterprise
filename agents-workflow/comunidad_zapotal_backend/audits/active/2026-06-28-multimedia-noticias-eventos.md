# Audit: Subida de multiples archivos multimedia en noticias y eventos

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Tecnologia: backend Django + frontend React (Vite)

## Objetivo

Permitir subir varios archivos multimedia (imagenes y videos)
tanto desde el panel de Django nativo como desde el panel
admin del frontend, tanto para noticias como para eventos.

## Estado actual (del diagnostico previo)

### Modelo
- `Multimedia` ya existe, permite tipo IMAGEN/VIDEO, FKs a
  Noticia y Evento (ambas nullable). Soporta multiple archivos.

### Serializer
- `MultimediaSerializer` existe y se usa como nested en
  `NoticiaSerializer` y `EventoSerializer` (read_only).
- `NoticiaEscrituraSerializer` y `EventoEscrituraSerializer`
  NO incluyen multimedia (solo imagen de portada).

### Admin Django
- `MultimediaInline` existe (extra=1, fields=['tipo', 'archivo']).
- `NoticiaAdmin` incluye `inlines = [MultimediaInline,
  ComentarioInline]` -> permite subir varios archivos en
  `/admin/content/noticia/<id>/change/`.
- `EventoAdmin` NO incluye `MultimediaInline` -> no se pueden
  agregar archivos desde el panel nativo de eventos.

### Frontend
- `AdminNoticias.jsx`: solo sube UNA imagen de portada
  (campo `imagen`, no la tabla `Multimedia`).
- `AdminEventos.jsx`: mismo problema.
- Ninguno permite subir varios archivos a la tabla
  `Multimedia`.

### Endpoints REST
- `MultimediaViewSet` existe (router `multimedias`), permite
  GET/POST/PUT/DELETE con IsAdminOrReadOnly + IsComuneroOrAdmin
  para escritura. SOPORTA la subida de archivos via REST.

## Alcance

### Incluye

Backend (1 archivo):

- `apps/content/admin.py`: agregar `MultimediaInline` a
  `EventoAdmin` para que `/admin/content/evento/<id>/change/`
  muestre el inline de archivos.

Frontend (3 archivos):

- `src/components/SubirMultimedia.jsx` (nuevo): componente
  reutilizable que permite:
  - Listar archivos ya subidos (de `Multimedia` con FK al item)
  - Subir varios archivos a la vez (`<input type="file" multiple>`)
  - Detectar tipo automaticamente (IMAGEN si mime empieza con
    `image/`, VIDEO si empieza con `video/`)
  - POST a `/api/v1/multimedias/` con FormData (campo `archivo`,
    FK `noticia` o `evento` segun el contexto, tipo)
  - DELETE de archivos (DELETE a `/api/v1/multimedias/<id>/`)
  - Preview de imagenes, icono para videos, tamano y nombre
  - Boton "Subir N archivos" que muestra el progreso
- `src/pages/Admin/AdminNoticias.jsx`: integrar `<SubirMultimedia>`
  debajo de los campos de la noticia. Cuando se edita una
  noticia existente, el componente se inicializa con los
  archivos ya subidos. Al crear una nueva, primero se guarda
  la noticia y luego se suben los archivos.
- `src/pages/Admin/AdminEventos.jsx`: idem para eventos.

## Estado actual vs deseado

| Accion | Antes | Despues |
|---|---|---|
| Subir 1 archivo (frontend) | Solo portada | Sin cambios |
| Subir N archivos (frontend) | NO se puede | Se puede via SubirMultimedia |
| Subir N archivos (Django admin, noticias) | Ya se puede | Sin cambios |
| Subir N archivos (Django admin, eventos) | NO se puede | Se agrega MultimediaInline |
| Ver galeria en detalle | OK | OK |
| Eliminar archivo de galeria | Solo Django admin | Frontend + Django admin |

## Recomendacion

1. Backend admin.py: agregar `MultimediaInline` a `EventoAdmin`.
2. Frontend: crear `<SubirMultimedia>` reutilizable.
3. Integrar en AdminNoticias y AdminEventos.
4. Verificar con Playwright.

## Verificacion

- `python manage.py check`: 0 issues.
- `python -m pytest apps/content`: tests existentes pasan.
- `npm run build`: sin errores.
- Playwright: ir a `/admin`, editar un evento, verificar que
  aparece el inline de multimedia. Luego ir al panel del
  frontend, editar el mismo evento, subir varios archivos,
  verificar que se guardan en `/api/v1/multimedias/` y
  aparecen en el detalle.
