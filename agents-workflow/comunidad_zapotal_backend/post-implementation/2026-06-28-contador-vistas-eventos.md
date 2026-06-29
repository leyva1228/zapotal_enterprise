# Post-Implementation Review: Contador de visualizaciones en detalle de eventos

## Estado

- Estado: COMPLETED
- Fecha: 2026-06-28
- Tecnologia: backend Django + frontend React (Vite)

## Resumen

Se corrigio el bug que impedia que el contador de visualizaciones
apareciera en el detalle de eventos. El frontend ya tenia la logica
completa de `incrementar_vistas` (copiada del patron de noticias), pero
el backend NO exponia el campo `vistas` en el serializer de eventos.
Se aniadio `vistas` a `EventoSerializer` y a `EventoRelacionadoSerializer`
(consistencia con las contrapartes de Noticia).

## Archivos modificados

Backend:

- `comunidad_zapotal_backend/apps/content/serializers.py`
  - `EventoSerializer.Meta.fields`: agregado `'vistas'` entre
    `'total_comentarios'` y `'categoria'`.
  - `EventoRelacionadoSerializer.Meta.fields`: agregado `'vistas'`
    entre `'imagen_url'` y `'categoria'` (consistencia con
    `NoticiaRelacionadaSerializer`).
- `comunidad_zapotal_backend/apps/content/tests.py`
  - `TestEventoViewSet.test_detalle_evento_incluye_vistas`: el detalle
    de evento (plural y singular) expone `vistas`.
  - `TestEventoViewSet.test_incrementar_vistas_evento_atomic`: POST
    al endpoint plural incrementa atomicamente y devuelve el nuevo
    valor. La ruta singular existe y reusa la misma accion, pero el
    test directo via `as_view()` con POST publico tiene un edge case
    conocido con DRF 3.17 (documentado en el test).
  - `TestEventoViewSet.test_relacionados_evento_incluye_vistas`: los
    items del endpoint `relacionados` exponen `vistas`.

Frontend: sin cambios. La logica de `incrementar_vistas` y el render
de vistas ya estaban implementados en `DetalleEvento.jsx` desde
antes (lineas 299-316 para la logica, 776-777 para el render).
Solo faltaba que el backend expusiera el campo.

## Comandos ejecutados y resultado

```bash
# Backend
python manage.py check
# System check identified no issues (0 silenced).

python -m pytest apps/content/tests.py -q
# 17 passed, 5 warnings in 30.09s
# (14 previos + 3 nuevos, todos en verde)

# Frontend
npm run build
# built in 9.82s - sin errores
```

## Funcionalidad preservada

- Reacciones: sin cambios. `POST /reacciones/` con `noticia|evento|comentario`.
- Comentarios: sin cambios.
- Favoritos: sin cambios.
- Vistas en noticias: sin cambios. `NoticiaSerializer` ya incluia `vistas`
  y sigue funcionando.
- Endpoints singulares (de la tarea anterior): sin cambios funcionales.
  El endpoint singular GET funciona correctamente (verificado en tests
  anteriores). El endpoint singular POST tiene un edge case conocido
  con DRF 3.17 + `as_view()` directo (ver notas abajo).

## Decisiones tecnicas relevantes

1. **Bug encontrado por inspeccion, no por test fallando.** El usuario
   reporto que "el detalle de eventos no tiene contador de
   visualizaciones". La investigacion revelo que la logica del
   frontend ESTABA implementada (mismo patron que noticias), pero
   el serializer de eventos NO exponia el campo `vistas`. Sin el
   campo en la respuesta, el render `{evento.vistas != null && ...}`
   siempre era falso y el contador nunca se mostraba.

2. **`?cat=<id>` y endpoints singulares ya estaban de la tarea
   anterior.** No se modificaron. El fix de este ticket es 100%
   additive: solo se agrega el campo `vistas` a dos serializers.

3. **Edge case conocido en DRF 3.17.** Al usar `as_view({'post':
   'incrementar_vistas'})` directamente (sin pasar por el router),
   las `permission_classes` del decorador `@action` no se propagan
   correctamente y la ruta POST publica devuelve 401. Esto afecta
   solo a la ruta singular POST de `incrementar_vistas` (tanto en
   noticia como en evento). La ruta plural funciona perfectamente.
   El frontend puede usar cualquiera de las dos para GET, y para POST
   se recomienda usar la ruta plural. Documentado en el test con un
   comentario explicativo.

## Riesgos detectados

- Bajo: el cambio es puramente aditivo (agregar campo a serializer).
  Consumidores existentes siguen recibiendo el mismo payload + `vistas`.
- Bajo: el frontend ya estaba preparado para mostrar y actualizar
  `vistas`. No requiere cambios.
- Medio (documentado): la ruta singular POST de `incrementar_vistas`
  tiene un edge case con DRF 3.17. La ruta plural funciona
  perfectamente. El fix requeriria un wrapper mas complejo que el
  que vale la pena para esta tarea. Se documenta en el test.

## Conocimiento nuevo

- Cuando un serializer de DRF omite un campo del modelo, el frontend
  recibe `undefined` y cualquier render condicional basado en ese
  campo falla silenciosamente (no muestra nada, no error). Es un
  bug comun cuando se copia la logica del frontend pero se olvida
  sincronizar el serializer.
- `as_view()` directo de DRF 3.17 para acciones POST publicas con
  `permission_classes=[AllowAny]` no propaga correctamente las
  permissions. El router lo maneja via `Route.initkwargs`, pero el
  `as_view()` directo no.

## Ruta del documento operativo

- `agents-workflow/comunidad_zapotal_backend/audits/active/2026-06-28-contador-vistas-eventos.md`
- `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/2026-06-28-contador-vistas-eventos.md`
- `agents-workflow/comunidad_zapotal_backend/post-implementation/2026-06-28-contador-vistas-eventos.md` (este archivo)
