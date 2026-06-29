# Audit: Reemplazar "Comunidad Campesina Zapotal" por el nombre oficial

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-28
- Tecnologia: frontend React + backend Django (emails y seed)

## Objetivo

Reemplazar todas las ocurrencias hardcodeadas de "Comunidad
Campesina Zapotal" (y la version corta "Comunidad Zapotal")
por el nombre oficial "Comunidad Campesina Niño Dios de Zapotal".

Esto afecta:
- Copyrights en Login, Registro, Footer.
- Texto al lado del logo en el Navbar (incluyendo el drawer).
- Titulos del hero en Login y Registro.
- Titulo h2 del Footer.
- Texto del home en App.jsx.
- Eyebrow y texto del Contacto.
- Texto de Autoridades, Donaciones, LibroReclamaciones, Perfil.
- Emails transaccionales (backend): el default fallback
  debe usar el nombre oficial.
- Seed de contenido estatico.

## Alcance

### Incluye

Frontend (cambio de string literal):

- `comunidad_zapotal_frontend/src/components/Footer.jsx`
- `comunidad_zapotal_frontend/src/components/Navbar.jsx`
- `comunidad_zapotal_frontend/src/components/Contacto/Contacto.jsx`
- `comunidad_zapotal_frontend/src/components/LibroReclamaciones/LibroReclamaciones.jsx`
- `comunidad_zapotal_frontend/src/pages/Admin/Autoridades.jsx`
- `comunidad_zapotal_frontend/src/pages/Donaciones/Donaciones.jsx`
- `comunidad_zapotal_frontend/src/pages/Login/Login.jsx`
- `comunidad_zapotal_frontend/src/pages/Registro/Registro.jsx`
- `comunidad_zapotal_frontend/src/pages/Perfil/Perfil.css`
- `comunidad_zapotal_frontend/src/App.jsx`

Backend (emails y seed):

- `comunidad_zapotal_backend/apps/comunidad/emails.py`
- `comunidad_zapotal_backend/apps/comunidad/services.py`
- `comunidad_zapotal_backend/apps/donaciones/views.py`
- `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_contenido_estatico.py`

### No incluye

- El campo `nombre_oficial` del modelo ConfiguracionComunidad
  (ya tiene el valor correcto: "Comunidad Campesina Nino Dios
  de Zapotal" en la migracion 0007 y en el seed).
- Los strings que NO se refieren al nombre oficial (ej: titulos
  de Google Maps "Plaza de Armas Zapotal", "Zapotal, Huarango",
  emails `admin@comunidadzapotal.com`, eventos JS con
  prefijo `zapotal_*`).
- Las paginas que ya usan `cfg.nombre_oficial` dinamicamente
  (NuestraHistoria, Conocenos, configuracion).

## Estado actual (ocurrencias)

Frontend (10 archivos):

| Archivo | Linea | Contexto |
|---|---|---|
| Autoridades.jsx | 61 | "Lideres de la Comunidad Campesina Zapotal" |
| Footer.jsx | 13, 65 | h2 + copyright |
| Navbar.jsx | 135, 138, 307 | alt logo + "Comunidad Zapotal" (logo + drawer) |
| Contacto.jsx | 311 | eyebrow "Comunidad Zapotal" |
| Donaciones.jsx | 190 | "Comunidad Campesina Zapotal financiar" |
| Login.jsx | 236, 373 | hero title + copyright |
| Registro.jsx | 221, 446, 524 | hero title + 2 copyrights |
| Perfil.css | 3 | variable CSS |
| App.jsx | 105 | p del home |
| LibroReclamaciones.jsx | 136 | "Campesina Zapotal. Nuestro compromiso" |

Backend (4 archivos):

| Archivo | Lineas | Notas |
|---|---|---|
| services.py | 165, 181, 199, 232, 248, 273, 328, 335, 353, 365 | emails transaccionales |
| emails.py | 262, 325, 382 | footers de emails |
| views.py | 555, 565 | email de donacion |
| seed_contenido_estatico.py | 64 | seed inicial |

## Riesgos

- Bajo: el cambio es solo de strings. No afecta logica, ni DB,
  ni migraciones.
- Bajo: en el backend, los emails YA usan `cfg.nombre_oficial`
  cuando esta disponible; solo hay que actualizar los fallbacks
  hardcodeados para que coincidan con el nombre oficial.
- Medio: el logo del Navbar dice "Comunidad Zapotal" (corto);
  pasarlo al nombre completo puede requerir ajustar el width
  del brand o reducir el font-size. Se evaluara visualmente.

## Recomendacion

1. Reemplazar todos los strings "Comunidad Campesina Zapotal"
   por "Comunidad Campesina Nino Dios de Zapotal".
2. Reemplazar "Comunidad Zapotal" (forma corta usada en el
   Navbar y en algunos eyebrows) por el nombre completo
   donde se refiera al nombre oficial de la institucion.
3. En el Navbar, si el nombre completo no cabe, reducir el
   font-size del brand o ajustar el width.
4. Verificar build + Playwright.
5. Commit + push.

## Verificacion sugerida

```bash
npm run build
node test-login-registro.mjs  # confirmar que no se rompio nada
```

Verificacion visual:
- Login/Registro/Footer: copyright dice "Comunidad Campesina
  Nino Dios de Zapotal"
- Navbar: el brand al lado del logo dice "Comunidad Campesina
  Nino Dios de Zapotal"
- App.jsx home: el h1/p menciona el nombre correcto
