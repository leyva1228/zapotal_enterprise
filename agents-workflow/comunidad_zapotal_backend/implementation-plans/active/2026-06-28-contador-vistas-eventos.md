# Plan: Contador de visualizaciones en detalle de eventos

## Estado

- Estado: APPROVED (auto-aprobado en sesion; el usuario ya dio la
  orden directa de reutilizar el patron del detalle de noticias)
- Requiere aprobacion humana: NO (tarea acotada, no toca zonas
  sensibles: `apps/accounts/`, `apps/core/`, `apps/donaciones/`,
  `zapotal_config/settings.py`, mobile/BFF, auth, permisos, tokens,
  frontend funcional)
- Fecha: 2026-06-28
- Tecnologia: backend Django + frontend React (Vite)

## Objetivo

Reutilizar el patron de conteo de visualizaciones del detalle de
noticias en el detalle de eventos, exponiendo el campo `vistas` en
los serializers de evento que el frontend ya consume.

## No objetivos

- No se modifica la logica de `incrementar_vistas` (ya es correcta).
- No se modifica el frontend (ya esta implementado).
- No se migra la base de datos.
- No se tocan permisos, auth, tokens ni settings.
- No se cambia la app Android, el BFF Spring Boot ni el gateway.
- No se cambia `src/api.js`.

## Skills obligatorias

- `writing-plans`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Archivos permitidos

Backend:

- `comunidad_zapotal_backend/apps/content/serializers.py`
- `comunidad_zapotal_backend/apps/content/tests.py`

Frontend: ninguno (la logica ya esta implementada y se activa sola
al recibir el campo `vistas` del backend).

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_backend/apps/accounts/`
- `comunidad_zapotal_backend/apps/core/`
- `comunidad_zapotal_backend/apps/donaciones/`
- `comunidad_zapotal_backend/zapotal_config/settings.py`
- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/`
- `comunidad_zapotal_mobilebff_and_mobile_old/zapotal-gateway/src/`
- `comunidad_zapotal_mobilebff_and_mobile_old/ComunidadZapotal3/app/`
- cualquier migracion nueva
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  (NO se toca: la logica ya funciona y se reutiliza tal cual para
  eventos)

## Micro-tareas

### Task 1: Backend - agregar `vistas` a EventoSerializer

- Objetivo: que el detalle de evento exponga el campo `vistas` al
  frontend, igual que el detalle de noticia.
- Archivos:
  - `comunidad_zapotal_backend/apps/content/serializers.py`
- Pasos:
  - En `EventoSerializer.Meta.fields`, agregar `'vistas'` despues de
    `'total_comentarios'` (o donde encaje mejor con el resto de
    campos).
  - NO agregar a `read_only_fields`: `vistas` es un campo del modelo
    que solo se incrementa via el endpoint dedicado, pero el
    serializer ya lo expone en lectura por estar en `fields`.
    Dejarlo asi (consistente con `NoticiaSerializer`, que tampoco
    lo lista en `read_only_fields`).
- Comando de verificacion: `python -c "from apps.content.serializers import EventoSerializer; print('vistas' in EventoSerializer.Meta.fields)"`
- Criterio de exito: `vistas` aparece en `EventoSerializer.Meta.fields`.
- Criterio de rollback: revertir el cambio en `serializers.py`.

### Task 2: Backend - agregar `vistas` a EventoRelacionadoSerializer

- Objetivo: consistencia con `NoticiaRelacionadaSerializer` (que ya
  incluye `vistas`).
- Archivos:
  - `comunidad_zapotal_backend/apps/content/serializers.py`
- Pasos:
  - En `EventoRelacionadoSerializer.Meta.fields`, agregar `'vistas'`
    despues de `'imagen_url'` (o donde encaje mejor).
- Comando de verificacion: idem Task 1.
- Criterio de exito: `vistas` aparece en
  `EventoRelacionadoSerializer.Meta.fields`.
- Criterio de rollback: revertir el cambio en `serializers.py`.

### Task 3: Backend - tests para el contador de eventos

- Objetivo: cubrir el flujo de vistas en eventos con tests minimos.
- Archivos:
  - `comunidad_zapotal_backend/apps/content/tests.py`
- Pasos:
  - `test_detalle_evento_incluye_vistas`: `GET /eventos/<pk>/` debe
    incluir `vistas` en el payload. Idem para la ruta singular
    `/evento/detalle/<pk>/`.
  - `test_incrementar_vistas_evento_atomic`: `POST /eventos/<pk>/incrementar_vistas/`
    debe incrementar el contador en 1 y devolver el nuevo valor.
    Idem para la ruta singular.
  - `test_relacionados_evento_incluye_vistas`: `GET /evento/detalle/<pk>/relacionados/`
    debe incluir `vistas` en los items.
- Comando de verificacion: `python -m pytest apps/content -q`.
- Criterio de exito: todos los tests pasan (los nuevos + los 14
  existentes).
- Criterio de rollback: revertir el cambio en `tests.py`.

### Task 4: Verificacion final

- Objetivo: ejecutar todos los comandos de verificacion y reportar.
- Comandos:
  - `python manage.py check` (backend)
  - `python -m pytest apps/content -q` (backend)
  - Smoke test con curl (si el server esta corriendo):
    - `curl -s http://127.0.0.1:8000/api/v1/eventos/1/ | python -c "import json,sys; print('vistas:', json.load(sys.stdin).get('vistas'))"`
    - `curl -s -X POST http://127.0.0.1:8000/api/v1/eventos/1/incrementar_vistas/ | python -c "import json,sys; print('vistas:', json.load(sys.stdin).get('vistas'))"`
  - Verificacion de no-regresion: `npm run build` (frontend, aunque
    no se toca, para asegurar que nada se rompio).
- Criterio de exito: todo en verde, `vistas` presente en respuestas
  de evento.
- Criterio de rollback: si algun test falla 2 veces por causa no
  relacionada, detenerse y reportar.
