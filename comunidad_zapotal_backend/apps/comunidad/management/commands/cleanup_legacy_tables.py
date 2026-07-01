"""
Elimina tablas huerfanas de modelos antiguos que fueron removidos del codigo.

Loop V2.1: limpia `reports_contactomensaje`, relicto del modelo
`ContactoMensaje` que fue eliminado en la primera ronda de esta seccion.
"""
from django.core.management.base import BaseCommand
from django.db import connection


TABLAS_HUERFANAS = [
    'reports_contactomensaje',
]


def _table_exists(cursor, nombre):
    vendor = connection.vendor
    if vendor == 'mysql':
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = %s",
            [nombre],
        )
    elif vendor == 'postgresql':
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_catalog = current_catalog AND table_name = %s",
            [nombre],
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_name = %s",
            [nombre],
        )
    return cursor.fetchone()[0] > 0


class Command(BaseCommand):
    help = 'Elimina tablas huerfanas de modelos antiguos (codigo muerto).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Solo listar las tablas que se eliminarian, sin eliminar.',
        )

    def handle(self, *args, **options):
        dry = options['dry_run']
        with connection.cursor() as cursor:
            for tabla in TABLAS_HUERFANAS:
                existe = _table_exists(cursor, tabla)
                if not existe:
                    self.stdout.write(f'  - {tabla}: no existe (skip).')
                    continue
                if dry:
                    self.stdout.write(f'  - {tabla}: existe (se eliminaria).')
                else:
                    cursor.execute(f'DROP TABLE IF EXISTS {tabla};')
                    self.stdout.write(self.style.SUCCESS(
                        f'  - {tabla}: eliminada.'
                    ))
        if dry:
            self.stdout.write(self.style.WARNING(
                'Dry run: no se elimino ninguna tabla. Corre sin --dry-run para aplicar.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Tablas huerfanas eliminadas correctamente.'
            ))
