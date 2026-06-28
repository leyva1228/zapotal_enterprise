"""
Vistas (endpoints) para la app de donaciones con Mercado Pago.

Los endpoints `iniciar`, `procesar` y `mis-donaciones` requieren
autenticacion (solo comuneros y autoridades pueden donar).
`webhook` queda publico porque MP lo llama sin auth.
`estadisticas` es publico (anonimo) para mostrar impacto en la landing.
La seguridad se basa en:
- Token opaco del Brick (no se puede falsificar un pago).
- Idempotencia por donation_id (no se puede reprocesar).
- Audit log de cada transaccion.
- Webhook firmado de MP (en produccion, validar source IP).
"""
import logging
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.services import EmailService
from apps.core.utils import log_audit_event, get_client_ip

from .models import Donacion
from .serializers import (
    IniciarDonacionSerializer,
    ProcesarPagoSerializer,
    DonacionSerializer,
    DonacionPublicaSerializer,
    EstadisticasDonacionesSerializer,
)
from .services import MercadoPagoService, MercadoPagoError
from .permissions import DonacionRateThrottle, WebhookRateThrottle


logger = logging.getLogger(__name__)


def _obtener_datos_payer(payer_data, donacion):
    """Extrae email y identificacion del payer que envio el Brick."""
    email = (payer_data or {}).get('email') or donacion.email_donante or ''
    identification = (payer_data or {}).get('identification')
    if not identification and donacion.documento_donante:
        identification = {'type': 'DNI', 'number': donacion.documento_donante}
    return email, identification


