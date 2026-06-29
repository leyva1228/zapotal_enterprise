# Audit: Estandarizar colores verde/dorado del navbar en todas las secciones

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Tecnologia: frontend React (Vite) + CSS

## Objetivo

Reemplazar los colores hardcodeados (verde, dorado, gris oscuro,
negro) en las paginas publicas y de admin por las variables
del navbar (`--nb-verde`, `--nb-verde-med`, `--nb-verde-claro`,
`--nb-dorado`, `--nb-dorado-light`) para que toda la web se vea
como un solo sistema con la misma paleta.

## Alcance

### Incluye

Frontend (10 archivos CSS prioritarios, publicos):

- `src/pages/Nosotros/Conocenos.css`
- `src/pages/Nosotros/Galeria.css`
- `src/pages/Nosotros/MarcoLegalPage.css`
- `src/pages/Nosotros/NuestraHistoria.css`
- `src/pages/Donaciones/Donaciones.css`
- `src/pages/Buscar/Buscar.css`
- `src/pages/Legal/LegalPage.css`
- `src/components/Contacto/Contacto.css`
- `src/components/LibroReclamaciones/LibroReclamaciones.css`
- `src/components/Footer.css` (solo ajustes menores)

### No incluye

- Admin pages (AdminLayout, AdminNoticias, etc.): no son visibles
  para usuarios publicos, baja prioridad.
- Login/Registro/Detalle: ya unificados en tareas anteriores.
- Navbar.css: ya usa los colores correctos (es la fuente).
- index.css: ya tiene las variables --nb-* definidas.
- El rebranding total (tipografia, espaciados, layouts): solo
  cambiamos COLOR de elementos existentes.

## Plan de implementacion (por batch)

### Batch 1: Paginas Nosotros (4 archivos)

- Conocenos.css: headings, hover de tarjetas, botones
- Galeria.css: hover de imagenes, bordes
- MarcoLegalPage.css: headings, hover de links
- NuestraHistoria.css: headings, hover de tarjetas, timeline

### Batch 2: Paginas de servicios (3 archivos)

- Donaciones.css: botones, montos, hover
- Buscar.css: filtros, resultados, hover
- LegalPage.css: headings, hover de links

### Batch 3: Componentes (3 archivos)

- Contacto.css: info, formulario, hover
- LibroReclamaciones.css: formulario, hover
- Footer.css: ajustes menores si quedan colores

## Recomendacion

1. Para cada archivo, identificar los colores hardcodeados
   relacionados con verde/dorado/negro/gris-oscuro.
2. Reemplazar por las variables del navbar.
3. NO tocar layouts, tipografia, espaciados.
4. Solo cambiar COLORES de elementos existentes.

## Verificacion

- `npm run build` despues de cada batch.
- Playwright spot-check de cada pagina modificada.

## Nota sobre el alcance

Este es un trabajo grande (10+ archivos CSS, muchos colores
hardcodeados). Se implementara en 3 commits separados, uno por
batch. Cada commit es verificable independientemente.
