from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.auth import OptionalJWTAuthentication
from apps.core.permissions import IsOwnerOrReadOnly
from .models import Mensaje, Notificacion
from .serializers import MensajeSerializer, NotificacionSerializer
from .services import MensajeService


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
        """
        Crea el mensaje a traves de MensajeService para garantizar:
        - Validacion de remitente != destinatario.
        - Creacion atomica del mensaje y su notificacion asociada.
        - Auditoria consistente.
        """
        try:
            mensaje = MensajeService.enviar_mensaje(
                remitente=self.request.user,
                destinatario=serializer.validated_data['destinatario'],
                contenido=serializer.validated_data['contenido'],
            )
        except ValueError as exc:
            raise DRFValidationError({'detail': str(exc)})
        # Sobrescribimos la instancia del serializer para que la respuesta
        # contenga el mensaje creado (incluye id, fecha, etc).
        serializer.instance = mensaje

    def create(self, request, *args, **kwargs):
        """
        Sobrescrito para devolver la respuesta con el serializer ya enlazado
        a la instancia creada por el service.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class NotificacionViewSet(viewsets.ModelViewSet):
    """
    Notificaciones para un usuario (Loop 3.1 — Modelo A inbox personal).

    MODELO (A): cada admin/comunero ve solo SUS notificaciones (donde
    ``destinatario=user``). NO hay broadcast, NO hay ``NotificacionLectura``.

    - Solo el destinatario ve sus notificaciones.
    - Solo el destinatario puede modificar (marcar como leida) o eliminar
      sus propias notificaciones.
    - El PATCH sobre una notificacion ajena retorna 403.
    """
    serializer_class = NotificacionSerializer
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filterset_fields = ['tipo', 'leido']
    ordering_fields = ['fecha', 'leido']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notificacion.objects.none()
        # MODELO (A): inbox personal. Cada usuario ve solo SUS notificaciones.
        return Notificacion.objects.filter(destinatario_id=user.id)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # MODELO (A): solo el destinatario puede modificar.
        if instance.destinatario_id != request.user.id:
            raise PermissionDenied('Solo el destinatario puede modificar esta notificacion.')
        if 'leido' in request.data:
            instance.leido = bool(request.data['leido'])
            if instance.leido and not instance.leido:
                pass  # ya estaba leido, no-op
            instance.save(update_fields=['leido'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='no-leidas/count')
    def no_leidas_count(self, request):
        """Cuenta las notificaciones no leidas del usuario actual (Loop 3.3).

        Usado por el badge del sidebar admin. Endpoint ligero: una sola query
        agregada COUNT, sin cargar objetos. Per-usuario (no global).
        """
        user = request.user
        if not user.is_authenticated:
            return Response({'count': 0})
        count = Notificacion.objects.filter(
            destinatario_id=user.id, leido=False,
        ).count()
        return Response({'count': count})
