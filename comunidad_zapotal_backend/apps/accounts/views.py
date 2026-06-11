import logging

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from apps.core.permissions import IsAdminUser, IsAdminOrReadOnly
from .models import Usuario
from .serializers import (
    UsuarioSerializer, UsuarioEscrituraSerializer, LoginSerializer,
)

logger = logging.getLogger(__name__)


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


class ContactoThrottle(AnonRateThrottle):
    scope = 'contacto'


class RegisterThrottle(AnonRateThrottle):
    scope = 'register'


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios del sistema.

    Permisos:
    - list/retrieve: usuarios autenticados
    - create: solo ADMIN
    - update/destroy: solo ADMIN
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
        if user.is_authenticated and getattr(user, 'tipo_usuario', None) == 'ADMIN':
            return qs
        return qs.filter(id=user.id)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_usuario(request):
    """
    Inicio de sesión con emisión de JWT.

    Body:
    - email (string, requerido)
    - password (string, requerido)

    Respuestas:
    - 200: tokens JWT + datos del usuario
    - 401: credenciales inválidas
    - 403: usuario inactivo
    - 429: demasiados intentos
    """
    logger.info('Login attempt from %s', request.META.get('REMOTE_ADDR'))

    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data.get('user')

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    if user.estado != 'ACTIVO':
        logger.warning('Login attempt on inactive user: %s', user.email)
        return Response(
            {
                'error': {
                    'code': 'USER_INACTIVE',
                    'message': 'El usuario se encuentra inactivo.',
                }
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    nombres = ''
    apellidos = ''
    dni = None
    if hasattr(user, 'comunero') and user.comunero:
        nombres = user.comunero.nombres
        apellidos = user.comunero.apellidos
        dni = user.comunero.dni

    usuario_data = {
        'id': user.id,
        'email': user.email,
        'tipo_usuario': user.tipo_usuario,
        'estado': user.estado,
        'nombres': nombres,
        'apellidos': apellidos,
        'dni': dni,
        'foto_perfil': request.build_absolute_uri(user.foto_perfil.url) if user.foto_perfil else None,
    }

    logger.info('Login successful for user %s', user.email)

    return Response({
        'access': str(access),
        'refresh': str(refresh),
        'usuario': usuario_data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterThrottle])
def register_usuario(request):
    """
    Registro de nuevos usuarios. Solo para USUARIO y COMUNERO;
    los ADMIN deben ser creados por otro ADMIN.

    Body:
    - email, password, tipo_usuario, comunero (opcional)
    """
    serializer = UsuarioEscrituraSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    logger.info('New user registered: %s (%s)', user.email, user.tipo_usuario)
    return Response(
        UsuarioSerializer(user, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )
