from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Prueba la conexión a la base de datos'

    def handle(self, *args, **options):
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('Conexión a la base de datos exitosa'))
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f'Error de conexión a la base de datos: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error inesperado: {e}'))