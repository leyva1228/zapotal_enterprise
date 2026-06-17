from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.permissions import IsAdminUser, IsAdminOrReadOnly
from .models import ContactoMensaje, LibroReclamacion
from .serializers import (
    ContactoMensajeSerializer,
    LibroReclamacionSerializer,
    LibroReclamacionCreateSerializer,
)


class ContactoMensajeViewSet(viewsets.ModelViewSet):
    """
    Mensajes de contacto.
    - Cualquier visitante puede crear (POST).
    - Solo ADMIN puede listar, ver, editar o eliminar.
    """
    queryset = ContactoMensaje.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['fecha']
    search_fields = ['nombre', 'email', 'asunto']
    ordering_fields = ['fecha']
    ordering = ['-fecha']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactoMensajeSerializer
        return ContactoMensajeSerializer


class LibroReclamacionViewSet(viewsets.ModelViewSet):
    """
    Libro de Reclamaciones (Ley N° 29571 - Perú).
    - Cualquier visitante puede crear un reclamo (POST).
    - Solo ADMIN puede listar, ver, cambiar estado o eliminar.
    """
    queryset = LibroReclamacion.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['estado', 'tipo', 'fecha']
    search_fields = ['nombre', 'email', 'descripcion']
    ordering_fields = ['fecha', 'estado']
    ordering = ['-fecha']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create']:
            return LibroReclamacionCreateSerializer
        return LibroReclamacionSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def cambiar_estado(self, request, pk=None):
        reclamo = self.get_object()
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
        serializer = self.get_serializer(reclamo)
        return Response(serializer.data)
