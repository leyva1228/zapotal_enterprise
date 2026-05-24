# Semantic Versioning Policy

Este proyecto sigue **Semantic Versioning (SemVer)** para mantener un versionamiento consistente en todo el ecosistema SaaS multi-stack.

## Formato: MAJOR.MINOR.PATCH

### PATCH (0.0.X)
Incrementa cuando:
- Se corrigen bugs
- Se realizan mejoras pequeñas
- Se optimiza código
- **No se rompe compatibilidad**

**Ejemplo:** `0.1.0` → `0.1.1`

### MINOR (0.X.0)
Incrementa cuando:
- Se agregan funcionalidades nuevas
- Se añaden módulos o APIs
- Se crean nuevas pantallas
- **Se mantiene compatibilidad hacia atrás**

**Ejemplo:** `0.1.1` → `0.2.0`

### MAJOR (X.0.0)
Incrementa cuando:
- Se cambia la arquitectura
- Se rompe compatibilidad
- Se rehacen APIs existentes
- Se realizan cambios estructurales grandes

**Ejemplo:** `1.4.2` → `2.0.0`

## Versión Global del Proyecto

Todo el ecosistema usa **la misma versión** (actual: `1.0.1`):

| Componente | Versión | Estado |
|---|---|---|
| zapotal_core_django | 1.0.1 | ✅ |
| zapotal_web_react | 1.0.1 | ✅ |
| zapotal_ms_spring_boot | — | 🔄 Pendiente |
| zapotal_app_kotlin | — | 🔄 Pendiente |

Esto garantiza sincronización entre componentes y facilita el soporte.

## Cronología

| Versión | Cambios | Fecha |
|---|---|---|
| 0.1.0 | Inicio del proyecto, arquitectura inicial | — |
| 1.0.0 | React + Django funcionales, uvicorn, start.bat, README | 2026-05-24 |
| 1.0.1 | Fix estáticos Django admin (WhiteNoise + collectstatic), ASGI config | 2026-05-24 |
| 2.0.0 | 🔄 Próximo: Integración Spring Boot + Kotlin/Android | — |

## Gestión de Versiones

### Archivos de versión
- **VERSION**: Archivo raíz con la versión actual
- Este documento: Política de versionamiento

### Git Tags
Cada versión se marca con tags Git:

```bash
git tag v0.1.0
git push origin v0.1.0
```

### Formato de tags
- Usar el prefijo `v` seguido del número: `v0.1.0`, `v0.2.0`, etc.
- Tags se creen después de hacer merge a `main`
- Tags se pushean al repositorio remoto

## Actualización de Versión

Para actualizar a una nueva versión:

1. Actualizar el archivo `VERSION` con el nuevo número
2. Crear el commit con mensaje: `chore: bump version to X.Y.Z`
3. Crear el tag: `git tag vX.Y.Z`
4. Pushear: `git push origin main && git push origin vX.Y.Z`

## Referencias

- [Semantic Versioning Official](https://semver.org/)
- [Git Tagging Guide](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
