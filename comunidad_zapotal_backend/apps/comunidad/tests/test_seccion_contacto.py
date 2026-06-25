"""Tests exhaustivos de la seccion CONTACTO (Loop 1.4 + V2.1).

Cubre:
- Codigo muerto eliminado (ContactoMensaje).
- Migracion del modelo MensajeContacto con 8 campos nuevos.
- Endpoint responder (envia email al visitante).
- Endpoint nota (guarda nota interna).
- Endpoint EmailContactoPublico (aplica override).
- Reply-To en email al admin.
- Audit log en actions.
- V2.1: endpoint set_prioridad (action admin).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.comunidad.models_institucionales import MensajeContacto
from apps.messaging.models import Notificacion


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
        is_active=True,
    )


@pytest.fixture
def mensaje(db):
    return MensajeContacto.objects.create(
        nombre='Visitante Test',
        email='visitante@example.com',
        telefono='999888777',
        asunto='Consulta general',
        mensaje='Quisiera saber mas sobre la comunidad.',
    )


# ============== Codigo muerto eliminado ==============


class TestCodigoMuertoEliminado:
    """Verifica que el modelo duplicado ContactoMensaje ya no existe."""

    def test_contactomensaje_modelo_eliminado(self):
        from apps.reports import models as reports_models
        assert not hasattr(reports_models, 'ContactoMensaje'), (
            'ContactoMensaje debe estar eliminado de apps.reports.models.'
        )

    def test_contactomensaje_viewset_eliminado(self):
        from apps.reports import views as reports_views
        assert not hasattr(reports_views, 'ContactoMensajeViewSet'), (
            'ContactoMensajeViewSet debe estar eliminado de apps.reports.views.'
        )

    def test_contactomensaje_serializer_eliminado(self):
        from apps.reports import serializers as reports_serializers
        assert not hasattr(reports_serializers, 'ContactoMensajeSerializer'), (
            'ContactoMensajeSerializer debe estar eliminado de apps.reports.serializers.'
        )

    def test_endpoint_contacto_mensajes_eliminado(self, api_client):
        """GET /api/v1/contacto-mensajes/ debe retornar 404."""
        r = api_client.get('/api/v1/contacto-mensajes/')
        assert r.status_code == 404


# ============== Migracion del modelo ==============


class TestMigracionModelo:
    def test_campos_nuevos_existen(self):
        campos = [f.name for f in MensajeContacto._meta.get_fields()]
        assert 'prioridad' in campos
        assert 'nota_admin' in campos
        assert 'nota_admin_at' in campos
        assert 'nota_admin_por' in campos
        assert 'respondido_por' in campos
        assert 'respondido_at' in campos
        assert 'respondido_texto' in campos
        assert 'respondido_desde_panel' in campos

    def test_prioridad_default_media(self, mensaje):
        """El campo prioridad tiene default 'MEDIA'."""
        assert mensaje.prioridad == 'MEDIA'

    def test_prioridad_choices(self, mensaje):
        from apps.comunidad.models_institucionales import MensajeContacto as MC
        choices = [c[0] for c in MC.Prioridad.choices]
        assert 'BAJA' in choices
        assert 'MEDIA' in choices
        assert 'ALTA' in choices

    def test_campos_administrativos_default_vacios(self, mensaje):
        assert mensaje.nota_admin == ''
        assert mensaje.nota_admin_at is None
        assert mensaje.nota_admin_por is None
        assert mensaje.respondido_por is None
        assert mensaje.respondido_at is None
        assert mensaje.respondido_texto == ''
        assert mensaje.respondido_desde_panel is False


# ============== Endpoint responder ==============


@pytest.mark.django_db
class TestEndpointResponder:
    def setup_method(self):
        from unittest.mock import patch
        self.patch_send = patch(
            'apps.comunidad.emails.enviar_respuesta_contacto',
            return_value=True,
        )
        self.patch_send.start()

    def teardown_method(self):
        self.patch_send.stop()

    def test_responder_requiere_admin(self, api_client, mensaje, comunero_user):
        api_client.force_authenticate(user=comunero_user)
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/responder/',
            {'respuesta_texto': 'Gracias por contactarnos.'},
            format='json',
        )
        assert r.status_code == 403

    def test_responder_sin_texto_retorna_400(self, api_client, admin_user, mensaje):
        api_client.force_authenticate(user=admin_user)
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/responder/',
            {'respuesta_texto': ''},
            format='json',
        )
        assert r.status_code == 400
        assert 'Falta respuesta_texto' in str(r.content)

    def test_responder_texto_largo_retorna_400(self, api_client, admin_user, mensaje):
        api_client.force_authenticate(user=admin_user)
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/responder/',
            {'respuesta_texto': 'x' * 5001},
            format='json',
        )
        assert r.status_code == 400
        assert '5000 caracteres' in str(r.content)

    def test_responder_exitoso_marca_respondido(self, api_client, admin_user, mensaje):
        api_client.force_authenticate(user=admin_user)
        texto = 'Gracias por contactarnos. Resolveremos en 48h.'
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/responder/',
            {'respuesta_texto': texto},
            format='json',
        )
        assert r.status_code == 200
        assert r.data == {'status': 'respondido', 'email_enviado': True}
        mensaje.refresh_from_db()
        assert mensaje.respondido is True
        assert mensaje.respondido_desde_panel is True
        assert mensaje.respondido_por == admin_user
        assert mensaje.respondido_texto == texto
        assert mensaje.respondido_at is not None

    def test_responder_falla_email_retorna_502(self, api_client, admin_user, mensaje):
        from unittest.mock import patch
        api_client.force_authenticate(user=admin_user)
        with patch('apps.comunidad.emails.enviar_respuesta_contacto', return_value=False):
            r = api_client.post(
                f'/api/v1/mensajes-contacto/{mensaje.id}/responder/',
                {'respuesta_texto': 'texto'},
                format='json',
            )
        assert r.status_code == 502
        # El mensaje NO debe marcarse como respondido si el email fallo.
        mensaje.refresh_from_db()
        assert mensaje.respondido is False


# ============== Endpoint nota_admin ==============


@pytest.mark.django_db
class TestEndpointNotaAdmin:
    def test_nota_requiere_admin(self, api_client, mensaje, comunero_user):
        api_client.force_authenticate(user=comunero_user)
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/nota/',
            {'nota': 'Llamar al visitante el lunes'},
            format='json',
        )
        assert r.status_code == 403

    def test_nota_guarda_campos(self, api_client, admin_user, mensaje):
        api_client.force_authenticate(user=admin_user)
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/nota/',
            {'nota': 'Revisar con el equipo legal'},
            format='json',
        )
        assert r.status_code == 200
        mensaje.refresh_from_db()
        assert mensaje.nota_admin == 'Revisar con el equipo legal'
        assert mensaje.nota_admin_at is not None
        assert mensaje.nota_admin_por == admin_user

    def test_nota_vacia_limpia_campo(self, api_client, admin_user, mensaje):
        """El admin puede limpiar su nota enviando string vacio."""
        mensaje.nota_admin = 'nota vieja'
        mensaje.save()
        api_client.force_authenticate(user=admin_user)
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/nota/',
            {'nota': ''},
            format='json',
        )
        assert r.status_code == 200
        mensaje.refresh_from_db()
        assert mensaje.nota_admin == ''


# ============== Endpoint EmailContactoPublico ==============


@pytest.mark.django_db
class TestEmailContactoPublico:
    def test_endpoint_publico_retorna_emails(self, api_client):
        r = api_client.get('/api/v1/public/email-contacto/')
        assert r.status_code == 200
        assert 'email_contacto' in r.data
        assert 'email_denuncias' in r.data

    def test_aplica_override(self, api_client, settings):
        settings.EMAIL_DESTINO_TEMPORAL = 'override@custom.com'
        r = api_client.get('/api/v1/public/email-contacto/')
        assert r.data['email_contacto'] == 'override@custom.com'

    def test_sin_override_retorna_email_db(self, api_client, settings):
        settings.EMAIL_DESTINO_TEMPORAL = ''
        r = api_client.get('/api/v1/public/email-contacto/')
        # Sin override, retorna el email de ConfiguracionComunidad.email_contacto
        assert r.data['email_contacto']  # truthy, no es vacio


# ============== Reply-To en email al admin ==============


@pytest.mark.django_db
class TestReplyToEmail:
    def test_email_tiene_reply_to_del_visitante(self, mensaje, settings):
        from unittest.mock import patch, MagicMock
        with patch('apps.comunidad.emails.EmailMessage') as mock_email_cls:
            mock_email = MagicMock()
            mock_email_cls.return_value = mock_email
            from apps.comunidad.emails import notificar_admin_mensaje_contacto
            notificar_admin_mensaje_contacto(mensaje)
        # Verificar que se construyo con reply_to=[mensaje.email]
        call_kwargs = mock_email_cls.call_args
        assert call_kwargs.kwargs.get('reply_to') == [mensaje.email]
        assert call_kwargs.kwargs.get('to')  # destinatario


# ============== Audit log en actions ==============


@pytest.mark.django_db
class TestAuditLog:
    def test_marcar_leido_crea_audit(self, api_client, admin_user, mensaje):
        from apps.core.models import AuditLog
        api_client.force_authenticate(user=admin_user)
        api_client.post(f'/api/v1/mensajes-contacto/{mensaje.id}/marcar_leido/')
        log = AuditLog.objects.filter(
            accion='UPDATE', modelo_afectado='MensajeContacto',
            objeto_id=str(mensaje.id),
        ).first()
        assert log is not None
        assert log.metadata.get('campo') == 'leido'

    def test_responder_crea_audit(self, api_client, admin_user, mensaje):
        from unittest.mock import patch
        from apps.core.models import AuditLog
        with patch('apps.comunidad.emails.enviar_respuesta_contacto', return_value=True):
            api_client.force_authenticate(user=admin_user)
            api_client.post(
                f'/api/v1/mensajes-contacto/{mensaje.id}/responder/',
                {'respuesta_texto': 'Test respuesta'},
                format='json',
            )
        log = AuditLog.objects.filter(
            accion='UPDATE', modelo_afectado='MensajeContacto',
            objeto_id=str(mensaje.id),
        ).first()
        assert log is not None
        assert 'Respuesta enviada' in log.descripcion
        assert log.metadata.get('caracteres') == 14


# ============== V2.1: set_prioridad action ==============

@pytest.mark.django_db
class TestSetPrioridad:
    """V2.1: endpoint PATCH-equivalente para cambiar la prioridad."""

    def test_set_prioridad_requiere_admin(self, api_client, mensaje, comunero_user):
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(comunero_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/set_prioridad/',
            {'prioridad': 'ALTA'}, format='json',
        )
        assert r.status_code == 403

    def test_set_prioridad_valida(self, api_client, admin_user, mensaje):
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/set_prioridad/',
            {'prioridad': 'ALTA'}, format='json',
        )
        assert r.status_code == 200
        assert r.json()['prioridad'] == 'ALTA'
        mensaje.refresh_from_db()
        assert mensaje.prioridad == 'ALTA'

    def test_set_prioridad_invalida_retorna_400(self, api_client, admin_user, mensaje):
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        r = api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/set_prioridad/',
            {'prioridad': 'URGENTE'}, format='json',
        )
        assert r.status_code == 400

    def test_set_prioridad_crea_audit(self, api_client, admin_user, mensaje):
        from apps.core.models import AuditLog
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken.for_user(admin_user).access_token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        api_client.post(
            f'/api/v1/mensajes-contacto/{mensaje.id}/set_prioridad/',
            {'prioridad': 'BAJA'}, format='json',
        )
        log = AuditLog.objects.filter(
            accion='UPDATE', modelo_afectado='MensajeContacto',
            objeto_id=str(mensaje.id),
        ).order_by('-id').first()
        assert log is not None
        assert log.metadata.get('valor') == 'BAJA'


# ============== V2.1: X-ZB-Validated header (skip doble validacion) ==============

@pytest.mark.django_db
class TestZBValidatedHeader:
    """V2.1: si el frontend ya valido ZB hace <5 min, el backend
    no debe volver a invocar ZeroBounce. Se detecta por el header
    ``X-ZB-Validated: <email>|<iso8601>``."""

    def test_sin_header_valida_normal(self, api_client, settings):
        from rest_framework import status as http_status
        settings.ZEROBOUNCE_SANDBOX = True
        from unittest.mock import patch
        with patch('apps.comunidad.zerobounce.validar_email') as mock_zb:
            mock_zb.return_value.es_valido = True
            r = api_client.post('/api/v1/contacto/', {
                'nombre': 'Visitante X', 'email': 'valid@example.com',
                'asunto': 'Test', 'mensaje': 'Mensaje de prueba suficiente.',
            }, format='json', HTTP_X_ZB_VALIDATED='')
        assert mock_zb.called, 'Sin header debe validar ZB igual'

    def test_header_reciente_no_llama_zb(self, api_client, settings):
        from unittest.mock import patch
        from django.utils import timezone
        ts = timezone.now().isoformat()
        with patch('apps.comunidad.zerobounce.validar_email') as mock_zb:
            r = api_client.post('/api/v1/contacto/', {
                'nombre': 'Visitante Y', 'email': 'valid@example.com',
                'asunto': 'Test', 'mensaje': 'Mensaje de prueba suficiente.',
            }, format='json', HTTP_X_ZB_VALIDATED=f'valid@example.com|{ts}')
            assert r.status_code in (200, 201), r.content
        assert not mock_zb.called, (
            'Con X-ZB-Validated reciente, no debe invocar ZeroBounce'
        )

    def test_header_email_distinto_aun_valida(self, api_client, settings):
        from unittest.mock import patch
        from django.utils import timezone
        ts = timezone.now().isoformat()
        with patch('apps.comunidad.zerobounce.validar_email') as mock_zb:
            mock_zb.return_value.es_valido = True
            api_client.post('/api/v1/contacto/', {
                'nombre': 'Visitante Z', 'email': 'valid@example.com',
                'asunto': 'Test', 'mensaje': 'Mensaje de prueba suficiente.',
            }, format='json', HTTP_X_ZB_VALIDATED=f'otro@example.com|{ts}')
        assert mock_zb.called, 'Email distinto debe re-validar'

    def test_header_expirado_revalida(self, api_client, settings):
        from unittest.mock import patch
        from django.utils import timezone
        from datetime import timedelta
        ts_expirado = (timezone.now() - timedelta(minutes=10)).isoformat()
        with patch('apps.comunidad.zerobounce.validar_email') as mock_zb:
            mock_zb.return_value.es_valido = True
            api_client.post('/api/v1/contacto/', {
                'nombre': 'Visitante W', 'email': 'valid@example.com',
                'asunto': 'Test', 'mensaje': 'Mensaje de prueba suficiente.',
            }, format='json', HTTP_X_ZB_VALIDATED=f'valid@example.com|{ts_expirado}')
        assert mock_zb.called, 'Header >5min debe re-validar'

    def test_header_malformado_no_rompe(self, api_client, settings):
        from unittest.mock import patch
        with patch('apps.comunidad.zerobounce.validar_email') as mock_zb:
            mock_zb.return_value.es_valido = True
            r = api_client.post('/api/v1/contacto/', {
                'nombre': 'Visitante V', 'email': 'valid@example.com',
                'asunto': 'Test', 'mensaje': 'Mensaje de prueba suficiente.',
            }, format='json', HTTP_X_ZB_VALIDATED='esto-no-es-header-valido')
        assert mock_zb.called


# ============== V2.1: rate limit per-email ==============

@pytest.mark.django_db(transaction=True)
class TestRateLimitPorEmail:
    """V2.1: max 3 mensajes/15min por combinacion IP+email."""

    def test_tres_mensajes_mismo_email_pasan(self, api_client, settings):
        from unittest.mock import patch
        from django.core.cache import cache
        cache.clear()
        settings.ZEROBOUNCE_SANDBOX = True
        with patch('apps.comunidad.zerobounce.validar_email') as mock_zb:
            mock_zb.return_value.es_valido = True
            for i in range(3):
                r = api_client.post('/api/v1/contacto/', {
                    'nombre': f'Vis{i}itante', 'email': 'repetido@example.com',
                    'asunto': f'Test {i}', 'mensaje': f'Mensaje de prueba {i} abc.',
                }, format='json')
                assert r.status_code in (200, 201), f'Intento {i}: {r.status_code} {r.content}'

    def test_cuarto_mensaje_mismo_email_bloqueado(self, api_client, settings):
        from unittest.mock import patch
        from apps.comunidad.views_institucionales import MensajeContactoPorEmailThrottle
        from django.core.cache import cache
        cache.clear()
        settings.ZEROBOUNCE_SANDBOX = True
        with patch('apps.comunidad.zerobounce.validar_email') as mock_zb:
            mock_zb.return_value.es_valido = True
            for i in range(3):
                api_client.post('/api/v1/contacto/', {
                    'nombre': f'Vis{i}itante', 'email': 'spam@example.com',
                    'asunto': f'Test {i}', 'mensaje': f'Mensaje de prueba {i} abc.',
                }, format='json')
            r = api_client.post('/api/v1/contacto/', {
                'nombre': 'Visi4tante', 'email': 'spam@example.com',
                'asunto': 'T4', 'mensaje': 'Mensaje de prueba 4 abc.',
            }, format='json')
        assert r.status_code == 429, f'Segundo 4to intento: {r.status_code}'


# ============== V2.1: command cleanup_legacy_tables ==============

class TestCleanupLegacyTables:
    """V2.1: el command cleanup_legacy_tables existe y es seguro."""

    def test_command_existe(self):
        from django.core.management import get_commands
        assert 'cleanup_legacy_tables' in get_commands()

    def test_dry_run_no_elimina(self, db):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command('cleanup_legacy_tables', '--dry-run', stdout=out)
        # El output debe mencionar dry-run
        assert 'Dry run' in out.getvalue() or 'no existe' in out.getvalue()
