# Audit: Contador de visualizaciones en detalle de eventos

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Autor/agente: opencode-go/minimax-m3
- Tecnologia: backend Django + frontend React (Vite)

## Objetivo

Reutilizar el patron de conteo de visualizaciones del detalle de noticias
en el detalle de eventos. El frontend ya tiene la logica de
`incrementar_vistas` implementada, pero el backend NO expone el campo
`vistas` en el serializer de eventos, por lo que el contador nunca
se muestra ni se actualiza en la UI.

## Alcance

### Incluye

Backend:

- `comunidad_zapotal_backend/apps/content/serializers.py`
  - Agregar `vistas` al `fields` de `EventoSerializer`.
  - Agregar `vistas` al `fields` de `EventoRelacionadoSerializer`
    (consistencia con `NoticiaRelacionadaSerializer` que ya lo incluye).
  - NO tocar `EventoEscrituraSerializer` (campo auto-managed, write_only
    no aporta valor para creacion/edicion).
- `comunidad_zapotal_backend/apps/content/tests.py`
  - Test que verifica que `vistas` viene en la respuesta del detalle
    de evento (plural y singular).
  - Test que verifica que `incrementar_vistas` en evento funciona
    atomicamente y devuelve el nuevo conteo.
  - Test que verifica que `vistas` viene en `relacionados/`.

Frontend:

- Sin cambios de codigo necesarios. La logica de `incrementar_vistas`
  ya esta implementada en `DetalleEvento.jsx` (lineas 299-316), y el
  render `{evento.vistas != null && <span>...{evento.vistas}...</span>}`
  ya esta en la UI (lineas 776-777). Solo faltaba que el backend
  expusiera el campo.
- Verificacion manual con curl: el endpoint devuelve `vistas` y el
  contador se incrementa.

### No incluye

- No se cambia la logica de `incrementar_vistas` (ya es correcta y
  atomica con `F('vistas') + 1`).
- No se cambia la logica del frontend (ya esta implementada).
- No se migra la base de datos.
- No se tocan permisos, auth, tokens ni settings.
- No se cambia la app Android, el BFF Spring Boot ni el gateway.
- No se cambia `src/api.js`.

## Contexto leido

- `AGENTS.md` (raiz)
- `graphify.md` (raiz)
- `comunidad_zapotal_backend/AGENTS.md`
- `comunidad_zapotal_backend/graphify/GRAPH_REPORT.md`
- `comunidad_zapotal_frontend/AGENTS.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/templates/implementation-plan-template.md`
- `agents-workflow/AGENTS.md`

Archivos inspeccionados (lectura):

- `comunidad_zapotal_backend/apps/content/serializers.py` (lineas
  143-318: NoticiaSerializer, EventoSerializer, NoticiaRelacionadaSerializer,
  EventoRelacionadoSerializer).
- `comunidad_zapotal_backend/apps/content/views.py` (lineas 173-184:
  NoticiaViewSet.incrementar_vistas; lineas 274-281:
  EventoViewSet.incrementar_vistas).
- `comunidad_zapotal_backend/apps/content/urls.py` (rutas singulares
  y plurales para `incrementar_vistas` en noticia y evento).
- `comunidad_zapotal_backend/apps/content/tests.py` (estado actual de
  tests).
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  (lineas 301-318: logica de incrementar_vistas; lineas 763-764:
  render de vistas).
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  (lineas 299-316: logica de incrementar_vistas; lineas 776-777:
  render de vistas).

## Estado actual

Backend:

- `NoticiaSerializer.Meta.fields` incluye `vistas` (linea 167).
- `EventoSerializer.Meta.fields` NO incluye `vistas` (lineas 236-240).
  Este es el bug.
- `NoticiaRelacionadaSerializer.Meta.fields` incluye `vistas`
  (linea 270).
- `EventoRelacionadoSerializer.Meta.fields` NO incluye `vistas`
  (lineas 294-298). Para consistencia.
- `NoticiaViewSet.incrementar_vistas` y `EventoViewSet.incrementar_vistas`
  son funcionalmente identicos: `update(vistas=F('vistas')+1)` + return
  del nuevo conteo. Ambos endpoints publicos (AllowAny). Ambos
  registrados en rutas plurales Y singulares (recien agregado en la
  tarea anterior).

Frontend:

- `DetalleNoticia.jsx` tiene la logica completa: `useEffect` que
  llama a `POST /noticias/<id>/incrementar_vistas/`, usa
  `localStorage`/`sessionStorage` con clave `visto_noticia_<id>_...`
  para evitar doble conteo, y actualiza el state con `data.vistas`.
- `DetalleEvento.jsx` tiene la MISMA logica: `useEffect` que llama a
  `POST /eventos/<id>/incrementar_vistas/`, usa `localStorage`/
  `sessionStorage` con clave `visto_evento_<id>_...`, y actualiza
  el state con `data.vistas`.
- Render de vistas en ambas paginas:
  `{evento.vistas != null && <span><FaEye /> {evento.vistas} visualizaciones</span>}`
  o equivalente.

Conclusion: el frontend ESTA listo. El bug esta en el backend:
`EventoSerializer` no expone `vistas`, por lo que el frontend recibe
`undefined` y el render nunca se muestra (`undefined != null` es
`true` pero `{undefined} visualizaciones` no aparece porque la
condicion es `evento.vistas != null`).

Verificacion rapida (ejecutada en este analisis):

```
=== NoticiaSerializer fields ===
  ...
  vistas
  ...
=== EventoSerializer fields ===
  (vistas NO aparece)
```

## Riesgos

- Bajo: el cambio es aditivo (agregar `vistas` al fields). No elimina
  ni renombra nada. Consumidores que ya usaban el endpoint seguiran
  recibiendo el mismo payload + el campo `vistas`.
- Bajo: el frontend ya esta preparado para mostrar y actualizar
  `vistas`. No requiere cambios.
- Ninguno: no toca zonas sensibles (auth, permisos, tokens,
  settings, mobile/BFF).

## Skills recomendadas

- `django-expert`
- `api-and-interface-design`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`

## Recomendacion

1. Agregar `'vistas'` al `fields` de `EventoSerializer`.
2. Agregar `'vistas'` al `fields` de `EventoRelacionadoSerializer`
   para consistencia con `NoticiaRelacionadaSerializer`.
3. Agregar 2 tests minimos:
   - `test_detalle_evento_incluye_vistas`: GET al detalle debe
     devolver `vistas` en el payload.
   - `test_incrementar_vistas_evento_atomic`: POST debe incrementar
     el contador y devolver el nuevo valor.
4. NO tocar el frontend: ya esta implementado.
5. Verificar con `pytest` + `manage.py check` + smoke test con curl.

## Verificacion sugerida

```bash
python manage.py check
python -m pytest apps/content -q
# Smoke test:
curl -s http://127.0.0.1:8000/api/v1/eventos/1/ | python -c "import json,sys; d=json.load(sys.stdin); print('vistas:', d.get('vistas'))"
curl -s -X POST http://127.0.0.1:8000/api/v1/eventos/1/incrementar_vistas/ | python -c "import json,sys; d=json.load(sys.stdin); print('vistas:', d.get('vistas'))"
```
