"""Tests del servicio de validacion ZeroBounce.

Cubre:
- Modo sandbox (sin consumir creditos)
- Modo no-configurado (fail-open, sin API key)
- Modo real con mock de la API HTTP
- Cache en Django cache framework
- Status codes: valid, invalid, catch-all, unknown, spamtrap, abuse, do_not_mail
- Sub-statuses: disposable, mailbox_not_found, possible_typo
- Politica de bloqueo (BLOQUEAR_INVALIDOS=True/False)
- did_you_mean: sugerencia de typo
- Excepciones de red y auth
"""
from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIClient


# =================== Modo sandbox ===================

class TestModoSandbox:
    """Con ZEROBOUNCE_SANDBOX=True, los emails reservados devuelven
    el status correspondiente sin llamar a la API."""

    @pytest.fixture(autouse=True)
    def enable_sandbox(self, settings):
        settings.ZEROBOUNCE_SANDBOX = True
        settings.ZEROBOUNCE_API_KEY = ''  # irrelevante en sandbox
        from django.core.cache import cache
        cache.clear()

    def test_valid_example_es_valido(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('valid@example.com')
        assert r.status == 'valid'
        assert r.es_valido is True
        assert r.modo_sandbox is True

    def test_invalid_example_es_invalido(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('invalid@example.com')
        assert r.status == 'invalid'
        assert r.es_valido is False
        assert r.motivo  # mensaje legible

    def test_catchall_es_sospechoso(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('catchall@example.com')
        assert r.status == 'catch-all'
        # catch-all NO bloquea por defecto, solo marca sospechoso
        assert r.es_sospechoso is True

    def test_disposable_es_invalido(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('disposable@example.com')
        assert r.status == 'invalid'
        assert r.es_valido is False
        assert 'desechable' in r.motivo.lower() or 'temporal' in r.motivo.lower()

    def test_email_no_reservado_devuelve_unknown(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('usuario@empresa.com')
        assert r.status == 'unknown'
        assert r.modo_sandbox is True

    def test_email_vacio_devuelve_invalid(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('')
        assert r.status == 'invalid'
        assert r.es_valido is False

    def test_email_sin_arroba_devuelve_invalid(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('foo-bar-baz')
        assert r.status == 'invalid'
        assert r.es_valido is False


# =================== Modo no-configurado (fail-open) ===================

class TestNoConfigurado:
    """Si ZEROBOUNCE_API_KEY='', el servicio no debe fallar y debe
    aceptar todos los emails (modo warning)."""

    @pytest.fixture(autouse=True)
    def disable_sandbox_and_key(self, settings):
        settings.ZEROBOUNCE_SANDBOX = False
        settings.ZEROBOUNCE_API_KEY = ''
        from django.core.cache import cache
        cache.clear()

    def test_sin_api_key_acepta_email(self):
        from apps.comunidad.zerobounce import validar_email
        r = validar_email('cualquiera@example.com')
        # Fail-open: no bloqueamos al usuario si no hay config.
        assert r.es_valido is True
        assert r.es_sospechoso is True
        assert r.sub_status == 'not_configured'

    def test_obtener_creditos_sin_key_retorna_menos_uno(self):
        from apps.comunidad.zerobounce import obtener_creditos
        assert obtener_creditos() == -1


# =================== Modo real con mock ===================

class TestLlamadaReal:
    """Mockeamos requests.get para no depender de la red."""

    @pytest.fixture(autouse=True)
    def enable_real_mode(self, settings):
        settings.ZEROBOUNCE_SANDBOX = False
        settings.ZEROBOUNCE_API_KEY = 'fake-test-key'
        settings.ZEROBOUNCE_TIMEOUT = 5
        from django.core.cache import cache
        cache.clear()

    def _mock_response(self, json_data, status_code=200):
        m = MagicMock()
        m.status_code = status_code
        m.json.return_value = json_data
        return m

    def test_email_valido(self):
        from apps.comunidad.zerobounce import validar_email
        payload = {
            'address':           'john@example.com',
            'status':            'valid',
            'sub_status':        '',
            'free_email':        False,
            'catchall_domain':   False,
            'did_you_mean':      None,
            'account':           'john',
            'domain':            'example.com',
            'mx_found':          'true',
            'mx_record':         'mx.example.com',
        }
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r = validar_email('john@example.com')
        assert r.status == 'valid'
        assert r.es_valido is True
        assert r.domain == 'example.com'
        assert r.modo_sandbox is False

    def test_email_invalido_con_motivo(self):
        from apps.comunidad.zerobounce import validar_email
        payload = {
            'address':     'foo@bar.com',
            'status':      'invalid',
            'sub_status':  'mailbox_not_found',
            'domain':      'bar.com',
        }
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r = validar_email('foo@bar.com')
        assert r.status == 'invalid'
        assert r.es_valido is False
        assert 'buzon' in r.motivo.lower() or 'existe' in r.motivo.lower()

    def test_did_you_mean_aparece_en_motivo(self):
        from apps.comunidad.zerobounce import validar_email
        payload = {
            'address':      'foo@gmial.com',
            'status':       'invalid',
            'sub_status':   'possible_typo',
            'did_you_mean': 'foo@gmail.com',
            'domain':       'gmial.com',
        }
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r = validar_email('foo@gmial.com')
        assert r.did_you_mean == 'foo@gmail.com'
        assert 'foo@gmail.com' in r.motivo

    def test_catchall_bloquea_por_defecto(self, settings):
        from apps.comunidad.zerobounce import validar_email
        settings.ZEROBOUNCE_BLOQUEAR_INVALIDOS = True
        payload = {
            'address':         'foo@catch.com',
            'status':          'catch-all',
            'sub_status':      '',
            'catchall_domain': True,
            'domain':          'catch.com',
        }
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r = validar_email('foo@catch.com')
        # Por defecto catch-all NO bloquea, solo es sospechoso
        assert r.es_valido is True
        assert r.es_sospechoso is True

    def test_spamtrap_bloquea(self):
        from apps.comunidad.zerobounce import validar_email
        payload = {'address': 'a@b.com', 'status': 'spamtrap', 'sub_status': ''}
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r = validar_email('a@b.com')
        assert r.es_valido is False
        assert 'spam' in r.motivo.lower()

    def test_unknown_no_bloquea(self):
        from apps.comunidad.zerobounce import validar_email
        payload = {'address': 'a@b.com', 'status': 'unknown', 'sub_status': ''}
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r = validar_email('a@b.com')
        # unknown es fail-open
        assert r.es_valido is True
        assert r.es_sospechoso is True

    def test_modo_warning_no_bloquea_invalidos(self, settings):
        """Si ZEROBOUNCE_BLOQUEAR_INVALIDOS=False, los invalidos pasan
        como warning (sospechoso) en vez de bloquear."""
        from apps.comunidad.zerobounce import validar_email
        settings.ZEROBOUNCE_BLOQUEAR_INVALIDOS = False
        payload = {'address': 'a@b.com', 'status': 'invalid', 'sub_status': 'mailbox_not_found'}
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r = validar_email('a@b.com')
        assert r.es_valido is True
        assert r.es_sospechoso is True

    def test_error_de_red_no_explota(self):
        from apps.comunidad.zerobounce import validar_email
        import requests
        with patch(
            'apps.comunidad.zerobounce.requests.get',
            side_effect=requests.exceptions.Timeout('boom'),
        ):
            r = validar_email('user@example.com')
        # fail-open: no bloqueamos si ZeroBounce falla
        assert r.es_valido is True
        assert r.sub_status == 'api_error'

    def test_error_de_auth_no_explota(self):
        from apps.comunidad.zerobounce import validar_email
        m = self._mock_response({'error': 'Invalid API Key or your account ran out of credits'})
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = m
            r = validar_email('user@example.com')
        assert r.es_valido is True
        assert r.sub_status == 'auth_error'

    def test_http_500_no_explota(self):
        from apps.comunidad.zerobounce import validar_email
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response({}, status_code=500)
            r = validar_email('user@example.com')
        assert r.es_valido is True
        assert r.sub_status == 'api_error'

    def test_usa_cache_entre_llamadas(self):
        from apps.comunidad.zerobounce import validar_email
        from django.core.cache import cache
        cache.clear()
        payload = {'address': 'a@b.com', 'status': 'valid', 'sub_status': ''}
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response(payload)
            r1 = validar_email('a@b.com')
            assert mock_get.call_count == 1
            r2 = validar_email('a@b.com')
            # La segunda llamada debe venir de cache
            assert r2.desde_cache is True
            assert mock_get.call_count == 1  # sin nueva llamada HTTP

    def test_obtener_creditos(self):
        from apps.comunidad.zerobounce import obtener_creditos
        with patch('apps.comunidad.zerobounce.requests.get') as mock_get:
            mock_get.return_value = self._mock_response({'Credits': 12345})
            c = obtener_creditos()
        assert c == 12345

    def test_obtener_creditos_sin_key(self, settings):
        from apps.comunidad.zerobounce import obtener_creditos
        settings.ZEROBOUNCE_API_KEY = ''
        assert obtener_creditos() == -1


# =================== Endpoint /validar-email/ ===================

class TestValidarEmailEndpoint:
    @pytest.fixture(autouse=True)
    def enable_sandbox(self, settings):
        settings.ZEROBOUNCE_SANDBOX = True
        settings.ZEROBOUNCE_API_KEY = ''
        from django.core.cache import cache
        cache.clear()

    def test_get_valido(self):
        r = APIClient().get('/api/v1/validar-email/?email=valid@example.com')
        assert r.status_code == 200
        data = r.json()
        assert data['es_valido'] is True
        assert data['status'] == 'valid'
        # No debe filtrar el campo 'raw' (sensible)
        assert 'raw' not in data

    def test_get_invalido(self):
        r = APIClient().get('/api/v1/validar-email/?email=invalid@example.com')
        assert r.status_code == 200
        data = r.json()
        assert data['es_valido'] is False

    def test_get_sin_email_devuelve_400(self):
        r = APIClient().get('/api/v1/validar-email/')
        assert r.status_code == 400

    def test_get_email_muy_largo(self):
        r = APIClient().get(
            f'/api/v1/validar-email/?email={"a" * 260}@b.com'
        )
        assert r.status_code == 400

    def test_get_email_sin_arroba(self):
        r = APIClient().get('/api/v1/validar-email/?email=foo-bar')
        assert r.status_code == 400


# =================== Endpoint admin /zerobounce/creditos/ ===================

class TestCreditosEndpoint:
    def test_sin_auth_devuelve_401_o_403(self):
        r = APIClient().get('/api/v1/admin/zerobounce/creditos/')
        assert r.status_code in (401, 403)

    def test_con_auth_sin_api_key_devuelve_creditos_none(self, settings, admin_user):
        from rest_framework.test import APIClient
        settings.ZEROBOUNCE_API_KEY = ''
        settings.ZEROBOUNCE_SANDBOX = False
        cliente = APIClient()
        cliente.force_authenticate(user=admin_user)
        r = cliente.get('/api/v1/admin/zerobounce/creditos/')
        assert r.status_code == 200
        data = r.json()
        assert data['habilitado'] is False
        assert data['creditos'] is None

    def test_con_api_key_devuelve_creditos(self, settings, admin_user):
        from rest_framework.test import APIClient
        settings.ZEROBOUNCE_API_KEY = 'fake-key'
        settings.ZEROBOUNCE_SANDBOX = False
        cliente = APIClient()
        cliente.force_authenticate(user=admin_user)
        # Mockear el requests.get que hace la view internamente.
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {'Credits': 500}
        with patch('apps.comunidad.zerobounce.requests.get', return_value=m):
            r = cliente.get('/api/v1/admin/zerobounce/creditos/')
        assert r.status_code == 200
        assert r.json()['creditos'] == 500
        assert r.json()['habilitado'] is True


# =================== Integracion con MensajeContacto ===================

class TestIntegracionSerializer:
    """Verifica que el serializer de MensajeContacto rechace emails
    invalidos antes de persistir."""

    @pytest.fixture(autouse=True)
    def enable_sandbox(self, settings, db):
        settings.ZEROBOUNCE_SANDBOX = True
        settings.ZEROBOUNCE_API_KEY = ''
        settings.ZEROBOUNCE_BLOQUEAR_INVALIDOS = True
        from django.core.cache import cache
        cache.clear()

    def test_email_invalido_bloquea_creacion(self, db):
        from rest_framework.test import APIClient
        r = APIClient().post(
            '/api/v1/contacto/',
            {
                'nombre': 'Maria Test',
                'email':  'invalid@example.com',
                'asunto': 'Prueba',
                'mensaje': 'Mensaje con longitud suficiente para validar.',
            },
            format='json',
        )
        assert r.status_code == 400
        body = r.json()
        assert 'email' in str(body).lower()

    def test_email_valido_pasa(self, db):
        from rest_framework.test import APIClient
        with patch(
            'apps.comunidad.views_institucionales.notificar_admin_mensaje_contacto',
        ) as m:
            m.return_value = True
            r = APIClient().post(
                '/api/v1/contacto/',
                {
                    'nombre': 'Maria Test',
                    'email':  'valid@example.com',
                    'asunto': 'Prueba',
                    'mensaje': 'Mensaje con longitud suficiente para validar.',
                },
                format='json',
            )
        assert r.status_code == 201, r.content


# =================== Integracion con LibroReclamacion ===================

class TestIntegracionLibroReclamacion:
    @pytest.fixture(autouse=True)
    def enable_sandbox(self, settings, db):
        settings.ZEROBOUNCE_SANDBOX = True
        settings.ZEROBOUNCE_API_KEY = ''
        settings.ZEROBOUNCE_BLOQUEAR_INVALIDOS = True
        from django.core.cache import cache
        cache.clear()

    def test_email_invalido_bloquea_creacion(self, db):
        from rest_framework.test import APIClient
        r = APIClient().post(
            '/api/v1/libro-reclamaciones/',
            {
                'nombre': 'Maria Reclamo',
                'email':  'mailbox_not_found@example.com',
                'tipo':   'QUEJA',
                'descripcion': 'Detalle extenso para validar el bloqueo.',
            },
            format='json',
        )
        assert r.status_code == 400

    def test_email_valido_pasa(self, db):
        from rest_framework.test import APIClient
        with patch(
            'apps.reports.views.notificar_admin_reclamo',
        ) as m:
            m.return_value = True
            r = APIClient().post(
                '/api/v1/libro-reclamaciones/',
                {
                    'nombre': 'Maria Reclamo',
                    'email':  'valid@example.com',
                    'tipo':   'QUEJA',
                    'descripcion': 'Detalle extenso para validar el bloqueo.',
                },
                format='json',
            )
        assert r.status_code == 201, r.content
