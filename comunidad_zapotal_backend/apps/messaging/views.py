from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsOwnerOrReadOnly
from .models import Mensaje, Notificacion
from .serializers import MensajeSerializer, NotificacionSerializer


class MensajeViewSet(viewsets.ModelViewSet):
    """
    Mensajes privados entre usuarios.
    - Usuarios autenticados pueden crear mensajes a otros usuarios.
    - Solo ven los mensajes donde son remitente o destinatario.
    - Solo el remitente o el destinatario pueden ver/editar/eliminar un mensaje.
    """
    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filterset_fields = ['remitente', 'destinatario', 'leido']
    ordering_fields = ['fecha', 'leido']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Mensaje.objects.none()
        return Mensaje.objects.filter(
            remitente_id=user.id
        ) | Mensaje.objects.filter(destinatario_id=user.id)

    def perform_create(self, serializer):
        serializer.save(remitente=self.request.user)


class NotificacionViewSet(viewsets.ModelViewSet):
    """
    Notificaciones para un usuario.
    - Solo el destinatario ve sus notificaciones.
    - Solo el destinatario puede marcar como leída.
    """
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filterset_fields = ['tipo', 'leido']
    ordering_fields = ['fecha', 'leido']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notificacion.objects.none()
        qs = Notificacion.objects.filter(destinatario_id=user.id)
        if getattr(user, 'tipo_usuario', None) == 'ADMIN':
            qs = qs | Notificacion.objects.all()
        return qs
