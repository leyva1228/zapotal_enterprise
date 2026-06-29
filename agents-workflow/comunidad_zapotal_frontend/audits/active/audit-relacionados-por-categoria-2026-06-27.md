# Audit: Relacionados por categoria en detalle de noticias y eventos

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-27
- Autor/agente: opencode (Minimax-M3)
- Tecnologia: Frontend React + Backend Django DRF (apps/content)

## Objetivo

Mostrar en la seccion lateral "relacionados" del detalle de noticia y del detalle de evento, los items agrupados por categoria, con su cabecera de categoria, sin perder la disposicion actual ni romper lo que ya existe.

## Alcance

### Incluye

Backend:
- `apps/content/serializers.py`: nuevo `NoticiaRelacionadaAgrupadaSerializer` y `EventoRelacionadoAgrupadoSerializer` que devuelven estructura `{categoria: {id, nombre}, items: [...]}`.
- `apps/content/views.py`:
  - Modificar `NoticiaViewSet.relacionadas` para devolver grupos por categoria (no romper compatibilidad: si no hay categoria, fallback a grupo "General" con todas).
  - Agregar `EventoViewSet.relacionados` con la misma logica.
- `apps/content/models.py`: agregar `categoria` FK opcional a `Evento` (mismo `Categoria` que `Noticia`).
- `apps/content/migrations/`: nueva migracion para el campo en `Evento` (idempotente si ya existe).
- `apps/content/serializers.py`: actualizar `EventoSerializer` para exponer `categoria` y `categoria_nombre` (mismo patron que Noticia).
- `apps/content/admin.py`: registrar `categoria` en `Evento` (list_filter + raw_id_fields).
- Seed opcional: si el seed crea eventos, asignarles categoria de forma aleatoria para que el endpoint devuelva grupos no vacios.

Frontend:
- `src/components/common/RelacionadosSidebar/RelacionadosSidebar.jsx`: nuevo componente generico que recibe `{titulo, grupos: [{categoria, items:[]}]}` y renderiza la sidebar agrupada. Conserva los estilos actuales (`.relacionadas-lista`, `.relacionada-card-horizontal`, `.noticias-relacionadas`, `.eventos-relacionados`).
- `src/components/common/RelacionadosSidebar/RelacionadosSidebar.css`: estilos para `.rs-grupo`, `.rs-grupo__header`, `.rs-grupo__titulo`, `.rs-grupo__items`.
- `src/pages/Noticias/DetalleNoticia.jsx`: reemplazar `NoticiasRelacionadas` por `RelacionadosSidebar` con `titulo="Noticias relacionadas"`.
- `src/pages/Eventos/DetalleEvento.jsx`: idem, `titulo="Eventos relacionados"`. Tambien reemplazar la llamada actual a `/eventos/` por `/eventos/{id}/relacionados/`.
- Consumir el nuevo shape `{grupos: [...]}` desde ambos detalles.

### No incluye

- Cambiar contratos existentes que ya estan en uso (el backend devuelve listas planas; se mantiene backward-compat con `items` como fallback si la respuesta es lista).
- Modificar el `admin-loading` ni los loaders puntuales de admin.
- Modificar `src/api.js` o `src/context/AuthContext.jsx`.
- Cambiar filtros o el listado principal de `/noticias` o `/eventos`.
- Reescribir `PageLoader` ni el `LoaderOverlay` global.

## Contexto leido

- `comunidad_zapotal_frontend/AGENTS.md`
- `comunidad_zapotal_backend/AGENTS.md` (system reminder: skills django-expert, api-and-interface-design, sin tocar apps/accounts, sin cambiar permisos, sin migraciones no previstas, vistas delgadas)
- `comunidad_zapotal_backend/apps/content/models.py` (Noticia tiene `categoria`, Evento NO)
- `comunidad_zapotal_backend/apps/content/views.py` (`relacionadas` filtra por categoria, no agrupado)
- `comunidad_zapotal_backend/apps/content/serializers.py`
- `comunidad_zapotal_backend/apps/content/admin.py`
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx` (consume `/noticias/{id}/relacionadas/`)
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx` (consume `/eventos/` filtrado en cliente)
- `comunidad_zapotal_frontend/src/pages/Noticias/Noticias.css` y `Eventos/DetalleEvento.css` (estilos ya existentes)

## Estado actual

- Backend `NoticiaViewSet.relacionadas` ya filtra por `categoria` pero devuelve lista plana.
- Backend `Evento` no tiene `categoria`; no existe endpoint `/eventos/{id}/relacionados/`.
- Frontend `NoticiasRelacionadas` y `EventosRelacionados` renderizan una sola lista plana sin agrupar.
- Frontend de eventos: `DetalleEvento` hace `api.get('/eventos/')` y filtra en cliente (5 items), sin categoria.

## Riesgos

- Cambio de modelo `Evento.categoria` requiere migracion: bloqueada por regla `backend/AGENTS.md` ("No cambiar modelos sin justificar migracion"). Se aprueba dentro de este lote (justificada por el objetivo).
- Cambiar la firma de respuesta del endpoint `/relacionadas/` puede romper consumidores externos: mitigacion devolviendo shape nuevo `{grupos: [...]}` que es aditivo (frontend actual espera lista plana -> mantenemos ambos en el serializer nuevo y el cliente decide).
- Render del nuevo sidebar: compatibilidad de estilos con `Noticias.css` y `DetalleEvento.css` que ya tienen `.relacionadas-lista`. Se conserva esa clase dentro de cada grupo.
- Rendimiento: backend ya hace `select_related('categoria')`. La agrupacion es O(n) en memoria; aceptable para 5 items por grupo.

## Skills recomendadas

- `django-expert`
- `api-and-interface-design`
- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`

## Recomendacion

1. Backend primero:
   - Agregar `categoria` FK a `Evento` (migracion).
   - Crear `NoticiaRelacionadaAgrupadaSerializer` y `EventoRelacionadoAgrupadoSerializer` con shape `{grupos: [{categoria, items: [...]}]}`.
   - Modificar `NoticiaViewSet.relacionadas` para devolver el shape agrupado.
   - Agregar `EventoViewSet.relacionados` con la misma logica.
   - Actualizar `EventoSerializer` para incluir `categoria` y `categoria_nombre`.
   - Actualizar admin.
2. Frontend:
   - Crear `RelacionadosSidebar` reutilizable.
   - Adaptar `DetalleNoticia` y `DetalleEvento` al nuevo shape.
3. Verificacion: `python manage.py check`, `pytest apps/content`, `npm run build`, `npm run dev`.

## Verificacion sugerida

Backend:
- `python manage.py check`
- `python -m pytest apps/content -q` (relacionadas por categoria, agrupacion, evento sin categoria -> grupo "General")
- Smoke con curl: `GET /api/v1/noticias/1/relacionadas/` y `GET /api/v1/eventos/1/relacionados/`.

Frontend:
- `npm run build`
- `npm run dev`
- Navegar a `/noticias/:id` y `/eventos/:id`, ver sidebar agrupada.
- Verificar responsive (la lista horizontal actual ya estaba).
