from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

import logging
from django.utils import timezone

from apps.core.permissions import IsAdminUser
from apps.core.utils import log_audit_event
from apps.comunidad.emails import (
    enviar_respuesta_reclamo,
    notificar_consumidor_cambio_estado_reclamo,
    notificar_admin_reclamo,
)
from .models import LibroReclamacion
from .services import ReclamacionService
from .serializers import (
    LibroReclamacionSerializer,
    LibroReclamacionCreateSerializer,
)

logger = logging.getLogger(__name__)


class LibroReclamacionPorEmailThrottle(SimpleRateThrottle):
    """V2.2: rate limit per-email para Libro de Reclamaciones (2/hora).

    Menos permisivo que el de contacto porque los reclamos tienen
    peso legal (Ley 29571). El identificador combina IP + email.
    """
    scope = 'libro_por_email'

    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        if period.endswith('min'):
            duration = int(period[:-3]) * 60
        elif period.endswith('sec'):
            duration = int(period[:-3])
        elif period.endswith('hour'):
            duration = int(period[:-4]) * 3600
        else:
            duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return (num_requests, duration)

    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        email = ''
        if hasattr(request, 'data') and isinstance(request.data, dict):
            email = (request.data.get('email') or '').strip().lower()
        if not email:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': f'{ip}:{email}',
        }


