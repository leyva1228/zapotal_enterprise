# Audit: Unificar diseno Login/Registro con el oro del navbar

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Autor/agente: opencode-go/minimax-m3
- Tecnologia: frontend React (Vite) + Tailwind

## Objetivo

Unificar Login y Registro:

1. Cambiar el "dorado casi dorado" del Login por el **mismo oro
   del navbar** (`--nb-dorado: #b8963e` / `--nb-dorado-light: #d4ae5a`).
2. Que el Registro tenga **diseno identico** al Login (mismo
   layout, mismos estilos, mismas fuentes). Hoy son distintos.
3. Que **ambos** tengan imagen de fondo en la parte izquierda
   (panel hero). Hoy solo Registro la tiene; Login usa un overlay
   verde sin imagen.

## Alcance

### Incluye

Frontend:

- `comunidad_zapotal_frontend/src/pages/Login/Login.jsx`
  - Cambiar clases `accent-*` por los hexes del navbar (`#b8963e`,
    `#d4ae5a`) en los puntos donde se usa el dorado:
    - `bg-accent-400` (linea del adorno) -> `#d4ae5a`
    - `text-accent-300` (icono de hoja) -> `#b8963e`
  - Agregar imagen de fondo en el `aside` del hero
    (`bg-hero-gradient` actual es solo gradiente verde).
  - Opcional: usar la misma imagen que Registro
    (`/img/login/Union-fondo login.jpg`).
- `comunidad_zapotal_frontend/src/pages/Registro/Registro.jsx`
  - Reemplazar el `rg-*` CSS class system (CSS custom de 600
    lineas) por las mismas clases Tailwind que usa Login, para
    que ambos compartan la misma estetica.
  - Mantener el hero con imagen de fondo (ya lo tiene, pero
    verificar que use el mismo path que Login).
  - Conservar la logica de registro (validaciones, DNI,
    Turnstile, etc.) - **solo diseno**.
- `comunidad_zapotal_frontend/src/index.css` (o equivalente)
  - Si hace falta, agregar variables CSS para los colores del
    navbar (`--nb-dorado: #b8963e` y `--nb-dorado-light: #d4ae5a`)
    para que ambos componentes las referencien.
- `comunidad_zapotal_frontend/src/pages/Registro/Registro.css`
  - Marcar como deprecated (mantenido solo por compatibilidad
    de imports) o eliminarlo si no hay mas referencias.

### No incluye

- No se cambia la logica de autenticacion (login, registro, OTP,
  2FA, validaciones backend).
- No se cambia el backend.
- No se cambia el navbar ni otros componentes.
- No se cambian las dependencias (Tailwind ya esta).
- No se migra la base de datos.

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

- `comunidad_zapotal_frontend/src/pages/Login/Login.jsx` (374 lineas,
  usa Tailwind classes con `accent-*` para el dorado).
- `comunidad_zapotal_frontend/src/pages/Login/Login.css` (VIRTUAL,
  solo 2 lineas de comentario).
- `comunidad_zapotal_frontend/src/pages/Registro/Registro.css` (617
  lineas, sistema CSS custom con `--gold: #b8912a`).
- `comunidad_zapotal_frontend/tailwind.config.js` (paleta: `accent`
  usa `#b8972a` y el navbar usa `#b8963e` - diferencia minima pero
  visible al ojo).
- `comunidad_zapotal_frontend/src/components/Navbar.css` (lineas
  9-13: `--nb-dorado: #b8963e`, `--nb-dorado-light: #d4ae5a`).
- `comunidad_zapotal_frontend/public/img/login/` (tiene 2
  imagenes: `fondo_login.png` y `Union-fondo login.jpg`).

## Estado actual

### Login (Login.jsx)
- Layout: `flex flex-col md:flex-row` - columna en movil, fila en
  desktop. **NO usa grid 1fr 1fr como Registro**.
- Hero (izquierda): `bg-hero-gradient` - **solo gradiente verde**,
  **SIN imagen de fondo**.
- Dorado: usa `bg-accent-400` y `text-accent-300` (del Tailwind
  config: `#e2b52a` y `#eecb53` respectivamente). Estos son
  diferentes al oro del navbar (`#b8963e` / `#d4ae5a`).
- Boton: `bg-primary-700 hover:bg-primary-800` (verde).

### Registro (Registro.jsx + Registro.css)
- Layout: `grid-template-columns: 1fr 1fr` con `.rg` class.
- Hero (izquierda): **SI tiene imagen de fondo**
  (`/img/login/Union-fondo login.jpg`) con overlay gradiente.
- Dorado: usa `--gold: #b8912a` (variable CSS propia).
- Sistema CSS custom de 617 lineas.
- **Diseno y estructura distintos al Login** (mismo proposito
  pero diferentes clases, diferentes layout, diferentes
  detalles).

### Colores del navbar (referencia)
- Verde: `--nb-verde: #1a3209`, `--nb-verde-med: #243f0f`,
  `--nb-verde-claro: #3a6019`.
- Dorado: `--nb-dorado: #b8963e`, `--nb-dorado-light: #d4ae5a`.

## Skills recomendadas

- `react-expert` - implementacion en React/Tailwind
- `frontend-ui-engineering` - diseno y consistencia visual
- `impeccable` - auditoria y mejora de UI
- `incremental-implementation` - micro-tareas
- `verification-before-completion` - build + Playwright
- `code-review-and-quality` - revision del diff

## Recomendacion

1. Estandarizar ambos (Login y Registro) al mismo layout
   flexbox/Tailwind (mas simple que el grid custom del Registro).
2. Usar el oro del navbar (`#b8963e` / `#d4ae5a`) en ambos, via
   variables CSS o clases Tailwind.
3. Agregar la imagen de fondo (`/img/login/Union-fondo login.jpg`)
   al hero del Login.
4. Refactor del Registro: migrar de CSS custom a Tailwind para
   compartir el mismo "lenguaje visual" que el Login (y que
   cualquier futura pantalla publica pueda usar el mismo set
   de utilidades).
5. Verificar con Playwright que ambos renderizan correctamente.

## Verificacion sugerida

```bash
npm run build
# build con Vite debe pasar sin errores
```

Verificacion visual con Playwright:

```js
// Login: verificar que el hero tiene imagen de fondo y el
// dorado del adorno/icono es el del navbar.
await page.goto('http://localhost:5173/login');
const heroBg = await page.evaluate(() =>
  window.getComputedStyle(document.querySelector('aside'))
    .backgroundImage
);
console.log(heroBg); // debe incluir url('...Union-fondo login.jpg')

// Registro: mismo diseno que login.
await page.goto('http://localhost:5173/registro');
// comparar layout, fuentes, colores.
```
