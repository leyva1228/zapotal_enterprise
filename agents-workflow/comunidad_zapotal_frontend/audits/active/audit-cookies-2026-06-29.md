# Audit: Manejo de cookies (banner de consentimiento)

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-29
- Autor/agente: opencode (modelo minimax-m3)
- Tecnologia: Frontend React (principal) + Backend Django (secundario, sin modelo de consentimiento)

## Objetivo

Auditar como se gestiona el consentimiento de cookies en el proyecto, identificar por que el modal no aparece al levantar el servidor y reportar huecos funcionales, de UX y de compliance.

## Alcance

### Incluye

- `comunidad_zapotal_frontend/src/components/Legal/BannerCookies.jsx` y `BannerCookies.css`
- `comunidad_zapotal_frontend/src/pages/Legal/CookiesPage.jsx` y `LegalPage.jsx`
- `comunidad_zapotal_frontend/src/App.jsx` (montaje del banner)
- `comunidad_zapotal_frontend/src/main.jsx` (bootstrap)
- `comunidad_zapotal_frontend/index.html` (sin pre-render script)
- `comunidad_zapotal_frontend/src/components/Footer.jsx` (link a politica)
- Busqueda de uso de `localStorage` / `sessionStorage` / `document.cookie` en `src/`
- Busqueda de modelo `CookieConsent` o equivalente en backend
- Comprobacion de z-index y orden de providers en `App.jsx`

### No incluye

- No se modifica codigo (este es solo audit / reporte).
- No se verifica el sitio en navegador (no hay browser MCP disponible aqui; se trabaja sobre el codigo).
- No se analiza BFF de Spring Boot ni app Android.
- No se audita cumplimiento legal especifico por pais (LPDP Peru, GDPR UE, etc.) - se mencionan riesgos, no se hace dictamen juridico.

## Contexto leido

- `comunidad_zapotal_frontend/AGENTS.md`
- `comunidad_zapotal_backend/AGENTS.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `agents-workflow/comunidad_zapotal_backend/audits/active/audit-modelos-django-y-consumo-react-2026-06-29.md` (audit previo - confirma que no hay modelo backend de cookies)

---

## Hallazgos clave (TL;DR)

1. **El banner existe, esta implementado y esta montado correctamente.** `BannerCookies.jsx` se renderiza dentro de `<BrowserRouter>` en `App.jsx:332`.
2. **La razon #1 por la que "no aparece" es que el navegador ya tiene `localStorage['zapotal_cookies_pref']` seteado.** El banner solo se muestra cuando esa clave esta ausente. Si el dev acepto/rechazo en una sesion anterior, queda persistido y nunca vuelve a salir.
3. **No hay forma visible de reabrir el banner** desde la UI una vez tomada la decision. No existe boton "Administrar cookies" en el footer ni en el perfil.
4. **No hay modelo backend** que registre el consentimiento. La eleccion vive solo en `localStorage` del navegador.
5. **El banner no aparece durante el boot** porque `AppShell` en `App.jsx:283-324` bloquea el render detras de un `<LoaderOverlay>` con `variant="no-navbar"` (z-index 900, top:0) hasta que `document.readyState === 'complete'`. Esto no es el problema principal (es solo una demora de ~400ms-8s), pero conviene saberlo.
6. **El toggle de "Analiticas" no tiene efecto real** porque no hay scripts de analytics en el proyecto que se carguen condicionalmente.
7. **El proyecto tiene una `CookiesPage` legal** (`/cookies` y `/politica-cookies`) servida desde `PaginaLegal` (modelo `PaginaLegal`, slug `cookies`). Esta pieza funciona, pero no esta enlazada desde el banner con un comportamiento contextual (solo `<a target="_blank">`).

---

## Inventario de piezas existentes

### Frontend

| Archivo | Lineas | Funcion |
|---|---|---|
| `src/components/Legal/BannerCookies.jsx` | 135 | Componente React del banner (modal de consentimiento). |
| `src/components/Legal/BannerCookies.css` | 74 | Estilos: position fixed, bottom 16px, z-index 9999, responsive. |
| `src/pages/Legal/CookiesPage.jsx` | 7 | Wrapper sobre `LegalPage` con icono `FaCookieBite`. |
| `src/pages/Legal/LegalPage.jsx` | 53 | Renderizador generico de paginas legales (lee de `usePaginaLegal(slug)`). |
| `src/components/Footer.jsx:54` | 1 | Link a `/cookies` (Politica de Cookies). |
| `src/App.jsx:32-33, 186-187, 332` | 5 | Import, rutas y montaje del banner. |

### Backend (sin modelo de cookies)

| Archivo | Linea | Detalle |
|---|---|---|
| `apps/comunidad/models_institucionales.py:235-260` | 26 | Modelo `PaginaLegal` con `SLUG_CHOICES` que incluye `('cookies', 'Politica de Cookies')`. |
| `apps/comunidad/views_institucionales.py` | - | ViewSet `PaginaLegalViewSet` + `PaginaLegalDetailView(slug=...)` -> `/api/v1/paginas-legales/cookies/`. |
| `apps/comunidad/serializers_institucionales.py` | - | `PaginaLegalSerializer` (titulo, contenido, version, fecha_vigencia). |
| `apps/core/utils.py:17` | 1 | `'authorization', 'cookie'` en una lista de headers permitidos (no es modelado, es allowlist para logging). |

**Conclusion backend:** No hay modelo `CookieConsent`. No hay endpoint para registrar/revocar consentimiento. La unica pieza backend relacionada es la pagina legal informativa (`PaginaLegal` con slug `cookies`).

---

## Logica del banner: como funciona hoy

### `BannerCookies.jsx` (resumen)

```text
const STORAGE_KEY = 'zapotal_cookies_pref';

