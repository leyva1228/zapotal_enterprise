# Post-Implementation Review: Endpoint singular /detalle/ + relacionados por categoria

## Estado

- Estado: COMPLETED
- Fecha: 2026-06-28
- Tecnologia: backend Django + frontend React (Vite)

## Resumen

Se estandarizo la nomenclatura de los endpoints de detalle a singular con
sufijo `detalle/` y se mejoro el endpoint de relacionados por categoria
con filtro opcional, sin romper reacciones, comentarios ni favoritos.

## Archivos modificados

Backend:

- `comunidad_zapotal_backend/apps/content/urls.py`
  - Agregadas 8 rutas singulares con `/detalle/` (4 para noticia, 4 para
    evento: retrieve, relacionadas/relacionados, comentarios,
    incrementar_vistas). Reusan los mismos ViewSets, no duplican logica.
- `comunidad_zapotal_backend/apps/content/views.py`
  - Helpers nuevos: `_parse_categoria_filtro(request)` y
    `_filtrar_por_categoria(items, categoria_id)`.
  - `NoticiaViewSet.relacionadas` y `EventoViewSet.relacionados`
    aceptan `?cat=<id>` para filtrar por categoria.
  - Documentacion de docstrings actualizada.
- `comunidad_zapotal_backend/apps/content/tests.py`
  - 6 tests nuevos:
    - `TestNoticiaViewSet.test_detalle_singular_noticia_public`
    - `TestNoticiaViewSet.test_relacionadas_singular_public`
    - `TestNoticiaViewSet.test_relacionadas_filtro_por_categoria`
    - `TestEventoViewSet.test_detalle_singular_evento_public`
    - `TestEventoViewSet.test_relacionados_singular_public`
    - `TestEventoViewSet.test_relacionados_filtro_por_categoria`
    - `TestEventoViewSet.test_rutas_plurales_siguen_funcionando`

Frontend:

- `comunidad_zapotal_frontend/src/App.jsx`
  - Rutas nuevas: `/noticia/detalle/:id` y `/evento/detalle/:id`.
  - Las rutas plurales `/noticias/:id` y `/eventos/:id` se mantienen.
  - Breadcrumb reconoce ambos formatos.
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  - `NoticiasRelacionadas` usa `linkBase="/noticia/detalle/"`.
  - Fetch de relacionadas apunta a `/noticia/detalle/<id>/relacionadas/`.
  - Si la noticia tiene categoria, envia `?cat=<id>` para que la
    sidebar muestre el grupo "mismo tema" arriba.
  - Reacciones, comentarios y favoritos: sin cambios.
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  - Idem para eventos: `linkBase="/evento/detalle/"`, fetch a
    `/evento/detalle/<id>/relacionados/?cat=<id>`.
  - Reacciones, comentarios y favoritos: sin cambios.
- `comunidad_zapotal_frontend/src/components/common/RelacionadosSidebar/RelacionadosSidebar.jsx`
  - Sin cambios: ya aceptaba `linkBase` configurable. Solo se documento
    su uso con la nueva nomenclatura.

## Comandos ejecutados y resultado

```bash
# Backend
python manage.py check
# System check identified no issues (0 silenced).

python -m pytest apps/content/tests.py -q
# 14 passed, 5 warnings in 29.17s
# (8 originales + 6 nuevos, todos en verde)

# Frontend
npm run build
# built in 17.99s - sin errores
# (eslint no es ejecutable en este repo por mismatch de versiones, no
#  es introducido por este cambio; build con Vite pasa)
```

Smoke test manual contra el servidor de tests con `Client` y `follow=True`:

```
=== RUTAS SINGULARES (nueva nomenclatura) ===
Noticia detalle:     200
Noticia relacionadas: 200
Noticia cat filter:  200
Evento detalle:      200
Evento relacionados: 200
Evento cat filter:   200

=== RUTAS PLURALES (regression: deben seguir funcionando) ===
Noticias detalle:     200
Noticias relacionadas: 200
Eventos detalle:      200
Eventos relacionados: 200
```

## Funcionalidad preservada

- Reacciones: `POST /reacciones/` con `noticia|evento|comentario`.
  Sin cambios.
- Comentarios: `GET/POST /comentarios/?noticia=<id>`,
  `GET /eventos/<id>/comentarios/`, `GET /noticias/<id>/comentarios/`
  y equivalentes singulares. Sin cambios funcionales.
- Favoritos: `GET/POST /favoritos/` con `tipo=NOTICIA|EVENTO` y
  `noticia|evento`. Sin cambios.
- Vistas: `POST /noticias/<id>/incrementar_vistas/` y equivalente
  singular. Sin cambios.

## Decisiones tecnicas relevantes

1. **No se eliminaron rutas plurales.** Conviven con las nuevas. Cero
   riesgo de regresion para admin, mobile/BFF, tests y frontend legacy.

2. **`as_view()` con un solo action dict.** Se intento pasar
   `action=`/`detail=` como initkwargs pero `ViewSetMixin.as_view()`
   en DRF 3.17 los rechaza si no son atributos de la clase. La
   solucion correcta es `as_view({'get': 'relacionadas'})` con un solo
   mapeo: DRF infiere `self.action` desde `self.action_map` en
   `initialize_request()` y la accion `@action(detail=True)` ejecuta
   su `get_object()` correctamente.

3. **Query param `?cat=<id>` (no `?categoria=<id>`).** El viewset tiene
   `filterset_fields = [..., 'categoria', ...]`. Si el cliente
   mandaba `?categoria=<id>`, el filter backend lo aplicaba al
   queryset base antes de `get_object()` y la entidad base dejaba
   de encontrarse (404). Usar `?cat=<id>` evita el conflicto y la
   documentacion lo explica.

4. **Filtro post-queryset, no pre.** Se aplica `_filtrar_por_categoria`
   a la lista ya armada (con `select_related` + `prefetch_related`
   del queryset base). Sin joins adicionales, performance estable.

## Riesgos detectados

- Bajo: el cambio es aditivo (nuevas rutas, nuevo query param). Las
  rutas plurales siguen funcionando y los tests de regression lo
  confirman.
- Bajo: el frontend ahora consume el endpoint singular, pero el
  servicio no cambia. Si por algun motivo el endpoint singular
  devolviera error, el `.catch()` de la sidebar la deja vacia
  (mismo comportamiento que antes).
- Bajo: lint de frontend no es ejecutable en este repo por
  incompatibilidad entre la version de eslint declarada y la
  requerida (pre-existente, no introducido por este cambio). El
  build con Vite pasa, que es lo importante.

## Conocimiento nuevo

- `ViewSetMixin.as_view()` en DRF 3.17: `action` y `detail` NO se
  pasan como initkwargs; `self.action` se infiere de
  `self.action_map` en `initialize_request()`.
- `filter_queryset()` se ejecuta tambien en `get_object()` para
  detail endpoints, por lo que cualquier query param que coincida
  con un `filterset_fields` se aplica al lookup del objeto base.

## Ruta del documento operativo

`agents-workflow/comunidad_zapotal_backend/audits/active/2026-06-28-endpoint-detalle-singular-relacionados.md`
`agents-workflow/comunidad_zapotal_backend/implementation-plans/active/2026-06-28-endpoint-detalle-singular-relacionados.md`
`agents-workflow/comunidad_zapotal_backend/post-implementation/2026-06-28-endpoint-detalle-singular-relacionados.md` (este archivo)
