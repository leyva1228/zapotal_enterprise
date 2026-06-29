# Audit: Endpoint de detalle singular + relacionados por categoria

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Autor/agente: opencode-go/minimax-m3
- Tecnologia: backend Django + frontend React (Vite)

## Objetivo

Estandarizar la nomenclatura de los endpoints de detalle a singular con sufijo
`detalle/` (es decir `/noticia/detalle/{id}/` y `/evento/detalle/{id}/`),
mejorar el endpoint de noticias relacionadas por categoria y asegurar que
la sidebar derecha del detalle muestre relacionadas por categoria sin romper
reacciones, comentarios ni favoritos.

## Alcance

### Incluye

Backend (Django + DRF):

- `comunidad_zapotal_backend/apps/content/urls.py`
  - agregar rutas singulares `noticia/detalle/<pk>/` y `evento/detalle/<pk>/`
  - agregar ruta singular de relacionadas:
    `noticia/detalle/<pk>/relacionadas/` y `evento/detalle/<pk>/relacionados/`
- `comunidad_zapotal_backend/apps/content/views.py`
  - mejorar `NoticiaViewSet.relacionadas` y `EventoViewSet.relacionados`
    para soportar filtro opcional por `?categoria=<id>` y mantener logica
    actual cuando no se envie query string
- `comunidad_zapotal_backend/apps/content/tests.py`
  - tests para los nuevos endpoints singulares
  - test para el endpoint de relacionadas con filtro por categoria

Frontend (React + Vite):

- `comunidad_zapotal_frontend/src/App.jsx`
  - agregar rutas `/noticia/detalle/:id` y `/evento/detalle/:id`
  - mantener compatibilidad con `/noticias/:id` y `/eventos/:id`
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  - detectar el parametro `id` (compatible con la nueva ruta)
  - consumir la nueva ruta singular de relacionadas
  - mantener logica existente de reacciones, comentarios y favoritos
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  - idem para eventos
- `comunidad_zapotal_frontend/src/components/common/RelacionadosSidebar/RelacionadosSidebar.jsx`
  - aceptar prop `linkBase` con default `'/noticias/'` y `'/eventos/'`
  - agregar soporte para `linkBase='/noticia/detalle/'` (singular) sin tocar
    consumidores actuales
- `comunidad_zapotal_frontend/src/components/Breadcrumb.jsx` (o el handler
  inline en `App.jsx`) - actualizar paths para reconocer la nueva ruta
  singular de detalle

### No incluye

- cambios en el modelo de datos (sin migracion)
- cambios en permisos o auth
- cambios en `apps/accounts/`, `apps/core/`, `apps/donaciones/`
- cambios en `src/api.js`
- cambios en la app mobile o en el BFF Spring Boot
- refactor del sidebar a otro componente distinto
- cualquier modificacion al diseno visual de la sidebar mas alla de lo
  estrictamente necesario para mostrar la categoria de la noticia relacionada

## Contexto leido

- `AGENTS.md` (raiz)
- `graphify.md` (raiz)
- `comunidad_zapotal_backend/AGENTS.md`
- `comunidad_zapotal_backend/graphify/GRAPH_REPORT.md`
- `comunidad_zapotal_frontend/AGENTS.md`
- `comunidad_zapotal_frontend/graphify/GRAPH_REPORT.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/templates/implementation-plan-template.md`
- `agents-workflow/AGENTS.md`

Archivos inspeccionados (lectura):

- `comunidad_zapotal_backend/apps/content/urls.py`
- `comunidad_zapotal_backend/apps/content/views.py`
- `comunidad_zapotal_backend/apps/content/serializers.py`
- `comunidad_zapotal_backend/apps/content/models.py`
- `comunidad_zapotal_backend/apps/content/tests.py`
- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/App.jsx`
- `comunidad_zapotal_frontend/src/components/common/RelacionadosSidebar/RelacionadosSidebar.jsx`
- `comunidad_zapotal_frontend/src/components/common/RelacionadosSidebar/RelacionadosSidebar.css`
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`

## Estado actual

Backend (Django + DRF):

- Rutas plurales existentes (NO se eliminan):
  - `GET /api/v1/noticias/<pk>/` y `GET /api/v1/eventos/<pk>/`
  - `GET /api/v1/noticias/<pk>/relacionadas/` y
    `GET /api/v1/eventos/<pk>/relacionados/`
  - `GET /api/v1/noticias/<pk>/comentarios/`
  - `POST /api/v1/noticias/<pk>/incrementar_vistas/`