[visible, setVisible]                 = useState(false)        // arranca oculto
[showPersonalizar, setShowPersonalizar] = useState(false)
[prefs, setPrefs]                     = useState({ necesarias: true, preferencias: true, analiticas: false })

useEffect mount:
  existing = readPreference()  // localStorage.getItem('zapotal_cookies_pref')
  if !existing: setVisible(true)        // <-- SOLO si no hay preferencia guardada
  else: setPrefs(existing)

handleAceptarTodo  -> { necesarias:true, preferencias:true, analiticas:true } + localStorage.setItem + setVisible(false)
handleRechazar     -> { necesarias:true, preferencias:false, analiticas:false } + localStorage.setItem + setVisible(false)
handleGuardar      -> localStorage.setItem(prefs) + setVisible(false)
```

Puntos clave:

- El banner se monta y consulta `localStorage` una sola vez (en el `useEffect` inicial).
- Una vez guardada la preferencia, **el componente nunca vuelve a mostrarse** en esa pestana/dispositivo, salvo recarga con `localStorage` limpio.
- **No hay listener de `storage` events** para sincronizar entre pestanas.
- **No hay mecanismo de "reabrir" el banner** (boton en footer/perfil, parametro URL, version bump de la politica, etc.).

### Montaje en `App.jsx`

```text
App (linea 275)
  <LoaderProvider>
    <AppShell>
      if (booting === true) -> <LoaderOverlay active={true} variant="no-navbar" mensaje="Cargando sistema" />
      else (linea 326-336):
        <AuthProvider>
          <ToastProvider>
            <BrowserRouter>
              <BodyScrollLock />
              <Layout />
              <BannerCookies />   <-- AQUI, dentro de <BrowserRouter>
            </BrowserRouter>
          </ToastProvider>
        </AuthProvider>
```

Observaciones sobre el montaje:

- `BannerCookies` esta **dentro** de `<BrowserRouter>` y **fuera** de `<Layout>`. Esto significa que se monta una sola vez para toda la app, lo cual es correcto.
- El estado `booting` de `AppShell` retrasa el montaje del banner hasta que `document.readyState === 'complete'` (o hasta 8s de fallback). Esto no bloquea el banner; solo lo retrasa entre ~400ms y 8s.
- `BannerCookies` **no** esta condicionado por la ruta, ni por el estado de autenticacion. Eso es correcto (se debe mostrar a todos los visitantes).

### Z-index y visibilidad

| Elemento | z-index | Cobertura |
|---|---|---|
| `BannerCookies` (`.bc-banner`) | 9999 | Solo banner (position fixed, bottom 16px) |
| `LoaderOverlay` (`.lo-root`) | 900 | Toda la pantalla durante boot |
| `LoaderOverlay` (`lo-no-navbar` variant) | 900 | `top: 0` (cubre toda la pantalla) |
| `ToastCenter` | 2000 | Solo toasts (position top) |
| `Navbar` | 1000-1100 | Solo header |

Mientras `booting=true` el `LoaderOverlay` esta sobre el viewport, pero como `BannerCookies` no esta montado todavia, no hay conflicto. Una vez `booting=false`, el loader desaparece y el banner queda visible por encima de todo (z-index 9999 > navbar 1000-1100).

**No hay un bug de z-index que oculte el banner.**

---

## Por que el banner NO aparece al levantar el servidor

Cuatro causas posibles, ordenadas por probabilidad:

### Causa #1 (la mas probable, ~90%): preferencia ya guardada en `localStorage`

**Sintoma:** "ya no me aparece".
**Causa:** En una sesion anterior, el dev (o el script) hizo click en "Aceptar todo" o "Rechazar", lo que dispara `localStorage.setItem('zapotal_cookies_pref', JSON.stringify(...))`. En cargas posteriores, `useEffect` lee esa clave y NO setea `visible=true`.
**Como verificarlo:**

1. Abrir DevTools -> Application -> Local Storage -> `http://localhost:5173` (o el host que uses).
2. Buscar la clave `zapotal_cookies_pref`.
3. Si existe, el banner no se mostrara hasta que se borre.
4. Hacer click derecho -> Delete, recargar la pagina, deberia aparecer.

