# Audit: Quitar "Publicado:" del meta-row del detalle de evento

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Autor/agente: opencode-go/minimax-m3
- Tecnologia: frontend React (Vite)

## Objetivo

Reemplazar la linea "Publicado: dd mmm yyyy" del meta-row inferior
del detalle de evento por el mismo patron que el detalle de
noticia: ojo de visualizaciones + fecha, sin el prefijo "Publicado:"
(redundante con el bloque verde superior que ya muestra "Fecha: ...").

## Alcance

### Incluye

Frontend:

- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  - Sin cambios (ya tiene el patron correcto: ojo + fecha).
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  - Linea 781: cambiar `<span className="yt-desc-fecha">Publicado: {formatFecha(evento.fecha)}</span>`
    por `<span className="yt-desc-fecha">{formatFecha(evento.fecha)}</span>`.
  - Linea 780: ya muestra el ojo + visualizaciones (de la tarea
    anterior). Se conserva.

### No incluye

- No se toca el backend.
- No se toca el bloque verde superior con "Fecha:" y "Ubicacion:".
- No se cambia `formatFecha`, `FaEye` ni los CSS.
- No se cambia el detalle de noticias.
- No se cambian otras pantallas.

## Contexto leido

- `AGENTS.md` (raiz)
- `graphify.md` (raiz)
- `comunidad_zapotal_frontend/AGENTS.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/templates/implementation-plan-template.md`
- `agents-workflow/AGENTS.md`

Archivos inspeccionados:

- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  (lineas 766-769: meta-row con ojo + fecha, patron correcto).
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  (lineas 778-781: meta-row con ojo + "Publicado: ...").

## Estado actual

Detalle de noticia (linea 769):
```jsx
<span className="yt-desc-fecha">{formatFecha(noticia.fecha_publicacion)}</span>
```

Detalle de evento (linea 781):
```jsx
<span className="yt-desc-fecha">Publicado: {formatFecha(evento.fecha)}</span>
```

El detalle de evento ya muestra el bloque verde con "Fecha: ..." y
"Ubicacion: ..." arriba. El "Publicado: ..." de abajo es redundante.

## Riesgos

- Bajo: cambio cosmético, una sola linea. No toca logica.
- Bajo: el campo `evento.vistas` ya viene del backend (de la tarea
  anterior) y ya se renderiza correctamente con `FaEye`.

## Skills recomendadas

- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`

## Recomendacion

Cambiar la linea 781 de `DetalleEvento.jsx` para que muestre solo
la fecha, igual que el detalle de noticia.

## Verificacion sugerida

```bash
npm run build
# build con Vite debe pasar sin errores
```

Verificacion visual: abrir el detalle de un evento y confirmar que
el meta-row inferior muestra "👁 N visualizaciones  dd mmm yyyy"
(sin "Publicado:"), igual que el detalle de noticia.
