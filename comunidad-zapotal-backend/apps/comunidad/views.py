import logging

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Comunero, Autoridad
from .serializers import (
    ComuneroSerializer, ComuneroListSerializer,
    AutoridadSerializer, AutoridadEscrituraSerializer,
)

logger = logging.getLogger(__name__)


class ComuneroViewSet(viewsets.ModelViewSet):
    queryset = Comunero.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado']
    search_fields = ['nombres', 'apellidos', 'dni', 'correo']
    ordering_fields = ['apellidos', 'nombres', 'fecha_registro']

    def get_serializer_class(self):
        if self.action == 'list':
            return ComuneroListSerializer
        return ComuneroSerializer


class AutoridadViewSet(viewsets.ModelViewSet):
    queryset = Autoridad.objects.select_related('comunero', 'usuario_registra')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cargo', 'estado', 'comunero']
    search_fields = ['comunero__nombres', 'comunero__apellidos']
    ordering_fields = ['fecha_inicio']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AutoridadEscrituraSerializer
        return AutoridadSerializer

    def perform_create(self, serializer):
        serializer.save(usuario_registra=self.request.user)
