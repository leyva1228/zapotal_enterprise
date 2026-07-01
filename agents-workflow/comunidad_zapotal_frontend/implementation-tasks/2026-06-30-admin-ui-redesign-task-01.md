# Implementation Task: 2026-06-30-admin-ui-redesign-task-01

## Estado

- Estado: ACTIVE
- Fecha: 2026-06-30
- Tecnologia: React + Vite + Tailwind

## Objetivo

Aplicar un rediseno visual controlado al shell y superficies compartidas del panel admin sin tocar logica.

## Archivos permitidos

- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.jsx`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.css`

## Archivos prohibidos

- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/`
- `comunidad_zapotal_frontend/src/components/RequireAuth*`
- `comunidad_zapotal_frontend/src/components/RequireAdmin*`

## Reglas

- no refactorizar logica
- no expandir alcance fuera del admin shell y estilos visuales compartidos
- detenerse si se requiere tocar handlers, auth o contratos

## Verificacion

- comando: `npm run build` y `npm run lint`
- resultado esperado: app compila y no aparecen errores nuevos por el cambio visual

## Entrega requerida

- archivos cambiados
- resumen de diff
- comandos ejecutados
- riesgos o bloqueos
