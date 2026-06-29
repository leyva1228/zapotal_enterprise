# Parallel Execution Policy

Los subagentes pueden trabajar en paralelo solo si no comparten:

- mismos archivos
- mismos contratos
- mismo modelo o migracion
- mismo flujo auth/permisos/tokens
- misma pagina critica o misma pantalla

## Regla practica

- Si hay duda, ejecutar secuencialmente.
- Si una tarea cambia contrato API y otra lo consume, no paralelizar.
- Cada subagente debe recibir archivos permitidos, archivos prohibidos y comando de verificacion.
