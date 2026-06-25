"""
Servicio wrapper sobre el SDK de Mercado Pago para la pasarela de pagos.

Por que este wrapper:
1. Centraliza la configuracion del SDK (singleton con access token).
2. Aisla la API de MP del codigo de vistas (testeable con mock).
3. Convierte errores de MP en excepciones Python claras.
4. Verificacion de firma de webhook (x-signature).
"""
import hashlib
import hmac
import json
import logging
from decimal import Decimal
from typing import Optional

import mercadopago
from django.conf import settings


logger = logging.getLogger(__name__)


# IPs publicas de Mercado Pago para notificaciones webhook.
# Fuente: https://www.mercadopago.com.pe/developer/es/docs/your-integrations/notifications/ipn
# MPs pueden cambiar estas IPs. Revisar periodicamente.
MERCADO_PAGO_IPS = frozenset({
    '216.33.196.4',
    '216.33.196.25',
    '216.33.196.37',
    '216.33.196.54',
    '216.33.196.58',
    '216.33.196.62',
    '216.33.196.64',
    '23.21.124.106',
    '50.16.225.132',
    '54.94.104.183',
    '54.207.212.174',
    '54.232.205.211',
    '54.232.207.61',
    '54.232.208.89',
    '54.233.79.186',
    '54.233.80.46',
    '54.233.85.62',
    '54.233.89.164',
    '54.233.91.246',
    '54.233.94.10',
    '54.233.94.226',
    '54.233.95.186',
    '54.233.95.55',
    '54.233.95.82',
    '54.233.96.131',
    '54.233.97.45',
    '54.233.98.25',
    '54.233.99.178',
    '54.233.99.50',
    '54.233.99.69',
    '54.233.99.82',
    '54.233.100.225',
    '54.233.100.42',
    '54.233.100.57',
    '54.233.103.112',
    '54.233.103.166',
    '54.233.103.199',
    '54.233.103.20',
    '54.233.103.90',
    '54.233.104.121',
    '54.233.105.179',
    '54.233.105.36',
    '54.237.248.62',
    '54.237.253.239',
    '54.237.254.43',
})


class MercadoPagoError(Exception):
    """Error al comunicarse con Mercado Pago o respuesta inesperada."""
    def __init__(self, message, mp_status=None, mp_response=None):
        super().__init__(message)
        self.mp_status = mp_status
        self.mp_response = mp_response


