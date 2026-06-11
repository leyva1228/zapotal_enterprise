# ADR-001: Custom User Model con email como identificador

**Fecha:** 2026-06-10
**Estado:** Aceptado

## Contexto

Django permite definir un modelo de usuario personalizado. El proyecto necesita
que el email sea el identificador único (no el username), y que existan
campos adicionales como `tipo_usuario` (ADMIN/COMUNERO/USUARIO) y `estado` (ACTIVO/INACTIVO).

## Decisión

- Crear `apps.accounts.models.Usuario` que hereda de `AbstractBaseUser` y `PermissionsMixin`.
- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = []`
- `objects = UsuarioManager()` con `create_user` y `create_superuser` basados en email.
- Activar `AUTH_USER_MODEL = 'accounts.Usuario'` en `settings.py`.

## Consecuencias

### Positivas
- Integración nativa con `django.contrib.auth`
- Soporte para `is_staff`, `is_superuser`, `groups`, `permissions`
- Compatible con `SimpleJWT` (que requiere AUTH_USER_MODEL)
- Login/logout con `authenticate()` y `login()` estándar de Django
- Admin de Django funciona con nuestro modelo

### Negativas
- Más código que usar AbstractUser
- Migración inicial debe hacerse antes de cualquier tabla

### Neutras
- Las queries a `Usuario` son equivalentes a las de cualquier modelo Django

## Alternativas Consideradas

1. **`AbstractUser`**: Más simple pero menos flexible. No permite reorganizar campos fácilmente.
2. **`AbstractBaseUser` solo**: Demasiado bajo nivel, tendríamos que implementar todo manualmente.
3. **Modelo User por defecto**: Insuficiente — no permite campos personalizados.

**Decisión final:** `AbstractBaseUser + PermissionsMixin` para máximo control.
