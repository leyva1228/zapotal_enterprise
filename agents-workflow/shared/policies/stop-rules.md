# Agent Stop Rules

El agente debe detenerse si:

1. una prueba falla dos veces despues de intentos razonables de fix
2. necesita tocar archivos fuera del alcance
3. necesita cambiar auth, permisos, tokens o settings no contemplados
4. necesita crear migraciones no previstas
5. el build falla por una causa no relacionada
6. el diff es mucho mayor al esperado
7. no puede verificar el cambio
8. hay conflicto entre contrato, graphify y codigo sin poder resolverlo con seguridad

Al detenerse, debe reportar en Markdown:

- que intento
- que fallo
- archivos afectados
- hipotesis
- opciones recomendadas
