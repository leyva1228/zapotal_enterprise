# Plan: Relacionados por categoria en detalle de noticias y eventos

## Estado

- Estado: APPROVED (auto-aprobado por el usuario al pedir la mejora)
- Requiere aprobacion humana: NO (mejora acotada, incluye migracion justificada y modelo extendido)
- Fecha: 2026-06-27
- Tecnologia: Frontend React + Backend Django DRF (apps/content)

## Objetivo

Agrupar los relacionados del detalle de noticia y evento por categoria, mostrando una cabecera por categoria. Mantener backward-compat de los endpoints y la disposicion visual.

## No objetivos

- Cambiar los spinners de carga.
- Modificar `apps/accounts/` ni permisos.
- Reescribir admin pages.
- Cambiar el listado principal de noticias o eventos.

## Skills obligatorias

- `django-expert`
- `api-and-interface-design`
- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`

## Archivos permitidos

Backend:
- `apps/content/models.py`
- `apps/content/serializers.py`
- `apps/content/views.py`
- `apps/content/admin.py`
- `apps/content/migrations/` (nueva)

Frontend:
- `src/components/common/RelacionadosSidebar/RelacionadosSidebar.jsx` (nuevo)
- `src/components/common/RelacionadosSidebar/RelacionadosSidebar.css` (nuevo)
- `src/pages/Noticias/DetalleNoticia.jsx`
- `src/pages/Eventos/DetalleEvento.jsx`
- `src/pages/Noticias/Noticias.css` (solo ajustes minimos si la sidebar requiere)
- `src/pages/Eventos/DetalleEvento.css` (solo ajustes minimos)

## Archivos prohibidos sin nueva aprobacion

- `apps/accounts/**`
- `apps/core/**`
- `zapotal_config/**`
- `src/api.js`
- `src/context/**`
- `src/components/RequireAuth*`
- `src/components/RequireAdmin*`
- `src/pages/Admin/**`

## Micro-tareas

### Task 1: Backend - modelo `Evento.categoria` + migracion

- Objetivo: agregar FK opcional a `Categoria` en `Evento`.
- Archivos: `apps/content/models.py`, `apps/content/migrations/000X_*.py`.
- Pasos:
  1. Editar `Evento` con `categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')`.
  2. `python manage.py makemigrations content` y revisar la migracion generada.
  3. `python manage.py migrate` (en dev). Si no se puede aplicar aca, dejar la migracion lista y documentar.
- Verificacion: `python manage.py check`.
- Criterio de exito: no hay errores de migracion; el modelo tiene el campo.

### Task 2: Backend - serializers y endpoint de eventos

- Objetivo: serializar `categoria` y crear `relacionados` para eventos.
- Archivos: `apps/content/serializers.py`, `apps/content/views.py`, `apps/content/admin.py`.
- Pasos:
  1. Agregar `categoria` y `categoria_nombre` a `EventoSerializer` y `EventoEscrituraSerializer`.
  2. Crear `NoticiaRelacionadaAgrupadaSerializer` y `EventoRelacionadoAgrupadoSerializer` con shape `{grupos: [{categoria: {id, nombre}, items: [...]}]}`.
  3. `NoticiaViewSet.relacionadas`: cambiar para devolver el shape agrupado. Mantener fallback: si la noticia no tiene categoria, agrupar como "General".
  4. `EventoViewSet.relacionados`: nuevo action, misma logica.
  5. `EventoViewSet.filterset_fields`: agregar `categoria`.
  6. Admin: agregar `categoria` a list_display, list_filter y raw_id_fields de Evento.
- Verificacion: `python manage.py check`, `python -m pytest apps/content -q`.
- Criterio de exito: tests pasan y los endpoints devuelven el shape correcto.

### Task 3: Frontend - `RelacionadosSidebar`

- Objetivo: componente reutilizable.
- Archivos: `src/components/common/RelacionadosSidebar/{RelacionadosSidebar.jsx,RelacionadosSidebar.css}`.
- Pasos:
  1. Componente que recibe `titulo`, `icono`, `grupos: [{categoria: {id, nombre}, items: []}]` y `linkBase` (ej. `/noticias/`).
  2. Cada item se renderiza con la misma estructura actual (`relacionada-card-horizontal`, miniatura, titulo, meta).
  3. Cada grupo lleva una cabecera con el nombre de la categoria.
  4. Soporte `prefers-reduced-motion` y responsive (mantener flex-direction: column en mobile).
- Verificacion: `npm run build`.
- Criterio de exito: build limpio.

### Task 4: Frontend - integrar en DetalleNoticia y DetalleEvento

- Objetivo: usar el nuevo sidebar.
- Archivos: `src/pages/Noticias/DetalleNoticia.jsx`, `src/pages/Eventos/DetalleEvento.jsx`.
- Pasos:
  1. `DetalleNoticia`: eliminar `NoticiasRelacionadas` interno, usar `<RelacionadosSidebar titulo="Noticias relacionadas" icono={<FaNewspaper/>} grupos={relacionadas.grupos || []} linkBase="/noticias/" />`. Manejar fallback: si la respuesta es lista plana, envolver como un unico grupo "General".
  2. `DetalleEvento`: idem con `<RelacionadosSidebar titulo="Eventos relacionados" icono={<FaCalendarAlt/>} ... />` y cambiar la llamada de `api.get('/eventos/')` a `api.get('/eventos/${eventoId}/relacionados/')`.
  3. Eliminar importes no usados de `FaCalendarAlt`/`FaNewspaper` si quedan inutilizados.
- Verificacion: `npm run build`, smoke en dev.
- Criterio de exito: las paginas cargan y la sidebar muestra grupos por categoria.

### Task 5: Verificacion final

- `python manage.py check`, `python -m pytest apps/content -q` (backend).
- `npm run build`, `npm run dev` (frontend).
- Reportar resultados.
