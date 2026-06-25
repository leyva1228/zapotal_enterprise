"""
V2.3: Purga notificaciones antiguas para evitar crecimiento ilimitado
de la tabla ``messaging_notificacion``.

Politica por defecto: elimina notificaciones leidas con mas de 90
dias de antiguedad, y notificaciones NO leidas con mas de 180 dias.

Cron sugerido (semanal, domingo 03:00 hora Lima):
    0 3 * * 0 cd /path/backend && venv/bin/python manage.py purge_old_notifications
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.messaging.models import Notificacion


class Command(BaseCommand):
    help = 'Purga notificaciones antiguas para mantener la tabla acotada.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=90,
            help='Dias para purgar notificaciones LEIDAS (default: 90).',
        )
        parser.add_argument(
            '--unread-days', type=int, default=180,
            help='Dias para purgar notificaciones NO leidas (default: 180).',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Solo contar las que se eliminarian.',
        )

    def handle(self, *args, **options):
        dry = options['dry_run']
        days_leidas = options['days']
        days_no_leidas = options['unread_days']
        ahora = timezone.now()

        cutoff_leidas = ahora - timedelta(days=days_leidas)
        cutoff_no_leidas = ahora - timedelta(days=days_no_leidas)

        qs_leidas = Notificacion.objects.filter(
            leido=True, fecha__lt=cutoff_leidas,
        )
        qs_no_leidas = Notificacion.objects.filter(
            leido=False, fecha__lt=cutoff_no_leidas,
        )

        n_leidas = qs_leidas.count()
        n_no_leidas = qs_no_leidas.count()

        if dry:
            self.stdout.write(self.style.WARNING(
                f'Dry run: se eliminarian {n_leidas} notificacion(es) leidas '
                f'(>{days_leidas}d) y {n_no_leidas} no leidas (>{days_no_leidas}d).'
            ))
            return

        # Purga en bulk. El .delete() en bulk emite un solo SQL DELETE,
        # mas eficiente que iterar.
        deleted_leidas, _ = qs_leidas.delete()
        deleted_no_leidas, _ = qs_no_leidas.delete()

        self.stdout.write(self.style.SUCCESS(
            f'Purgadas: {deleted_leidas} leidas (>{days_leidas}d) + '
            f'{deleted_no_leidas} no leidas (>{days_no_leidas}d). '
            f'Total eliminado: {deleted_leidas + deleted_no_leidas}.'
        ))
