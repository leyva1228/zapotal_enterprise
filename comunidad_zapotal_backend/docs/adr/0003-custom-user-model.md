# ADR-0003: Custom User Model con AbstractBaseUser

## Estado
Aceptado (2026-06-10)

## Contexto
El sistema requiere que los usuarios se identifiquen con su **email** (no username). Adicionalmente, se necesitan campos custom como `tipo_usuario` (ADMIN, COMUNERO, USUARIO), `estado` (ACTIVO, INACTIVO), `comunero` (FK opcional).

## Decisión
- Crear `Usuario` que hereda de `AbstractBaseUser + PermissionsMixin`
- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = []`
- `objects = UsuarioManager()` con `create_user` y `create_superuser`
- `AUTH_USER_MODEL = 'accounts.Usuario'` en settings

## Consecuencias

### Positivas
- Email como identificador único (más usable)
- Compatible con `django.contrib.auth` (admin, permisos, groups)
- Soporte para `is_active`, `is_staff`, `is_superuser`, `last_login`, `date_joined`
- Control total sobre `save()`, `clean()`, manager

### Negativas
- **CRÍTICO:** La primera migración debe hacerse ANTES del primer `migrate`. Si no, hay que borrar la DB y empezar de nuevo.

### Implementación
Ver `apps/accounts/models.py:Usuario`.
