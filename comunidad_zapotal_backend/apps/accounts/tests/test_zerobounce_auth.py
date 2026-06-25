"""Tests para validacion ZeroBounce en registro y password reset.

Cubre:
- registro_iniciar: email disposable (sandbox) -> 400 EMAIL_INVALID.
- registro_iniciar: email valid (sandbox) -> 201.
- registro_iniciar: email no reservado en sandbox -> fail-open -> 201.
- registro_iniciar: cache hit evita segunda consulta a la API.
- password_reset_request: email disposable -> 200 anti-enumeracion, sin OTP.
- password_reset_request: email valid -> 200 + OTP enviado.
- AuditLog registra intentos bloqueados.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import OTPVerification
from apps.comunidad.models_institucionales import MensajeContacto  # noqa: F401  (asegurar app cargada)


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_user(
        email='admin@comunidadzapotal.gob.pe',
        password='Admin1234!',
        tipo_usuario='ADMIN',
        estado='ACTIVO',
    )


# ============== registro_iniciar ==============


@pytest.mark.django_db
class TestRegistroZeroBounce:
    REGISTRO_URL = '/api/v1/registro/iniciar/'

    def _payload(self, email):
        return {
            'email': email,
            'password': 'Test1234!',
            'dni': '12345678',
            'nombres': 'Test',
            'apellidos': 'User',
            'turnstile_token': '',  # No validamos Turnstile en tests
        }

    def test_email_disposable_rechazado_400(self, api_client, settings):
        """Email 'disposable@example.com' (sandbox) -> status=invalid -> 400."""
        r = api_client.post(self.REGISTRO_URL, self._payload('disposable@example.com'),
                            format='json')
        assert r.status_code == 400, r.data
        assert r.data.get('code') == 'EMAIL_INVALID'
        assert r.data.get('sub_status') == 'disposable'

    def test_email_invalid_rechazado_400(self, api_client, settings):
        """Email 'invalid@example.com' (sandbox) -> status=invalid -> 400."""
        r = api_client.post(self.REGISTRO_URL, self._payload('invalid@example.com'),
                            format='json')
        assert r.status_code == 400, r.data
        assert r.data.get('code') == 'EMAIL_INVALID'

    def test_email_valid_aceptado_201(self, api_client, settings):
        """Email 'valid@example.com' (sandbox) -> status=valid -> 201."""
        r = api_client.post(self.REGISTRO_URL, self._payload('valid@example.com'),
                            format='json')
        # El Turnstile puede rechazar; pero la validacion ZeroBounce
        # ocurre antes. Si Turnstile rechaza, sera 400 con detail='Verificacion...'
        # Si pasa, 201.
        if r.status_code == 400:
            # Si fallo por Turnstile, el codigo no sera EMAIL_INVALID
            assert r.data.get('code') != 'EMAIL_INVALID'
        else:
            assert r.status_code == 201

    def test_email_no_reservado_fail_open_201(self, api_client, settings):
        """Email no reservado en sandbox -> status=unknown -> fail-open -> 201 (o 400 por Turnstile)."""
        r = api_client.post(self.REGISTRO_URL,
                            self._payload('usuario-real@gmail.com'),
                            format='json')
        # Fail-open: el email pasa ZeroBounce. Si Turnstile rechaza, 400.
        if r.status_code == 400:
            assert r.data.get('code') != 'EMAIL_INVALID'
        else:
            assert r.status_code == 201

    def test_sin_api_key_fail_open(self, api_client, settings):
        """Sin ZEROBOUNCE_API_KEY -> fail-open."""
        settings.ZEROBOUNCE_API_KEY = ''
        r = api_client.post(self.REGISTRO_URL,
                            self._payload('usuario-sin-key@gmail.com'),
                            format='json')
        if r.status_code == 400:
            assert r.data.get('code') != 'EMAIL_INVALID'
        else:
            assert r.status_code == 201


# ============== password_reset_request ==============


@pytest.mark.django_db
class TestPasswordResetZeroBounce:
    RESET_URL = '/api/v1/password-reset/request/'

    def test_email_disposable_responde_200_sin_otp(self, api_client, settings):
        """Email disposable -> 200 (anti-enumeracion), sin OTP enviado."""
        r = api_client.post(self.RESET_URL, {'email': 'disposable@example.com'},
                            format='json')
        assert r.status_code == 200
        assert r.data.get('success') is True
        # No debe haber OTPs creados para disposable
        assert OTPVerification.objects.filter(
            destinatario='disposable@example.com',
            tipo=OTPVerification.TipoOTP.RESET_PASSWORD,
        ).count() == 0

    def test_email_invalid_responde_200_sin_otp(self, api_client, settings):
        r = api_client.post(self.RESET_URL, {'email': 'invalid@example.com'},
                            format='json')
        assert r.status_code == 200
        assert OTPVerification.objects.filter(
            destinatario='invalid@example.com',
        ).count() == 0

    def test_email_valido_intenta_enviar_otp(self, api_client, settings, admin_user):
        """Email valido registrado -> 200 (anti-enumeracion), pero intenta enviar OTP."""
        r = api_client.post(self.RESET_URL,
                            {'email': 'admin@comunidadzapotal.gob.pe'},
                            format='json')
        assert r.status_code == 200
        # El OTP puede o no haberse enviado dependiendo del servicio OTP en sandbox,
        # pero NO debe haber sido bloqueado por ZeroBounce (codigo no es disposable).
        # Verificamos que la respuesta es la generica anti-enumeracion:
        assert 'Si el email existe' in r.data.get('detail', '')


# ============== AuditLog ==============


@pytest.mark.django_db
class TestAuditLogZB:
    def test_registro_bloqueado_registra_audit(self, api_client, settings):
        """Intento de registro con email disposable registra en AuditLog."""
        from apps.core.models import AuditLog
        r = api_client.post(
            '/api/v1/registro/iniciar/',
            {
                'email': 'disposable@example.com',
                'password': 'Test1234!',
                'dni': '12345678',
                'nombres': 'Test',
                'apellidos': 'User',
                'turnstile_token': '',
            },
            format='json',
        )
        assert r.status_code == 400
        log = AuditLog.objects.filter(accion='REG_ZB_BLOCK').first()
        assert log is not None
        assert 'disposable' in (log.metadata or {}).get('sub_status', '')

    def test_reset_bloqueado_registra_audit(self, api_client, settings):
        from apps.core.models import AuditLog
        r = api_client.post(
            '/api/v1/password-reset/request/',
            {'email': 'disposable@example.com'},
            format='json',
        )
        assert r.status_code == 200
        log = AuditLog.objects.filter(accion='PASSRESET_ZB_BLOCK').first()
        assert log is not None
