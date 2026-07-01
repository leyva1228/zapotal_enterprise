# Plan: Rediseno visual panel admin frontend

## Estado

- Estado: IN_PROGRESS
- Requiere aprobacion humana: NO
- Fecha: 2026-06-30
- Tecnologia: React + Vite + Tailwind

## Objetivo

Elevar la calidad visual del panel `/admin` del frontend mejorando layout, espaciado, color, profundidad y consistencia visual sin alterar logica ni comportamiento.

## No objetivos

- no cambiar endpoints ni datos
- no tocar auth, permisos o rutas protegidas
- no refactorizar paginas admin fuera de lo necesario para presentacion
- no cambiar flujos CRUD ni handlers

## Skills obligatorias

- `writing-plans`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `frontend-design`
- `webapp-testing`

## Archivos permitidos

- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.jsx`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.css`

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/`
- `comunidad_zapotal_frontend/src/components/RequireAuth*`
- `comunidad_zapotal_frontend/src/components/RequireAdmin*`
- cualquier archivo fuera de `src/pages/Admin/` salvo bloqueo real

## Micro-tareas

### Task 1: Rediseno shell admin

- Objetivo: mejorar sidebar, topbar, contenedor principal y card de perfil
- Archivos:
  - `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.jsx`
  - `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.css`
- Pasos:
  - inspeccionar estructura existente
  - ajustar solo markup visual si hace falta
  - aplicar tokens y espaciado consistentes
  - agregar microinteracciones CSS y soporte reduced motion
  - revisar diff
- Comando de verificacion: build + validacion visual
- Criterio de exito: shell mas claro, premium y consistente sin romper rutas ni acciones
- Criterio de rollback: retirar wrappers o clases nuevas que afecten responsive o jerarquia

### Task 2: Estilos compartidos dashboard y superficies admin

- Objetivo: unificar cards, stats, listas, tablas, badges, inputs y botones del dashboard admin
- Archivos:
  - `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.css`
- Pasos:
  - definir estilos faltantes para clases `dash-*`
  - mejorar superficies, sombras, separaciones y hover/focus
  - mantener clases existentes sin tocar logica de `AdminDashboard.jsx`
  - revisar diff
- Comando de verificacion: build + validacion visual
- Criterio de exito: dashboard coherente con el nuevo shell y sin regressions funcionales
- Criterio de rollback: retirar estilos que hagan ilegible el contenido o generen overflow

### Task 3: Verificacion final

- Objetivo: comprobar que el panel sigue funcionando y que el cambio es solo visual
- Archivos:
  - sin nuevos archivos obligatorios
- Pasos:
  - ejecutar verificacion minima
  - levantar app y revisar `/admin`
  - revisar diff final
  - documentar resultados
- Comando de verificacion:
  - `npm run build`
  - `npm run lint`
- Criterio de exito: sin errores nuevos de compilacion atribuibles al cambio visual
- Criterio de rollback: detenerse y reportar si falla una verificacion por causa relacionada
