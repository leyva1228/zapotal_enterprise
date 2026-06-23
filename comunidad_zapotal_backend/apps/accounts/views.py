"""
Vistas de accounts: login, register (solo admin).
"""
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone

from apps.core.permissions import IsAdminUser
from apps.core.utils import get_client_ip, log_audit_event
from .models import Usuario, Comunero
from .serializers import (
    UsuarioSerializer, UsuarioEscrituraSerializer, LoginSerializer, ComuneroSerializer,
)

logger = logging.getLogger(__name__)


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


class ContactoThrottle(AnonRateThrottle):
    scope = 'contacto'


class RegisterThrottle(AnonRateThrottle):
    scope = 'register'


class ComuneroViewSet(viewsets.ModelViewSet):
    """
    CRUD de comuneros.
    - Lectura: publica.
    - Escritura: solo ADMIN.
    """
    queryset = Comunero.objects.all()
    serializer_class = ComuneroSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['estado']
    search_fields = ['dni', 'nombres', 'apellidos']
    ordering_fields = ['apellidos', 'nombres', 'dni']
    ordering = ['apellidos', 'nombres']


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios del sistema.

    Permisos:
    - list: solo ADMIN
    - retrieve: usuario autenticado o ADMIN
    - create: solo ADMIN
    - update/destroy: solo ADMIN (o self para PATCH parcial de su perfil)
    """
    queryset = Usuario.objects.select_related('comunero')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['tipo_usuario', 'estado']
    search_fields = ['email']
    ordering_fields = ['fecha_registro', 'email']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioEscrituraSerializer
        return UsuarioSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and (
            getattr(user, 'es_admin_efectivo', False)
            or getattr(user, 'tipo_usuario', None) == 'ADMIN'
        ):
            return qs
        return qs.filter(id=user.id) if user.is_authenticated else qs.none()

    def get_object(self):
        """Permite a un usuario ver/editar su propio perfil sin ser ADMIN."""
        obj = super().get_object()
        user = self.request.user
        if user.is_authenticated and (
            getattr(user, 'es_admin_efectivo', False)
            or getattr(user, 'tipo_usuario', None) == 'ADMIN'
            or obj.id == user.id
        ):
            return obj
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('Solo puedes ver tu propio perfil.')

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        nuevo_estado = request.data.get('estado')
        if (nuevo_estado == Usuario.EstadoUsuario.ACTIVO
                and instance.estado == Usuario.EstadoUsuario.PENDIENTE_OTP):
            return Response(
                {
                    'detail': 'No se puede activar un usuario que no verifico su email. Espere a que complete el OTP.',
                    'code': 'USER_NOT_VERIFIED',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)


def _build_usuario_payload(user, request=None):
    """Helper usado por login tradicional y login 2FA."""
    nombres, apellidos, dni = '', '', None
    foto = None
    if hasattr(user, 'comunero') and user.comunero:
        nombres = user.comunero.nombres
        apellidos = user.comunero.apellidos
        dni = user.comunero.dni
    if user.foto_perfil:
        if request is not None:
            try:
                foto = request.build_absolute_uri(user.foto_perfil.url)
            except Exception:
                foto = user.foto_perfil.url
        else:
            foto = user.foto_perfil.url
    autoridad = user.get_autoridad_vigente()
    return {
        'id': user.id,
        'email': user.email,
        'tipo_usuario': user.tipo_usuario,
        'estado': user.estado,
        'nombres': nombres,
        'apellidos': apellidos,
        'dni': dni,
        'foto_perfil': foto,
        'foto_perfil_url': foto,
        'telefono': getattr(user, 'telefono', None),
        'es_admin': getattr(user, 'es_admin_efectivo', False),
        'es_autoridad': autoridad is not None,
        'autoridad_cargo': autoridad.cargo if autoridad else None,
        'two_factor_enabled': getattr(user, 'two_factor_enabled', False),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_usuario(request):
    """
    Login publico con emision de JWT.
    Redirige a /api/v1/auth/login/ para el flujo 2FA-aware, pero se mantiene
    este endpoint para compatibilidad y para el caso sin 2FA.
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data.get('user')

    if user.estado in (
        Usuario.EstadoUsuario.BLOQUEADO,
        Usuario.EstadoUsuario.RECHAZADO,
        Usuario.EstadoUsuario.INACTIVO,
    ):
        code_map = {
            Usuario.EstadoUsuario.BLOQUEADO: 'USER_BLOCKED',
            Usuario.EstadoUsuario.RECHAZADO: 'USER_REJECTED',
            Usuario.EstadoUsuario.INACTIVO: 'USER_INACTIVE',
        }
        return Response(
            {'error': {
                'code': code_map.get(user.estado, 'USER_INACTIVE'),
                'message': f'Estado invalido: {user.estado}',
            }},
            status=status.HTTP_403_FORBIDDEN,
        )

    if user.estado == Usuario.EstadoUsuario.PENDIENTE_OTP:
        return Response(
            {'error': {
                'code': 'USER_PENDING_OTP',
                'message': 'Debes verificar el codigo de registro.',
            }},
            status=status.HTTP_403_FORBIDDEN,
        )

    if user.two_factor_enabled:
        # Delegamos al nuevo endpoint 2FA-aware via header
        from .views_auth import login_usuario_v2
        return login_usuario_v2(request)

    refresh = RefreshToken.for_user(user)
    log_audit_event(
        usuario=user, accion='LOGIN', descripcion='Inicio de sesion exitoso',
        request=request, metadata={'metodo': 'password'},
    )
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'usuario': _build_usuario_payload(user, request),
        'requiere_otp': False,
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
@throttle_classes([RegisterThrottle])
def register_usuario(request):
    """
    Registro administrativo. Solo accesible para ADMIN.
    El registro publico se ha movido a /api/v1/registro/iniciar/.
    """
    serializer = UsuarioEscrituraSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    logger.info('New user (admin): %s (%s)', user.email, user.tipo_usuario)
    log_audit_event(
        usuario=request.user,
        accion='CREATE',
        modelo_afectado='Usuario',
        objeto_id=str(user.id),
        descripcion=f'Usuario {user.email} creado por admin',
        request=request,
    )
    return Response(
        UsuarioSerializer(user, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )
