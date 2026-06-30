# Plan: Hardening del banner de cookies (frontend)

> **Para Hermes:** Implementar este plan micro-tarea por micro-tarea.
> Las micro-tareas son independientes entre sí salvo la #1 (que es prerequisito de las demás) y #3-#4 (que dependen de la firma `open()` expuesta por #1).

**Goal:** Cerrar las 10 vulnerabilidades / huecos de compliance listados en el audit `audit-cookies-2026-06-29.md` sin tocar backend ni romper el resto del frontend.

**Architecture:**
- Refactorizar `BannerCookies.jsx` para que:
  - Exporte un singleton store (custom event) que cualquier botón "Administrar cookies" pueda disparar.
  - Guarde `{ preferencias, politica_version, fecha, fuente }` en `localStorage` con versionado.
  - Re-muestre el banner si la `version` guardada no coincide con la `version` de la página legal servida por el backend (best-effort, no bloqueante).
  - Escuche el `storage` event para sincronizar entre pestañas.
  - Respete `navigator.doNotTrack` y `globalPrivacyControl`.
  - Implemente el guardado de la decisión con `try/catch` y fallback a `sessionStorage` en modo incognito de Safari.
  - Cargue condicionalmente `<script>` externos (helper `loadConditionalScript`).
- Añadir un botón "Administrar cookies" en `Footer.jsx` y en la tab "Seguridad" de `Perfil.jsx` que dispare el re-apertura del banner.
- Añadir `<noscript>` específico para cookies en `index.html` (en adición al genérico).

**Tech Stack:** React 19 + Vite, localStorage/sessionStorage, custom events, sin nuevas dependencias.

---

## Estado

- Estado: APPROVED
- Requiere aprobacion humana: SI (audit READY_FOR_PLAN, usuario indico "implementa las mejoras necesarias")
- Fecha: 2026-06-29
- Tecnologia: Frontend React (comunidad_zapotal_frontend)

## Objetivo

Cubrir los 10 hallazgos del audit `audit-cookies-2026-06-29.md` mediante cambios **exclusivamente frontend**, sin tocar backend, sin migraciones, sin nuevas dependencias, sin romper consumidores.

## No objetivos

