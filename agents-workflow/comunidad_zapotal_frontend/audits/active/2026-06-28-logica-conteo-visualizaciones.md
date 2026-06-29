# Audit: Logica de conteo de visualizaciones robusta

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Autor/agente: opencode-go/minimax-m3
- Tecnologia: frontend React (Vite)

## Objetivo

Mejorar la logica de conteo de visualizaciones para que:

1. **Usuarios anonimos** (sin sesion): cuenten una vez POR NAVEGADOR
   (persistente, no por sesion de browser). Si cierran el browser y
   vuelven a abrir, NO se cuenta de nuevo.
2. **Usuarios autenticados** (COMUNERO, ADMIN, INVITADO): cuenten una
   vez POR USUARIO. Si un COMUNERO entra a la noticia, cierra sesion
   y vuelve a entrar logueado, NO se cuenta de nuevo.
3. Misma logica para noticias y eventos (mismo helper reutilizable).

## Alcance

### Incluye

Frontend:

- `comunidad_zapotal_frontend/src/hooks/useDelayedLoading.js`
  - NO se toca. (es de loading, no tiene relacion)
- `comunidad_zapotal_frontend/src/hooks/` (nuevo directorio si no existe)
  - Crear `useAnonymousId.js`: hook que genera y persiste un ID
    anonimo unico en `localStorage` bajo la clave
    `zapotal_anon_id`. Si ya existe, lo devuelve. Si no, genera
    un UUID v4 y lo guarda.
- `comunidad_zapotal_frontend/src/pages/Noticias/DetalleNoticia.jsx`
  - Importar el hook `useAnonymousId`.
  - Reemplazar la logica actual de `useEffect` para `incrementar_vistas`
    por una que use:
    - `localStorage` SIEMPRE (no `sessionStorage`).
    - Clave `visto_noticia_<id>_user_<anonId>` para anonimos.
    - Clave `visto_noticia_<id>_user_<userId>` para autenticados
      (cualquier tipo: COMUNERO, ADMIN, INVITADO).
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  - Idem para eventos, con clave `visto_evento_<id>_user_<id>`.

### No incluye

- No se toca el backend (la logica de incremento atomic con
  `F('vistas') + 1` ya es correcta).
- No se cambia el serializer.
- No se cambia `src/api.js`.
- No se cambia el render visual (ya muestra ojo + visualizaciones + fecha).
- No se cambian otras pantallas.
- No se cambia el `ReloadContext` ni el auth.
- No se agrega telemetria/servidor de tracking.

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
  (lineas 301-318: useEffect de incrementar_vistas; 373-377:
  hasPermission para INVITADO).
- `comunidad_zapotal_frontend/src/pages/Eventos/DetalleEvento.jsx`
  (lineas 299-316: useEffect de incrementar_vistas; 371-375:
  hasPermission para INVITADO).

## Estado actual

### Logica actual (linea 302-318 en DetalleNoticia, 300-316 en DetalleEvento):

```javascript
useEffect(() => {
  if (!noticiaId || !noticia) return;
  const claveLocal = estaAuth && usuarioId
    ? `visto_noticia_${noticiaId}_user_${usuarioId}`
    : `visto_noticia_${noticiaId}_session`;
  const storage = (typeof window !== "undefined")
    ? (estaAuth && usuarioId ? window.localStorage : window.sessionStorage)
    : null;
  if (storage && !storage.getItem(claveLocal)) {
    api.post(`/noticias/${noticiaId}/incrementar_vistas/`)
      .then(({ data }) => {
        setNoticia((prev) => prev ? { ...prev, vistas: data.vistas } : prev);
        try { storage.setItem(claveLocal, new Date().toISOString()); } catch (e) { /* noop */ }
      })
      .catch(err => console.warn("Error al incrementar vistas:", err));
  }
}, [noticiaId, noticia, estaAuth, usuarioId]);
```

### Problemas identificados:

1. **Anonimos usan `sessionStorage`**: el contador se resetea cuando
   el browser cierra. Si un usuario anonimo abre la noticia, la
   cuenta sube. Si cierra el browser, abre de nuevo la misma
   noticia, la cuenta vuelve a subir. NO deberia.
2. **No hay manejo explicito de usuarios INVITADO** ("global"): un
   usuario INVITADO autenticado cae en la rama `estaAuth && usuarioId`
   (porque si tiene `usuarioId`), asi que usa `localStorage` con
   `user_<id>`. Esto en realidad funciona bien (se cuenta una vez
   por usuario INVITADO), pero el codigo no lo documenta ni lo
   distingue de COMUNERO/ADMIN.
3. **No hay helper reutilizable**: la misma logica esta duplicada
   en DetalleNoticia y DetalleEvento. Si cambia la politica, hay
   que tocar dos lugares.

### Lo que el usuario pide:

> "que aumente solo cuando sea un nuevo usuario anotino o global que
> si podra ver la noticia pero no comentar ni reaccionar, que
> cuando tambien un usuario de tipo comunero logueado entre al
> detalle por primera vez, si cierra sesion y vuelve a entrar
> loguado a la misma noticia no contara como una visualizacion
> mas. [...] esta mejora de el conteo tambien debe contar solo
> una vez en el detalle para el usuario de tipo admin al igual
> que el usuario de tipo comunero"

Traduccion:
- Anonimo: 1 vez por navegador (persistente).
- Global/INVITADO: 1 vez por usuario.
- COMUNERO: 1 vez por usuario.
- ADMIN: 1 vez por usuario.

Esto es EXACTAMENTE lo que deberia hacer la logica, pero con
`localStorage` siempre (no `sessionStorage` para anonimos) y con
un ID anonimo persistente.

