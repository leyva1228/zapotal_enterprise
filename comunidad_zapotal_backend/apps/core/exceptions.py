"""
Custom DRF exception handler para estandarizar respuestas de error.

Formato de error consistente:
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Error de validación",
        "details": {...}
    }
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Handler de excepciones que estandariza todas las respuestas de error.
    """
    response = exception_handler(exc, context)

    if response is None:
        logger.exception('Unhandled exception in %s', context.get('view'))
        return Response(
            {
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Error interno del servidor.',
                }
            },
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    error_data = {
        'error': {
            'code': getattr(exc, 'default_code', 'ERROR').upper(),
            'message': _get_error_message(exc, response),
        }
    }

    if isinstance(response.data, dict) and 'detail' in response.data:
        error_data['error']['message'] = str(response.data['detail'])
    elif isinstance(response.data, dict):
        error_data['error']['details'] = response.data
    elif isinstance(response.data, list):
        error_data['error']['details'] = response.data

    if isinstance(exc, Exception):
        logger.warning(
            'API exception: %s | view=%s | status=%s',
            exc.__class__.__name__,
            context.get('view'),
            response.status_code,
        )

    response.data = error_data
    return response


def _get_error_message(exc, response):
    """Genera un mensaje legible para el error."""
    if hasattr(exc, 'detail'):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        if isinstance(detail, dict):
            return 'Error de validación.'
        if isinstance(detail, list):
            return str(detail[0]) if detail else 'Error.'
    return 'Ha ocurrido un error.'
