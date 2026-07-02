"""
Vistas de la app core: listado de AuditLog y raiz de API.
"""
import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse

from apps.core.models import AuditLog
from apps.core.permissions import IsAdminUser
from apps.core.serializers import AuditLogSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_root(request: Request, format: str | None = None) -> Response:
    """
    Indice navegable de la API.

    Evita depender del APIRootView del primer DefaultRouter incluido, que solo
    muestra sus propios recursos cuando varias apps comparten el prefijo /api/v1/.
    """
    return Response({
        'usuarios': reverse('usuarios-list', request=request, format=format),
        'comuneros': reverse('comuneros-list', request=request, format=format),
        'autoridades': reverse('autoridad-list', request=request, format=format),
        'comites-comunales': reverse('comite-comunal-list', request=request, format=format),
        'categorias': reverse('categoria-list', request=request, format=format),
        'noticias': reverse('noticia-list', request=request, format=format),
        'eventos': reverse('evento-list', request=request, format=format),
        'multimedias': reverse('multimedia-list', request=request, format=format),
        'comentarios': reverse('comentario-list', request=request, format=format),
        'reacciones': reverse('reaccion-list', request=request, format=format),
        'favoritos': reverse('favorito-list', request=request, format=format),
        'mensajes': reverse('mensaje-list', request=request, format=format),
        'notificaciones': reverse('notificacion-list', request=request, format=format),
        'libro-reclamaciones': reverse('libro-reclamacion-list', request=request, format=format),
        'configuracion': reverse('configuracion-comunidad', request=request, format=format),
        'marco-legal': reverse('marco-legal-list', request=request, format=format),
        'paginas-legales': reverse('pagina-legal-list', request=request, format=format),
        'hitos-historicos': reverse('hito-historico-list', request=request, format=format),
        'galeria': reverse('galeria-imagen-list', request=request, format=format),
        'mensajes-contacto': reverse('mensaje-contacto-list', request=request, format=format),
        'audit-log': reverse('audit-log-list', request=request, format=format),
        'donaciones': reverse('donaciones:iniciar', request=request, format=format).rsplit('iniciar/', 1)[0],
        'cms/contenido': reverse('cms-contenido-list', request=request, format=format),
    })


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