## Solucion propuesta

1. **Nuevo hook `useAnonymousId`** en
   `comunidad_zapotal_frontend/src/hooks/useAnonymousId.js`:
   - Lee/genera un UUID v4 en `localStorage` bajo
     `zapotal_anon_id`.
   - Lo expone via `useMemo` para que sea estable durante la vida
     del componente.
   - Si no hay `window` (SSR), devuelve `null`.

2. **Refactor del useEffect** en DetalleNoticia y DetalleEvento:
   - Determinar `identificador`:
     - Si `estaAuth && usuarioId`: `user_<usuarioId>` (cubre
       COMUNERO, ADMIN e INVITADO por igual).
     - Si no: `anon_<anonId>` (donde `anonId` viene del hook).
   - Clave: `visto_<tipo>_<id>_<identificador>`.
   - Storage: SIEMPRE `localStorage` (no `sessionStorage`).
   - Si la clave NO existe en `localStorage`: llamar al endpoint
     de incremento y guardar la clave.

3. **Reaccion a cambios de sesion** (logout/login): el `useEffect`
   ya tiene `[noticiaId, noticia, estaAuth, usuarioId]` como deps.
   Si un usuario cierra sesion y abre la misma noticia, el
   `identificador` cambia de `user_<X>` a `anon_<Y>`, lo que
   hace que la clave sea diferente. Para evitar doble conteo en
   ese caso, la logica debe ser:
   - Si el usuario YA VIO la noticia como anonimo (clave
     `anon_<Y>` existe) y ahora esta logueado, NO contar de
     nuevo (porque ya conto como anonimo).
   - Si el usuario YA VIO la noticia como logueado y ahora esta
     deslogueado, NO contar de nuevo (porque ya conto como
     logueado).

   Esto se logra con la siguiente regla: si la clave para el
   identificador actual NO existe PERO existe una clave "previa"
   (anonimo o user) que ya vio la noticia, NO contar.

   En la practica, esto se puede simplificar: usamos una sola
   clave por noticia que NO depende del identificador:
   `visto_<tipo>_<id>` (sin sufijo de usuario). Pero esto rompe
   el caso de "varios usuarios en el mismo navegador" (ej:
   cybercafe). Compromiso:
   - Si el usuario esta logueado: usar `user_<id>`.
   - Si el usuario no esta logueado: usar `anon_<id>`.
   - Si el usuario pasa de logueado a deslogueado, el
     `identificador` cambia. Para evitar doble conteo en ese
     flujo especifico (cerrar sesion), al desloguearse el
     `anon_<id>` del hook NO deberia cambiar (es estable por
     navegador). Entonces:
     - Caso 1: anonimo ve noticia -> clave `visto_<tipo>_<id>_anon_<X>`.
     - Caso 2: se loguea como COMUNERO -> clave
       `visto_<tipo>_<id>_user_<Y>`. SI existe la clave anon,
       NO contar.
     - Caso 3: cierra sesion -> clave
       `visto_<tipo>_<id>_anon_<X>`. SI existe la clave user
       del usuario anterior, NO contar.

   Esto ultimo es complejo. Para simplificar y cumplir con el
   requisito del usuario, usamos la siguiente regla:
   - Si existe CUALQUIER clave `visto_<tipo>_<id>_*` para este
     item, NO contar.

   Esto cubre todos los casos:
   - Un mismo navegador (anonimo) ve la noticia: cuenta 1 vez.
   - El mismo navegador (anonimo) recarga: NO cuenta (ya existe).
   - El mismo navegador se loguea: NO cuenta (ya existe la
     clave anon).
   - El usuario se desloguea: NO cuenta (ya existe la clave user
     del usuario anterior o la clave anon si ya existia).
   - Diferentes usuarios en el mismo navegador (cybercafe):
     cuentan cada uno 1 vez (porque tienen diferentes `user_<id>`).

   Implementacion: en el useEffect, antes de incrementar, listar
   todas las claves con prefijo `visto_<tipo>_<id>_` y si hay
   alguna, NO incrementar.

## Riesgos

- Bajo: el cambio es solo frontend. El backend no se toca.
- Bajo: la logica anterior usaba `sessionStorage` para anonimos,
  lo que era MENOS restrictivo (contaba mas veces). La nueva
  logica contara MENOS veces (lo que es lo que el usuario quiere).
- Bajo: si el usuario limpia su `localStorage`, el contador se
  resetea para ese navegador. Esto es aceptable y consistente
  con el requisito.
- Medio: el helper `crypto.randomUUID()` no esta disponible en
  todos los browsers antiguos. Fallback: `Math.random()` + timestamp
  + un contador en `localStorage` (suficientemente unico para
  este proposito).

## Skills recomendadas

- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`

## Recomendacion

1. Crear `useAnonymousId` hook.
2. Refactorizar ambos `useEffect` para usar el hook + `localStorage`
   + la regla de "no contar si ya existe cualquier clave vista".
3. NO tocar el backend.
4. Verificar con `npm run build`.

## Verificacion sugerida

```bash
npm run build
# build con Vite debe pasar sin errores
```

Verificacion visual/manual (con DevTools):
1. Abrir detalle de noticia como anonimo -> incrementa.
2. Recargar -> NO incrementa.
3. Cerrar browser, abrir de nuevo -> NO incrementa.
4. Login como COMUNERO, ver misma noticia -> NO incrementa.
5. Logout, ver misma noticia como anonimo -> NO incrementa.
6. Login como ADMIN en otro browser, ver misma noticia ->
   incrementa (es otro navegador).
