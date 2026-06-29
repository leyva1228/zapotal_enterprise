# Post-Implementation Review: Logica de conteo de visualizaciones robusta

## Estado

- Estado: COMPLETED
- Fecha: 2026-06-28
- Tecnologia: frontend React (Vite)

## Resumen

Se refactorizo la logica de `incrementar_vistas` en `DetalleNoticia`
y `DetalleEvento` para que use `localStorage` siempre (no
`sessionStorage`), con un ID anonimo persistente por navegador
(generado via nuevo hook `useAnonymousId`) y el ID de usuario para
logueados (cualquier tipo: COMUNERO, ADMIN, INVITADO). La regla
"ya vio" se chequea por prefijo, evitando doble conteo al cambiar
entre anonimo y logueado en el mismo navegador.

## Archivos modificados

Frontend:

- `comunidad_zapotal_frontend/src/hooks/useAnonymousId.js` (nuevo)
  - Hook reutilizable que genera/lee un UUID v4 en
    `localStorage` bajo `zapotal_anon_id`. Fallback a
    `Math.random()` + timestamp si `crypto.randomUUID()` no esta
    disponible. Retorna `null` en SSR.
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  - Importa `useAnonymousId`.
  - `useEffect` de `incrementar_vistas` reescrito: usa
    `localStorage` siempre, discriminador `user_<id>` o
    `anon_<anonId>`, regla "ya vio" por prefijo.
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  - Idem para eventos.

## Comandos ejecutados y resultado

```bash
npm run build
# built in 8.87s - sin errores
```

## Funcionalidad preservada

- Backend: sin cambios. El endpoint `POST /noticias/<id>/incrementar_vistas/`
  y `POST /eventos/<id>/incrementar_vistas/` sigue siendo atomico
  con `F('vistas') + 1`.
- Render visual: sin cambios. Ya muestra "👁 N visualizaciones  dd mmm yyyy"
  (de la tarea anterior).
- Reacciones, comentarios, favoritos: sin cambios.

## Politica implementada

| Escenario | Comportamiento |
|---|---|
| Anonimo ve noticia/evento por primera vez | Cuenta 1 vez |
| Anonimo recarga la misma pagina | NO cuenta (ya existe clave `anon_<X>`) |
| Anonimo cierra browser y vuelve a abrir | NO cuenta (localStorage persiste) |
| Anonimo se loguea como COMUNERO y ve misma pagina | NO cuenta (ya existe clave `anon_<X>`) |
| COMUNERO ve noticia/evento por primera vez | Cuenta 1 vez |
| COMUNERO recarga | NO cuenta (ya existe `user_<id>`) |
| COMUNERO cierra sesion y ve como anonimo | NO cuenta (ya existe `user_<id>`) |
| ADMIN ve noticia/evento por primera vez | Cuenta 1 vez |
| INVITADO (global) ve noticia/evento por primera vez | Cuenta 1 vez |
| Diferentes usuarios en el mismo navegador (cybercafe) | Cada uno cuenta 1 vez (diferente `user_<id>`) |
| Usuario limpia localStorage | Vuelve a contar (esperado) |

## Decisiones tecnicas relevantes

1. **Hook `useAnonymousId` separado.** Reutilizable desde cualquier
   pagina que necesite tracking anonimo (futuro: noticias vistas,
   eventos vistos, etc.).

2. **Regla "ya vio" por prefijo, no por clave exacta.** Esto cubre
   el caso de cambio de sesion (anon -> logueado -> anon) sin
   necesidad de migrar claves. Si existe CUALQUIER clave con el
   prefijo `visto_<tipo>_<id>_`, NO se cuenta.

3. **`localStorage` siempre, no `sessionStorage`.** La logica
   anterior usaba `sessionStorage` para anonimos, lo que permitia
   doble conteo al cerrar/abrir el browser. Ahora es consistente
   con logueados: persistente.

4. **AnonId estable entre renders y entre cambios de sesion.** El
   `useAnonymousId` usa `useMemo([])` para que el ID no cambie
   durante la vida del componente. Asi, si el usuario pasa de
   anonimo a logueado, el `anonId` sigue siendo el mismo (aunque
   ya no se use como discriminador principal).

5. **Fallback para browsers antiguos.** Si `crypto.randomUUID()`
   no esta disponible, se usa `Math.random() + Date.now()` como
   fallback. Suficientemente unico para el proposito.

## Ruta del documento operativo

- `agents-workflow/comunidad_zapotal_frontend/audits/active/2026-06-28-logica-conteo-visualizaciones.md`
- `agents-workflow/comunidad_zapotal_frontend/implementation-plans/active/2026-06-28-logica-conteo-visualizaciones.md`
- `agents-workflow/comunidad_zapotal_frontend/post-implementation/2026-06-28-logica-conteo-visualizaciones.md` (este archivo)
