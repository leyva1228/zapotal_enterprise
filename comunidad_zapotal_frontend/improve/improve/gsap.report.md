# Reporte de Análisis: gsap

**Proyecto:** Comunidad Campesina Zapotal — Portal Web
**Fecha:** 2026-06-10

## Resumen Ejecutivo

GSAP no está instalado en el proyecto (confirmado en package.json). Las animaciones actuales son CSS puras y AOS (v2.3.4). La app tiene oportunidades claras para GSAP en animaciones de entrada del hero, stagger en grids de cards, y transiciones de página, pero el costo de ~30KB debe justificarse frente a mejorar AOS o usar CSS nativo.

## Estado Actual

- **GSAP en package.json**: No
- **AOS**: v2.3.4 instalado y usado para scroll reveals
- **CSS Animations**: Transiciones básicas, hover effects, keyframes

## Análisis de Componentes

| Componente | Animación Actual | Potencial con GSAP | Prioridad |
|-----------|-----------------|-------------------|-----------|
| Hero (App.js) | CSS fade-in básico (o sin animación) | Timeline con stagger (título → subtítulo → CTA) | Media |
| Navbar | CSS transition para sticky | ScrollTrigger para cambio de fondo + sombra progresivo | Baja |
| Cards grids | AOS fade-up | Stagger + scale con ScrollTrigger | Media |
| Page Transitions | Sin animación | Fade + scale entre rutas | Media |
| Comentarios | Sin animación | Slide-in para nuevos comentarios | Baja |
| Loading Screen | CSS spinner/pulse | Animación de logo con timeline | Baja |

## Recomendaciones

1. **No instalar GSAP si solo se busca scroll reveal** — mejorar AOS es más simple
2. **Instalar GSAP si se planea**: hero con timeline, stagger en grids, y/o transiciones de página
3. **Para instalación parcial**: importar solo `gsap` core (sin plugins extras) para mantener bundle pequeño
4. **Crear hook `useScaleIn`** o `useStagger` para reutilizar patrones de animación
5. **Considerar Framer Motion** como alternativa: mejor integración con React, ~35KB

## Prioridad de Acción

| Acción | Prioridad | Esfuerzo |
|--------|-----------|----------|
| Decidir entre GSAP, Framer Motion o mejorar CSS/AOS | Alta | Bajo |
| Hero entrance animation | Media | Bajo |
| Stagger cards (reemplazar AOS) | Media | Medio |
| Page transitions | Baja | Medio |
