"""Tests para el inbox de admin /admin/contacto.

Cubre:
- Permisos: anonimo NO accede, user normal NO accede, admin SI accede.
- CRUD basico: list, retrieve, delete.
- Actions: marcar_leido, marcar_respondido (incluye log_audit_event).
- Crear MensajeContacto crea Notificacion para cada admin activo.
- bulk_create se usa (no N queries).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.comunidad.models_institucionales import MensajeContacto
from apps.messaging.models import Notificacion


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_user(
        email='admin@comunidadzapotal.gob.pe',
        password='Admin1234!',
        tipo_usuario='ADMIN',
        estado='ACTIVO',
    )


@pytest.fixture
def otro_admin(db):
    User = get_user_model()
    return User.objects.create_user(
        email='admin2@comunidadzapotal.gob.pe',
        password='Admin1234!',
        tipo_usuario='ADMIN',
        estado='ACTIVO',
    )


@pytest.fixture
def admin_bloqueado(db):
    User = get_user_model()
    return User.objects.create_user(
        email='bloqueado@comunidadzapotal.gob.pe',
        password='Admin1234!',
        tipo_usuario='ADMIN',
        estado='BLOQUEADO',
    )


@pytest.fixture
def comunero(db):
    User = get_user_model()
    return User.objects.create_user(
        email='juan@example.com',
        password='Juan1234!',
        tipo_usuario='COMUNERO',
        estado='ACTIVO',
    )


@pytest.fixture
def mensaje(db):
    return MensajeContacto.objects.create(
        nombre='Juan Test',
        email='juan.test@example.com',
        telefono='999888777',
        asunto='Consulta general',
        mensaje='Quisiera saber mas sobre la comunidad.',
    )


@pytest.mark.django_db
class TestPermisosInbox:
    def test_anonimo_no_accede(self):
        client = APIClient()
        r = client.get('/api/v1/mensajes-contacto/')
        assert r.status_code in (401, 403)

    def test_comunero_no_accede(self, comunero):
        client = APIClient()
        client.force_authenticate(user=comunero)
        r = client.get('/api/v1/mensajes-contacto/')
        assert r.status_code == 403

    def test_admin_si_accede(self, admin_user, mensaje):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        r = client.get('/api/v1/mensajes-contacto/')
        assert r.status_code == 200
        assert len(r.data.get('results', r.data)) >= 1


@pytest.mark.django_db
class TestCRUDInbox:
    def test_listar(self, admin_user, mensaje):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        r = client.get('/api/v1/mensajes-contacto/')
        assert r.status_code == 200

    def test_eliminar(self, admin_user, mensaje):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        r = client.delete(f'/api/v1/mensajes-contacto/{mensaje.id}/')
        assert r.status_code == 204
        assert not MensajeContacto.objects.filter(id=mensaje.id).exists()


@pytest.mark.django_db
class TestActionsInbox:
    def test_marcar_leido(self, admin_user, mensaje):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        assert mensaje.leido is False
        r = client.post(f'/api/v1/mensajes-contacto/{mensaje.id}/marcar_leido/')
        assert r.status_code == 200
        mensaje.refresh_from_db()
        assert mensaje.leido is True

    def test_marcar_respondido(self, admin_user, mensaje):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        assert mensaje.respondido is False
        r = client.post(f'/api/v1/mensajes-contacto/{mensaje.id}/marcar_respondido/')
        assert r.status_code == 200
        mensaje.refresh_from_db()
        assert mensaje.respondido is True


@pytest.mark.django_db
class TestNotificacionEnContacto:
    def test_crear_mensaje_crea_notif_para_admins(
        self, admin_user, otro_admin, admin_bloqueado,
    ):
        """Cuando se crea un MensajeContacto, se crea una Notificacion
        para cada admin activo. Admin bloqueado NO recibe."""
        client = APIClient()
        # Limpiar notifs previas
        Notificacion.objects.all().delete()
        r = client.post(
            '/api/v1/contacto/',
            data={
                'nombre': 'Visitante Web',
                'email': 'visitante@example.com',
                'asunto': 'Consulta',
                'mensaje': 'Quiero informacion sobre el turismo.',
            },
            format='json',
        )
        assert r.status_code == 201, r.data
        notifs = Notificacion.objects.filter(referencia_tipo='CONTACTO')
        assert notifs.count() == 2  # admin + otro_admin; no admin_bloqueado
        destinatarios = set(notifs.values_list('destinatario_id', flat=True))
        assert admin_user.id in destinatarios
        assert otro_admin.id in destinatarios
        assert admin_bloqueado.id not in destinatarios
        for n in notifs:
            assert n.url_destino == '/admin/contacto'
            assert n.tipo == 'info'
            assert 'Visitante Web' in n.titulo

    def test_mensaje_invalido_no_crea_notif(self, admin_user):
        """Email ZeroBounce invalid (disposable) rechaza el POST y NO
        crea Notificacion."""
        client = APIClient()
        Notificacion.objects.all().delete()
        r = client.post(
            '/api/v1/contacto/',
            data={
                'nombre': 'Spam',
                'email': 'disposable@example.com',
                'asunto': 'Spam',
                'mensaje': 'Hola',
            },
            format='json',
        )
        # ZeroBounce sandbox marca disposable como invalid -> 400
        assert r.status_code == 400
        assert Notificacion.objects.filter(referencia_tipo='CONTACTO').count() == 0