- ViewSets con acciones custom: `NoticiaViewSet.relacionadas` y
  `EventoViewSet.relacionados`. Logica: trae hasta 5 de la categoria del
  item base, completa con hasta 3 de otras categorias. Devuelve shape
  `{ grupos: [{ categoria, label, items: [...] }] }`.
- Tests existentes: `TestNoticiaViewSet.test_relacionadas_endpoint`
  verifica que el endpoint sea publico.

Frontend (React + Vite):

- Rutas plurales: `/noticias/:id` y `/eventos/:id` (App.jsx).
- Breadcrumb reconoce `/noticias/<id>` y `/eventos/<id>`.
- `DetalleNoticia.jsx` y `DetalleEvento.jsx` consumen:
  - `GET /noticias/<id>/` y `GET /eventos/<id>/`
  - `POST /noticias/<id>/incrementar_vistas/` y
    `POST /eventos/<id>/incrementar_vistas/`
  - `GET /noticias/<id>/relacionadas/` y
    `GET /eventos/<id>/relacionados/`
  - logica completa de reacciones, comentarios, favoritos
- `RelacionadosSidebar` recibe `linkBase` (`/noticias/` o `/eventos/`) y
  construye `<Link to={`${linkBase}${item.id}`}>`.

## Riesgos

- Contratos API: agregar endpoints nuevos sin eliminar los antiguos
  mantiene compatibilidad. La guia de workflow senala
  "No cambiar contratos API sin revisar consumidores y documentarlo".
  Decisión: agregar (no renombrar). Los consumidores existentes no se
  tocan.
- UX: la sidebar solo aparece si `relacionadas.grupos.length > 0` o
  `relacionados.grupos.length > 0`. Si la nueva ruta singular no devuelve
  datos, la sidebar se oculta igual que antes.
- Performance: las consultas a `relacionadas` y `relacionados` ya estan
  optimizadas (`select_related` + `prefetch_related` en el queryset
  base). Agregar filtro opcional por `categoria` no agrega joins
  adicionales.
- Mobile: la app Android (BFF Spring Boot) y el gateway son zonas
  sensibles listadas en AGENTS.md. No se tocan.
- Migraciones: no se modifica el modelo. No hay migraciones nuevas.

## Skills recomendadas

- `django-expert`
- `api-and-interface-design`
- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Recomendacion

1. Mantener las rutas plurales existentes para no romper consumidores
   (admin, mobile, tests, frontend legacy).
2. Agregar rutas singulares con `detalle/` y reusar el mismo ViewSet
   (`NoticiaViewSet`, `EventoViewSet`) para que las acciones
   `relacionadas` / `relacionados` queden disponibles con ambas
   nomenclaturas.
3. Agregar query param opcional `?categoria=<id>` al endpoint
   de relacionadas para permitir filtrar por categoria sin necesidad de
   reimplementar la logica.
4. En el frontend, agregar las nuevas rutas en `App.jsx` y mantener
   compatibilidad con las plurales. La sidebar debe seguir funcionando
   con `linkBase` configurable para soportar ambas formas.
5. Reacciones, comentarios y favoritos: NO se tocan. Las APIs y la
   logica de envio existente siguen exactamente iguales.

## Verificacion sugerida

Backend:

```bash
python manage.py check
python -m pytest apps/content -q
ruff check apps/content
```

Frontend:

```bash
npm run build
npm run lint
```

Verificacion manual con curl (contra el servidor local):

```bash
curl -s http://127.0.0.1:8000/api/v1/noticia/detalle/1/ | head
curl -s http://127.0.0.1:8000/api/v1/noticia/detalle/1/relacionadas/ | head
curl -s 'http://127.0.0.1:8000/api/v1/noticia/detalle/1/relacionadas/?categoria=2' | head
curl -s http://127.0.0.1:8000/api/v1/evento/detalle/1/ | head
curl -s http://127.0.0.1:8000/api/v1/evento/detalle/1/relacionados/ | head
```

Rutas plurales existentes (regression):

```bash
curl -s http://127.0.0.1:8000/api/v1/noticias/1/ | head
curl -s http://127.0.0.1:8000/api/v1/noticias/1/relacionadas/ | head
```