**Causa raiz del UX:** no hay forma de reabrir el banner desde la UI.

### Causa #2 (probable, ~30%): `localStorage` se setea en algun lugar inesperado

**Sintoma:** "nunca vi el banner, ni siquiera la primera vez".
**Causa posible:** algun script pre-carga o extension del navegador (u otro componente React) escribe la clave `zapotal_cookies_pref` con un valor por defecto antes de que el `useEffect` del banner se ejecute.

**Como verificarlo:**

1. En la consola del navegador, ejecutar:
   ```js
   Object.keys(localStorage).filter(k => k.includes('cookie'))
   // Esperado: solo ['zapotal_cookies_pref'] si el usuario decidio
   ```
2. Inspeccionar el valor: deberia ser un JSON con `necesarias, preferencias, analiticas`.
3. Si la clave existe con un valor anomalo (ej. `null`, `""`, `{}`), el `readPreference()` lo parsea y considera que ya hay decision.

**Nota:** El `useEffect` solo se dispara una vez en mount. Si React.StrictMode (dev) lo monta dos veces, la primera llamada a `setVisible(true)` y la segunda `setVisible(true)` no producen problema. Pero si entre las dos llamadas algo escribe `localStorage`, el segundo `useEffect` encontrara la clave y NO mostrara el banner. Esto seria un caso raro pero posible.

### Causa #3 (poco probable, ~10%): el boot loader se queda pegado

**Sintoma:** "el banner nunca aparece, ni pasados 10 segundos".
**Causa posible:** `AppShell` queda con `booting=true` para siempre si el evento `window.load` nunca dispara y el fallback de 8s tampoco se ejecuta (poco probable pero posible si el `setTimeout` no se monta por algun error de React).

**Como verificarlo:**

1. En consola: `document.readyState` debe ser `'complete'`.
2. Si esta en `'loading'` por mas de 8s, hay un problema de carga de recursos (red, fonts, etc.).
3. Inspeccionar Network tab para detectar requests colgadas.

**Observacion:** esta causa no es exclusiva del banner; bloquearia toda la app.

### Causa #4 (poco probable, ~5%): el banner se monta fuera del viewport

**Sintoma:** "el banner aparece pero no se ve".
**Causa posible:** en pantallas muy pequenas o con algun CSS que rompa el layout (`position: fixed; bottom: 16px`), el banner podria quedar fuera del viewport visible.

**Como verificarlo:**

1. En DevTools, buscar el selector `.bc-banner`.
2. Inspeccionar el bounding box.
3. Verificar `display`, `visibility`, `opacity` y `transform`.

**Observacion:** el CSS del banner tiene `@media (max-width: 600px)` que ajusta el padding y el flex-direction de los botones, pero no rompe la visibilidad.

---

## Diagnostico final

**El banner no aparece porque ya hay una decision guardada en `localStorage`.** Esto es, en realidad, **el comportamiento correcto** de un banner de cookies: una vez que el usuario decide, no se le vuelve a molestar. El problema es de **UX**:

- El dev que esta probando no tiene forma visible de reabrir el banner.
- Un usuario que quiera **cambiar** su decision despues (ej. "acepte todo pero ahora quiero rechazar analiticas") tampoco tiene forma de hacerlo sin entrar a DevTools.

