# Plan: Unificar diseno Login/Registro con el oro del navbar

## Estado

- Estado: APPROVED (auto-aprobado en sesion; el usuario ya dio la
  orden directa con el resultado esperado)
- Requiere aprobacion humana: NO (cambio cosmético de frontend,
  no toca zonas sensibles)
- Fecha: 2026-06-28
- Tecnologia: frontend React (Vite) + Tailwind

## Objetivo

Unificar Login y Registro: mismo layout, mismo oro (del navbar),
misma imagen de fondo en el hero izquierdo.

## No objetivos

- No se cambia la logica de autenticacion.
- No se cambia el backend.
- No se cambia el navbar.
- No se migra la base de datos.

## Skills obligatorias

- `writing-plans`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`
- `react-expert` (impl)
- `frontend-ui-engineering` (UX consistency)
- `impeccable` (audit pass)

## Archivos permitidos

Frontend:

- `comunidad_zapotal_frontend/src/pages/Login/Login.jsx`
- `comunidad_zapotal_frontend/src/pages/Registro/Registro.jsx`
- `comunidad_zapotal_frontend/src/pages/Registro/Registro.css`
  (migrar o deprecar)
- `comunidad_zapotal_frontend/src/index.css` (variables CSS si hace
  falta)

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/`
- `comunidad_zapotal_frontend/src/components/Navbar*`
- cualquier archivo del backend
- migraciones nuevas
- dependencias nuevas en `package.json`

## Micro-tareas

### Task 1: Frontend - variables CSS compartidas para el navbar

- Objetivo: exponer el oro del navbar como variables CSS globales
  (ademas de las locales en `Navbar.css`) para que Login/Registro
  las puedan usar sin duplicar hexes.
- Archivos:
  - `comunidad_zapotal_frontend/src/index.css`
- Pasos:
  - Agregar en `:root` (o en `@layer base`):
    ```css
    :root {
      --nb-dorado:       #b8963e;
      --nb-dorado-light: #d4ae5a;
      --nb-verde:        #1a3209;
    }
    ```
- Verificacion: `npm run build`.
- Criterio de exito: variables disponibles.
- Criterio de rollback: revertir el cambio.

### Task 2: Frontend - Login con oro del navbar + imagen de fondo

- Objetivo: cambiar el "dorado casi dorado" del Login por el oro
  del navbar y agregar imagen de fondo en el hero.
- Archivos:
  - `comunidad_zapotal_frontend/src/pages/Login/Login.jsx`
- Pasos:
  - Cambiar las clases `bg-accent-400` y `text-accent-300` del
    adorno por estilos inline o clases con el hex del navbar
    (`#b8963e` / `#d4ae5a`).
  - Cambiar el `aside` (hero) para que tenga imagen de fondo:
    ```jsx
    <aside
      className="relative md:w-1/2 flex items-center justify-center py-16 md:py-0 bg-cover bg-center"
      style={{ backgroundImage: "url('/img/login/Union-fondo login.jpg')" }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary-950/80 via-primary-900/70 to-primary-800/60" />
      ...
    </aside>
    ```
- Verificacion: Playwright verifica que el hero tiene imagen
  de fondo y que el dorado es el del navbar.
- Criterio de exito: render correcto en `/login`.
- Criterio de rollback: revertir el cambio.

### Task 3: Frontend - Registro con mismo diseno que Login

- Objetivo: que el Registro tenga el mismo layout, mismo
  estilo, mismas fuentes que el Login.
- Archivos:
  - `comunidad_zapotal_frontend/src/pages/Registro/Registro.jsx`
  - `comunidad_zapotal_frontend/src/pages/Registro/Registro.css`
    (migrar a Tailwind o deprecar)
- Pasos:
  - Refactor del JSX: usar las mismas clases Tailwind que Login
    (flexbox 1:1, mismo hero con imagen, mismo panel derecho,
    mismas fuentes, mismos colores).
  - Conservar la logica de registro (validaciones, DNI,
    Turnstile, password strength, etc.) - **solo cambiar
    diseno**.
  - Mantener el `Registro.css` solo si hay clases no migradas;
    si no, marcar como deprecated.
- Verificacion: Playwright verifica que el render es
  consistente con Login.
- Criterio de exito: render correcto en `/registro` con el
  mismo look que Login.
- Criterio de rollback: revertir el cambio.

### Task 4: Verificacion final y push

- Comandos:
  - `npm run build`
  - Playwright: comparar render de Login y Registro
  - `git add` + `git commit` + `git push origin master`
- Criterio de exito: build pasa, Playwright confirma
  consistencia visual, push exitoso.
- Criterio de rollback: si build falla, revertir.
