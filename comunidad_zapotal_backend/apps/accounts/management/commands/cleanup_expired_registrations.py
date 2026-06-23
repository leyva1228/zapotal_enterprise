"""
Management command: cleanup_expired_registrations.

Elimina usuarios en estado PENDIENTE_OTP cuyo OTP haya expirado hace
mas de OTP_CLEANUP_GRACE_MINUTES minutos (ademas del VALIDEZ_MINUTOS del OTP).

Uso:
    python manage.py cleanup_expired_registrations
    python manage.py cleanup_expired_registrations --dry-run
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Usuario, OTPVerification, PendingApproval
from apps.core.utils import log_audit_event

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Elimina usuarios PENDIENTE_OTP cuyo OTP ha expirado (libera email/DNI/telefono).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Muestra cuantos se eliminarian sin ejecutar cambios.',
        )

    def handle(self, *args, **options):
        grace = getattr(settings, 'OTP_CLEANUP_GRACE_MINUTES', 15)
        validity = getattr(settings, 'OTP_VALIDITY_MINUTES', 10)
        umbral = timezone.now() - timedelta(minutes=validity + grace)

        candidatos = Usuario.objects.filter(
            estado=Usuario.EstadoUsuario.PENDIENTE_OTP,
        )
        eliminados = 0
        for u in candidatos:
            # Buscar el OTP mas reciente
            ultimo_otp = u.otps.order_by('-creado_en').first() if hasattr(u, 'otps') else None
            if ultimo_otp is None:
                # Nunca tuvo OTP, cumple la condicion por antiguedad del usuario
                if u.fecha_registro >= umbral:
                    continue
            else:
                if ultimo_otp.creado_en >= umbral:
                    continue

            if options['dry_run']:
                eliminados += 1
                self.stdout.write(f'[DRY-RUN] Eliminaria usuario {u.id} ({u.email})')
                continue

            with transaction.atomic():
                email = u.email
                dni = u.comunero.dni if u.comunero else None
                OTPVerification.objects.filter(usuario=u).delete()
                PendingApproval.objects.filter(usuario=u).delete()
                # Guardar info antes de eliminar (auditoria)
                try:
                    log_audit_event(
                        usuario=u,
                        accion='DELETE',
                        modelo_afectado='Usuario',
                        objeto_id=str(u.id),
                        descripcion=f'Limpieza automatica: usuario PENDIENTE_OTP expirado',
                        metadata={'motivo': 'otp_expirado', 'email_liberado': email, 'dni_liberado': dni},
                    )
                except Exception:  # noqa: BLE001
                    logger.warning('No se pudo escribir audit log para limpieza de %s', email)
                u.delete()  # CASCADE borra Comunero
            eliminados += 1
            self.stdout.write(self.style.WARNING(
                f'Eliminado usuario {u.id} ({email}, DNI {dni})'
            ))

        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS(
                f'[DRY-RUN] Se habrian eliminado {eliminados} usuarios expirados.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Cleanup completado. {eliminados} usuarios eliminados.'
            ))
