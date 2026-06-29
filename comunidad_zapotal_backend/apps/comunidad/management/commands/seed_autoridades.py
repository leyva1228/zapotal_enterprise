"""
Crea 6 autoridades con sus respectivos usuarios del sistema.

Las autoridades son:
  1. Presidente (admin)
  2. Vicepresidente (admin)
  3. Secretario
  4. Tesorero
  5. Regidor
  6. Vocal

Idempotente: si la autoridad o el usuario ya existe, no duplica.

Uso:
    python manage.py seed_autoridades
"""
from datetime import date

from django.core.management.base import BaseCommand
from apps.accounts.models import Usuario, Comunero
from apps.comunidad.models import Autoridad


AUTORIDADES = [
    {
        'dni': '00000001',
        'cargo': Autoridad.TipoCargo.PRESIDENTE,
        'es_admin': True,
        'email': 'presidente@zapotal.com',
        'descripcion': 'Presidente de la Comunidad Campesina de Zapotal. Lidera las asambleas generales y representa legalmente a la comunidad.',
    },
    {
        'dni': '00000002',
        'cargo': Autoridad.TipoCargo.VICEPRESIDENTE,
        'es_admin': True,
        'email': 'vicepresidente@zapotal.com',
        'descripcion': 'Vicepresidenta y coordinadora de programas sociales. Reemplaza al presidente en su ausencia.',
    },
    {
        'dni': '00000003',
        'cargo': Autoridad.TipoCargo.SECRETARIO,
        'es_admin': False,
        'email': 'secretario@zapotal.com',
        'descripcion': 'Encargado de la documentacion oficial, actas de asamblea y archivo comunal.',
    },
    {
        'dni': '00000004',
        'cargo': Autoridad.TipoCargo.TESORERO,
        'es_admin': False,
        'email': 'tesorero@zapotal.com',
        'descripcion': 'Administra los recursos financieros de la comunidad y presenta informes trimestrales.',
    },
    {
        'dni': '00000005',
        'cargo': Autoridad.TipoCargo.REGIDOR,
        'es_admin': False,
        'email': 'regidor1@zapotal.com',
        'descripcion': 'Regidor de obras y mantenimiento. Supervisa la infraestructura comunal.',
    },
    {
        'dni': '00000006',
        'cargo': Autoridad.TipoCargo.VOCAL,
        'es_admin': False,
        'email': 'vocal1@zapotal.com',
        'descripcion': 'Vocal de educacion y cultura. Coordina actividades culturales y educativas.',
    },
]


class Command(BaseCommand):
    help = 'Crea 6 autoridades con usuario y cargo vinculado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password', type=str, default='Zapotal2026',
            help='Contrasena de las autoridades (default: Zapotal2026).',
        )

    def handle(self, *args, **options):
        password = options['password']
        hoy = date.today()
        autoridades = []

        for cfg in AUTORIDADES:
            # Buscar o crear el comunero
            comunero, _ = Comunero.objects.get_or_create(
                dni=cfg['dni'],
                defaults={
                    'nombres': cfg['email'].split('@')[0].title(),
                    'apellidos': 'Comunero Zapotal',
                },
            )

            # Crear o actualizar el usuario
            usuario, user_created = Usuario.objects.get_or_create(
                email=cfg['email'],
                defaults={
                    'tipo_usuario': (
                        Usuario.TipoUsuario.ADMIN
                        if cfg['es_admin']
                        else Usuario.TipoUsuario.COMUNERO
                    ),
                    'estado': Usuario.EstadoUsuario.ACTIVO,
                    'comunero': comunero,
                    'is_staff': cfg['es_admin'],
                    'email_verificado': True,
                },
            )
            if user_created or not usuario.has_usable_password():
                usuario.set_password(password)
                usuario.save()

            # Crear o actualizar la autoridad
            autoridad, _ = Autoridad.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'comunero': comunero,
                    'cargo': cfg['cargo'],
                    'cargo_tipo': cfg['cargo'],
                    'periodo_inicio': date(hoy.year, 1, 1),
                    'periodo_fin': date(hoy.year + 4, 12, 31),
                    'activo': True,
                    'es_admin': cfg['es_admin'],
                    'fecha_inicio': date(hoy.year, 1, 1),
                    'periodo': f'{hoy.year}-{hoy.year + 4}',
                },
            )
            autoridades.append(autoridad)

        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {len(autoridades)} autoridades (usuarios + cargos) listos'
        ))
