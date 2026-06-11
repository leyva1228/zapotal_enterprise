# Reporte de Análisis: accessibility-testing

**Proyecto:** Comunidad Campesina Zapotal — Portal Web
**Fecha:** 2026-06-10

## Resumen Ejecutivo

La aplicación tiene problemas de accesibilidad que deben corregirse para cumplir WCAG 2.1 AA. El marcado HTML base usa `lang="en"` en vez de `lang="es"`, hay elementos interactivos sin semántica adecuada, y falta manejo de foco en contenido dinámico. No hay pruebas automatizadas de accesibilidad.

## Puntos Fuertes

- Los formularios usan etiquetas label asociadas a inputs
- Los enlaces de navegación son elementos `<a>` con atributos href válidos
- Las imágenes decorativas tienen `alt=""` (vacio) donde corresponde
- Los botones de icono tienen aria-label en varios casos (Navbar)
- Contraste de color básico presente en texto sobre fondos claros

## Áreas de Mejora

- **`<html lang="en">` en public/index.html**: El contenido está en español pero el atributo lang dice "en". Debe ser `lang="es"`.
- **Meta description genérica**: "Web site created using create-react-app" no es descriptiva para SEO ni accesibilidad cognitiva.
- **Elementos interactivos no semánticos**: Algunos divs o spans usados como botones sin role="button" ni tabIndex.
- **Manejo de foco en modales/contenido dinámico**: Al abrir dropdowns en Navbar o comentarios, el foco no se mueve al nuevo contenido.
- **Sin skip-to-content link**: Los usuarios de teclado deben tabular toda la navegación antes de llegar al contenido principal.
- **Sin aria-live para regiones dinámicas**: Los mensajes de error de formularios, carga de datos, y comentarios no usan aria-live para notificar a lectores de pantalla.
- **Contraste en navbar/footer**: Verificar contraste de texto claro sobre fondo oscuro cumple 4.5:1.
- **Sin roles ARIA en navegación**: `<nav>` sin aria-label para distinguir navegación principal de secundaria.
- **Enlaces de "Leer más"**: Si hay enlaces con texto genérico como "Leer más" sin contexto, no son accesibles para screen readers.

## Recomendaciones

1. Cambiar `<html lang="en">` a `<html lang="es">` en public/index.html
2. Actualizar meta description con texto descriptivo del portal comunitario
3. Agregar skip-to-content link como primer elemento focusable
4. Agregar aria-live="polite" en contenedores de comentarios y resultados de búsqueda
5. Agregar aria-label descriptivo a la navegación principal (`<nav aria-label="Navegación principal">`)
6. Manejar foco al abrir/cerrar dropdowns del navbar
7. Verificar y corregir contraste de color en navbar, botones y footer con herramienta axe DevTools
8. Agregar pruebas de accesibilidad automatizadas con jest-axe o axe-core en CI

## Prioridad de Acción

| Acción | Prioridad | Esfuerzo |
|--------|-----------|----------|
| lang="es" en HTML | Alta | Bajo |
| Skip-to-content link | Alta | Bajo |
| aria-live en regiones dinámicas | Alta | Bajo |
| Contraste navbar/footer | Alta | Bajo |
| Manejo de foco en modales | Alta | Medio |
| aria-label en navegación | Alta | Bajo |
| Meta description | Media | Bajo |
| Pruebas de accesibilidad | Media | Medio |
