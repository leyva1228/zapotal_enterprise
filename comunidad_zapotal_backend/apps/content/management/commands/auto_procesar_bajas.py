import logging
from django.core.management.base import BaseCommand
from apps.content.services_user import BajaService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Procesa solicitudes de baja PENDIENTE cuyo plazo de gracia expiró (via BajaService).'

    def handle(self, *args, **options):
        count = BajaService.procesar_pendientes_vencidas()
        self.stdout.write(self.style.SUCCESS(f'{count} baja(s) auto-procesada(s).'))
