import re
from django.core.exceptions import ValidationError


def validar_dni(value: str) -> str:
    if not re.fullmatch(r'\d{8}', value):
        raise ValidationError('El DNI debe tener exactamente 8 dígitos numéricos.')
    return value


def validar_telefono(value: str) -> str:
    if value and not re.fullmatch(r'\d{6,15}', value):
        raise ValidationError('El teléfono debe tener entre 6 y 15 dígitos.')
    return value
