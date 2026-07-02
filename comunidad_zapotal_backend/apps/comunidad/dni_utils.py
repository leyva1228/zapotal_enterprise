"""
Helpers para el manejo de DNI.

El DNI peruano es dato sensible: 8 digitos unicos por persona.
En endpoints publicos se enmascara como '12****56' (primeros 2 y
ultimos 2 caracteres) salvo para usuarios administradores, que
pueden ver el DNI completo para fines de gestion institucional.
"""
from typing import Any


def mask_dni(dni: str | None) -> str:
    """Devuelve el DNI enmascarado en formato '12****56'.

    Casos:
        None o '' -> ''
        '12' (menos de 4 caracteres) -> '**' (asteriscos por la cantidad)
        '86615615' -> '86****15'
    """
    if not dni:
        return ''
    if len(dni) < 4:
        return '*' * len(dni)
    return f'{dni[:2]}****{dni[-2:]}'


def can_view_full_dni(user: Any) -> bool:  # noqa: ANN401
    """Indica si el usuario autenticado puede ver DNI completo.

    Acepta cualquier objeto con atributos is_authenticated, is_superuser
    y tipo_usuario (Usuario, AnonymousUser, None).

    Reglas:
        - anonimo (no autenticado): False
        - COMUNERO autenticado: False
        - ADMIN autenticado (tipo_usuario=ADMIN o is_superuser): True
        - autoridad con es_admin=True activa: True (gestiona la institucion)
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_superuser', False):
        return True
    return getattr(user, 'tipo_usuario', None) == 'ADMIN'
