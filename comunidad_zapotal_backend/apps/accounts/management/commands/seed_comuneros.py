"""
Crea los comuneros base de la plataforma.

Idempotente: si un DNI ya existe, no lo duplica.
Ademas crea un usuario comunero demo (juan@zapotal.com) para login.

Uso:
    python manage.py seed_comuneros
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import Comunero, Usuario


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
    help = 'Crea 7 comuneros base + usuario demo comunero.'

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

        comunero, _ = Comunero.objects.get_or_create(
            dni='10000001',
            defaults={'nombres': 'Juan Demo', 'apellidos': 'Comunero Zapotal'},
        )
        usuario, user_created = Usuario.objects.get_or_create(
            email='juan@zapotal.com',
            defaults={
                'tipo_usuario': Usuario.TipoUsuario.COMUNERO,
                'estado': Usuario.EstadoUsuario.ACTIVO,
                'comunero': comunero,
                'email_verificado': True,
            },
        )
        if user_created or not usuario.has_usable_password():
            usuario.set_password('Zapotal2026')
            usuario.save()
        self.stdout.write(self.style.SUCCESS(f'  [OK] Usuario comunero demo: juan@zapotal.com / Zapotal2026'))
