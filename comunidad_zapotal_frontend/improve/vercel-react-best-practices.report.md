# Reporte de Análisis: vercel-react-best-practices

**Nota:** El skill `vercel-react-best-practices` no existe en el registro de skills. Este reporte cubre las mejores prácticas para despliegue en Vercel de un proyecto React (CRA).

**Proyecto:** Comunidad Campesina Zapotal — Portal Web
**Fecha:** 2026-06-10

## Resumen Ejecutivo

El proyecto usa Create React App, que es desplegable en Vercel con configuración mínima. Sin embargo, hay varias optimizaciones recomendadas: configurar SPA fallback para React Router, optimizar build, agregar headers de caché, y migrar a Vite o Next.js para mejor performance y SEO.

## Estado Actual

- **Framework**: Create React App (react-scripts 5.0.1)
- **Router**: React Router v7 (BrowserRouter — necesita configuración SPA en servidor)
- **Build output**: `build/` (CRA por defecto)
- **Despliegue**: No hay configuración de Vercel visible (vercel.json)

## Mejores Prácticas para Vercel

### 1. Configuración Mínima (vercel.json)
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```
Necesario para que React Router funcione correctamente en rutas hijas.

### 2. Optimizaciones de Build
- CRA build produce bundles grandes. Agregar `GENERATE_SOURCEMAP=false` en build para reducir tamaño
- Analizar bundle con `npx source-map-explorer build/static/js/*.js`
- React.lazy() para reducir bundle inicial

### 3. Headers de Caché
```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }
      ]
    }
  ]
}
```

### 4. CSP y Security Headers
Agregar Content-Security-Policy, X-Content-Type-Options, y otros headers de seguridad en vercel.json.

### 5. Migración Recomendada
CRA está en mantenimiento mínimo (2022). Vercel recomienda migrar a:
- **Next.js** (recomendado por Vercel): SSR, SSG, ISR, mejor SEO, API routes
- **Vite**: Build más rápido (~10x), mejor code splitting, tree-shaking superior

### 6. Variables de Entorno
Configurar en Vercel Dashboard:
- `REACT_APP_API_URL` → URL de producción del backend

### 7. Monitoreo
Vercel Analytics para Core Web Vitals y Web Analytics para tráfico.

## Recomendaciones

1. **Antes de desplegar**: asegurar que vercel.json existe con rewrites para SPA routing
2. **Después de desplegar**: verificar que React Router funciona en rutas hijas (refrescar en /eventos)
3. **Optimizar build**: `CI=false GENERATE_SOURCEMAP=false react-scripts build`
4. **Configurar headers**: caché agresivo para assets estáticos, caché mínimo para HTML
5. **Migrar a Vite o Next.js** para mejores velocidades de build y rendimiento del sitio
6. **Agregar Vercel Analytics** para monitorear LCP/INP/CLS reales
7. **Variables de entorno**: configurar en Vercel dashboard, no en código

## Prioridad de Acción

| Acción | Prioridad | Esfuerzo |
|--------|-----------|----------|
| vercel.json con rewrites | Alta | Bajo |
| Variables de entorno en Vercel | Alta | Bajo |
| Cache headers | Alta | Bajo |
| CSP headers | Media | Bajo |
| Security headers | Media | Bajo |
| Migrar a Vite | Media | Alto |
| Migrar a Next.js | Baja | Alto |
| Vercel Analytics | Baja | Bajo |
