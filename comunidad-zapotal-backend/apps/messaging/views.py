import logging

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Mensaje, Notificacion
from .serializers import MensajeSerializer, NotificacionSerializer

logger = logging.getLogger(__name__)


class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje.objects.select_related('remitente', 'destinatario')
    serializer_class = MensajeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'leido', 'remitente', 'destinatario']
    search_fields = ['asunto', 'cuerpo']
    ordering_fields = ['fecha_envio']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(remitente=user) | qs.filter(destinatario=user)
        return qs

    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, pk=None):
        mensaje = self.get_object()
        mensaje.leido = True
        mensaje.estado = Mensaje.EstadoMensaje.LEIDO
        mensaje.fecha_lectura = timezone.now()
        mensaje.save(update_fields=['leido', 'estado', 'fecha_lectura'])
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(remitente=self.request.user)
        logger.info(
            f'Mensaje enviado: {self.request.user.email} -> '
            f'{serializer.validated_data["destinatario"].email}'
        )


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.select_related('usuario')
    serializer_class = NotificacionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo', 'leido', 'usuario']
    ordering_fields = ['fecha']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(usuario=user)
        return qs

    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, pk=None):
        notif = self.get_object()
        notif.leido = True
        notif.save(update_fields=['leido'])
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def marcar_todas_leido(self, request):
        notifs = self.get_queryset().filter(leido=False)
        count = notifs.update(leido=True)
        return Response({'status': f'{count} notificaciones marcadas como leídas.'})
