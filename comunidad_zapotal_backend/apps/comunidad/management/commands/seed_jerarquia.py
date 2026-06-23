"""
Management command: seed inicial de jerarquia administrativa.
Crea un Comunero ficticio, Autoridad PRESIDENTE y un superuser admin.
Idempotente.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

from apps.accounts.models import Usuario, Comunero
from apps.comunidad.models import Autoridad


class Command(BaseCommand):
    help = 'Crea datos iniciales de jerarquia administrativa (presidente + admin).'

    def handle(self, *args, **options):
        # Comunero para presidente
        presidente_comunero, _ = Comunero.objects.get_or_create(
            dni='00000001',
            defaults={'nombres': 'Presidente', 'apellidos': 'Inicial'},
        )

        # Superuser admin (idempotente)
        admin, created = Usuario.objects.get_or_create(
            email='admin@zapotal.com',
            defaults={
                'tipo_usuario': Usuario.TipoUsuario.ADMIN,
                'estado': Usuario.EstadoUsuario.ACTIVO,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created or not admin.has_usable_password():
            admin.set_password('Admin123456')
            admin.save()
        self.stdout.write(self.style.SUCCESS(f'Admin: {admin.email}'))

        # Autoridad presidente vinculada al admin
        Autoridad.objects.update_or_create(
            usuario=admin,
            defaults={
                'comunero': presidente_comunero,
                'cargo': Autoridad.TipoCargo.PRESIDENTE,
                'cargo_tipo': Autoridad.TipoCargo.PRESIDENTE,
                'periodo_inicio': date(2026, 1, 1),
                'periodo_fin': date(2030, 12, 31),
                'activo': True,
                'fecha_inicio': date(2026, 1, 1),
                'periodo': '2026-2030',
            },
        )
        self.stdout.write(self.style.SUCCESS('Autoridad PRESIDENTE creada.'))
        self.stdout.write(self.style.SUCCESS('Seed de jerarquia completado.'))
