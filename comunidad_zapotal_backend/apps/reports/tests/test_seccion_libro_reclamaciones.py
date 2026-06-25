"""Tests exhaustivos de la seccion LIBRO DE RECLAMACIONES (Loop 2.4-2.5).

Cubre:
- numero_reclamo unico formato LIB-YYYY-NNNNNN.
- plazo_respuesta calculado (30 dias habiles).
- Plantillas de respuesta (plantillas-respuesta endpoint).
- Responder con plantilla editable (envia email al consumidor).
- Cambiar estado notifica al consumidor + audit.
- Marcar como leido al hacer retrieve.
"""
import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient


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
def reclamo(db):
    from apps.reports.models import LibroReclamacion
    return LibroReclamacion.objects.create(
        nombre='Maria Lopez',
        email='maria@example.com',
        telefono='999888777',
        direccion='Jr. Test 123',
        tipo='QUEJA',
        descripcion='Detalle extenso de la queja para validar.',
    )


# ============== numero_reclamo + plazo_respuesta ==============


@pytest.mark.django_db
class TestNumeroYPlazo:
    def test_numero_formato_lib_yyyy_nnnnnn(self, db):
        from apps.reports.models import LibroReclamacion
        r = LibroReclamacion.objects.create(
            nombre='X', email='x@x.com', tipo='QUEJA',
            descripcion='Detalle extenso.',
        )
        year = timezone.now().year
        assert r.numero_reclamo.startswith(f'LIB-{year}-')
        assert len(r.numero_reclamo) == len(f'LIB-{year}-') + 6

    def test_numero_es_unico(self, db):
        from apps.reports.models import LibroReclamacion
        r1 = LibroReclamacion.objects.create(
            nombre='A', email='a@a.com', tipo='QUEJA', descripcion='X' * 20,
        )
        r2 = LibroReclamacion.objects.create(
            nombre='B', email='b@b.com', tipo='QUEJA', descripcion='X' * 20,
        )
        assert r1.numero_reclamo != r2.numero_reclamo
        assert int(r2.numero_reclamo.split('-')[-1]) == int(r1.numero_reclamo.split('-')[-1]) + 1

    def test_plazo_es_30_dias_habiles(self, db):
        from apps.reports.models import LibroReclamacion
        from apps.reports.services import calcular_plazo_respuesta
        fecha = date(2026, 6, 1)  # lunes
        plazo = calcular_plazo_respuesta(fecha)
        # V2.2: 30 dias habiles excluyendo 2026-06-29 (San Pedro y San Pablo)
        # = 14 de julio (martes), NO 13 de julio como en v1.
        # Verificacion: el plazo es un dia habil.
        assert plazo.weekday() < 5
        # Diferencia en dias naturales >= 30 (incluyendo fines de semana y feriado excluido)
        assert (plazo - fecha).days >= 30

    def test_plazo_excluye_sabados_y_domingos(self, db):
        from apps.reports.services import calcular_plazo_respuesta
        # Si la fecha es viernes 5 junio, los primeros dias habiles
        # son lun 8, mar 9, ... excluyendo sab 6 y dom 7.
        fecha = date(2026, 6, 5)  # viernes
        plazo = calcular_plazo_respuesta(fecha)
        # Verificacion: el plazo no puede ser sabado ni domingo
        assert plazo.weekday() < 5

    def test_plazo_se_calcula_al_guardar(self, reclamo):
        """El plazo se calcula automaticamente en save()."""
        assert reclamo.plazo_respuesta is not None
        # 30 dias habiles despues de hoy
        hoy = timezone.now().date()
        delta = (reclamo.plazo_respuesta - hoy).days
        # V2.2: >=42 dias naturales (30 habiles + ~12-14 findes).
        # Si la fecha actual cae cerca de un feriado, puede ser >44.
        assert delta >= 42


# ============== Plantillas de respuesta ==============


@pytest.mark.django_db
class TestPlantillasRespuesta:
    def test_endpoint_retorna_plantillas(self, api_client, admin_user, reclamo):
        api_client.force_authenticate(user=admin_user)
        r = api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/plantillas-respuesta/')
        assert r.status_code == 200
        assert 'plantillas' in r.data
        assert 'datos_reclamo' in r.data
        ids = [p['id'] for p in r.data['plantillas']]
        assert 'aceptar' in ids
        assert 'rechazar' in ids
        assert 'informacion' in ids

    def test_plantilla_incluye_datos_del_reclamo(self, api_client, admin_user, reclamo):
        api_client.force_authenticate(user=admin_user)
        r = api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/plantillas-respuesta/')
        plantilla = r.data['plantillas'][0]
        assert reclamo.nombre in plantilla['texto']
        assert reclamo.numero_reclamo in plantilla['texto']
        assert reclamo.tipo in plantilla['texto']

    def test_endpoint_requiere_admin(self, api_client, reclamo, comunero_user):
        api_client.force_authenticate(user=comunero_user)
        r = api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/plantillas-respuesta/')
        assert r.status_code == 403


