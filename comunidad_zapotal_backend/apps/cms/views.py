from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.core.permissions import IsAdminOrReadOnly
from .models import ContenidoEstatico
from .serializers import ContenidoEstaticoPublicSerializer, ContenidoEstaticoAdminSerializer


class ContenidoEstaticoViewSet(viewsets.ModelViewSet):
    queryset = ContenidoEstatico.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return ContenidoEstaticoAdminSerializer
        return ContenidoEstaticoPublicSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        seccion = self.request.query_params.get('seccion')
        if seccion:
            qs = qs.filter(seccion=seccion)
        if not (self.request.user and self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(activo=True)
        return qs.order_by('orden', 'seccion')
