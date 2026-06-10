import logging

from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioRegistroSerializer, LoginSerializer

logger = logging.getLogger(__name__)


class LoginThrottle(AnonRateThrottle):
    rate = '10/hour'


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioRegistroSerializer
        return UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_usuario(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'ok': False, 'errores': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = authenticate(request=request, username=email, password=password)

    if user is None:
        logger.warning(f'Login fallido: {email} desde {request.META.get("REMOTE_ADDR")}')
        return Response(
            {'ok': False, 'mensaje': 'Correo o contraseña incorrectos.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        return Response(
            {'ok': False, 'mensaje': 'El usuario se encuentra inactivo.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)
    logger.info(f'Login exitoso: {email} desde {request.META.get("REMOTE_ADDR")}')

    foto_url = None
    if user.foto_perfil:
        foto_url = request.build_absolute_uri(user.foto_perfil.url)

    return Response({
        'ok': True,
        'mensaje': 'Inicio de sesión correcto.',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'usuario': {
            'id': user.id,
            'nombres': user.first_name,
            'apellidos': user.last_name,
            'email': user.email,
            'dni': user.dni,
            'tipo_usuario': user.tipo_usuario,
            'dni_verificado': user.dni_verificado,
            'foto_perfil': foto_url,
        },
    })
