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
from .services import AuthService
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
    # search_fields vacio: el search se maneja manualmente en
    # filter_queryset() para incluir campos del Comunero relacionado
    # (email + nombres + apellidos + dni).
    search_fields = []
    ordering_fields = ['fecha_registro', 'email']

    def get_permissions(self):
        """Relaja el permiso de retrieve/update/partial_update para que un
        usuario autenticado pueda ver/editar SU propio perfil (foto,
        telefono, etc.) sin ser admin. `get_object` valida luego que el
        target sea el propio usuario o admin. List/destroy siguen siendo
        admin-only.
        """
        if self.action in ('retrieve', 'update', 'partial_update'):
            return [IsAuthenticated()]
        return [IsAdminUser()]

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

    def filter_queryset(self, queryset):
        """Override LOOP 1:
        - Magic value 'PENDIENTE' mapea a ambos estados pendientes.
        - Search extendido a nombre/apellido/DNI del comunero relacionado.
        """
        from django.db.models import Q
        from django.http import QueryDict

        estado = self.request.query_params.get('estado')
        if estado in ('PENDIENTE', 'PENDIENTE_OTP,PENDIENTE_APROBACION'):
            queryset = queryset.filter(
                Q(estado='PENDIENTE_OTP')
                | Q(estado='PENDIENTE_APROBACION')
            )
            # Reconstruimos el QueryDict sin 'estado' para que
            # django-filter no lo re-procese (causaria 400).
            new_qd = QueryDict(mutable=True)
            for k, v in self.request.query_params.items():
                if k != 'estado':
                    new_qd.appendlist(k, v)
            self.request._request.GET = new_qd

        # Aplicar filtros estandar (tipo_usuario, etc).
        queryset = super().filter_queryset(queryset)

        # Extender el search para incluir campos del Comunero relacionado.
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(comunero__nombres__icontains=search)
                | Q(comunero__apellidos__icontains=search)
                | Q(comunero__dni__icontains=search)
            )

        return queryset

    def get_object(self):
        """Permite a un usuario ver/editar su propio perfil sin ser ADMIN.
        `get_permissions` ya valida que solo los autenticados pueden llegar
        aca en update/partial_update. Aqui confirmamos que el target es
        el propio user (o admin).
        """
        obj = super().get_object()
        user = self.request.user
        if user.is_authenticated and (
            getattr(user, 'es_admin_efectivo', False)
            or getattr(user, 'tipo_usuario', None) == 'ADMIN'
            or obj.id == user.id
        ):
            return obj
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('Solo puedes ver/editar tu propio perfil.')

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        nuevo_estado = request.data.get('estado')
        estado_anterior = instance.estado
        if (nuevo_estado == Usuario.EstadoUsuario.ACTIVO
                and instance.estado == Usuario.EstadoUsuario.PENDIENTE_OTP):
            return Response(
                {
                    'detail': 'No se puede activar un usuario que no verifico su email. Espere a que complete el OTP.',
                    'code': 'USER_NOT_VERIFIED',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = super().partial_update(request, *args, **kwargs)
        # Notificaciones internas: aprobacion, rechazo, bloqueo, desbloqueo.
        self._notificar_cambio_estado(instance, estado_anterior, nuevo_estado, actor_id=request.user.id)
        return response

    def _notificar_cambio_estado(self, instance, estado_anterior, nuevo_estado, actor_id=None):
        """Crea Notificacion para el usuario afectado y notifica a otros admins."""
        from apps.accounts.models import Usuario
        from apps.messaging.models import Notificacion
        # No notificar si no hubo cambio de estado
        if not nuevo_estado or estado_anterior == nuevo_estado:
            return
        tipo_map = {
            Usuario.EstadoUsuario.ACTIVO: 'aprobacion_cuenta',
            Usuario.EstadoUsuario.RECHAZADO: 'rechazo_cuenta',
            Usuario.EstadoUsuario.BLOQUEADO: 'cuenta_bloqueada',
            Usuario.EstadoUsuario.INACTIVO: 'cuenta_inactivada',
        }
        tipo = tipo_map.get(nuevo_estado)
        if not tipo:
            return
        titulo_map = {
            'aprobacion_cuenta': 'Tu cuenta fue aprobada',
            'rechazo_cuenta': 'Tu solicitud de cuenta fue rechazada',
            'cuenta_bloqueada': 'Tu cuenta fue bloqueada',
            'cuenta_inactivada': 'Tu cuenta fue inactivada',
        }
        # 1) Notificar al usuario afectado
        Notificacion.objects.create(
            destinatario=instance,
            titulo=titulo_map[tipo],
            mensaje=f'Estimado/a {instance.email}, el estado de tu cuenta cambio a {nuevo_estado}.',
            tipo=tipo,
            url_destino='/cuenta',
        )
        # 2) Notificar a otros admins del cambio (excluyendo al actor que hizo el cambio)
        admins = Usuario.objects.filter(tipo_usuario='ADMIN', estado='ACTIVO')
        if actor_id is not None:
            admins = admins.exclude(id=actor_id)
        admin_notifs = [
            Notificacion(
                destinatario=admin,
                titulo=f'Admin: cuenta de {instance.email} -> {nuevo_estado}',
                mensaje=f'El estado cambio de {estado_anterior} a {nuevo_estado}.',
                tipo='info',
                url_destino=f'/admin/usuarios?estado={nuevo_estado}',
                referencia_tipo='USUARIO',
                referencia_id=instance.id,
            )
            for admin in admins
        ]
        if admin_notifs:
            Notificacion.objects.bulk_create(admin_notifs, batch_size=50)


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
    Si el usuario tiene 2FA activo, retorna requires_2fa + token_temp.
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data.get('user')

    # --- Auto-desbloqueo si bloqueo temporal expiró ---
    if user.estado == Usuario.EstadoUsuario.BLOQUEADO and user.bloqueado_hasta:
        if timezone.now() >= user.bloqueado_hasta:
            user.estado = Usuario.EstadoUsuario.ACTIVO
            user.is_active = True
            user.bloqueado_hasta = None
            user.failed_login_attempts = 0
            user.save(update_fields=['estado', 'is_active', 'bloqueado_hasta', 'failed_login_attempts'])
            logger.info('Bloqueo temporal expirado para usuario %s', user.email)

    # --- Estados que bloquean login ---
    if user.estado in (
        Usuario.EstadoUsuario.BLOQUEADO,
        Usuario.EstadoUsuario.RECHAZADO,
        Usuario.EstadoUsuario.INACTIVO,
        Usuario.EstadoUsuario.DE_BAJA,
    ):
        code_map = {
            Usuario.EstadoUsuario.BLOQUEADO: 'USER_BLOCKED',
            Usuario.EstadoUsuario.RECHAZADO: 'USER_REJECTED',
            Usuario.EstadoUsuario.INACTIVO: 'USER_INACTIVE',
            Usuario.EstadoUsuario.DE_BAJA: 'USER_DE_BAJA',
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
        token_temp = AuthService.issue_short_token(user)
        return Response({
            'requires_2fa': True,
            'token_temp': token_temp,
            'usuario_id': user.id,
        }, status=status.HTTP_202_ACCEPTED)

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
