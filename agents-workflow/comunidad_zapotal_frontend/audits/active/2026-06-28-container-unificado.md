# Audit: Estandarizar ancho de container en todas las secciones

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Tecnologia: frontend React

## Objetivo

Estandarizar el ancho de todas las secciones publicas para
que usen el mismo container (mismo max-width, mismo padding
lateral, misma direccion de centrado). Que el footer
comparta el mismo container que el resto.

Actualmente cada pagina tiene su propio max-width:
- Footer: 1450px
- Navbar (drawer): 1100px
- Home hero: 1050px
- AutoridadesPage: 1200px
- LibroReclamaciones: 1200px
- Contacto: 1280px
- Conocenos: 1150px
- Buscar: 960px
- Legal: 880px
- Autoridades: 750px
- etc.

Esto da una sensacion de "cada pagina es de su padre". El
usuario quiere que se vea como un solo sistema con el mismo
ancho util, igual que el footer.

## Alcance

### Incluye

Frontend:

- `comunidad_zapotal_frontend/src/index.css`
  - Agregar clase `.container-zapotal` con `max-width: 1200px;
    margin: 0 auto; padding: 0 24px;` (o el ancho que se defina
    en el plan, mirando el footer como referencia).
- `comunidad_zapotal_frontend/src/components/Footer.css`
  - Reemplazar `.footer-container` max-width: 1450px por el
    container estandar.
- `comunidad_zapotal_frontend/src/components/Navbar.css`
  - Alinear el brand, el search, las acciones, el drawer
    al mismo container.
- `comunidad_zapotal_frontend/src/App.css`
  - Alinear `.home-hero-content` al container.
- `comunidad_zapotal_frontend/src/pages/Autoridades/AutoridadesPage.css`
  - Alinear `.au-container` al container.
- `comunidad_zapotal_frontend/src/components/Contacto/Contacto.css`
  - Alinear al container.
- `comunidad_zapotal_frontend/src/pages/Nosotros/Conocenos.css`
  - Alinear al container.
- `comunidad_zapotal_frontend/src/components/LibroReclamaciones/LibroReclamaciones.css`
  - Alinear al container.
- `comunidad_zapotal_frontend/src/pages/Buscar/Buscar.css`
  - Alinear al container.
- `comunidad_zapotal_frontend/src/pages/Legal/LegalPage.css`
  - Alinear al container.

### No incluye

- No se cambia el responsive (mobile breakpoints).
- No se cambia el branding, colores o tipografia.
- No se cambia la logica de los componentes.
- No se cambia el backend.

## Estado actual (anchos)

```
Footer:              1450px
Contacto:            1280px
AutoridadesPage:     1200px
LibroReclamaciones:  1200px
Conocenos:           1150px
Navbar drawer:       1100px
Home hero:           1050px
Buscar:               960px
Legal:                880px
Autoridades (lista):  750px
```

## Recomendacion

1. Definir container unico: `max-width: 1200px; margin: 0 auto;
   padding: 0 24px;` (alineado con el footer pero mas estrecho
   que 1450px para que se vea "un poquito mas estrecho" como
   pidio el usuario).
2. Aplicar este container a TODAS las secciones publicas
   (Navbar, Footer, home, Autoridades, Contacto, Conocenos,
   LibroReclamaciones, Buscar, Legal, etc.).
3. Verificar visualmente con Playwright.
4. Commit + push.

## Verificacion sugerida

```bash
npm run build
```

Verificacion visual con Playwright:

```js
// Verificar que el main-content de cada pagina tenga el mismo
// max-width (1200px) y el mismo padding lateral.
const w = await page.evaluate(() => {
  const el = document.querySelector('.container-zapotal, main, [class*="container"]');
  return el ? window.getComputedStyle(el).maxWidth : null;
});
console.log('Container max-width:', w);
```
