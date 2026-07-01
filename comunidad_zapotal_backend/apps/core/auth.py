"""Authentication classes for Zapotal Enterprise."""
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class OptionalJWTAuthentication(JWTAuthentication):
    """JWT auth that gracefully handles expired/missing tokens.

    Default JWTAuthentication raises AuthenticationFailed when a token
    is expired, invalid, or malformed — which causes DRF to return 401
    *before* any permission class (e.g. IsAdminOrReadOnly) can allow
    public GET access.

    This override catches the exception and returns None, allowing DRF
    to fall through to the next auth class or permission check.

    Use on endpoints that are publicly readable but also need to recognize
    admin users for write operations (e.g. paginas-legales, notificaciones).
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed as e:
            logger.debug('OptionalJWTAuthentication: %s', e)
            return None
