# Reporte de Análisis: animejs

**Proyecto:** Comunidad Campesina Zapotal — Portal Web
**Fecha:** 2026-06-10

## Resumen Ejecutivo

Anime.js no está instalado ni se usa en el proyecto. Es una alternativa más ligera (~24.5KB modular) que GSAP para animaciones que no requieren ScrollTrigger. Destaca en animaciones de texto (splitText, scrambleText) y SVG (morphing, drawing).

## Estado Actual

- **anime.js en package.json**: No
- **Animaciones actuales**: CSS + AOS
- **Comparativa vs GSAP**: Anime.js es más simple pero carece de scroll-driven animations nativas

## Evaluación de Uso Potencial

### Donde anime.js brillaría:
- **Text splitting**: Efectos de letra-por-letra en títulos del hero o secciones
- **Scramble text**: Efecto de revelado de texto (útil para cargar estados o transiciones)
- **Stagger simple**: Listas de ítems con entrada escalonada
- **Iconos SVG**: Pequeñas animaciones en iconos de redes sociales o branding

### Donde GSAP es mejor:
- **Scroll-driven animations**: ScrollTrigger no tiene equivalente en anime.js
- **Timelines complejas**: Mejor API de orquestación secuencial
- **Cross-browser consistency**: GSAP tiene mayor madurez

## Recomendación

**No instalar anime.js en este momento.** Para las necesidades actuales del proyecto:
- GSAP cubre mejor el caso de uso principal (scroll reveals + hero animation)
- CSS + AOS son suficientes para animaciones simples
- Si en el futuro se requieren efectos de texto avanzados, anime.js puede agregarse como complemento de GSAP

## Prioridad de Acción

| Acción | Prioridad | Esfuerzo |
|--------|-----------|----------|
| Evaluar si se necesita anime.js | Baja | Bajo |
| Implementar solo si se requieren efectos de texto | Baja | Medio |
