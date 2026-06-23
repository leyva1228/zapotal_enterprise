from rest_framework.throttling import ScopedRateThrottle


class DonacionRateThrottle(ScopedRateThrottle):
    """
    Rate limit para endpoints de donacion:
    - 5 requests/min por IP para evitar spam de donacion iniciada.
    - 10 requests/min por IP para webhook de MP (MP puede reintentar).
    """
    scope = 'donaciones'


class WebhookRateThrottle(ScopedRateThrottle):
    scope = 'donaciones_webhook'
