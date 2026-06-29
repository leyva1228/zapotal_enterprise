"""
Crea los comuneros base de la plataforma.

Idempotente: si un DNI ya existe, no lo duplica.

Uso:
    python manage.py seed_comuneros
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import Comunero


COMUNEROS = [
    ('00000001', 'Juan Carlos', 'Perez Lopez'),
    ('00000002', 'Maria Elena', 'Gutierrez Ramirez'),
    ('00000003', 'Pedro Antonio', 'Sanchez Morales'),
    ('00000004', 'Ana Lucia', 'Torres Vega'),
    ('00000005', 'Luis Alberto', 'Rojas Cardenas'),
    ('00000006', 'Rosa Maria', 'Chavez Quispe'),
    ('00000007', 'Miguel Angel', 'Huaman Diaz'),
]


class Command(BaseCommand):
    help = 'Crea 7 comuneros base de la plataforma.'

    def handle(self, *args, **options):
        creados = 0
        existentes = 0
        for dni, nombres, apellidos in COMUNEROS:
            _, created = Comunero.objects.get_or_create(
                dni=dni,
                defaults={'nombres': nombres, 'apellidos': apellidos},
            )
            if created:
                creados += 1
            else:
                existentes += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creados} nuevos, {existentes} ya existian (total: {Comunero.objects.count()})'
        ))