Esto no es solo un incoveniente de developer: es un **problema de compliance**. Regulaciones como GDPR (UE) y LPDP (Peru, Ley 29733) exigen que el usuario pueda **retirar o modificar su consentimiento** tan facilmente como lo dio. Si la unica forma es borrar el `localStorage` o desinstalar el sitio, no se cumple el principio de "facilidad de retiro".

---

## Riesgos identificados

### Funcionales / UX

| # | Riesgo | Severidad | Detalle |
|---|---|---|---|
| 1 | Sin UI para reabrir/cambiar decision | Alta | El usuario (y el dev) no puede modificar la preferencia despues del primer click. |
| 2 | `localStorage` no sincroniza entre pestanas | Media | Si el usuario decide "Rechazar" en una pestana, la otra sigue mostrando la decision anterior hasta recargar. No hay listener de `storage` event. |
| 3 | El toggle "Analiticas" no controla nada | Alta (compliance) | No hay scripts de analytics que se carguen condicionalmente. El usuario cree que decidio sobre "Analiticas" pero no tiene efecto. Esto es enga~oso. |
| 4 | Sin versionado de la politica | Alta (compliance) | Si la politica de cookies cambia (ej. nuevo proveedor), el usuario no es re-notificado. No hay `version` ni comparacion contra `politica_version` guardada. |
| 5 | Sin timestamp en la decision | Media | No se guarda cuando se tomo la decision. Para auditoria de compliance, suele requerirse fecha/hora. |
| 6 | Sin `doNotTrack` / `Global Privacy Control` | Media | Navegadores que envian `DNT: 1` o `Sec-GPC: 1` no son respetados por defecto. |

### Backend / Compliance

| # | Riesgo | Severidad | Detalle |
|---|---|---|---|
| 7 | Sin modelo `CookieConsent` | Alta | No hay rastro server-side del consentimiento. En una auditoria de INDECOPI o entidad equivalente, esto es un hallazgo. |
| 8 | Sin endpoint de revocacion | Alta | Si el usuario escribe a privacidad@ para retirar consentimiento, no hay endpoint que registre la revocacion. Solo queda en `localStorage`. |
| 9 | Sin logica de bloqueo de scripts no esenciales | Alta | No hay carga condicional de scripts. Cualquier `<script>`第三方 (futuro) correria sin gate de consentimiento. |
| 10 | Sin CMP homologado | Media | Para algunos mercados (UE, CA) se requieren CMPs homologados (IAB TCF, OneTrust, Cookiebot, etc.). El banner propio no es un CMP. |

### Tecnicos / Codigo

| # | Riesgo | Severidad | Detalle |
|---|---|---|---|
| 11 | `useEffect` sin cleanup | Baja | Si el componente se desmonta antes de que termine la lectura de `localStorage`, no hay cleanup. En la practica es sincronico, asi que el riesgo es minimo. |
| 12 | Sin `<noscript>` fallback para el banner | Baja | Si el usuario tiene JS desactivado, el banner nunca aparece. El `<noscript>` en `index.html:17` solo dice "Necesitas habilitar JavaScript". |
| 13 | Sin tests E2E del banner | Media | No hay tests de Playwright que verifiquen la primera carga, el click en "Aceptar todo", y el segundo reload sin banner. |
| 14 | `localStorage` falla en modo incognito Safari | Baja | `try/catch` en `writePreference` lo cubre, pero no hay fallback a `sessionStorage` o cookie. |
| 15 | CSS `pointer-events: none` en contenedor | Baja | Solo el `__inner` recibe clicks. Esto es intencional para no bloquear la pagina, pero si el `__inner` queda cubierto por otro elemento, los botones quedan inaccesibles. |

---

## Comparativa con la pagina legal estatica

`/cookies` y `/politica-cookies` (slugs del modelo `PaginaLegal`) renderizan la politica **informativa** desde la BD via `usePaginaLegal`. Esto esta **separado** del banner:

- El banner = gestion activa del consentimiento.
- La pagina = texto legal editable.

La separacion es correcta en diseno, pero el banner no consulta la pagina para validar su version contra la decision guardada. Esto es el riesgo #4 arriba.

---

## Lo que se deberia hacer (recomendaciones)

> Esta seccion NO se implementa en este audit. Solo se describe para el plan futuro.

### Corto plazo (fix de UX minimo)

