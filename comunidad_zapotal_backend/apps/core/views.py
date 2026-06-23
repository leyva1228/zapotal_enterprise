"""
Vistas de la app core: listado de AuditLog.
"""
import logging
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.models import AuditLog
from apps.core.permissions import IsAdminUser
from apps.core.serializers import AuditLogSerializer

logger = logging.getLogger(__name__)


class AuditLogListView(generics.ListAPIView):
    """
    GET /api/v1/audit-log/

    Filtros: accion, usuario, modelo_afectado, timestamp__gte, timestamp__lte, objeto_id.
    Solo accesible para administradores activos.
    """
    queryset = AuditLog.objects.select_related('usuario', 'autoridad').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['accion', 'usuario', 'modelo_afectado', 'objeto_id']
    ordering_fields = ['timestamp', 'accion']
    ordering = ['-timestamp']
