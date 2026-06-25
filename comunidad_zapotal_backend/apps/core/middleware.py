"""
Middleware de auditoria: registra POST/PUT/PATCH/DELETE autenticados exitosos.
Middleware CSP: Content-Security-Policy para Mercado Pago Brick SDK.
"""
import logging
from django.conf import settings
from apps.core.utils import log_audit_event

logger = logging.getLogger(__name__)

WHITELIST_PREFIXES = (
    '/api/schema/',
    '/api/docs/',
    '/health/',
    '/static/',
    '/media/',
    '/backend/',
    '/favicon.ico',
)

ACTION_MAP = {
    'POST': 'CREATE',
    'PUT': 'UPDATE',
    'PATCH': 'UPDATE',
    'DELETE': 'DELETE',
}


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if (
                request.method in ACTION_MAP
                and response.status_code < 400
                and not request.path.startswith(WHITELIST_PREFIXES)
                and getattr(request, 'user', None)
                and request.user.is_authenticated
            ):
                log_audit_event(
                    usuario=request.user,
                    accion=ACTION_MAP[request.method],
                    descripcion=f'{request.method} {request.path}',
                    request=request,
                )
        except Exception as exc:  # noqa: BLE001
            logger.exception('AuditMiddleware fallo: %s', exc)
        return response


class ContentSecurityPolicyMiddleware:
    """
    Agrega header Content-Security-Policy a todas las respuestas.

    Permite los dominios necesarios para Mercado Pago Brick SDK:
      - mpago.la (SDK JS, estilos)
      - www.mercadopago.com.pe (API)
      - sdk.mercadopago.pe (Brick SDK)
    Mantiene restricciones para XSS.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        csp = getattr(settings, 'CONTENT_SECURITY_POLICY', None)
        if csp:
            response['Content-Security-Policy'] = csp
        return response
