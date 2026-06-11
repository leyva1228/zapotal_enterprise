"""
Health check endpoints para monitoreo de la aplicación.
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os


def health_check(request):
    """
    Health check básico.

    Returns:
        200: Servicio saludable
        503: Servicio degradado
    """
    health = {
        'status': 'ok',
        'database': 'unknown',
        'debug': settings.DEBUG,
    }
    status_code = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        health['database'] = 'healthy'
    except Exception as e:
        health['status'] = 'degraded'
        health['database'] = 'unhealthy'
        health['error'] = str(e) if settings.DEBUG else 'database connection failed'
        status_code = 503

    return JsonResponse(health, status=status_code)


def readiness_check(request):
    """Readiness check (la app está lista para recibir tráfico)."""
    return health_check(request)


def liveness_check(request):
    """Liveness check (la app está viva, no necesariamente lista)."""
    return JsonResponse({'status': 'alive'}, status=200)
