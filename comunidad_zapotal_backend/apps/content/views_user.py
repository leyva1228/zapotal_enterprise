"""Vistas para favoritos, solicitudes de baja y busqueda global."""
import logging
from django.utils import timezone
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.accounts.models import Usuario
from apps.core.permissions import IsAdminUser
from apps.core.utils import get_client_ip, log_audit_event
from apps.messaging.models import Notificacion
from .models import Favorito, SolicitudBaja, Noticia, Evento, Categoria
from .serializers import NoticiaSerializer, EventoSerializer
from .serializers_user import FavoritoSerializer, SolicitudBajaSerializer
from .services_user import BajaService

try:
    from apps.comunidad.serializers import AutoridadSerializer
except ImportError:
    AutoridadSerializer = None

logger = logging.getLogger(__name__)


# =====================================================================
# FAVORITOS
# =====================================================================

class FavoritoViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Favorito.objects.filter(usuario=self.request.user)
        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.select_related('noticia', 'evento').order_by('-fecha_agregado')

    def perform_create(self, serializer):
        favorito, created = serializer.save(usuario=self.request.user)
        if not created:
            raise Exception('El favorito ya existe.')
        log_audit_event(
            usuario=self.request.user,
            accion='CREATE',
            modelo_afectado='Favorito',
            objeto_id=str(favorito.id),
            descripcion=f'Favorito agregado ({favorito.tipo})',
            request=self.request,
        )

    def perform_destroy(self, instance):
        log_audit_event(
            usuario=self.request.user,
            accion='DELETE',
            modelo_afectado='Favorito',
            objeto_id=str(instance.id),
            descripcion=f'Favorito eliminado ({instance.tipo})',
            request=self.request,
        )
        instance.delete()


