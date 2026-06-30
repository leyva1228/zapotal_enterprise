# Post-implementation review: Hardening del banner de cookies (frontend)

- Estado: COMPLETED
- Fecha: 2026-06-29
- Tecnologia: Frontend React (comunidad_zapotal_frontend)
- Plan: `agents-workflow/comunidad_zapotal_frontend/implementation-plans/active/2026-06-29-hardening-banner-cookies.md`
- Audit origen: `agents-workflow/comunidad_zapotal_frontend/audits/active/audit-cookies-2026-06-29.md`

## Alcance implementado

Refactor del banner de cookies + helpers publicos + 2 botones de re-apertura (Footer y Perfil) + `<noscript>` defensivo, todo sin tocar backend ni contratos API.

## Archivos cambiados (resumen de diff)

| Archivo | Tipo | Resumen |
|---|---|---|
| `src/components/Legal/BannerCookies.jsx` | modificado | Refactor a storage v2 (version+timestamp+fuente), exporta `openBannerCookies`, `loadConditionalScript`, `getCookiePreferences`, `resetCookiePreferences`, `COOKIE_STORAGE_KEY`, `COOKIE_STORAGE_VERSION`. Agregados listeners de `storage` event, `zapotal:cookies:open`, `zapotal:cookies:changed`, soporte DNT/GPC, consulta best-effort a `/paginas-legales/cookies/` para versionado de politica, fallback a `sessionStorage` para Safari incognito. |
| `src/components/Legal/BannerCookies.css` | modificado | z-index 9999 -> 10000 (documentado inline por encima de LoaderOverlay/Navbar/ToastCenter). |
| `src/hooks/useBannerCookies.js` | creado | Hook publico reactivo para que Footer, Perfil y futuros componentes puedan abrir/resetear/consultar el banner y cargar scripts condicionales. |
| `src/components/Footer.jsx` | modificado | Boton "Administrar cookies" en la seccion "Legal" (debajo de Politica de Cookies). |
| `src/components/Footer.css` | modificado | Estilos `.footer-admin-cookies` (identico a un `<a>`, pero es `<button type="button">`); responsive ajustado. |
| `src/pages/Perfil/Perfil.jsx` | modificado | Import de `FaCookieBite` + `useBannerCookies`. Card "Preferencias de cookies" al final de la tab "Seguridad" con resumen de decision actual + botones "Administrar cookies" y "Restablecer y volver a preguntar". |
| `src/pages/Perfil/Perfil.css` | modificado | Estilos `.perfil-cookies-card`, `.perfil-cookies-summary`, `.perfil-cookies-actions`, `.perfil-cookies-date` + responsive. |
| `index.html` | modificado | `<noscript>` adicional especifico para cookies (antes del `<noscript>` generico). |

## Hallazgos del audit cubiertos

| # | Riesgo | Estado |
|---|---|---|
| 1 | Sin UI para reabrir/cambiar decision | Cubierto (botones en Footer y en Perfil/Seguridad). |
| 2 | `localStorage` no sincroniza entre pestanas | Cubierto (listener de `storage` event + custom event interno). |
| 3 | Toggle "Analiticas" no controla nada | Cubierto (helper `loadConditionalScript` disponible; ademas cualquier script futuro usara esta API). |
| 4 | Sin versionado de politica | Cubierto (consulta best-effort a `/paginas-legales/cookies/` con timeout 1.5s; si la version cambia, re-muestra el banner). |
| 5 | Sin timestamp de la decision | Cubierto (campo `fecha` ISO-8601 en el payload; se muestra en Perfil). |
| 6 | Sin DNT / GPC | Cubierto (auto-aplica `analiticas=false` cuando aplica). |
| 10 | `pointer-events: none` en contenedor | Documentado en CSS; se mantiene la intencion; el `inner` recibe todos los clicks. |
| 12 | Sin `<noscript>` fallback para el banner | Cubierto (banner especifico de cookies en `index.html`). |
| 14 | `localStorage` falla en modo incognito Safari | Cubierto (fallback a `sessionStorage`). |

## Hallazgos NO cubiertos (requieren decision fuera del alcance frontend)

