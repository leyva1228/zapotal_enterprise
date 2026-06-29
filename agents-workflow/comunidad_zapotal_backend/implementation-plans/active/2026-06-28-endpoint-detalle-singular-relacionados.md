# Plan: Endpoint singular /detalle/ + relacionados por categoria

## Estado

- Estado: APPROVED (auto-aprobado en sesion; usuario ya dio la orden
  directa con la nomenclatura final esperada)
- Requiere aprobacion humana: NO (tarea acotada, no toca zonas
  sensibles: `apps/accounts/`, `apps/core/`, `apps/donaciones/`,
  `zapotal_config/settings.py`, mobile/BFF, auth, permisos, tokens)
- Fecha: 2026-06-28
- Tecnologia: backend Django + frontend React (Vite)

## Objetivo

Estandarizar la nomenclatura de los endpoints de detalle a singular con
sufijo `detalle/` y mejorar el endpoint de relacionados por categoria, sin
romper reacciones, comentarios ni favoritos.

## No objetivos

- No se elimina ninguna ruta plural existente.
- No se migra la base de datos.
- No se tocan permisos, auth, tokens ni settings.
- No se modifica la app Android, el BFF Spring Boot ni el gateway.
- No se cambia el diseno visual del sidebar mas alla de aceptar
  `linkBase` configurable (parametro ya soportado, solo se documenta).
- No se cambia `src/api.js`.

## Skills obligatorias

- `writing-plans`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Archivos permitidos

Backend:

- `comunidad_zapotal_backend/apps/content/urls.py`
- `comunidad_zapotal_backend/apps/content/views.py`
- `comunidad_zapotal_backend/apps/content/tests.py`

Frontend:

- `comunidad_zapotal_frontend/src/App.jsx`
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
- `comunidad_zapotal_frontend/src/components/common/RelacionadosSidebar/RelacionadosSidebar.jsx`

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

## Micro-tareas

### Task 1: Backend - agregar rutas singulares con /detalle/

- Objetivo: exponer `/noticia/detalle/<pk>/` y `/evento/detalle/<pk>/`
  con la misma semantica que las rutas plurales actuales.
- Archivos:
  - `comunidad_zapotal_backend/apps/content/urls.py`
- Pasos:
  - declarar `app_name = 'content'` y `basename` por si se usan en reverse
  - registrar `NoticiaViewSet` y `EventoViewSet` con basename singular
    (`noticia` y `evento`) en un DefaultRouter paralelo, o agregar rutas
    `path()` explicitas. Decision: usar rutas `path()` explicitas
    montando el viewset con `as_view({...})` para no chocar con los
    basenames plurales.
  - mapear las acciones:
    `noticia/detalle/<pk>/` -> `retrieve`
    `noticia/detalle/<pk>/relacionadas/` -> `relacionadas`
    `noticia/detalle/<pk>/comentarios/` -> `comentarios`
    `noticia/detalle/<pk>/incrementar_vistas/` -> `incrementar_vistas`
  - idem para evento (`relacionados` en vez de `relacionadas`).
- Comando de verificacion: `python manage.py check` y curl manual.
- Criterio de exito: las 4 rutas singulares por entidad responden
  correctamente, las rutas plurales siguen respondiendo.
- Criterio de rollback: revertir el cambio en `urls.py`.

### Task 2: Backend - mejorar relacionadas con filtro ?categoria=

- Objetivo: permitir filtrar el endpoint de relacionadas por una
  categoria especifica via query param, sin romper la logica por
  defecto.
- Archivos:
  - `comunidad_zapotal_backend/apps/content/views.py`
- Pasos:
  - en `NoticiaViewSet.relacionadas`:
    - leer `request.query_params.get('categoria')` (acepta id numerico)
    - si viene, override: traer hasta `limit` (5) noticias de esa
      categoria, publicas y distintas de la noticia base
    - si no viene, mantener la logica actual
  - idem para `EventoViewSet.relacionados`
  - actualizar la firma interna `_agrupar_por_categoria` para que reciba
    un parametro `categoria_filtro` opcional
- Comando de verificacion: pytest del modulo `apps/content`.
- Criterio de exito: el endpoint sigue funcionando como antes y ademas
  acepta `?categoria=<id>` devolviendo solo items de esa categoria.