# =====================================================================
# SOLICITUDES DE BAJA (usuario)
# =====================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_estado_baja(request):
    """GET /api/v1/mi-cuenta/estado-baja/ -- historial de solicitudes del usuario."""
    qs = SolicitudBaja.objects.filter(usuario=request.user).select_related('revisado_por')
    return Response(SolicitudBajaSerializer(qs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def solicitar_baja(request):
    """POST /api/v1/mi-cuenta/solicitar-baja/"""
    serializer = SolicitudBajaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    usuario = request.user
    if SolicitudBaja.objects.filter(
        usuario=usuario, estado=SolicitudBaja.EstadoSolicitud.PENDIENTE,
    ).exists():
        return Response(
            {'detail': 'Ya tienes una solicitud de baja pendiente.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    solicitud = BajaService.crear_solicitud(usuario, serializer.validated_data['motivo'])

    log_audit_event(
        usuario=usuario,
        accion='BAJA_REQUESTED',
        modelo_afectado='SolicitudBaja',
        objeto_id=str(solicitud.id),
        descripcion=f'Usuario {usuario.email} solicito baja',
        request=request,
        metadata={'motivo': solicitud.motivo},
    )
    return Response(SolicitudBajaSerializer(solicitud).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelar_baja(request):
    """POST /api/v1/mi-cuenta/cancelar-baja/"""
    solicitud = BajaService.cancelar_solicitud(request.user)
    if not solicitud:
        return Response(
            {'detail': 'No tienes solicitudes de baja pendientes.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    log_audit_event(
        usuario=request.user,
        accion='BAJA_CANCELLED',
        modelo_afectado='SolicitudBaja',
        objeto_id=str(solicitud.id),
        descripcion=f'Usuario {request.user.email} cancelo su solicitud de baja',
        request=request,
    )
    return Response({'status': 'ok'})


# =====================================================================
# ADMIN: gestion de solicitudes de baja
# =====================================================================

class SolicitudBajaPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAdminUser])
def listar_solicitudes_baja(request):
    """GET /api/v1/solicitudes-baja/"""
    qs = SolicitudBaja.objects.all().select_related('usuario', 'revisado_por')
    estado = request.query_params.get('estado')
    if estado:
        qs = qs.filter(estado=estado)
    qs = qs.order_by('-fecha_solicitud')

    paginator = SolicitudBajaPagination()
    page = paginator.paginate_queryset(qs, request)
    if page is not None:
        serializer = SolicitudBajaSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    return Response(SolicitudBajaSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def total_solicitudes_baja(request):
    """GET /api/v1/solicitudes-baja/totales/ -- conteo por estado."""
    counts = {}
    for estado, _ in SolicitudBaja.EstadoSolicitud.choices:
        counts[estado] = SolicitudBaja.objects.filter(estado=estado).count()
    counts['total'] = SolicitudBaja.objects.count()
    return Response(counts)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def asignar_en_revision(request, solicitud_id):
    """POST /api/v1/solicitudes-baja/{id}/marcar-en-revision/"""
    solicitud, error = BajaService.asignar_en_revision(solicitud_id, request.user)
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
    log_audit_event(
        usuario=request.user,
        accion='BAJA_REVIEW_STARTED',
        modelo_afectado='SolicitudBaja',
        objeto_id=str(solicitud.id),
        descripcion=f'Admin {request.user.email} empezo a revisar baja de {solicitud.usuario.email}',
        request=request,
    )
    return Response(SolicitudBajaSerializer(solicitud).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def aprobar_baja(request, solicitud_id):
    """POST /api/v1/solicitudes-baja/{id}/aprobar/"""
    solicitud, error = BajaService.aprobar_solicitud(
        solicitud_id, request.user,
        notas=request.data.get('notas_admin', ''),
    )
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
    log_audit_event(
        usuario=request.user,
        accion='BAJA_APPROVED',
        modelo_afectado='Usuario',
        objeto_id=str(solicitud.usuario_id),
        descripcion=f'Baja aprobada para {solicitud.usuario.email}',
        request=request,
        metadata={'solicitud_id': solicitud.id, 'notas': request.data.get('notas_admin', '')},
    )
    return Response({'status': 'ok', 'estado': solicitud.estado})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def rechazar_baja(request, solicitud_id):
    """POST /api/v1/solicitudes-baja/{id}/rechazar/"""
    solicitud, error = BajaService.rechazar_solicitud(
        solicitud_id, request.user,
        notas=request.data.get('notas_admin', ''),
    )
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
    log_audit_event(
        usuario=request.user,
        accion='BAJA_REJECTED',
        modelo_afectado='SolicitudBaja',
        objeto_id=str(solicitud.id),
        descripcion=f'Baja rechazada para {solicitud.usuario.email}',
        request=request,
        metadata={'notas': request.data.get('notas_admin', '')},
    )
    return Response({'status': 'ok', 'estado': solicitud.estado})


# =====================================================================
# BUSQUEDA GLOBAL
# =====================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_global(request):
    """GET /api/v1/buscar/?q=texto"""
    q = (request.query_params.get('q') or '').strip()
    if len(q) < 3:
        return Response({
            'query': q,
            'total': 0,
            'resultados': {
                'noticias': [],
                'eventos': [],
                'autoridades': [],
            },
        })

    noticias = list(
        Noticia.objects.filter(
            Q(titulo__icontains=q) | Q(contenido__icontains=q) | Q(resumen__icontains=q),
            estado='PUBLICADA',
        ).order_by('-fecha_publicacion')[:5]
    )
    eventos = list(
        Evento.objects.filter(
            Q(titulo__icontains=q) | Q(descripcion__icontains=q) | Q(lugar__icontains=q),
        ).order_by('-fecha')[:5]
    )
    from apps.comunidad.models import Autoridad
    autoridades = list(
        Autoridad.objects.filter(
            Q(cargo__icontains=q) | Q(comunero__nombres__icontains=q) | Q(comunero__apellidos__icontains=q),
            activo=True,
        ).select_related('comunero')[:5]
    )

    return Response({
        'query': q,
        'total': len(noticias) + len(eventos) + len(autoridades),
        'resultados': {
            'noticias': NoticiaSerializer(noticias, many=True, context={'request': request}).data,
            'eventos': EventoSerializer(eventos, many=True, context={'request': request}).data,
            'autoridades': AutoridadSerializer(autoridades, many=True, context={'request': request}).data,
        },
    })


# =====================================================================
# NOTIFICACIONES (helpers)
# =====================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contador_no_leidas(request):
    """GET /api/v1/notificaciones/contador-no-leidas/"""
    count = Notificacion.objects.filter(destinatario=request.user, leido=False).count()
    return Response({'count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_todas_leidas(request):
    """POST /api/v1/notificaciones/marcar-todas-leidas/"""
    updated = Notificacion.objects.filter(destinatario=request.user, leido=False).update(leido=True)
    return Response({'updated': updated})