1. **Anadir un boton "Administrar cookies" en el footer** que vuelva a abrir el banner. En `Footer.jsx` debajo del link "Politica de Cookies", o como un sub-item.
2. **Anadir un boton "Administrar cookies" en el perfil del usuario** (tab "Privacidad" o "Mi cuenta") que dispare un modal con la misma UI del banner, precargado con las preferencias guardadas.
3. **Escuchar el `storage` event** en `BannerCookies` para sincronizar entre pestanas.
4. **Versionar la politica**: guardar `{ preferencias, politica_version, fecha }` en `localStorage` y comparar contra un campo `version` que sirva `usePaginaLegal('cookies')`. Si cambia, re-mostrar el banner.
5. **Timestamp de la decision**: incluir `fecha: new Date().toISOString()` en el JSON guardado.

### Mediano plazo (compliance basico)

6. **Crear un modelo backend `CookieConsent`** en una app nueva o como parte de `core`:
   ```python
   class CookieConsent(models.Model):
       usuario = ForeignKey(Usuario, null=True, blank=True, on_delete=SET_NULL)
       anon_id = CharField(max_length=64, blank=True)  # para usuarios no logueados
       necesarias = BooleanField(default=True)
       preferencias = BooleanField(default=False)
       analiticas = BooleanField(default=False)
       politica_version = CharField(max_length=20)
       user_agent = CharField(max_length=500, blank=True)
       ip_origen = GenericIPAddressField(null=True, blank=True)
       fecha = DateTimeField(auto_now_add=True, db_index=True)
   ```
7. **Enviar la decision al backend** en `handleAceptarTodo`, `handleRechazar` y `handleGuardar` (POST a un endpoint nuevo, best-effort, sin bloquear la UI).
8. **Endpoint publico** `POST /api/v1/cookies/consent/` que registre el consentimiento (anon o autenticado).
9. **Endpoint admin** `GET /api/v1/cookies/consent/estadisticas/` con conteo de aceptaciones/rechazos (para el dashboard).
10. **Carga condicional de scripts**: mover cualquier `<script>` futuro (analytics, chat, etc.) a un helper `loadScript(url)` que verifique `localStorage['zapotal_cookies_pref'].analiticas` antes de inyectar el tag.

### Largo plazo (compliance avanzado)

11. **Integrar un CMP homologado** si se planea publicidad programatica o retargeting (ej. Cookiebot, Iubenda, OneTrust).
12. **Documentar la politica de cookies en lenguaje claro**, con tabla de "que cookie, para que, quien, duracion".
13. **Bloquear preventivamente cookies no esenciales** en el servidor (Set-Cookie con `SameSite=Lax` y limpiar cookies third-party que no respeten el consentimiento).
14. **Anadir banner de "politica actualizada"** cuando se publica una nueva version (similar a GitHub cuando cambian los TOS).
15. **Anadir tests E2E** en `test-*.mjs` con Playwright:
    - Primera carga muestra el banner.
    - Click en "Aceptar todo" guarda localStorage y oculta el banner.
    - Segunda carga no muestra el banner.
    - Click en "Administrar cookies" en el footer lo reabre con las preferencias actuales.

---

## Verificacion inmediata (sin tocar codigo)

Para confirmar la causa #1 (la mas probable) ahora mismo:

1. Abrir DevTools -> Application -> Local Storage -> `http://localhost:5173` (o el puerto que uses).
2. Buscar `zapotal_cookies_pref`. **Si existe**, esa es la causa. Borrarla y recargar deberia mostrar el banner.
3. Si **no existe**, entonces el `useEffect` no esta seteando `visible=true` por alguna otra razon. En ese caso:
   - Inspeccionar el componente: `<div class="bc-banner" role="dialog">` deberia estar en el DOM despues de ~8s.
   - Si no esta en el DOM, el componente no se esta montando (problema de orden en `App.jsx` o de import).
   - Si esta en el DOM pero invisible, problema de CSS (display, opacity, transform).
4. Probar en una ventana incognito. Si el banner aparece ahi pero no en la ventana normal, confirma que es un tema de `localStorage` previo.

Si el problema persiste, abrir `dist/index.html` o el build de produccion y comparar con el codigo fuente para descartar cache del navegador o del service worker (aunque el proyecto no parece tener SW segun `index.html`).

---

## Entregable

- Este archivo: `agents-workflow/comunidad_zapotal_frontend/audits/active/audit-cookies-2026-06-29.md`
- Estado: READY_FOR_PLAN
- Proximo paso sugerido: si se decide actuar, crear plan en `agents-workflow/comunidad_zapotal_frontend/implementation-plans/active/` con micro-tareas que no toquen backend hasta que la decision de compliance este tomada.
