"""
Servicio wrapper sobre el SDK de Mercado Pago para la pasarela de pagos.

Por que este wrapper:
1. Centraliza la configuracion del SDK (singleton con access token).
2. Aisla la API de MP del codigo de vistas (testeable con mock).
3. Convierte errores de MP en excepciones Python claras.
"""
import logging
from decimal import Decimal
from typing import Optional

import mercadopago
from django.conf import settings


logger = logging.getLogger(__name__)


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
