# Plan: Filtros de categoría y mejoras de diseño en /nosotros/galeria

**Fecha:** 2026-06-30
**Auditoría:** `02-audits/galeria-filtros-2026-06-30.md`

## Objetivo

1. Exponer las 7 categorías temáticas de `GaleriaImagen` como segundo grupo de filtros combinado con el tipo (Todas / Noticias / Eventos).
2. Mejorar proporciones, tipografía, accesibilidad y feedback visual del hero, grid y lightbox.

## Alcance

**Permitido:**
- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.jsx`
- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.css`

**Prohibido (zonas sensibles o fuera de alcance):**
- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/*`
- `comunidad_zapotal_frontend/src/components/RequireAuth*`
- `comunidad_zapotal_frontend/src/components/RequireAdmin*`
- `comunidad_zapotal_frontend/src/pages/Admin/*`
- `comunidad_zapotal_backend/**`
- Cualquier otro archivo del repo

## Skills a usar

- `frontend-ui-engineering` (proporciones, tipografía, accesibilidad, paleta)
- `react-expert` (estado, efectos, accesibilidad JSX)
- `incremental-implementation` (micro-tareas, verificación por paso)
- `verification-before-completion` (build + lint antes de declarar listo)

## Categorías a exponer (alineadas con backend `GaleriaImagen.Categoria`)

| Key backend   | Label UI         | Icono (react-icons) |
|---------------|------------------|---------------------|
| COMUNIDAD     | Comunidad        | FaUsers             |
| AUTORIDADES   | Autoridades      | FaUserTie           |
| FESTIVIDADES  | Festividades     | FaStar              |
| INFRAESTRUCTURA | Infraestructura | FaRoad              |
| NATURALEZA    | Naturaleza       | FaLeaf              |
| PATRIMONIO    | Patrimonio       | FaLandmark          |
| OTRO          | Otro             | FaEllipsisH         |

## Micro-tareas

### MT-1 — Refactor JSX: estado, constantes y carga
- Agregar `CATEGORIAS` const con `{key, label, icon}`.
- Nuevo estado `categoria` con default `'TODAS'`.
- `cargar` ahora depende de `[filtro, categoria]` y envía `?categoria=<key>` cuando no es `TODAS`.
- `useEffect` de cierre de lightbox reacciona a ambos.
- Reemplazar `role="tab"` por `role="group"` + `aria-pressed` en ambos grupos de chips.

### MT-2 — UI: dos grupos de filtros
- Renderizar dos bloques `.galeria-filtros__grupo` dentro de `.galeria-filtros`:
  - **Tipo:** Todas / Noticias / Eventos.
  - **Categoría:** Todas / Comunidad / Autoridades / ... / Otro.
- En desktop: misma fila visual, separados por divisor vertical sutil.
- En mobile (<=700px): scroll horizontal independiente por grupo con `overflow-x: auto` y `scroll-snap-type: x mandatory`.

### MT-3 — Badge de categoría en cada card
- Nuevo `.galeria-card__cat-badge` arriba a la izquierda (el badge actual de noticia/evento se queda a la derecha).
- Texto pequeño, fondo verde navbar + dorado, similar al chip activo.

### MT-4 — Mejoras de proporciones, tipografía y accesibilidad
- Hero: `height: clamp(380px, 45vh, 520px)`; título `clamp(36px, 4.4vw, 56px)`.
- Cards: `aspect-ratio: 3 / 2` (más cine, mejor para fotos comunitarias).
- Lightbox: agregar `aria-labelledby` al caption, `aria-label` al contenedor.
- Foco visible consistente en todos los chips.
- Espaciado del grid: `gap: clamp(16px, 2vw, 26px)`.
- Padding del contenedor consistente con el resto del sitio.

### MT-5 — Verificación
- `npm run build` (debe pasar sin warnings nuevos).
- `npm run lint` (debe pasar sin errores).
- Diff revisado contra el código actual.

## Criterios de "hecho"

- [ ] Dos grupos de chips visibles y combinables.
- [ ] Cambiar tipo o categoría recarga la lista con `?con_noticia=1` / `?con_evento=1` / `?categoria=<key>` correctos.
- [ ] Badge de categoría visible en cada card.
- [ ] Hero más proporcionado, no domina la pantalla.
- [ ] Aspect ratio de cards más natural.
- [ ] Accesibilidad: `aria-pressed`, `aria-labelledby`, foco visible, semántica correcta.
- [ ] Responsive sin overflow horizontal.
- [ ] `npm run build` y `npm run lint` pasan.