class MercadoPagoService:
    """
    Wrapper del SDK de Mercado Pago para operaciones de pago.

    PCI DSS: Este servicio NUNCA recibe, almacena ni transmite datos de tarjeta.
    Solo recibe el token opaco generado por el Payment Brick en el frontend.
    """

    _sdk = None

    @classmethod
    def get_sdk(cls):
        """Singleton del SDK de MP configurado con el access token."""
        if cls._sdk is None:
            access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
            if not access_token:
                raise MercadoPagoError(
                    "MERCADO_PAGO_ACCESS_TOKEN no esta configurado en .env. "
                    "Ver plan-donaciones-mercadopago.md seccion 4.3."
                )
            cls._sdk = mercadopago.SDK(access_token)
        return cls._sdk

    @classmethod
    def reset_sdk(cls):
        """Resetea el singleton (util para tests o cambio de credenciales)."""
        cls._sdk = None

    @classmethod
    def crear_pago(
        cls,
        *,
        transaction_amount: Decimal,
        token: str,
        description: str,
        payment_method_id: Optional[str] = None,
        issuer_id: Optional[str] = None,
        installments: int = 1,
        payer_email: Optional[str] = None,
        payer_identification: Optional[dict] = None,
        external_reference: Optional[str] = None,
        notification_url: Optional[str] = None,
    ) -> dict:
        """
        Crea un pago en Mercado Pago.

        Args:
            transaction_amount: Monto en PEN (puede ser Decimal o float).
            token: Token opaco del Payment Brick (NO datos de tarjeta).
            description: Descripcion del pago.
            payment_method_id: visa, mastercard, yape, etc. (opcional, MP lo infiere).
            issuer_id: ID del banco emisor (opcional).
            installments: Numero de cuotas (default 1 = sin cuotas).
            payer_email: Email del pagador.
            payer_identification: dict con {type, number} (DNI/RUC).
            external_reference: ID interno de la donacion para reconciliacion.
            notification_url: URL del webhook de MP.

        Returns:
            dict con el payment object de MP (id, status, status_detail, etc).

        Raises:
            MercadoPagoError si la API rechaza la peticion.
        """
        sdk = cls.get_sdk()

        amount = float(transaction_amount)
        if amount <= 0:
            raise MercadoPagoError(f"Monto invalido: {amount}")

        payment_data = {
            "transaction_amount": amount,
            "token": token,
            "description": description[:255],
            "installments": installments,
        }

        if payment_method_id:
            payment_data["payment_method_id"] = payment_method_id
        if issuer_id:
            payment_data["issuer_id"] = issuer_id
        if external_reference:
            payment_data["external_reference"] = str(external_reference)
        if notification_url:
            payment_data["notification_url"] = notification_url

        payer = {}
        if payer_email:
            payer["email"] = payer_email
        if payer_identification and payer_identification.get("number"):
            payer["identification"] = {
                "type": payer_identification.get("type", "DNI"),
                "number": str(payer_identification["number"]),
            }
        if payer:
            payment_data["payer"] = payer

        logger.info(
            "MercadoPago crear_pago: amount=%s, external_ref=%s, has_payer=%s",
            amount, external_reference, bool(payer),
        )

        try:
            result = sdk.payment().create(payment_data)
        except Exception as e:
            logger.exception("Excepcion al llamar MP payment().create()")
            raise MercadoPagoError(f"Error de conexion con Mercado Pago: {e}")

        mp_status_code = result.get("status")
        if mp_status_code not in (200, 201):
            logger.error("MP rechazo crear_pago: status=%s response=%s", mp_status_code, result)
            raise MercadoPagoError(
                f"Mercado Pago rechazo el pago (HTTP {mp_status_code})",
                mp_status=mp_status_code,
                mp_response=result,
            )

        payment = result.get("response", {})
        if not payment.get("id"):
            raise MercadoPagoError(
                f"MP no devolvio payment id: {result}",
                mp_status=mp_status_code,
                mp_response=result,
            )

        logger.info("MP pago creado: id=%s status=%s", payment.get("id"), payment.get("status"))
        return payment

    @classmethod
    def obtener_pago(cls, payment_id: int) -> dict:
        """Consulta un pago existente en MP (util para webhook y reconciliacion)."""
        sdk = cls.get_sdk()
        try:
            result = sdk.payment().get(payment_id)
        except Exception as e:
            raise MercadoPagoError(f"Error al obtener pago {payment_id} de MP: {e}")

        if result.get("status") != 200:
            raise MercadoPagoError(
                f"No se pudo obtener pago {payment_id}: {result}",
                mp_status=result.get("status"),
                mp_response=result,
            )

        return result.get("response", {})

    @classmethod
    def reembolsar(cls, payment_id: int, amount: Optional[Decimal] = None) -> dict:
        """
        Reembolsa total o parcialmente un pago aprobado.

        Args:
            payment_id: ID del pago en MP.
            amount: Monto a reembolsar (None = reembolso total).

        Returns:
            dict con el refund object de MP.
        """
        sdk = cls.get_sdk()
        refund_data = {}
        if amount is not None:
            refund_data["amount"] = float(amount)

        try:
            result = sdk.refund().create(payment_id, refund_data if refund_data else None)
        except Exception as e:
            raise MercadoPagoError(f"Error al reembolsar pago {payment_id}: {e}")

        if result.get("status") not in (200, 201):
            raise MercadoPagoError(
                f"No se pudo reembolsar {payment_id}: {result}",
                mp_status=result.get("status"),
                mp_response=result,
            )

        return result.get("response", {})

    @staticmethod
    def verificar_firma_webhook(request_body: bytes, x_signature_header: str, secret: str) -> bool:
        """
        Verifica la firma HMAC-SHA256 de una notificacion webhook de MP.

        El header x-signature tiene formato:
          ts=<timestamp>,v1=<hash>

        Pasos:
          1. Extraer ts y v1 del header.
          2. Construir el mensaje como: "id:<data.id>;ts:<timestamp>;"
          3. Calcular HMAC-SHA256(secret, msg) y comparar con v1.

        Returns:
            True si la firma es valida, False en caso contrario.
        """
        if not x_signature_header or not secret:
            return False

        try:
            partes = dict(p.split('=', 1) for p in x_signature_header.split(','))
        except (ValueError, AttributeError):
            return False

        ts = partes.get('ts')
        v1 = partes.get('v1')
        if not ts or not v1:
            return False

        try:
            data_id = json.loads(request_body).get('data', {}).get('id', '')
        except (json.JSONDecodeError, AttributeError):
            return False

        msg = f"id:{data_id};ts:{ts};".encode('utf-8')
        expected = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()

        return hmac.compare_digest(expected, v1)

    @staticmethod
    def ip_permitida(ip: str) -> bool:
        """
        Valida si una IP esta en la lista de IPs conocidas de Mercado Pago.

        En DEBUG=True permite 127.0.0.1 y ::1 para desarrollo local.
        En produccion se puede override via settings.MERCADO_PAGO_WEBHOOK_ALLOWED_IPS.
        """
        if not ip:
            return False

        if settings.DEBUG and ip in ('127.0.0.1', '::1'):
            return True

        allowed_ips = getattr(settings, 'MERCADO_PAGO_WEBHOOK_ALLOWED_IPS', None)
        if allowed_ips is not None:
            return ip in allowed_ips

        return ip in MERCADO_PAGO_IPS

    @staticmethod
    def mapear_estado_mp(mp_status: str) -> str:
        """
        Mapea el status de MP a nuestro enum interno de Donacion.
        """
        mapping = {
            'approved':  'APROBADO',
            'in_process': 'EN_PROCESO',
            'pending':   'EN_PROCESO',
            'rejected':  'RECHAZADO',
            'cancelled': 'CANCELADO',
            'refunded':  'REEMBOLSADO',
            'charged_back': 'REEMBOLSADO',
        }
        return mapping.get(mp_status, 'EN_PROCESO')