- Criterio de rollback: revertir el cambio en `views.py`.

### Task 3: Backend - tests para los nuevos endpoints

- Objetivo: cubrir los nuevos endpoints con tests minimos.
- Archivos:
  - `comunidad_zapotal_backend/apps/content/tests.py`
- Pasos:
  - `test_detalle_singular_noticia`: `GET /noticia/detalle/<pk>/`
    debe funcionar y devolver 200 publico.
  - `test_detalle_singular_evento`: idem.
  - `test_relacionadas_singular`: `GET /noticia/detalle/<pk>/relacionadas/`
    debe devolver 200 publico.
  - `test_relacionadas_filtro_categoria`: con `?categoria=<id>` solo
    trae items de esa categoria.
  - `test_relacionados_singular`: idem para evento.
- Comando de verificacion: `python -m pytest apps/content -q`.
- Criterio de exito: todos los tests pasan.
- Criterio de rollback: revertir el cambio en `tests.py`.

### Task 4: Frontend - rutas y consumir endpoint singular

- Objetivo: agregar las nuevas rutas en el App.jsx, hacer que
  `DetalleNoticia` y `DetalleEvento` consuman el endpoint singular,
  manteniendo las rutas plurales como alias.
- Archivos:
  - `comunidad_zapotal_frontend/src/App.jsx`
  - `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  - `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
- Pasos:
  - en `App.jsx`: agregar `<Route path="/noticia/detalle/:id">` y
    `<Route path="/evento/detalle/:id">` con los mismos componentes
    `DetalleNoticia` y `DetalleEvento`. Actualizar el handler del
    breadcrumb para reconocer `/noticia/detalle/:id` y
    `/evento/detalle/:id` ademas de los plurales.
  - en `DetalleNoticia.jsx`: cambiar la URL de relacionadas a
    `/noticia/detalle/${noticiaId}/relacionadas/` (debe seguir
    funcionando el endpoint). Dejar la llamada al detalle igual
    (`/noticias/${noticiaId}/`) porque el endpoint de detalle por id
    numerico es estable.
  - idem para `DetalleEvento.jsx` (`/evento/detalle/<id>/relacionados/`).
  - reaciones, comentarios y favoritos: NO se tocan.
- Comando de verificacion: `npm run build` + `npm run lint`.
- Criterio de exito: la pagina de detalle carga, la sidebar muestra
  las relacionadas, y los endpoints de reacciones/comentarios/favoritos
  siguen disparandose.
- Criterio de rollback: revertir los 3 archivos.

### Task 5: Frontend - RelacionadosSidebar con linkBase singular

- Objetivo: la sidebar debe generar links consistentes con la
  nomenclatura nueva cuando el componente padre asi lo indique.
- Archivos:
  - `comunidad_zapotal_frontend/src/components/common/RelacionadosSidebar/RelacionadosSidebar.jsx`
- Pasos:
  - el prop `linkBase` ya esta implementado; verificar que el default
    siga siendo `"/"` (no rompe nada)
  - en `DetalleNoticia.jsx`: pasar `linkBase="/noticia/detalle/"` y
    `linkBase="/noticias/"` (mantener el plural como fallback si la
    nueva ruta devolviera error)
  - en `DetalleEvento.jsx`: idem (`/evento/detalle/` y `/eventos/`)
  - decision: pasar siempre la ruta singular nueva porque el sidebar
    es solo cosmetico, no afecta carga de datos.
- Comando de verificacion: `npm run build` + `npm run lint`.
- Criterio de exito: la sidebar genera links a la nueva ruta.
- Criterio de rollback: revertir el prop en el componente padre.

### Task 6: Verificacion final

- Objetivo: ejecutar todos los comandos de verificacion y reportar
  resultados.
- Comandos:
  - `python manage.py check` (backend)
  - `python -m pytest apps/content -q` (backend)
  - `ruff check apps/content` (backend)
  - `npm run build` (frontend)
  - `npm run lint` (frontend)
- Criterio de exito: todo en verde.
- Criterio de rollback: si algun test falla 2 veces por causa no
  relacionada, detenerse y reportar.
