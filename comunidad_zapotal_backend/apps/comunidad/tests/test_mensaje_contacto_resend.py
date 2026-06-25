"""Tests de la integracion Resend en MensajeContacto.

Cubre el helper :func:`apps.comunidad.emails.notificar_admin_mensaje_contacto`
y la llamada desde el view de creacion publica. Se mockea el backend de
Django para no tocar la red ni requerir API key real.

Loop 1.5: actualizado a EmailMessage (con reply_to).
"""
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.comunidad.models_institucionales import (
    ConfiguracionComunidad, MensajeContacto,
)


@pytest.fixture
def cliente():
    return APIClient()


@pytest.fixture
def cfg_con_email(db, settings):
    settings.EMAIL_DESTINO_TEMPORAL = ''
    ConfiguracionComunidad.get_solo()
    cfg = ConfiguracionComunidad.get_solo()
    cfg.email_contacto = 'admin@comunidadzapotal.com'
    cfg.nombre_oficial = 'Comunidad Test'
    cfg.save()
    return cfg


# =================== notificar_admin_mensaje_contacto ===================

class TestNotificarAdminMensajeContacto:
    def test_envia_correo_al_email_contacto(self, cfg_con_email, db):
        from apps.comunidad.emails import notificar_admin_mensaje_contacto

        msg = MensajeContacto.objects.create(
            nombre='Juan', email='juan@test.com', asunto='Saludo',
            mensaje='Hola comunidad, este es un mensaje de prueba.',
        )
        with patch('apps.comunidad.emails.EmailMessage') as mock_email_cls:
            mock_email = mock_email_cls.return_value
            ok = notificar_admin_mensaje_contacto(msg)
        assert ok is True
        assert mock_email_cls.called
        kwargs = mock_email_cls.call_args.kwargs
        assert 'admin@comunidadzapotal.com' in kwargs['to']
        # subject es posicional o kwarg
        subject = mock_email_cls.call_args.args[0] if mock_email_cls.call_args.args else kwargs.get('subject', '')
        assert 'Saludo' in subject
        assert 'Juan' in subject
        assert kwargs.get('reply_to') == [msg.email]
        assert mock_email.send.called

    def test_si_send_mail_falla_no_explota(self, cfg_con_email, db):
        from apps.comunidad.emails import notificar_admin_mensaje_contacto

        msg = MensajeContacto.objects.create(
            nombre='Maria', email='maria@test.com', asunto='X',
            mensaje='Mensaje lo suficientemente largo para validar.',
        )
        with patch(
            'apps.comunidad.emails.EmailMessage',
            side_effect=Exception('Resend 500'),
        ):
            ok = notificar_admin_mensaje_contacto(msg)

        assert ok is False

    def test_sin_email_destino_no_envia(self, db, settings):
        from apps.comunidad.emails import notificar_admin_mensaje_contacto

        settings.EMAIL_DESTINO_TEMPORAL = ''
        ConfiguracionComunidad.get_solo()
        cfg = ConfiguracionComunidad.get_solo()
        cfg.email_contacto = ''
        cfg.save()
        settings.ADMIN_EMAILS = []
        msg = MensajeContacto.objects.create(
            nombre='Anon', email='a@b.com', asunto='X',
            mensaje='Mensaje suficientemente largo para validar.',
        )
        with patch('apps.comunidad.emails.EmailMessage') as mock_email_cls:
            ok = notificar_admin_mensaje_contacto(msg)
        assert ok is False
        assert not mock_email_cls.called

    def test_sin_email_contacto_cae_a_admin_emails(self, db, settings):
        from apps.comunidad.emails import notificar_admin_mensaje_contacto

        settings.EMAIL_DESTINO_TEMPORAL = ''
        ConfiguracionComunidad.get_solo()
        cfg = ConfiguracionComunidad.get_solo()
        cfg.email_contacto = ''
        cfg.save()
        settings.ADMIN_EMAILS = ['fallback@admin.com']
        msg = MensajeContacto.objects.create(
            nombre='X', email='a@b.com', asunto='X',
            mensaje='Mensaje suficientemente largo para validar.',
        )
        with patch('apps.comunidad.emails.EmailMessage') as mock_email_cls:
            mock_email = mock_email_cls.return_value
            ok = notificar_admin_mensaje_contacto(msg)
        assert ok is True
        assert 'fallback@admin.com' in mock_email_cls.call_args.kwargs['to']


# =================== Integracion con el view ===================

