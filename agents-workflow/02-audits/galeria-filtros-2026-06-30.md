# Auditoría: /nosotros/galeria

**Fecha:** 2026-06-30
**Stack afectado:** comunidad_zapotal_frontend (React 19 + Vite)
**Archivos auditados:**
- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.jsx`
- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.css`

## Contrato API actual

**Endpoint:** `GET /galeria/` (ViewSet: `GaleriaImagenViewSet`)
**Filtros soportados por backend:**
- `?categoria=COMUNIDAD|AUTORIDADES|FESTIVIDADES|INFRAESTRUCTURA|NATURALEZA|PATRIMONIO|OTRO`
- `?con_noticia=1`
- `?con_evento=1`
- `?activo=true|false`

**Serializer expone:** `id, titulo, descripcion, imagen, imagen_url, imagen_url_externa, categoria, categoria_display, fecha, orden, activo, noticia, noticia_titulo, evento, evento_titulo`

## Estado actual del frontend

### Lo que ya funciona bien
- Hero con título/subtítulo editables desde `useConfiguracion` + `useTextosSeccion('GALERIA_HERO')`.
- Filtro principal por tipo: `TODOS | NOTICIAS | EVENTOS` (mapea a `?con_noticia=1` / `?con_evento=1`).
- Grid responsive con `auto-fill, minmax(260px, 1fr)`.
- Lightbox accesible con teclado (Escape, flechas), contador de posición, navegación con flechas, botones de "Ver noticia completa" / "Ver evento completo".
- Estados de loading (skeleton), error y empty con copy por filtro.
- Paleta verde navbar + dorado + crema consistente con el resto del sitio.
- `useTextosSeccion` ya integrado → el admin puede editar textos sin tocar código.

### Hallazgos (issues)

1. **Falta exposición de categorías temáticas al usuario público.**
   El modelo `GaleriaImagen.categoria` ya tiene 7 valores (`COMUNIDAD, AUTORIDADES, FESTIVIDADES, INFRAESTRUCTURA, NATURALEZA, PATRIMONIO, OTRO`), el backend ya filtra por `?categoria=`, el serializer ya expone `categoria_display`, pero el frontend no los ofrece como filtro. El comentario en el código lo reconoce: "no se exponen al usuario publico".

2. **No hay forma de combinar tipo + categoría.** El usuario solo puede filtrar por uno u otro. Falta un segundo eje de filtrado.

3. **Proporciones del hero demasiado altas para muchas pantallas.** `height: 520px` fijo hace que en pantallas 1366x768 ocupe el 68% del viewport sin mostrar nada más. En mobile 420px (línea media del responsive) compite con la primera fila de cards.

4. **Aspect ratio de cards 4/3 deja mucho "cielo" en imágenes horizontales típicas de la comunidad.** Mejor 3/2 o 16/10.

5. **Tipografía del título del hero en verde claro (#3a6019) sobre fondo oscuro con sombra dorada** funciona, pero el `letter-spacing: 0.5px` y la `font-size: clamp(40px, 5.5vw, 64px)` se ven algo oversized en desktop. Bajar tope a `clamp(36px, 4.4vw, 56px)`.

6. **Filtros usan `role="tab"` con `aria-selected`**, pero en realidad son toggles independientes (no un tablist con paneles asociados). Mejor `role="group"` + `aria-pressed`.

7. **El `useCallback([filtro])` debería re-fetchear también cuando cambia `categoria`.** Hoy `cargar` solo depende de `filtro`, lo cual es un bug latente si se agrega categoría sin tocar la dependencia.

8. **No hay badge de categoría en cada card.** El usuario no sabe a qué categoría pertenece una imagen sin hacer clic.

9. **Accesibilidad del lightbox:** falta `aria-label` en el contenedor y `aria-labelledby` apuntando al `h3` del caption.

10. **Conteo de chips: `counts.NOTICIAS` y `counts.EVENTOS` se calculan sobre `items` post-filtro, lo que da 0 si ya filtramos por NOTICIAS y luego miramos el chip NOTICIAS** (correcto, pero confunde). No es bloqueante.

## Decisión

Implementar filtros de **tipo + categoría** combinados, manteniendo la arquitectura actual. Aprovechar para mejorar proporciones, tipografía, accesibilidad y consistencia visual. **Sin tocar backend, sin tocar `api.js`, sin tocar `context/`, sin tocar `RequireAuth*`, sin tocar `Admin/`.**

## Riesgos

- Re-render por doble filtro: el efecto ya usa `useCallback([filtro])`, se actualizará a `[filtro, categoria]`.
- Si la respuesta del backend cambia de forma (paginación vs lista plana), el fallback `data.results || data || []` ya lo cubre.
- Categoría vacía o con valor desconocido: el backend filtra exacto, así que valores no soportados devuelven lista vacía. No hay error 500.

## Verificación esperada

- `npm run build` sin warnings nuevos.
- `npm run lint` sin errores.
- Render manual: hero proporcionado, dos grupos de chips visibles, combinación tipo+categoría devuelve resultados correctos, badge de categoría visible en cada card, lightbox accesible.