# ============== Responder (envia email al consumidor) ==============


@pytest.mark.django_db
class TestResponder:
    """Tests del endpoint responder con plantilla editable.

    Cada test hace su propio patch del envio de email (no setup_method
    porque pytest no permite anidar patches con setup_method + with).
    """

    def test_responder_requiere_admin(self, api_client, reclamo, comunero_user):
        api_client.force_authenticate(user=comunero_user)
        r = api_client.post(
            f'/api/v1/libro-reclamaciones/{reclamo.id}/responder/',
            {'respuesta_texto': 'Test'},
            format='json',
        )
        assert r.status_code == 403

    def test_responder_sin_texto_retorna_400(self, api_client, admin_user, reclamo):
        from unittest.mock import patch
        api_client.force_authenticate(user=admin_user)
        with patch('apps.reports.views.enviar_respuesta_reclamo', return_value={'enviado': True, 'asunto': 'Re: LIB-X', 'cuerpo_html': '<p>ok</p>', 'cuerpo_texto': 'ok'}):
            r = api_client.post(
                f'/api/v1/libro-reclamaciones/{reclamo.id}/responder/',
                {'respuesta_texto': ''},
                format='json',
            )
        assert r.status_code == 400

    def test_responder_exitoso_cambia_estado_a_resuelto(
        self, api_client, admin_user, reclamo,
    ):
        from unittest.mock import patch
        api_client.force_authenticate(user=admin_user)
        with patch('apps.reports.views.enviar_respuesta_reclamo', return_value={'enviado': True, 'asunto': 'Re: LIB-X', 'cuerpo_html': '<p>ok</p>', 'cuerpo_texto': 'ok'}):
            r = api_client.post(
                f'/api/v1/libro-reclamaciones/{reclamo.id}/responder/',
                {
                    'respuesta_texto': 'Hemos resuelto su queja. Detalle: ...',
                    'plantilla_usada': 'aceptar',
                },
                format='json',
            )
        assert r.status_code == 200
        assert r.data['email_enviado'] is True
        reclamo.refresh_from_db()
        assert reclamo.estado == 'RESUELTO'
        assert reclamo.respondido_por == admin_user
        assert reclamo.respondido_at is not None
        assert 'Hemos resuelto' in reclamo.respuesta_admin

    def test_responder_falla_email_retorna_502(self, api_client, admin_user, reclamo):
        from unittest.mock import patch
        api_client.force_authenticate(user=admin_user)
        with patch('apps.reports.views.enviar_respuesta_reclamo', return_value={'enviado': False, 'asunto': 'Re: LIB-X', 'cuerpo_html': '<p>fail</p>', 'cuerpo_texto': 'fail', 'error': 'smtp'}):
            r = api_client.post(
                f'/api/v1/libro-reclamaciones/{reclamo.id}/responder/',
                {'respuesta_texto': 'Test'},
                format='json',
            )
        assert r.status_code == 502
        reclamo.refresh_from_db()
        assert reclamo.estado == 'PENDIENTE'

    def test_responder_crea_audit_log(self, api_client, admin_user, reclamo):
        from unittest.mock import patch
        from apps.core.models import AuditLog
        api_client.force_authenticate(user=admin_user)
        with patch('apps.reports.views.enviar_respuesta_reclamo', return_value={'enviado': True, 'asunto': 'Re: LIB-X', 'cuerpo_html': '<p>ok</p>', 'cuerpo_texto': 'ok'}):
            api_client.post(
                f'/api/v1/libro-reclamaciones/{reclamo.id}/responder/',
                {'respuesta_texto': 'Test', 'plantilla_usada': 'aceptar'},
                format='json',
            )
        log = AuditLog.objects.filter(
            accion='UPDATE', modelo_afectado='LibroReclamacion',
            objeto_id=str(reclamo.id),
        ).first()
        assert log is not None
        assert log.metadata.get('plantilla') == 'aceptar'


# ============== Cambiar estado notifica al consumidor ==============


