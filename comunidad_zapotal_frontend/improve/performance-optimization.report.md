# Reporte de Análisis: performance-optimization

**Proyecto:** Comunidad Campesina Zapotal — Portal Web
**Fecha:** 2026-06-10

## Resumen Ejecutivo

El proyecto usa Create React App (CRA) que produce bundles grandes por defecto. No hay lazy loading, code splitting, ni optimización de imágenes. Las fuentes y assets de terceros potencialmente bloquean el render inicial. No hay monitoreo de Core Web Vitals.

## Puntos Fuertes

- web-vitals está en package.json listo para usarse
- Las imágenes en public/ permiten caché HTTP estático
- La app es una SPA liviana sin librerías pesadas (no hay Chart.js, no hay mapas pesados — Google Maps solo en Contacto)

## Áreas de Mejora

- **Sin lazy loading por ruta**: Toda la aplicación se carga en un bundle único. React Router está configurado pero sin React.lazy.
- **Sin code splitting**: No hay división de código en ningún nivel. Componentes de páginas completas (Eventos, Noticias completo con Detalle) se cargan siempre.
- **Imágenes sin optimizar**: Las imágenes (hero, logos, noticias) se cargan sin dimensiones explícitas ni formatos modernos (WebP/AVIF). Sin lazy loading para imágenes below-the-fold.
- **Google Maps iframe en Contacto**: Carga un script de terceros que puede bloquear el render. Sin lazy loading en el iframe.
- **AOS (Animate On Scroll)**: Librería de animación de ~30KB que se carga completa pero solo se usa para fade-in básico. Alternativa más ligera posible.
- **Sin performance budget**: No hay configuración de límites de bundle, tamaño de imágenes, o tiempos de carga.
- **Sin precarga de fuentes**: Si se usan Google Fonts, cargan sin font-display: swap.

## Recomendaciones

1. Implementar React.lazy + Suspense para todas las rutas:
   - `const Home = lazy(() => import('./pages/Home'))`
2. Optimizar imágenes: convertir a WebP, agregar width/height, añadir loading="lazy" en imágenes below-the-fold
3. Agregar lazy loading al iframe de Google Maps con `<iframe loading="lazy">`
4. Evaluar reemplazar AOS con Intersection Observer nativo o una implementación ligera de ~2KB
5. Configurar un performance budget básico en package.json con bundlesize
6. Agregar métricas web-vitals y enviarlas a un endpoint de analytics
7. Migrar de CRA a Vite para mejor tree-shaking, code splitting automático y tiempos de build

## Prioridad de Acción

| Acción | Prioridad | Esfuerzo |
|--------|-----------|----------|
| React.lazy + Suspense | Alta | Bajo |
| Lazy loading imágenes y iframe | Alta | Bajo |
| WebP conversion de imágenes | Alta | Medio |
| Evaluar reemplazo de AOS | Media | Bajo |
| web-vitals analytics | Media | Bajo |
| Migración a Vite | Media | Alto |
| Performance budget | Baja | Bajo |
