"""Tests de la notificacion de Libro de Reclamaciones via Resend."""
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.comunidad.models_institucionales import ConfiguracionComunidad


@pytest.fixture
def cfg(db):
    ConfiguracionComunidad.get_solo()
    cfg = ConfiguracionComunidad.get_solo()
    cfg.email_contacto = 'admin@comunidadzapotal.gob.pe'
    cfg.nombre_oficial = 'Comunidad Test'
    cfg.save()
    return cfg


@pytest.mark.django_db
class TestNotificarAdminReclamo:
    def _crear_reclamo(self):
        from apps.reports.models import LibroReclamacion
        return LibroReclamacion.objects.create(
            nombre='Maria Reclamante',
            email='maria@example.com',
            telefono='987654321',
            direccion='Av. Test 123',
            tipo='QUEJA',
            descripcion='Detalle extenso de la queja para validar el helper.',
        )

    def test_envia_correo_con_override(self, cfg, settings):
        from apps.comunidad.emails import notificar_admin_reclamo

        rec = self._crear_reclamo()
        settings.EMAIL_DESTINO_TEMPORAL = 'override@example.com'
        with patch('apps.comunidad.emails.send_mail') as mock_send:
            mock_send.return_value = 1
            ok = notificar_admin_reclamo(rec)
        assert ok is True
        assert mock_send.call_args.kwargs['recipient_list'] == ['override@example.com']

    def test_si_falla_no_explota(self, cfg, settings):
        from apps.comunidad.emails import notificar_admin_reclamo

        rec = self._crear_reclamo()
        with patch(
            'apps.comunidad.emails.send_mail',
            side_effect=Exception('SMTP error'),
        ):
            ok = notificar_admin_reclamo(rec)
        assert ok is False


@pytest.mark.django_db
class TestLibroReclamacionCreateViewEnviaEmail:
    def test_crear_reclamo_dispara_notificacion(self, cfg, settings):
        settings.EMAIL_DESTINO_TEMPORAL = 'admin@comunidadzapotal.gob.pe'
        with patch(
            'apps.reports.views.notificar_admin_reclamo',
        ) as mock_notify:
            mock_notify.return_value = True
            r = APIClient().post(
                '/api/v1/libro-reclamaciones/',
                {
                    'nombre': 'Pedro Reclamo',
                    'email': 'pedro@example.com',
                    'telefono': '987654321',
                    'direccion': 'Calle Real 123',
                    'tipo': 'RECLAMO',
                    'descripcion': 'Detalle extenso del reclamo para validar el envio.',
                },
                format='json',
            )
        assert r.status_code == 201, r.content
        assert mock_notify.called
        args = mock_notify.call_args.args
        assert args[0].email == 'pedro@example.com'

    def test_crear_reclamo_no_falla_si_resend_cae(self, cfg, settings):
        settings.EMAIL_DESTINO_TEMPORAL = 'admin@comunidadzapotal.gob.pe'
        with patch(
            'apps.reports.views.notificar_admin_reclamo',
            side_effect=Exception('boom'),
        ):
            r = APIClient().post(
                '/api/v1/libro-reclamaciones/',
                {
                    'nombre': 'Otro Reclamo',
                    'email': 'otro@example.com',
                    'tipo': 'QUEJA',
                    'descripcion': 'Detalle extenso del reclamo para validar.',
                },
                format='json',
            )
        # El reclamo se crea OK aunque Resend falle
        assert r.status_code == 201
        from apps.reports.models import LibroReclamacion
        assert LibroReclamacion.objects.filter(email='otro@example.com').exists()
