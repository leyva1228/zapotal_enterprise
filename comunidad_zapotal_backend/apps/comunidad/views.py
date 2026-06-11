from rest_framework import viewsets

from apps.core.permissions import IsAdminOrReadOnly
from .models import Autoridad
from .serializers import AutoridadSerializer


class AutoridadViewSet(viewsets.ModelViewSet):
    """
    Autoridades de la comunidad.
    - Lectura pública.
    - Escritura solo ADMIN.
    """
    queryset = Autoridad.objects.select_related('comunero', 'usuario')
    serializer_class = AutoridadSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['cargo', 'periodo', 'fecha_inicio']
    search_fields = ['cargo', 'comunero__nombres', 'comunero__apellidos']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    ordering = ['-fecha_inicio']