class IniciarDonacionView(APIView):
    """
    POST /api/v1/donaciones/iniciar/

    Requiere autenticacion (solo comuneros/autoridades pueden donar).
    Crea una Donacion en estado PENDIENTE y retorna el public_key
    para que el frontend inicialice el Payment Brick.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [DonacionRateThrottle]

    def post(self, request):
        serializer = IniciarDonacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        nombre_default = ''
        if hasattr(request.user, 'nombre_completo'):
            nombre_default = request.user.nombre_completo or ''
        if not nombre_default:
            nombre_default = getattr(request.user, 'username', '')

        donacion = Donacion.objects.create(
            usuario=request.user,
            nombre_donante=data.get('nombre_donante', '') or nombre_default,
            email_donante=data.get('email_donante', '') or request.user.email,
            documento_donante=data.get('documento_donante', '') or getattr(request.user, 'documento_identidad', '') or '',
            monto=data['monto'],
            mensaje=data.get('mensaje', ''),
            anonima=data.get('anonima', False),
            destinatario=data.get('destinatario', 'COMUNIDAD'),
            ip_origen=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            estado='PENDIENTE',
        )

        log_audit_event(
            usuario=request.user,
            accion='DONACION_CREADA',
            objeto_id=donacion.id,
            modelo_afectado='Donacion',
            descripcion=f'Donacion de S/ {donacion.monto} {"(anonima)" if donacion.anonima else f"por {donacion.email_display}"}',
            ip_address=get_client_ip(request),
            metadata={
                'monto': str(donacion.monto),
                'destinatario': donacion.destinatario,
                'anonima': donacion.anonima,
            },
        )

        return Response({
            'donation_id': donacion.id,
            'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
            'monto': str(donacion.monto),
            'moneda': donacion.moneda,
            'env': settings.MERCADO_PAGO_ENV,
            'status': 'ready_for_brick',
        }, status=status.HTTP_201_CREATED)


class ProcesarPagoView(APIView):
    """
    POST /api/v1/donaciones/procesar/

    Llamado por el Payment Brick (onSubmit) con el token opaco y los datos
    del payer. Crea el pago en MP y actualiza el estado de la donacion.
    Idempotente: si la donacion ya fue procesada, retorna el estado actual.
    Requiere autenticacion: solo el usuario que inicio la donacion puede procesarla.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [DonacionRateThrottle]

    def post(self, request):
        serializer = ProcesarPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        donation_id = data['donation_id']
        try:
            donacion = Donacion.objects.get(id=donation_id)
        except Donacion.DoesNotExist:
            return Response(
                {'detail': f'No existe la donacion #{donation_id}.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if donacion.usuario_id and donacion.usuario_id != request.user.id:
            return Response(
                {'detail': 'No tienes permiso para procesar esta donacion.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if donacion.estado in ('APROBADO', 'EN_PROCESO', 'REEMBOLSADO', 'CANCELADO'):
            return Response(
                {'status': donacion.estado.lower(), 'detail': f'La donacion ya esta en estado {donacion.estado}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if donacion.estado == 'RECHAZADO':
            return Response(
                {'status': 'rejected', 'detail': 'Esta donacion ya fue rechazada. Inicia una nueva.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payer_email, payer_identification = _obtener_datos_payer(data.get('payer', {}), donacion)

        donacion.estado = 'EN_PROCESO'
        donacion.save(update_fields=['estado', 'updated_at'])

        try:
            payment = MercadoPagoService.crear_pago(
                transaction_amount=donacion.monto,
                token=data['token'],
                payment_method_id=data.get('payment_method_id') or None,
                issuer_id=data.get('issuer_id') or None,
                installments=int(data.get('installments') or 1),
                payer_email=payer_email or None,
                payer_identification=payer_identification,
                external_reference=str(donacion.id),
                notification_url=settings.MERCADO_PAGO_WEBHOOK_URL or None,
                description=f"Donacion #{donacion.id} a Comunidad Zapotal",
            )
        except MercadoPagoError as e:
            donacion.estado = 'RECHAZADO'
            donacion.estado_detalle = str(e)[:500]
            donacion.save()
            log_audit_event(
                accion='DONACION_RECHAZADA',
                objeto_id=donacion.id,
                modelo_afectado='Donacion',
                descripcion=f'Mercado Pago rechazo la donacion: {e}',
                ip_address=get_client_ip(request),
            )
            return Response(
                {'status': 'rejected', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mp_status = payment.get('status', 'in_process')
        nuevo_estado = MercadoPagoService.mapear_estado_mp(mp_status)

        with transaction.atomic():
            donacion.estado = nuevo_estado
            donacion.mp_payment_id = payment.get('id')
            donacion.mp_status = mp_status
            donacion.mp_status_detail = payment.get('status_detail', '')
            donacion.mp_payment_method = payment.get('payment_method_id', '')
            donacion.mp_payment_type = payment.get('payment_type_id', '')
            donacion.mp_installments = payment.get('installments')
            donacion.mp_raw_response = payment
            if nuevo_estado == 'APROBADO':
                donacion.aprobado_at = timezone.now()
            donacion.save()

        log_audit_event(
            accion=f'DONACION_{nuevo_estado}',
            objeto_id=donacion.id,
            modelo_afectado='Donacion',
            descripcion=f'Donacion {donacion.id}: {nuevo_estado} (mp_id={donacion.mp_payment_id}, method={donacion.mp_payment_method})',
            ip_address=get_client_ip(request),
            metadata={
                'mp_payment_id': donacion.mp_payment_id,
                'mp_status': donacion.mp_status,
                'estado': donacion.estado,
            },
        )

        if donacion.estado == 'APROBADO':
            try:
                _enviar_email_confirmacion(donacion)
            except Exception as e:
                logger.exception("Fallo email de confirmacion para donacion %s: %s", donacion.id, e)

        return Response({
            'donation_id': donacion.id,
            'status': donacion.estado.lower(),
            'mp_payment_id': donacion.mp_payment_id,
            'status_detail': donacion.mp_status_detail,
            'mp_payment_method': donacion.mp_payment_method,
        })


class DonacionesWebhookView(APIView):
    """
    POST /api/v1/donaciones/webhook/

    Recibe notificaciones IPN de Mercado Pago. Idempotente.
    Seguridad: verifica firma HMAC-SHA256 (x-signature) y origen IP.
    """
    permission_classes = [AllowAny]
    throttle_classes = [WebhookRateThrottle]

    def post(self, request):
        x_signature = request.META.get('HTTP_X_SIGNATURE', '')
        x_request_id = request.META.get('HTTP_X_REQUEST_ID', '')
        remote_ip = request.META.get('REMOTE_ADDR', '')

        logger.info(
            "Webhook MP: x-request-id=%s remote_ip=%s",
            x_request_id, remote_ip,
        )

        secret = settings.MERCADO_PAGO_WEBHOOK_SECRET
        if secret and not MercadoPagoService.verificar_firma_webhook(
            request.body, x_signature, secret,
        ):
            logger.warning(
                "Webhook MP: firma invalida ip=%s x-request-id=%s",
                remote_ip, x_request_id,
            )
            return Response({'detail': 'Firma invalida.'}, status=403)

        if not MercadoPagoService.ip_permitida(remote_ip):
            logger.warning(
                "Webhook MP: IP no permitida %s x-request-id=%s",
                remote_ip, x_request_id,
            )
            return Response({'detail': 'IP no permitida.'}, status=403)
        mp_type = request.data.get('type')
        mp_id = request.data.get('data', {}).get('id')

        if mp_type != 'payment' or not mp_id:
            logger.info("Webhook MP ignorado: type=%s id=%s", mp_type, mp_id)
            return Response({'detail': 'Tipo no procesado.'}, status=200)

        try:
            mp_payment_id = int(mp_id)
        except (ValueError, TypeError):
            return Response({'detail': 'ID invalido.'}, status=200)

        try:
            donacion = Donacion.objects.get(mp_payment_id=mp_payment_id)
        except Donacion.DoesNotExist:
            logger.warning("Webhook MP: donacion no encontrada para mp_payment_id=%s", mp_payment_id)
            return Response({'detail': 'Donacion no encontrada en BD.'}, status=200)

        notif_id = x_request_id or f"mp-{mp_payment_id}-{mp_id}"
        if donacion.mp_notification_id == notif_id:
            logger.info("Webhook MP: notificacion duplicada %s para donacion %s", notif_id, donacion.id)
            return Response({'status': 'ok', 'duplicated': True})

        try:
            payment = MercadoPagoService.obtener_pago(mp_payment_id)
        except MercadoPagoError as e:
            logger.exception("Webhook MP: error al obtener pago %s: %s", mp_payment_id, e)
            return Response({'detail': str(e)}, status=200)

        mp_status = payment.get('status', donacion.mp_status)
        nuevo_estado = MercadoPagoService.mapear_estado_mp(mp_status)

        cambios = donacion.estado != nuevo_estado or donacion.mp_status_detail != payment.get('status_detail', '')
        if cambios or not donacion.mp_notification_id:
            estado_anterior = donacion.estado
            donacion.estado = nuevo_estado
            donacion.mp_status = mp_status
            donacion.mp_status_detail = payment.get('status_detail', '')
            donacion.mp_payment_method = payment.get('payment_method_id', donacion.mp_payment_method)
            donacion.mp_payment_type = payment.get('payment_type_id', donacion.mp_payment_type)
            donacion.mp_installments = payment.get('installments', donacion.mp_installments)
            donacion.mp_raw_response = payment
            donacion.mp_notification_id = notif_id
            if nuevo_estado == 'APROBADO' and not donacion.aprobado_at:
                donacion.aprobado_at = timezone.now()
            donacion.save()

            log_audit_event(
                accion='WEBHOOK_DONACION',
                objeto_id=donacion.id,
                modelo_afectado='Donacion',
                descripcion=f'Webhook MP: donacion {donacion.id} {estado_anterior} -> {nuevo_estado} (mp_status={mp_status})',
                metadata={'mp_status': mp_status, 'estado': nuevo_estado},
            )
            if nuevo_estado == 'APROBADO' and estado_anterior != 'APROBADO':
                try:
                    _enviar_email_confirmacion(donacion)
                except Exception as e:
                    logger.exception("Fallo email webhook para donacion %s: %s", donacion.id, e)
        else:
            logger.debug("Webhook MP sin cambios para donacion %s", donacion.id)

        return Response({'status': 'ok'})


class MisDonacionesView(APIView):
    """
    GET /api/v1/donaciones/mis-donaciones/

    Lista las donaciones del usuario autenticado (paginado).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        donaciones = Donacion.objects.filter(usuario=request.user)
        estado = request.query_params.get('estado')
        if estado:
            donaciones = donaciones.filter(estado=estado)
        donaciones = donaciones.order_by('-created_at')[:100]

        serializer = DonacionSerializer(donaciones, many=True)
        return Response({
            'count': donaciones.count() if not estado else donaciones.count(),
            'results': serializer.data,
        })


class DonacionDetailView(APIView):
    """
    GET /api/v1/donaciones/<id>/

    Detalle de una donacion. Publico para comprobantes, pero solo el
    dueno o un admin pueden ver datos completos (DNI, IP, etc).
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        donacion = get_object_or_404(Donacion, pk=pk)

        es_admin = request.user.is_authenticated and (
            request.user.is_staff
            or getattr(request.user, 'tipo_usuario', None) == 'ADMIN'
        )
        es_dueno = (
            request.user.is_authenticated
            and donacion.usuario_id == request.user.id
        )
        puede_ver_datos_completos = es_admin or es_dueno

        if donacion.anonima and not puede_ver_datos_completos:
            serializer = DonacionPublicaSerializer(donacion)
        else:
            serializer = DonacionSerializer(donacion)
        return Response(serializer.data)


class EstadisticasDonacionesView(APIView):
    """
    GET /api/v1/donaciones/estadisticas/

    Stats publicas para mostrar en la landing de donaciones.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db.models import Sum, Count, Avg
        qs = Donacion.objects.filter(estado='APROBADO')

        total_recaudado = qs.aggregate(s=Sum('monto'))['s'] or Decimal('0.00')
        cantidad = qs.count()
        donantes_unicos = qs.exclude(usuario__isnull=True).values('usuario').distinct().count() + \
                          qs.filter(usuario__isnull=True).exclude(email_donante='').values('email_donante').distinct().count()
        promedio = qs.aggregate(p=Avg('monto'))['p'] or Decimal('0.00')
        ultima = qs.order_by('-created_at').values_list('created_at', flat=True).first()

        por_destinatario = dict(
            qs.values('destinatario').annotate(total=Sum('monto')).values_list('destinatario', 'total')
        )

        data = {
            'total_recaudado': str(total_recaudado),
            'cantidad_donaciones': cantidad,
            'donantes_unicos': donantes_unicos,
            'promedio_donacion': str(promedio),
            'ultima_donacion': ultima,
            'por_destinatario': {k: str(v) for k, v in por_destinatario.items()},
        }
        serializer = EstadisticasDonacionesSerializer(data)
        return Response(serializer.data)


class AdminDonacionesListView(APIView):
    """GET /api/v1/donaciones/admin/lista/ (admin)."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Donacion.objects.all()
        estado = request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        destinatario = request.query_params.get('destinatario')
        if destinatario:
            qs = qs.filter(destinatario=destinatario)
        desde = request.query_params.get('desde')
        if desde:
            qs = qs.filter(created_at__gte=desde)
        hasta = request.query_params.get('hasta')
        if hasta:
            qs = qs.filter(created_at__lte=hasta)
        search = (request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(nombre_donante__icontains=search)
                | Q(email_donante__icontains=search)
                | Q(documento_donante__icontains=search)
                | Q(mp_payment_id__icontains=search)
                | Q(usuario__email__icontains=search)
                | Q(mensaje__icontains=search)
            )

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = min(200, max(1, int(request.query_params.get('page_size', 20))))
        except (TypeError, ValueError):
            page_size = 20

        total = qs.count()
        offset = (page - 1) * page_size
        items = qs.order_by('-created_at')[offset:offset + page_size]
        serializer = DonacionSerializer(items, many=True)
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if total else 0,
            'results': serializer.data,
        })


class AdminReembolsarDonacionView(APIView):
    """POST /api/v1/admin/donaciones/<id>/reembolsar/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        donacion = get_object_or_404(Donacion, pk=pk)
        if donacion.estado != 'APROBADO':
            return Response(
                {'detail': f'Solo se pueden reembolsar donaciones APROBADAS. Estado actual: {donacion.estado}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not donacion.mp_payment_id:
            return Response(
                {'detail': 'Esta donacion no tiene mp_payment_id, no se puede reembolsar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refund = MercadoPagoService.reembolsar(donacion.mp_payment_id)
        except MercadoPagoError as e:
            return Response(
                {'detail': f'Error al reembolsar en MP: {e}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        donacion.estado = 'REEMBOLSADO'
        donacion.reembolsado_at = timezone.now()
        donacion.estado_detalle = f"Reembolso MP id={refund.get('id', '?')}"
        donacion.save()

        log_audit_event(
            usuario=request.user,
            accion='DONACION_REEMBOLSADA',
            objeto_id=donacion.id,
            modelo_afectado='Donacion',
            descripcion=f'Reembolso de S/ {donacion.monto} (mp_refund_id={refund.get("id")})',
            ip_address=get_client_ip(request),
        )
        return Response({
            'status': 'ok',
            'donation_id': donacion.id,
            'mp_refund_id': refund.get('id'),
            'monto_reembolsado': refund.get('amount'),
        })


class AdminCancelarDonacionView(APIView):
    """POST /api/v1/admin/donaciones/<id>/cancelar/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        donacion = get_object_or_404(Donacion, pk=pk)
        if donacion.estado != 'PENDIENTE':
            return Response(
                {'detail': f'Solo se pueden cancelar donaciones PENDIENTES. Estado actual: {donacion.estado}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        donacion.estado = 'CANCELADO'
        donacion.estado_detalle = f'Cancelada por admin {request.user.email}'
        donacion.save()
        log_audit_event(
            usuario=request.user,
            accion='DONACION_CANCELADA',
            objeto_id=donacion.id,
            modelo_afectado='Donacion',
            descripcion=f'Admin {request.user.email} cancelo la donacion',
            ip_address=get_client_ip(request),
        )
        return Response({'status': 'ok', 'donation_id': donacion.id})


def _enviar_email_confirmacion(donacion):
    """Envia email de confirmacion al donante tras pago aprobado."""
    email_dest = donacion.email_display
    if not email_dest:
        logger.warning("Donacion %s aprobada sin email, no se envia confirmacion.", donacion.id)
        return
    asunto = f"Gracias por tu donacion de S/ {donacion.monto} a Comunidad Zapotal"
    cuerpo_texto = (
        f"Hola {donacion.nombre_display},\n\n"
        f"Gracias por tu donacion de S/ {donacion.monto} a la Comunidad Campesina Niño Dios de Zapotal.\n\n"
        f"Tu pago fue aprobado por Mercado Pago.\n"
        f"ID de transaccion: {donacion.mp_payment_id}\n"
        f"Fecha: {donacion.aprobado_at.strftime('%d/%m/%Y %H:%M') if donacion.aprobado_at else 'ahora'}\n"
        f"Destino: {donacion.get_destinatario_display()}\n"
    )
    if donacion.mensaje:
        cuerpo_texto += f"\nTu mensaje: \"{donacion.mensaje}\"\n"
    cuerpo_texto += (
        "\nTu aporte se traduce en obras concretas para nuestra comunidad.\n\n"
        "Comunidad Campesina Niño Dios de Zapotal\n"
    )
    try:
        EmailService.enviar_notificacion(
            destinatario=email_dest,
            asunto=asunto,
            cuerpo=cuerpo_texto,
        )
    except Exception as e:
        logger.exception("Error enviando email de confirmacion: %s", e)
        raise