- No se crea modelo backend `CookieConsent`. (Riesgos #7-#8 del audit; se marcan como PENDIENTE para un plan backend posterior).
- No se integra CMP homologado. (Riesgo #9 del audit; sigue pendiente).
- No se cambian rutas, ni contratos API, ni el sistema de auth.
- No se modifica `api.js` ni `AuthContext.jsx`.

## Riesgos del audit cubiertos (numeracion del audit)

| # | Riesgo | Como se cubre |
|---|---|---|
| 1 | Sin UI para reabrir/cambiar decision | Botón en Footer y en Perfil (Seguridad) que dispara `openBannerCookies()`. |
| 2 | `localStorage` no sincroniza entre pestanas | Listener de `storage` event; al cambiar, otra pestaña abre/actualiza el banner. |
| 3 | Toggle "Analiticas" no controla nada | Helper `loadConditionalScript(url, categoria)` que gatea por `localStorage.zapotal_cookies_pref.analiticas`. |
| 4 | Sin versionado de politica | Se guarda `politica_version`; al montar, si la pagina legal `/paginas-legales/cookies/` reporta una `version` distinta, se vuelve a mostrar el banner. |
| 5 | Sin timestamp de la decision | Se guarda `fecha` ISO 8601 en el objeto de preferencias. |
| 6 | Sin DNT / GPC | Si `navigator.doNotTrack === '1'` o `navigator.globalPrivacyControl === true`, se setea `analiticas: false` por defecto y se sugiere rechazar. |
| 10 | `pointer-events: none` en contenedor | Se mantiene la intencion (no bloquear scroll), pero se sube el `z-index` por encima del modal de LoaderOverlay (`>= 9999`) y se documenta. |

Riesgos **NO cubiertos** (requieren backend o CMP, fuera del alcance):

- #7, #8 (modelo `CookieConsent` y endpoint revocacion): requieren Django; se dejan como PENDIENTE.
- #9 (CMP homologado): decision comercial, no tecnica.
- #11-#15 del audit: baja severidad; #13 (tests E2E) queda como recomendacion.

## Archivos permitidos

- `comunidad_zapotal_frontend/src/components/Legal/BannerCookies.jsx` (modificar)
- `comunidad_zapotal_frontend/src/components/Legal/BannerCookies.css` (modificar)
- `comunidad_zapotal_frontend/src/components/Footer.jsx` (modificar)
- `comunidad_zapotal_frontend/src/components/Footer.css` (modificar)
- `comunidad_zapotal_frontend/src/pages/Perfil/Perfil.jsx` (modificar)
- `comunidad_zapotal_frontend/src/pages/Perfil/Perfil.css` (modificar)
- `comunidad_zapotal_frontend/index.html` (modificar, anadir `<noscript>` de cookies)
- `comunidad_zapotal_frontend/src/hooks/useBannerCookies.js` (crear, hook publico)

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/AuthContext.jsx`
- `comunidad_zapotal_frontend/src/App.jsx` (NO se toca el montaje del banner; el store vive en su propio modulo)
- `comunidad_zapotal_backend/**`
- Cualquier otro componente o pagina

## Skills aplicadas

- `writing-plans` (este documento)
- Politica `stop-rules.md`
- Politica `skill-policy.md`
- Template `implementation-task-template.md`

## Micro-tareas

### Task 1: Refactor de `BannerCookies.jsx` (storage v2 + helpers publicos)

**Objetivo:** Que el banner soporte versionado, timestamp, sync entre pestanas, DNT/GPC y exponga una API publica (`openBannerCookies`, `loadConditionalScript`, constante `STORAGE_KEY`).

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/components/Legal/BannerCookies.jsx`
- Modificar: `comunidad_zapotal_frontend/src/components/Legal/BannerCookies.css` (subir z-index a 10000; ajustar pointer-events del inner para que NO queden inputs bloqueados por overlays futuros)

**Pasos:**
1. Escribir en `BannerCookies.jsx`:
   - Constante `STORAGE_KEY = 'zapotal_cookies_pref'` y `STORAGE_VERSION = 2`.
   - `readPreference()` que retorna `null` si `version` no es la actual (migracion silenciosa: re-mostrar banner).
   - `writePreference(prefs, fuente)` que guarda `{ version: 2, preferencias: { necesarias, preferencias, analiticas }, politica_version, fecha, fuente }`. `fuente` ∈ `'banner' | 'perfil' | 'footer' | 'api' | 'auto-dnt' | 'auto-gpc' | 'auto-version'`.
   - Helper publico `openBannerCookies({ desde } = {})` que dispara un `CustomEvent('zapotal:cookies:open', { detail: { desde } })` y queda escuchado por el banner.
   - Helper publico `loadConditionalScript(src, categoria)` que:
     - Lee `localStorage[STORAGE_KEY]`.
     - Si la `categoria` (`'analiticas' | 'preferencias'`) esta en `false` o no hay decision previa y `DNT/GPC` estan activos, **no** inyecta el `<script>`.
     - Si esta permitida, inyecta dinamicamente. Devuelve un booleano.
   - `useEffect` principal:
     - Lee `localStorage`.
     - Si no hay decision guardada o `version` desactualizada: `setVisible(true)`.
     - Si hay decision guardada: `setPrefs(decision.preferencias)`, `setVisible(false)`.
     - Si `DNT/GPC` activos y la decision previa permitia analiticas: forzar `analiticas=false` y guardar con `fuente='auto-dnt'` o `'auto-gpc'`.
     - Listener de `window`:
       - `storage` (con `key === STORAGE_KEY`): re-leer y, si la otra pestana decidio, abrir/ocultar el banner segun corresponda.
       - `zapotal:cookies:open`: `setVisible(true)`, `setShowPersonalizar(true)`.
   - `handleAceptarTodo` / `handleRechazar` / `handleGuardar` usan `writePreference(prefs, 'banner')` con `politica_version` y `fecha`.
   - Anadir consulta **best-effort** a `/paginas-legales/cookies/` para obtener `version`. Si la `politica_version` guardada difiere, forzar `setVisible(true)` con `fuente='auto-version'`. Si la consulta falla (timeout, 404), no mostrar banner; el failure no debe romper la UI.
2. CSS: subir `.bc-banner { z-index: 10000; }` y documentar inline que esto lo deja por encima de `LoaderOverlay` (z 900) y `Navbar` (z 1000-1100).
3. Verificacion: `cd comunidad_zapotal_frontend && npm run build` debe pasar sin errores.

**Comando de verificacion:**
```bash
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_frontend"
npm run build
```

**Criterio de exito:** Build pasa, sin warnings nuevos. Banner renderiza, persiste, y expone `openBannerCookies` + `loadConditionalScript` en el export.

**Criterio de rollback:** Revertir los cambios en `BannerCookies.jsx` y `BannerCookies.css` (git restore).

---

### Task 2: Hook publico `useBannerCookies` + boton en `Footer.jsx`

**Objetivo:** Permitir que el Footer dispare la re-apertura del banner sin acoplarse al store interno.

**Archivos:**
- Crear: `comunidad_zapotal_frontend/src/hooks/useBannerCookies.js` (exporta `useBannerCookies()` con `{ open, prefs, hasDecision, reset, loadConditionalScript }`).
- Modificar: `comunidad_zapotal_frontend/src/components/Footer.jsx` (anadir un item "Administrar cookies" en la seccion "Legal", debajo del link a `/cookies`).
- Modificar: `comunidad_zapotal_frontend/src/components/Footer.css` (estilo del boton de admin, debe verse identico a un link `<li><a>` pero con `cursor: pointer` y `type="button"`).

**Pasos:**
1. Crear `useBannerCookies.js`:
   - `open(desde)` -> dispara el CustomEvent.
   - `prefs` -> lee `localStorage` reactivamente (listener).
   - `hasDecision` -> booleano derivado.
   - `reset()` -> limpia `localStorage[STORAGE_KEY]` y dispara `open('reset')`.
   - `loadConditionalScript` -> re-export del helper.
2. En `Footer.jsx`: importar `useBannerCookies`, anadir debajo del link "Politica de Cookies":
   ```jsx
   <li>
     <button type="button" className="footer-admin-cookies" onClick={() => open('footer')}>
       <FaCookieBite /> Administrar cookies
     </button>
   </li>
   ```
3. En `Footer.css`: anadir `.footer-admin-cookies` con la misma tipografia/color que los `<a>` y `background: transparent; border: 0; padding: 0; text-align: left; cursor: pointer;`.
4. Verificacion: `npm run build`.

**Comando de verificacion:**
```bash
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_frontend"
npm run build
```

**Criterio de exito:** Boton aparece en el footer en `www.comunidadzapotal.org/` (o localhost) y, al hacer click, abre el banner en modo personalizar con las preferencias precargadas.

**Criterio de rollback:** Revertir los 3 archivos.

---

### Task 3: Boton "Administrar cookies" en Perfil (tab Seguridad)

**Objetivo:** Que un usuario logueado pueda revisar y cambiar su decision desde su perfil (cumple hallazgo #1 y requisito GDPR/LPDP de "facilidad de retiro").

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Perfil/Perfil.jsx` (anadir card en tab "Seguridad" debajo de los cambios de password/2FA).
- Modificar: `comunidad_zapotal_frontend/src/pages/Perfil/Perfil.css` (estilos del card, coherentes con `.perfil-security-card`).

**Pasos:**
1. En `Perfil.jsx`: importar `useBannerCookies` y, dentro de la tab "Seguridad" (buscar el render condicional `tab === 'seguridad' && (...)`), anadir:
   ```jsx
   <div className="perfil-security-card perfil-cookies-card">
     <h3><FaCookieBite /> Preferencias de cookies</h3>
     <p>Tu decision actual: {resumenDecision}.</p>
     <button type="button" className="perfil-btn" onClick={() => openBanner('perfil')}>
       Administrar cookies
     </button>
     {hasDecision && (
       <button type="button" className="perfil-btn perfil-btn--ghost" onClick={() => reset()}>
         Restablecer y volver a preguntar
       </button>
     )}
   </div>
   ```
2. `resumenDecision` se calcula a partir de `prefs`: si todas true -> "Aceptaste todas"; si solo necesarias -> "Rechazaste las no esenciales"; etc.
3. CSS: `.perfil-cookies-card { ... }` (reusa `.perfil-security-card`).
4. Verificacion: `npm run build`.

**Comando de verificacion:**
```bash
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_frontend"
npm run build
```

**Criterio de exito:** En `/perfil?tab=seguridad` aparece un card "Preferencias de cookies" con el boton "Administrar cookies" que abre el banner. Si ya hay decision, aparece tambien "Restablecer y volver a preguntar".

**Criterio de rollback:** Revertir los 2 archivos.

---

### Task 4: `<noscript>` de cookies + cleanup final

**Objetivo:** Avisar al usuario sin JS que no podemos registrar su decision de cookies (cumple parcialmente riesgo #12 del audit) y dejar el repo limpio.

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/index.html` (anadir un `<noscript>` adicional, especifico para cookies).

**Pasos:**
1. En `index.html`, dentro de `<body>`, **antes** del `<noscript>` genérico actual, anadir:
   ```html
   <noscript>
     <div style="padding:16px;background:#fff8e1;border:1px solid #d4a72c;text-align:center;font-family:sans-serif;">
      Este sitio usa cookies no esenciales que requieren JavaScript. Si lo tienes
      desactivado, no se registrara tu preferencia de cookies. Consulta nuestra
      <a href="/politica-cookies">Politica de Cookies</a>.
    </div>
   </noscript>
   ```
2. Verificacion: `npm run build` (debe seguir generando el bundle).

**Comando de verificacion:**
```bash
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_frontend"
npm run build
```

**Criterio de exito:** El `<noscript>` aparece en el HTML estatico generado en `dist/index.html` y `dist/index.html` se genera sin errores.

**Criterio de rollback:** Revertir `index.html`.

---

## Verificacion final (post todas las tasks)

1. `cd comunidad_zapotal_frontend && npm run build` -> exit 0, sin warnings nuevos.
2. `cd comunidad_zapotal_frontend && npm run lint` -> sin errores introducidos por este cambio.
3. Crear post-implementation review en `agents-workflow/comunidad_zapotal_frontend/post-implementation/review-hardening-cookies-2026-06-29.md`.

## Riesgos residuales

- Si la consulta a `/paginas-legales/cookies/` es lenta, el banner se mostrara con un pequeno delay. Esto se mitiga con `Promise.race` + timeout 1.5s, **best-effort**.
- El helper `loadConditionalScript` solo se usa desde codigo. No se cambia ningun `<script>` actual del proyecto (no hay scripts de analytics). Queda listo para uso futuro.
- `DNT`/`GPC` cambian a `analiticas=false` solo si no hay decision previa o si la decision previa permitia. Si el usuario ya decidio y el toggle estaba activo, **se respeta** la decision explicita y no se sobreescribe silenciosamente.
