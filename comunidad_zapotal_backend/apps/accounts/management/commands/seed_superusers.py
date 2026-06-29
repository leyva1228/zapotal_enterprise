"""
Crea el superuser administrador principal de la plataforma.

Idempotente: si ya existe el admin@zapotal.com no hace nada.

Uso:
    python manage.py seed_superusers
    python manage.py seed_superusers --admin-password=Miclave123
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import Usuario


class Command(BaseCommand):
    help = 'Crea el superuser admin@zapotal.com si no existe.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-password', type=str, default='Admin123456',
            help='Contrasena del superuser (default: Admin123456).',
        )
        parser.add_argument(
            '--admin-email', type=str, default='admin@zapotal.com',
            help='Email del superuser (default: admin@zapotal.com).',
        )

    def handle(self, *args, **options):
        email = options['admin_email']
        password = options['admin_password']

        admin, created = Usuario.objects.get_or_create(
            email=email,
            defaults={
                'tipo_usuario': Usuario.TipoUsuario.ADMIN,
                'estado': Usuario.EstadoUsuario.ACTIVO,
                'is_staff': True,
                'is_superuser': True,
                'email_verificado': True,
            },
        )
        if created or not admin.has_usable_password():
            admin.set_password(password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                f'  [OK] {email} creado/actualizado con password'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'  [OK] {email} ya existe (sin cambios)'
            ))
        return admin