- #7, #8 (modelo `CookieConsent` + endpoint revocacion server-side): requieren Django + migracion + admin UI. **Pendiente** - recomendado para un plan backend dedicado.
- #9 (CMP homologado): decision comercial/legal (IAB TCF, Cookiebot, OneTrust). **Pendiente** de decision estrategica.
- #11, #13, #15 (baja severidad / recomendaciones): tests E2E Playwright quedan como trabajo futuro.

## Comandos ejecutados y resultados

```bash
# Build de produccion
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_frontend"
npm run build
# Resultado: exit 0. 228 modulos transformados. Sin warnings nuevos.
# El warning preexistente de "chunks > 500 kB" NO fue introducido por este cambio.

# Verificacion del bundle generado
grep -c "no se registrara" dist/index.html      # 1   -> <noscript> presente
grep -c "zapotal_cookies_pref" dist/assets/*.js  # 1   -> storage key presente

# Lint
npm run lint
# Resultado: "eslint" no se reconoce como comando. ESLint no esta instalado
# en node_modules del proyecto (issue preexistente, no introducido por este cambio).
```

## Comportamiento esperado

1. **Primera carga del sitio (sin decision previa)**: banner aparece. Si el navegador tiene DNT/GPC, se sugiere automaticamente `analiticas=false` y se abre en modo "Personalizar".
2. **Click en "Aceptar todo" / "Rechazar" / "Guardar preferencias"**: se guarda `{ version: 2, preferencias: {...}, politica_version, fecha, fuente }` en `localStorage`. Se dispara el custom event `zapotal:cookies:changed`.
3. **Recarga**: si la `version` de la politica legal cambio (best-effort contra el backend, con timeout 1.5s), el banner vuelve a salir. Si la version es la misma, el banner NO aparece.
4. **Click en "Administrar cookies" del Footer**: dispara el custom event `zapotal:cookies:open`; el banner se abre en modo "Personalizar" con las preferencias actuales precargadas.
5. **Perfil -> tab Seguridad**: muestra la decision actual (con fecha) y permite abrir o resetear.
6. **Reset**: limpia `localStorage` y re-abre el banner.
7. **Otra pestana decide**: la pestana actual se sincroniza via `storage` event y se cierra/sincroniza su banner.

## Compatibilidad hacia atras (migracion silenciosa)

Si un usuario tiene en `localStorage` la version antigua (objeto plano sin campo `version`), `getCookiePreferences()` retorna `null` y se vuelve a mostrar el banner. No se borra el dato antiguo (queda hasta que el usuario decida otra vez). Esto es intencional: no se sobreescribe la decision del usuario sin su consentimiento.

## Riesgos residuales

- La consulta a `/paginas-legales/cookies/` puede fallar (timeout, 404, CORS). Esto se trata como failure silencioso: el banner se muestra/oculta segun la decision previa. Documentado inline.
- `DNT`/`GPC` cambian a `analiticas=false` solo si no hay decision previa o si la decision previa permitia. Si el usuario ya decidio y el toggle estaba en `false`, **se respeta** y no se sobreescribe.
- El bundle JS aumenta muy poco (~3-5 KB minificado) por las nuevas funciones. Esto esta dentro del orden natural.

## Verificacion manual recomendada (no automatizable en sandbox)

Para que el equipo confirme en navegador:

1. `cd comunidad_zapotal_frontend && npm run dev`
2. Abrir `http://localhost:5173` en incognito.
3. **Esperado**: banner aparece. Aceptar.
4. Recargar. **Esperado**: banner NO aparece.
5. Scroll al footer. Click en "Administrar cookies". **Esperado**: banner se abre en modo "Personalizar" con la decision actual marcada.
6. Login -> ir a `/perfil?tab=seguridad`. Scroll al final de la tab. **Esperado**: aparece el card "Preferencias de cookies" con la decision y los botones.
7. Abrir DevTools -> Application -> Local Storage. **Esperado**: clave `zapotal_cookies_pref` con el nuevo schema (version 2).
8. Abrir dos pestanas. En una, hacer click en "Restablecer y volver a preguntar". **Esperado**: la otra pestana tambien reabre el banner.

## Proximos pasos sugeridos

- Plan backend `2026-07-...-cookies-consent-modelo.md` para cubrir hallazgos #7 y #8.
- Considerar Playwright E2E test para la primera carga + click "Aceptar todo" + reload sin banner + click en "Administrar cookies" del footer (hallazgo #13 del audit).