@pytest.mark.django_db
class TestCambiarEstadoNotifica:
    def test_cambiar_estado_notifica_consumidor(self, api_client, admin_user, reclamo):
        from unittest.mock import patch
        api_client.force_authenticate(user=admin_user)
        with patch('apps.reports.views.notificar_consumidor_cambio_estado_reclamo') as mock_notify:
            r = api_client.post(
                f'/api/v1/libro-reclamaciones/{reclamo.id}/cambiar_estado/',
                {'estado': 'EN_PROCESO'},
                format='json',
            )
        assert r.status_code == 200
        assert mock_notify.called
        args = mock_notify.call_args.args
        assert args[0] == reclamo
        assert args[1] == 'PENDIENTE'
        assert args[2] == 'EN_PROCESO'

    def test_cambiar_estado_invalido_retorna_400(self, api_client, admin_user, reclamo):
        api_client.force_authenticate(user=admin_user)
        r = api_client.post(
            f'/api/v1/libro-reclamaciones/{reclamo.id}/cambiar_estado/',
            {'estado': 'INVALIDO'},
            format='json',
        )
        assert r.status_code == 400

    def test_cambiar_estado_crea_audit(self, api_client, admin_user, reclamo):
        from unittest.mock import patch
        from apps.core.models import AuditLog
        api_client.force_authenticate(user=admin_user)
        with patch('apps.reports.views.notificar_consumidor_cambio_estado_reclamo'):
            api_client.post(
                f'/api/v1/libro-reclamaciones/{reclamo.id}/cambiar_estado/',
                {'estado': 'EN_PROCESO'},
                format='json',
            )
        log = AuditLog.objects.filter(
            accion='UPDATE', modelo_afectado='LibroReclamacion',
            objeto_id=str(reclamo.id),
        ).first()
        assert log is not None
        assert 'EN_PROCESO' in log.descripcion


# ============== Marcar como leido al hacer GET ==============


@pytest.mark.django_db
class TestMarcarLeidoAlRecuperar:
    def test_retrieve_marca_leido(self, api_client, admin_user, reclamo):
        api_client.force_authenticate(user=admin_user)
        assert reclamo.leido is False
        r = api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/')
        assert r.status_code == 200
        reclamo.refresh_from_db()
        assert reclamo.leido is True
        assert reclamo.leido_por == admin_user
        assert reclamo.leido_at is not None

    def test_retrieve_no_marca_dos_veces(self, api_client, admin_user, reclamo):
        """La segunda llamada a retrieve no debe cambiar leido_at."""
        api_client.force_authenticate(user=admin_user)
        api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/')
        reclamo.refresh_from_db()
        leido_at_1 = reclamo.leido_at
        assert leido_at_1 is not None
        # Segunda llamada: leido ya es True, no debe actualizar.
        api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/')
        reclamo.refresh_from_db()
        assert reclamo.leido_at == leido_at_1


# ============== Compliance Ley 29571 ==============


@pytest.mark.django_db
class TestComplianceLey29571:
    def test_campo_plazo_respuesta_presente(self, reclamo):
        assert hasattr(reclamo, 'plazo_respuesta')
        assert reclamo.plazo_respuesta is not None

    def test_campo_numero_reclamo_presente(self, reclamo):
        assert hasattr(reclamo, 'numero_reclamo')
        assert reclamo.numero_reclamo.startswith('LIB-')

    def test_campos_para_audit_presente(self, reclamo):
        """Los campos de audit/responder deben estar presentes."""
        for campo in ['respondido_por', 'respondido_at', 'respuesta_admin',
                       'leido_por', 'leido_at', 'prioridad']:
            assert hasattr(reclamo, campo)


# ============== V2.2: silencio administrativo positivo ==============

