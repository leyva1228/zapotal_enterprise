"""Views institucionales (Fase 5)."""
import logging

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle, SimpleRateThrottle
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.core.permissions import IsAdminOrReadOnly, IsAdminUser
from .emails import notificar_admin_mensaje_contacto
from .zerobounce import validar_email as zb_validar, obtener_creditos as zb_creditos
from .models_institucionales import (
    ConfiguracionComunidad, MarcoLegalItem, PaginaLegal,
    HitoHistorico, GaleriaImagen, MensajeContacto,
    CategoriaGaleria, TextoSeccionInterna,
)
from .serializers_institucionales import (
    ConfiguracionComunidadSerializer, MarcoLegalItemSerializer,
    PaginaLegalSerializer, PaginaLegalPublicSerializer,
    HitoHistoricoSerializer, GaleriaImagenSerializer,
    MensajeContactoSerializer, MensajeContactoCreateSerializer,
    CategoriaGaleriaSerializer, TextoSeccionInternaSerializer,
)
from .serializers_institucionales import (
    ConfiguracionComunidadSerializer, MarcoLegalItemSerializer,
    PaginaLegalSerializer, PaginaLegalPublicSerializer,
    HitoHistoricoSerializer, GaleriaImagenSerializer,
    MensajeContactoSerializer, MensajeContactoCreateSerializer,
)

logger = logging.getLogger(__name__)


class ValidarEmailThrottle(ScopedRateThrottle):
    """Rate limit del endpoint publico de validacion de email:
    max 20 requests/hora por IP (suficiente para live-typing + foco)."""
    scope = 'validar_email'


