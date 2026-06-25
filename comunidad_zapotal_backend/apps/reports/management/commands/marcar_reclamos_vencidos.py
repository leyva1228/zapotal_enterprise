"""
V2.2: Comando para implementar el SILENCIO ADMINISTRATIVO POSITIVO
(Ley 29571 Art. 24.2 - Codigo de Proteccion y Defensa del Consumidor).

Cuando un reclamo no ha sido atendido dentro del plazo legal (30 dias
habiles), el proveedor debe presumirse responsable. Este comando:

1. Busca reclamos con plazo_respuesta < hoy y estado != RESUELTO.
2. Cambia su estado a VENCIDO.
3. Crea un audit log del cambio.
4. Crea una notificacion para todos los admins activos.

Cron sugerido (diario, 06:00 hora Lima):
    0 6 * * * cd /path/backend && venv/bin/python manage.py marcar_reclamos_vencidos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.reports.models import LibroReclamacion
from apps.core.utils import log_audit_event


class Command(BaseCommand):
    help = 'Marca como VENCIDOS los reclamos con plazo legal excedido (silencio administrativo positivo).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Solo listar los reclamos que se marcarian, sin modificar.',
        )

    def handle(self, *args, **options):
        dry = options['dry_run']
        hoy = timezone.now().date()
        qs = LibroReclamacion.objects.filter(
            plazo_respuesta__lt=hoy,
        ).exclude(estado=LibroReclamacion.EstadoReclamacion.RESUELTO)
        # Solo los que NO estan ya en VENCIDO (idempotente).
        qs = qs.exclude(estado=LibroReclamacion.EstadoReclamacion.VENCIDO)

        candidatos = list(qs.values('id', 'numero_reclamo', 'estado', 'plazo_respuesta', 'nombre'))
        if not candidatos:
            self.stdout.write(self.style.SUCCESS(
                f'Sin reclamos vencidos al {hoy}.'
            ))
            return

        if dry:
            self.stdout.write(self.style.WARNING(
                f'Dry run: {len(candidatos)} reclamo(s) se marcarian como VENCIDO:'
            ))
            for c in candidatos:
                self.stdout.write(
                    f'  - {c["numero_reclamo"]} | {c["nombre"]} | plazo={c["plazo_respuesta"]} | estado={c["estado"]}'
                )
            return

        # Notificar a admins ANTES de cambiar el estado, para que la
        # notificacion refleje el estado anterior.
        from apps.messaging.services import notificar_todos_los_admins  # noqa: F401
        for c in candidatos:
            try:
                notificar_todos_los_admins(
                    tipo='RECLAMO_ESTADO_CAMBIADO',
                    titulo=f'Reclamo vencido por silencio administrativo',
                    mensaje=(
                        f'El reclamo {c["numero_reclamo"]} de {c["nombre"]} '
                        f'ha vencido (plazo {c["plazo_respuesta"]}). '
                        f'Conforme a Ley 29571, se presume la responsabilidad '
                        f'del proveedor.'
                    ),
                    url_destino=f'/admin/reclamaciones/{c["id"]}',
                )
            except Exception as exc:  # pragma: no cover - la notificacion es best-effort
                self.stdout.write(self.style.WARNING(
                    f'  ! No se pudo notificar admin del reclamo {c["numero_reclamo"]}: {exc}'
                ))

        # Cambiar estado a VENCIDO en bulk (atomic).
        updated = qs.update(estado=LibroReclamacion.EstadoReclamacion.VENCIDO)
        for c in candidatos:
            log_audit_event(
                usuario=None,
                accion='UPDATE',
                modelo_afectado='LibroReclamacion',
                objeto_id=str(c['id']),
                descripcion=(
                    f'Reclamo {c["numero_reclamo"]} marcado como VENCIDO '
                    f'(silencio administrativo positivo, plazo {c["plazo_respuesta"]})'
                ),
                request=None,
                metadata={'plazo_respuesta': str(c['plazo_respuesta']), 'trigger': 'cron_vencidos'},
            )

        self.stdout.write(self.style.SUCCESS(
            f'{updated} reclamo(s) marcados como VENCIDO al {hoy}.'
        ))
