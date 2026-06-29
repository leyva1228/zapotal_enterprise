# Agents Workflow Instructions

`agents-workflow/` es la zona operativa para agentes. Aqui viven auditorias, planes, ejecucion, revisiones y post-implementacion en archivos Markdown.

## Regla

- No guardar trabajo operativo nuevo en `docs/`.
- Todo audit, plan, task log, review o post-implementation nuevo debe ir aqui.
- Mantener un archivo `.md` por unidad de trabajo.

## Orden recomendado

1. crear auditoria
2. crear plan
3. obtener aprobacion
4. ejecutar micro-tareas
5. guardar evidencia de verificacion
6. crear review/post-implementation

## Estructura

- `shared/`: politicas, plantillas y checklists
- `<tecnologia>/audits/`
- `<tecnologia>/implementation-plans/`
- `<tecnologia>/implementation-tasks/`
- `<tecnologia>/post-implementation/`
