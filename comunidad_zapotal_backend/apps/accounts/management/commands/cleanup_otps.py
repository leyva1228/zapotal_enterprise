"""
Management command: limpieza de OTPs expirados.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import OTPVerification


class Command(BaseCommand):
    help = 'Elimina OTPs expirados y usados.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Eliminar OTPs creados hace mas de N dias (default: 1).',
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options['days'])
        qs = OTPVerification.objects.filter(creado_en__lt=cutoff)
        # No eliminamos OTPs pendientes activos (expira_en > now)
        qs = qs.exclude(usado=False, expira_en__gt=timezone.now())
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'Eliminados {count} OTPs.'))