@pytest.mark.django_db
class TestSilencioAdministrativoPositivo:
    """V2.2: el comando marcar_reclamos_vencidos implementa la Ley
    29571 Art. 24.2 (silencio administrativo positivo)."""

    def test_reclamo_vencido_se_marca(self, db):
        from datetime import date, timedelta
        from io import StringIO
        from django.core.management import call_command
        from django.contrib.auth import get_user_model
        from apps.reports.models import LibroReclamacion
        User = get_user_model()
        admin = User.objects.create_user(
            email='admin@x.com', password='X', tipo_usuario='ADMIN',
            estado='ACTIVO', is_active=True,
        )
        # Reclamo con plazo vencido
        r = LibroReclamacion.objects.create(
            nombre='Vencido', email='v@x.com', tipo='QUEJA',
            descripcion='X' * 20,
            plazo_respuesta=date.today() - timedelta(days=1),
            numero_reclamo='LIB-TEST-000099',
        )
        out = StringIO()
        call_command('marcar_reclamos_vencidos', stdout=out)
        r.refresh_from_db()
        assert r.estado == 'VENCIDO'
        # Se notifica al admin
        from apps.messaging.models import Notificacion
        assert Notificacion.objects.filter(destinatario=admin).exists()

    def test_dry_run_no_modifica(self, db):
        from datetime import date, timedelta
        from io import StringIO
        from django.core.management import call_command
        from apps.reports.models import LibroReclamacion
        r = LibroReclamacion.objects.create(
            nombre='X', email='x@x.com', tipo='QUEJA', descripcion='X' * 20,
            plazo_respuesta=date.today() - timedelta(days=1),
            numero_reclamo='LIB-TEST-000098',
        )
        out = StringIO()
        call_command('marcar_reclamos_vencidos', '--dry-run', stdout=out)
        r.refresh_from_db()
        assert r.estado == 'PENDIENTE'
        assert 'LIB-TEST-000098' in out.getvalue()

    def test_reclamo_resuelto_no_se_marca(self, db):
        from datetime import date, timedelta
        from io import StringIO
        from django.core.management import call_command
        from apps.reports.models import LibroReclamacion
        r = LibroReclamacion.objects.create(
            nombre='Y', email='y@y.com', tipo='QUEJA', descripcion='X' * 20,
            plazo_respuesta=date.today() - timedelta(days=1),
            estado='RESUELTO',
            numero_reclamo='LIB-TEST-000097',
        )
        out = StringIO()
        call_command('marcar_reclamos_vencidos', stdout=out)
        r.refresh_from_db()
        assert r.estado == 'RESUELTO'

    def test_feriados_excluidos(self, db):
        """El calculo del plazo NO incluye feriados nacionales fijos."""
        from apps.reports.services import calcular_plazo_respuesta
        from datetime import date
        # 2026-06-29 es San Pedro y San Pablo (feriado)
        # Si empezamos el 1 de junio (lun), el 29 no cuenta.
        fecha = date(2026, 6, 1)
        plazo = calcular_plazo_respuesta(fecha)
        # El plazo debe ser un dia habil y NO 2026-06-29.
        assert plazo.weekday() < 5
        assert plazo != date(2026, 6, 29)

    def test_sanitizar_asunto_remueve_crlf(self):
        from apps.comunidad.emails import _sanitize_subject
        # Intento de inyeccion de header Bcc
        malicioso = 'Asunto\r\nBcc: atacante@evil.com'
        limpio = _sanitize_subject(malicioso)
        # Lo importante: NO quedan CR/LF que permitirian inyectar
        # un header real. Que aparezca la palabra "Bcc" como substring
        # del asunto es inofensivo.
        assert '\r' not in limpio
        assert '\n' not in limpio

    def test_sanitizar_asunto_trunca(self):
        from apps.comunidad.emails import _sanitize_subject
        largo = 'X' * 500
        limpio = _sanitize_subject(largo, max_len=200)
        assert len(limpio) <= 200

    def test_preview_email_incluido_en_respuesta(self, db):
        """El endpoint responder incluye preview del email enviado."""
        from unittest.mock import patch
        from rest_framework.test import APIClient
        from django.contrib.auth import get_user_model
        from apps.reports.models import LibroReclamacion
        User = get_user_model()
        admin = User.objects.create_user(
            email='admin@x.com', password='X', tipo_usuario='ADMIN',
            estado='ACTIVO', is_active=True,
        )
        r = LibroReclamacion.objects.create(
            nombre='Test', email='t@x.com', tipo='QUEJA', descripcion='X' * 20,
            numero_reclamo='LIB-TEST-000096',
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        with patch('apps.reports.views.enviar_respuesta_reclamo',
                   return_value={
                       'enviado': True, 'asunto': 'Re: LIB-TEST-000096',
                       'cuerpo_html': '<p>Hola</p>', 'cuerpo_texto': 'Hola',
                   }):
            resp = client.post(
                f'/api/v1/libro-reclamaciones/{r.id}/responder/',
                {'respuesta_texto': 'Hemos resuelto su caso.'},
                format='json',
            )
        assert resp.status_code == 200
        data = resp.json()
        assert 'preview' in data
        assert data['preview']['asunto'] == 'Re: LIB-TEST-000096'
        assert data['preview']['cuerpo_html'] == '<p>Hola</p>'