class TestMensajeContactoCreateViewEnviaEmail:
    def test_crear_mensaje_publico_dispara_notificacion(self, cfg_con_email, db):
        with patch(
            'apps.comunidad.views_institucionales.notificar_admin_mensaje_contacto',
        ) as mock_notify:
            mock_notify.return_value = True
            r = APIClient().post(
                '/api/v1/contacto/',
                {
                    'nombre': 'Lucía Vargas',
                    'email': 'lucia@example.com',
                    'asunto': 'Consulta sobre terrenos',
                    'mensaje': 'Buenas tardes, quisiera información sobre los requisitos.',
                },
                format='json',
            )
        assert r.status_code == 201
        assert mock_notify.called
        # El objeto creado se pasa al notificador
        args = mock_notify.call_args.args
        assert args[0].email == 'lucia@example.com'

    def test_crear_mensaje_no_falla_si_resend_cae(self, cfg_con_email, db):
        with patch(
            'apps.comunidad.views_institucionales.notificar_admin_mensaje_contacto',
            side_effect=Exception('SMTP timeout'),
        ):
            r = APIClient().post(
                '/api/v1/contacto/',
                {
                    'nombre': 'Carlos Prueba',
                    'email': 'carlos@example.com',
                    'asunto': 'Otro asunto',
                    'mensaje': 'Mensaje de prueba con longitud suficiente.',
                },
                format='json',
            )
        # El mensaje se crea OK aunque Resend falle
        assert r.status_code == 201
        assert MensajeContacto.objects.filter(email='carlos@example.com').exists()

    def test_rate_limit_se_apica_antes_de_envio(self, cfg_con_email, db):
        """El view expone ScopedRateThrottle con scope 'contacto'.
        Confirmamos que la clase esta configurada correctamente; el
        comportamiento granular del throttle ya se cubre en los tests
        de fase5 (test_validacion_mensaje_minimo_10_caracteres y
        posteriores que invocan el endpoint con el mismo client).
        """
        from apps.comunidad.views_institucionales import MensajeContactoCreateView
        assert any(
            getattr(t, 'scope', None) == 'contacto'
            for t in MensajeContactoCreateView.throttle_classes
        )

    def test_override_email_destino_temporal(self, cfg_con_email, settings):
        """Cuando EMAIL_DESTINO_TEMPORAL esta configurado, el correo
        va a esa direccion aunque el campo email_contacto de la
        ConfiguracionComunidad tenga otra direccion.
        """
        from apps.comunidad.emails import notificar_admin_mensaje_contacto

        msg = MensajeContacto.objects.create(
            nombre='Test Override',
            email='user@example.com',
            asunto='Asunto de prueba',
            mensaje='Mensaje con longitud suficiente para validar el envio.',
        )
        settings.EMAIL_DESTINO_TEMPORAL = 'override@example.com'
        with patch('apps.comunidad.emails.EmailMessage') as mock_email_cls:
            mock_email = mock_email_cls.return_value
            ok = notificar_admin_mensaje_contacto(msg)
        assert ok is True
        assert mock_email_cls.call_args.kwargs['to'] == ['override@example.com']

    def test_si_override_vacio_cae_a_email_contacto_cfg(self, cfg_con_email, settings):
        """Si EMAIL_DESTINO_TEMPORAL es string vacio, se usa el
        email_contacto de la ConfiguracionComunidad."""
        from apps.comunidad.emails import notificar_admin_mensaje_contacto

        msg = MensajeContacto.objects.create(
            nombre='Sin Override',
            email='user2@example.com',
            asunto='Otro asunto',
            mensaje='Mensaje con longitud suficiente para validar.',
        )
        settings.EMAIL_DESTINO_TEMPORAL = ''
        with patch('apps.comunidad.emails.EmailMessage') as mock_email_cls:
            mock_email = mock_email_cls.return_value
            ok = notificar_admin_mensaje_contacto(msg)
        assert ok is True
        assert mock_email_cls.call_args.kwargs['to'] == [
            cfg_con_email.email_contacto,
        ]

    def test_acepta_alias_legacy_nombres_correo(self, cfg_con_email, db):
        """El serializer debe aceptar tanto `nombre`/`nombres` y
        `email`/`correo` (alias para compatibilidad con frontend legacy).
        Sin esto el frontend que enviaba `nombres`/`correo` recibia 400
        con `nombre` y `email` requeridos.
        """
        with patch(
            'apps.comunidad.views_institucionales.notificar_admin_mensaje_contacto',
        ) as mock_notify:
            mock_notify.return_value = True
            r = APIClient().post(
                '/api/v1/contacto/',
                {
                    'nombres': 'Maria Conocenos',
                    'correo':  'maria.conocenos@example.com',
                    'asunto':  'Consulta sobre servicios',
                    'mensaje': 'Mensaje de prueba con longitud suficiente.',
                },
                format='json',
            )
        assert r.status_code == 201, r.content
        msg = MensajeContacto.objects.get(email='maria.conocenos@example.com')
        assert msg.nombre == 'Maria Conocenos'

    def test_validacion_detalle_en_400(self, cfg_con_email, db):
        """Cuando el payload es invalido, el 400 debe incluir detalles
        por campo para que el frontend pueda mostrarlos."""
        r = APIClient().post(
            '/api/v1/contacto/',
            {'nombre': 'X', 'email': 'no-es-email', 'asunto': '', 'mensaje': 'corto'},
            format='json',
        )
        assert r.status_code == 400
        body = r.json()
        # La API envuelve el error: body['error']['details'] contiene
        # el detalle por campo
        details = body.get('error', {}).get('details') or body.get('details') or body
        assert 'nombre' in details or 'email' in details or 'asunto' in details or 'mensaje' in details