class ValidarEmailView(APIView):
    """Endpoint publico GET /api/v1/validar-email/?email=foo@bar.com

    Utilizado por el frontend para mostrar feedback en vivo al usuario
    mientras escribe (live validation tipo debounce). Consume 1 credito
    de ZeroBounce por llamada (excepto si el status es ``unknown``).
    """
    permission_classes = [AllowAny]
    throttle_classes = [ValidarEmailThrottle]

    def get(self, request):
        email = (request.GET.get('email') or '').strip()
        if not email or '@' not in email:
            return Response(
                {'valido': False, 'motivo': 'Email vacio o sin @.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(email) > 254:  # RFC 5321 limite practico
            return Response(
                {'valido': False, 'motivo': 'Email demasiado largo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR')
        )
        resultado = zb_validar(email, ip_address=ip or None)
        # Log de uso (no del email completo por Ley 29733)
        logger.info(
            'ZeroBounce validar-email status=%s sub=%s ip=%s sandbox=%s',
            resultado.status, resultado.sub_status,
            '.'.join((ip or '?').split('.')[:2]) if ip else '?',
            resultado.modo_sandbox,
        )
        # No devolver 'raw' al cliente (informacion sensible de ZeroBounce)
        payload = resultado.to_dict()
        payload.pop('raw', None)
        return Response(payload)


class ZeroBounceCreditosView(APIView):
    """Endpoint admin GET /api/v1/admin/zerobounce/creditos/

    Retorna el saldo actual de creditos. Solo accesible para admins.
    Devuelve ``-1`` si la API key no esta configurada o si hay error
    de comunicacion.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.conf import settings
        habilitado = bool(getattr(settings, 'ZEROBOUNCE_API_KEY', ''))
        sandbox = bool(getattr(settings, 'ZEROBOUNCE_SANDBOX', False))
        creditos = zb_creditos() if habilitado and not sandbox else None
        return Response({
            'habilitado': habilitado,
            'sandbox':    sandbox,
            'creditos':   creditos,
        })


class EmailContactoPublicoView(APIView):
    """Endpoint publico GET /api/v1/public/email-contacto/

    Retorna el email destino activo (aplica el override
    ``settings.EMAIL_DESTINO_TEMPORAL`` si esta definido). Usado por
    el frontend para mostrar el mailto correcto sin redeploy.

    No expone PII ni requiere autenticacion.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from .emails import _resolver_destinatario
        return Response({
            'email_contacto': _resolver_destinatario(tipo='contacto'),
            'email_denuncias': _resolver_destinatario(tipo='denuncia'),
        })


class ConfiguracionComunidadView(generics.RetrieveUpdateAPIView):
    """Singleton: siempre retorna/actualiza el registro pk=1.

    GET publico. PATCH solo ADMIN.
    """
    serializer_class = ConfiguracionComunidadSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        return ConfiguracionComunidad.get_solo()

    def perform_update(self, serializer):
        # Loop 1 v2: registrar quien modifico.
        serializer.save(actualizado_por=self.request.user)


class MarcoLegalItemViewSet(viewsets.ModelViewSet):
    """Items editables del Marco Legal."""
    queryset = MarcoLegalItem.objects.filter(activo=True)
    serializer_class = MarcoLegalItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering = ['orden', 'id']
    filterset_fields = ['activo']


class PaginaLegalViewSet(viewsets.ModelViewSet):
    """Paginas legales (admin). Para la vista publica, ver PaginaLegalDetailView."""
    queryset = PaginaLegal.objects.all()
    serializer_class = PaginaLegalSerializer
    permission_classes = [IsAdminOrReadOnly]


class PaginaLegalDetailView(generics.RetrieveAPIView):
    """Endpoint publico para una pagina legal por slug."""
    serializer_class = PaginaLegalPublicSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return PaginaLegal.objects.filter(activo=True)


class HitoHistoricoViewSet(viewsets.ModelViewSet):
    """Linea de tiempo historica (publica lectura, admin escritura)."""
    queryset = HitoHistorico.objects.filter(activo=True)
    serializer_class = HitoHistoricoSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering = ['orden', '-anio', '-fecha']
    filterset_fields = ['activo']


class GaleriaImagenViewSet(viewsets.ModelViewSet):
    """Galeria de imagenes (publica lectura, admin escritura con upload)."""
    queryset = GaleriaImagen.objects.select_related('noticia', 'evento').filter(activo=True)
    serializer_class = GaleriaImagenSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    ordering = ['orden', '-fecha']
    filterset_fields = ['categoria', 'activo']

    def get_queryset(self):
        qs = super().get_queryset()
        cat = self.request.query_params.get('categoria')
        if cat:
            qs = qs.filter(categoria=cat)
        return qs


class MensajeContactoThrottle(ScopedRateThrottle):
    """Rate limit por IP: max 5 mensajes/hora."""
    scope = 'contacto'

    def get_cache_key(self, request, view):
        # El scope='contacto' ya throttla por IP, suficiente para
        # ataques distribuidos. Para un throttle adicional por email
        # se usa MensajeContactoPorEmailThrottle en la cadena.
        return super().get_cache_key(request, view)


class MensajeContactoPorEmailThrottle(SimpleRateThrottle):
    """V2.1: Rate limit adicional por email (3/15min).

    Evita que un mismo email pueda enviar multiples mensajes en
    paralelo. El identificador combina IP + email normalizado
    (case-insensitive, sin espacios) para que attackers que rotan
    IP no evadan el control.

    NOTA: usa ``SimpleRateThrottle`` (no ScopedRateThrottle) porque
    la vista no tiene ``throttle_scope`` y ScopedRateThrottle ignora
    el scope propio cuando el view no lo define.
    """
    scope = 'contacto_por_email'

    def parse_rate(self, rate):
        """Override: acepta formatos compuestos como ``3/15min`` o
        ``3/1h``. El parser nativo de DRF solo conoce el primer
        caracter de la unidad (s/m/h/d), asi que no soporta 15min.
        """
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        # Detectar sufijo compuesto (min, hour, day, sec)
        if period.endswith('min'):
            duration = int(period[:-3]) * 60
        elif period.endswith('sec'):
            duration = int(period[:-3])
        elif period.endswith('hour'):
            duration = int(period[:-4]) * 3600
        elif period.endswith('day'):
            duration = int(period[:-3]) * 86400
        else:
            # Fallback al parser nativo (s/m/h/d como primer caracter)
            duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return (num_requests, duration)

    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        email = ''
        if hasattr(request, 'data') and isinstance(request.data, dict):
            email = (
                request.data.get('email')
                or request.data.get('correo')
                or ''
            ).strip().lower()
        if not email:
            return None  # sin email no se throttle (deja al otro throttle actuar)
        return self.cache_format % {
            'scope': self.scope,
            'ident': f'{ip}:{email}',
        }


class MensajeContactoCreateView(generics.CreateAPIView):
    """Endpoint publico POST para enviar mensajes de contacto.

    Tras guardar el mensaje, dispara una notificacion al email
    institucional (Resend via django-anymail). Un fallo de SMTP no
    interrumpe la creacion: el mensaje queda persistido y se registra
    en los logs.
    """
    serializer_class = MensajeContactoCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [MensajeContactoThrottle, MensajeContactoPorEmailThrottle]

    def perform_create(self, serializer):
        ip = self.request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or \
             self.request.META.get('REMOTE_ADDR')
        ua = self.request.META.get('HTTP_USER_AGENT', '')[:500]
        instance = serializer.save(
            ip_origen=ip or None,
            user_agent=ua or '',
        )
        # Metricas de validacion de email (ZeroBounce) si el serializer
        # guardo el resultado en el context.
        zb_info = self.context.get('email_validacion_zb') if hasattr(self, 'context') else None
        if zb_info:
            logger.info(
                'MensajeContacto id=%s email_zb status=%s sub=%s valido=%s',
                instance.id,
                zb_info.get('status'),
                zb_info.get('sub_status'),
                zb_info.get('valido'),
            )
        # Notificar al buzon institucional. La operacion es best-effort:
        # si Resend falla, el mensaje sigue creado.
        try:
            enviado = notificar_admin_mensaje_contacto(instance)
            if enviado:
                logger.info(
                    'Notificacion de contacto enviada al admin (id=%s).',
                    instance.id,
                )
            else:
                logger.info(
                    'Notificacion de contacto NO enviada (id=%s) - sin destino o backend local.',
                    instance.id,
                )
        except Exception:
            logger.exception(
                'Excepcion inesperada al notificar contacto id=%s.',
                instance.id,
            )
        # Notificacion interna: crear Notificacion para cada admin activo
        # para que aparezca en /admin/notificaciones.
        self._crear_notificaciones_admin(instance)

    def _crear_notificaciones_admin(self, instance):
        from apps.accounts.models import Usuario
        from apps.messaging.models import Notificacion
        admins = Usuario.objects.filter(tipo_usuario='ADMIN', estado='ACTIVO')
        titulo = f'Nuevo mensaje de contacto de {instance.nombre}'
        preview = (instance.mensaje or '')[:200]
        notifs = [
            Notificacion(
                destinatario=admin,
                titulo=titulo,
                mensaje=preview,
                tipo='info',
                url_destino='/admin/contacto',
                referencia_tipo='CONTACTO',
                referencia_id=instance.id,
            )
            for admin in admins
        ]
        if notifs:
            Notificacion.objects.bulk_create(notifs, batch_size=50)
            logger.info(
                'Creadas %d notificaciones de contacto para admins (msg id=%s).',
                len(notifs), instance.id,
            )

    def create(self, request, *args, **kwargs):
        # Honeypot anti-spam: campo 'website' debe estar vacio
        if request.data.get('website'):
            return Response(
                {'detail': 'Spam detectado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class MensajeContactoAdminViewSet(viewsets.ModelViewSet):
    """CRUD admin para los mensajes recibidos.

    Acceso restringido a administradores activos. La vista publica de creacion
    esta en MensajeContactoCreateView. Por seguridad, este ViewSet NO es de
    solo lectura para anonimos: requiere rol admin en todas las acciones.
    """
    queryset = MensajeContacto.objects.all()
    serializer_class = MensajeContactoSerializer
    permission_classes = [IsAdminUser]
    ordering = ['-fecha']
    filterset_fields = ['leido', 'respondido']

    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, pk=None):
        obj = self.get_object()
        obj.leido = True
        obj.save(update_fields=['leido'])
        from apps.core.utils import log_audit_event
        log_audit_event(
            usuario=request.user,
            accion='UPDATE',
            modelo_afectado='MensajeContacto',
            objeto_id=str(obj.id),
            descripcion='Mensaje de contacto marcado como leido',
            request=request,
            metadata={'campo': 'leido', 'valor': True},
        )
        return Response({'status': 'leido'})

    @action(detail=True, methods=['post'])
    def marcar_respondido(self, request, pk=None):
        """Marca como respondido via mailto. NO envia email (eso lo hace
        el action `responder`)."""
        obj = self.get_object()
        obj.respondido = True
        obj.save(update_fields=['respondido'])
        from apps.core.utils import log_audit_event
        log_audit_event(
            usuario=request.user,
            accion='UPDATE',
            modelo_afectado='MensajeContacto',
            objeto_id=str(obj.id),
            descripcion='Mensaje de contacto marcado como respondido',
            request=request,
            metadata={'campo': 'respondido', 'valor': True},
        )
        return Response({'status': 'respondido'})

    @action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        """Envia una respuesta al visitante via email y marca como respondido.

        Body: {respuesta_texto: str}
        Efectos:
        - Envia email al visitante (con reply_to = admin).
        - Marca `respondido=True`, `respondido_desde_panel=True`.
        - Setea `respondido_por`, `respondido_at`, `respondido_texto`.
        - Crea audit log.
        """
        obj = self.get_object()
        texto = (request.data.get('respuesta_texto') or '').strip()
        if not texto:
            return Response(
                {'detail': 'Falta respuesta_texto.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(texto) > 5000:
            return Response(
                {'detail': 'La respuesta no puede superar 5000 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from .emails import enviar_respuesta_contacto
        enviado = enviar_respuesta_contacto(obj, texto, request.user)
        if not enviado:
            return Response(
                {'detail': 'No se pudo enviar el email. Intenta de nuevo.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        from django.utils import timezone
        obj.respondido = True
        obj.respondido_desde_panel = True
        obj.respondido_por = request.user
        obj.respondido_at = timezone.now()
        obj.respondido_texto = texto
        obj.save(update_fields=[
            'respondido', 'respondido_desde_panel',
            'respondido_por', 'respondido_at', 'respondido_texto',
        ])
        from apps.core.utils import log_audit_event
        log_audit_event(
            usuario=request.user,
            accion='UPDATE',
            modelo_afectado='MensajeContacto',
            objeto_id=str(obj.id),
            descripcion='Respuesta enviada al visitante desde el panel',
            request=request,
            metadata={'caracteres': len(texto)},
        )
        return Response({'status': 'respondido', 'email_enviado': True})

    @action(detail=True, methods=['post'])
    def set_prioridad(self, request, pk=None):
        """Actualiza la prioridad del mensaje (BAJA / MEDIA / ALTA)."""
        from .models_institucionales import MensajeContacto
        obj = self.get_object()
        nueva = (request.data.get('prioridad') or '').strip().upper()
        if nueva not in dict(MensajeContacto.Prioridad.choices):
            return Response(
                {'detail': f'Prioridad invalida. Use una de: {list(dict(MensajeContacto.Prioridad.choices).keys())}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj.prioridad = nueva
        obj.save(update_fields=['prioridad'])
        from apps.core.utils import log_audit_event
        log_audit_event(
            usuario=request.user,
            accion='UPDATE',
            modelo_afectado='MensajeContacto',
            objeto_id=str(obj.id),
            descripcion=f'Prioridad actualizada a {nueva}',
            request=request,
            metadata={'campo': 'prioridad', 'valor': nueva},
        )
        return Response({'status': 'ok', 'prioridad': nueva})

    @action(detail=True, methods=['post'])
    def nota(self, request, pk=None):
        """Guarda una nota interna del admin (NO se envia al visitante)."""
        from django.utils import timezone
        obj = self.get_object()
        nota = (request.data.get('nota') or '').strip()
        obj.nota_admin = nota
        obj.nota_admin_at = timezone.now()
        obj.nota_admin_por = request.user
        obj.save(update_fields=['nota_admin', 'nota_admin_at', 'nota_admin_por'])
        from apps.core.utils import log_audit_event
        log_audit_event(
            usuario=request.user,
            accion='UPDATE',
            modelo_afectado='MensajeContacto',
            objeto_id=str(obj.id),
            descripcion='Nota interna agregada al mensaje de contacto',
            request=request,
            metadata={'caracteres': len(nota)},
        )
        return Response({'status': 'ok'})


# ============================================================================
# Loop 1 v2: Categorias de Galeria + Textos de Secciones Internas
# ============================================================================
# Estas vistas existen para que Kotlin/Spring Boot y React consuman
# la misma fuente de verdad (single source of truth) de los textos
# que antes estaban hardcodeados en el frontend.


class CategoriaGaleriaViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista de categorias de galeria (publico).

    GET /api/v1/galerias/categorias/ -> lista todas las categorias activas
    """
    queryset = CategoriaGaleria.objects.filter(activo=True)
    serializer_class = CategoriaGaleriaSerializer
    pagination_class = None
    ordering = ['orden', 'nombre']


class CategoriaGaleriaAdminViewSet(viewsets.ModelViewSet):
    """CRUD admin para gestionar las categorias de la galeria."""
    queryset = CategoriaGaleria.objects.all()
    serializer_class = CategoriaGaleriaSerializer
    permission_classes = [IsAdminOrReadOnly]


class TextoSeccionInternaViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista de textos de secciones internas (publico, filtrable por idioma).

    GET /api/v1/textos-seccion/?idioma=es-PE
    GET /api/v1/textos-seccion/?seccion=CONOCENOS_HERO
    """
    queryset = TextoSeccionInterna.objects.filter(activo=True)
    serializer_class = TextoSeccionInternaSerializer
    pagination_class = None
    filterset_fields = ['seccion', 'idioma', 'activo']
    ordering = ['seccion', 'key']


class TextoSeccionInternaAdminViewSet(viewsets.ModelViewSet):
    """CRUD admin para textos de secciones internas."""
    queryset = TextoSeccionInterna.objects.all()
    serializer_class = TextoSeccionInternaSerializer
    permission_classes = [IsAdminOrReadOnly]
