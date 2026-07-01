# Audit: Rediseno visual panel admin frontend

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-30
- Autor/agente: OpenCode / gpt-5.4
- Tecnologia: React + Vite + Tailwind

## Objetivo

Mejorar la experiencia visual del panel `/admin` del frontend con ajustes de UI/UX en layout, color, espaciado, jerarquia visual y microinteracciones sutiles, sin modificar logica de negocio ni contratos.

## Alcance

### Incluye

- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.jsx`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.css`
- clases visuales compartidas del dashboard renderizado dentro del layout admin

### No incluye

- `src/api.js`
- `src/context/`
- `src/components/RequireAuth*`
- `src/components/RequireAdmin*`
- cambios de auth, rutas, fetch, estados, eventos, handlers o contratos API
- cambios funcionales en filtros, tablas, formularios o acciones CRUD

## Contexto leido

- `AGENTS.md`
- `graphify.md`
- `comunidad_zapotal_frontend/AGENTS.md`
- `comunidad_zapotal_frontend/graphify/GRAPH_REPORT.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `agents-workflow/shared/checklists/preflight-checklist.md`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.jsx`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.css`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminDashboard.jsx`
- `comunidad_zapotal_frontend/src/index.css`
- `comunidad_zapotal_frontend/src/App.css`

## Estado actual

El panel admin ya tiene shell funcional con sidebar, topbar, cards, tablas, formularios y dashboard, pero presenta una mezcla visual entre estilos utilitarios y CSS manual. La base es usable, pero la jerarquia visual, la profundidad, el espaciado, el ritmo entre bloques y la consistencia de color pueden mejorar. Tambien faltan estilos dedicados para varias clases del dashboard.

## Riesgos

- contratos API: bajo, no se tocaran requests ni datos
- seguridad: bajo, no se tocara auth ni permisos
- migraciones: nulo
- UX: medio, un cambio visual amplio puede afectar legibilidad si no se verifica responsive
- performance: bajo, se priorizaran animaciones CSS ligeras y `prefers-reduced-motion`

## Skills recomendadas

- `frontend-design`
- `theme-factory`
- `brand-guidelines`
- `modern-web-design`
- `webapp-testing`
- `incremental-implementation`
- `verification-before-completion`

## Recomendacion

Redisenar primero el shell admin y los estilos compartidos desde CSS y clases ya existentes. Mantener intacta la logica del layout y de las paginas admin. Usar una paleta derivada del sistema visual actual del proyecto: verdes profundos, acentos dorados y superficies mas limpias. Incorporar microinteracciones sutiles solo con CSS cuando sea posible.

## Verificacion sugerida

- `npm run build`
- `npm run lint`
- validacion visual manual de `/admin` en desktop y viewport movil