class LibroReclamacionViewSet(viewsets.ModelViewSet):
    """
    Libro de Reclamaciones (Ley N° 29571 - Perú).
    - Cualquier visitante puede crear un reclamo (POST).
    - Solo ADMIN puede listar, ver, cambiar estado o eliminar.
    - Restriccion: por privacidad (PII / Ley de Proteccion de Datos),
      los datos solo son accesibles a admins.
    """
    queryset = LibroReclamacion.objects.all()
    permission_classes = [IsAdminUser]
    filterset_fields = ['estado', 'tipo', 'leido', 'prioridad', 'fecha']
    search_fields = ['nombre', 'email', 'descripcion', 'numero_reclamo']
    ordering_fields = ['fecha', 'estado', 'prioridad', 'plazo_respuesta']
    ordering = ['-fecha']
    throttle_classes = []  # solo se aplica en create (override abajo)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action in ['create']:
            return LibroReclamacionCreateSerializer
        return LibroReclamacionSerializer

    def get_throttles(self):
        if self.action == 'create':
            return [LibroReclamacionPorEmailThrottle()]
        return []

    def perform_create(self, serializer):
        instance = serializer.save()
        # Notificar al buzon destino (override > email_contacto > ADMIN_EMAILS).
        try:
            enviado = notificar_admin_reclamo(instance)
            if enviado:
                logger.info(
                    'Notificacion de reclamo enviada al admin (id=%s numero=%s).',
                    instance.id, instance.numero_reclamo,
                )
        except Exception:
            logger.exception(
                'Excepcion inesperada al notificar reclamo id=%s.',
                instance.id,
            )
        # Notificacion interna: admins ven el reclamo en /admin/notificaciones.
        # Wrap en try/except para que un fallo en el buzon NO impida crear el reclamo.
        try:
            self._crear_notificaciones_admin(instance)
        except Exception:
            logger.exception(
                'Excepcion inesperada al crear notificaciones admin para reclamo id=%s.',
                instance.id,
            )

    def _crear_notificaciones_admin(self, instance):
        from apps.accounts.models import Usuario
        from apps.messaging.models import Notificacion
        admins = Usuario.objects.filter(tipo_usuario='ADMIN', estado='ACTIVO')
        titulo = f'Nuevo reclamo {instance.numero_reclamo} de {instance.nombre}'
        preview = (instance.descripcion or '')[:200]
        notifs = [
            Notificacion(
                destinatario=admin,
                titulo=titulo,
                mensaje=preview,
                tipo='nuevo_reclamo',  # Loop 3.x
                url_destino=f'/admin/reclamaciones?libro={instance.id}',
                referencia_tipo='RECLAMO',
                referencia_id=instance.id,
            )
            for admin in admins
        ]
        if notifs:
            Notificacion.objects.bulk_create(notifs, batch_size=50)
            logger.info(
                'Creadas %d notificaciones de reclamo para admins (id=%s).',
                len(notifs), instance.id,
            )

    def retrieve(self, request, *args, **kwargs):
        """Al hacer GET, marca el reclamo como leido por el admin."""
        instance = self.get_object()
        if not instance.leido:
            instance.leido = True
            instance.leido_at = timezone.now()
            instance.leido_por = request.user
            instance.save(update_fields=['leido', 'leido_at', 'leido_por'])
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def cambiar_estado(self, request, pk=None):
        reclamo = self.get_object()
        estado_anterior = reclamo.estado
        nuevo_estado = request.data.get('estado')
        estados_validos = [e[0] for e in LibroReclamacion.EstadoReclamacion.choices]
        if nuevo_estado not in estados_validos:
            return Response(
                {
                    'error': {
                        'code': 'INVALID_ESTADO',
                        'message': f'Estado debe ser uno de: {estados_validos}',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        reclamo.estado = nuevo_estado
        reclamo.save()
        # Notificar al consumidor por email (no in-app porque es anonimo).
        notificar_consumidor_cambio_estado_reclamo(reclamo, estado_anterior, nuevo_estado)
        # Notificar al admin que hizo el cambio (audit).
        from apps.messaging.models import Notificacion
        Notificacion.objects.create(
            destinatario=request.user,
            titulo=f'Reclamo {reclamo.numero_reclamo} -> {nuevo_estado}',
            mensaje=f'Cambiaste el estado de {estado_anterior} a {nuevo_estado}.',
            tipo='reclamo_estado_cambiado',
            url_destino=f'/admin/reclamaciones?libro={reclamo.id}',
            referencia_tipo='RECLAMO',
            referencia_id=reclamo.id,
        )
        log_audit_event(
            usuario=request.user, accion='UPDATE',
            modelo_afectado='LibroReclamacion', objeto_id=str(reclamo.id),
            descripcion=f'Cambio de estado {estado_anterior} -> {nuevo_estado}',
            request=request,
        )
        serializer = self.get_serializer(reclamo)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='plantillas-respuesta')
    def plantillas_respuesta(self, request, pk=None):
        """Retorna las plantillas predefinidas disponibles para responder."""
        reclamo = self.get_object()
        return Response({
            'plantillas': ReclamacionService.obtener_plantillas_respuesta(reclamo),
            'datos_reclamo': {
                'numero': reclamo.numero_reclamo,
                'nombre': reclamo.nombre,
                'tipo': reclamo.tipo,
                'descripcion': reclamo.descripcion,
                'plazo_respuesta': reclamo.plazo_respuesta,
            },
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def responder(self, request, pk=None):
        """Envia una respuesta al consumidor via email y marca como RESUELTO.

        Body: {respuesta_texto: str, plantilla_usada?: str}
        El admin edita la plantilla seleccionada y envia el texto final.
        """
        reclamo = self.get_object()
        texto = (request.data.get('respuesta_texto') or '').strip()
        if not texto:
            return Response({'detail': 'Falta respuesta_texto.'}, status=400)
        if len(texto) > 10000:
            return Response(
                {'detail': 'La respuesta no puede superar 10000 caracteres.'},
                status=400,
            )
        resultado_email = enviar_respuesta_reclamo(reclamo, texto, request.user)
        if not resultado_email.get('enviado'):
            return Response(
                {'detail': 'No se pudo enviar el email. Intenta de nuevo.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        reclamo.respuesta_admin = texto
        reclamo.respondido_por = request.user
        reclamo.respondido_at = timezone.now()
        reclamo.estado = LibroReclamacion.EstadoReclamacion.RESUELTO
        reclamo.save()
        from apps.messaging.models import Notificacion
        Notificacion.objects.create(
            destinatario=request.user,
            titulo=f'Reclamo {reclamo.numero_reclamo} respondido',
            mensaje=f'Se envio respuesta al consumidor {reclamo.nombre}.',
            tipo='info',
            url_destino=f'/admin/reclamaciones?libro={reclamo.id}',
            referencia_tipo='RECLAMO',
            referencia_id=reclamo.id,
        )
        log_audit_event(
            usuario=request.user, accion='UPDATE',
            modelo_afectado='LibroReclamacion', objeto_id=str(reclamo.id),
            descripcion='Reclamo respondido desde el panel',
            request=request,
            metadata={
                'caracteres': len(texto),
                'plantilla': request.data.get('plantilla_usada', ''),
            },
        )
        return Response({
            'status': 'respondido',
            'email_enviado': True,
            'estado': reclamo.estado,
            'preview': {
                'asunto': resultado_email.get('asunto', ''),
                'cuerpo_html': resultado_email.get('cuerpo_html', ''),
                'cuerpo_texto': resultado_email.get('cuerpo_texto', ''),
            },
        })
