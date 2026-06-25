"""Tests para notificaciones automaticas en eventos del sistema.

Cubre:
- Crear MensajeContacto crea Notificacion para cada admin activo.
- Crear LibroReclamacion crea Notificacion para admins.
- Aprobar/Rechazar/Bloquear usuario crea Notificacion para el usuario y admins.
- Signal de Noticia publicada crea Notificacion bulk.
- Signal de Evento creado crea Notificacion bulk.
- Endpoint GET /notificaciones/no-leidas/count/ retorna conteo correcto.
- Admin ve conteo global; no-admin solo el suyo.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.comunidad.models_institucionales import MensajeContacto
from apps.content.models import Noticia, Evento, Categoria
from apps.messaging.models import Notificacion
from apps.reports.models import LibroReclamacion


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
def otro_admin(db):
    User = get_user_model()
    return User.objects.create_user(
        email='admin2@comunidadzapotal.gob.pe',
        password='Admin1234!',
        tipo_usuario='ADMIN',
        estado='ACTIVO',
        is_active=True,
    )


@pytest.fixture
def comunero_user(db):
    User = get_user_model()
    return User.objects.create_user(
        email='juan@comunidadzapotal.gob.pe',
        password='Juan1234!',
        tipo_usuario='COMUNERO',
        estado='PENDIENTE_APROBACION',
        is_active=True,
    )


# ============== MensajeContacto ==============


@pytest.mark.django_db
class TestNotifMensajeContacto:
    def test_crea_notif_para_admins(self, admin_user, otro_admin):
        client = APIClient()
        Notificacion.objects.all().delete()
        r = client.post('/api/v1/contacto/', {
            'nombre': 'Web Visitante',
            'email': 'visitante@example.com',
            'asunto': 'Hola',
            'mensaje': 'Quisiera mas informacion sobre la comunidad.',
        }, format='json')
        assert r.status_code == 201
        notifs = Notificacion.objects.filter(referencia_tipo='CONTACTO')
        assert notifs.count() == 2


# ============== LibroReclamacion ==============


@pytest.mark.django_db
class TestNotifLibroReclamacion:
    def test_crea_notif_para_admins(self, admin_user, otro_admin):
        client = APIClient()
        Notificacion.objects.all().delete()
        r = client.post('/api/v1/libro-reclamaciones/', {
            'nombre': 'Consumidor',
            'email': 'consumidor@example.com',
            'telefono': '999888777',
            'direccion': 'Jr. Test 123',
            'tipo': 'QUEJA',
            'descripcion': 'Detalle de la queja de prueba con suficiente detalle.',
        }, format='json')
        assert r.status_code == 201, r.data
        notifs = Notificacion.objects.filter(referencia_tipo='RECLAMO')
        assert notifs.count() == 2
        for n in notifs:
            assert '/admin/reclamaciones' in n.url_destino


# ============== Estado de usuario ==============


@pytest.mark.django_db
class TestNotifEstadoUsuario:
    def test_aprobar_usuario_crea_notif_para_usuario_y_admins(
        self, admin_user, otro_admin, comunero_user,
    ):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        Notificacion.objects.all().delete()
        r = client.patch(
            f'/api/v1/usuarios/{comunero_user.id}/',
            {'estado': 'ACTIVO'},
            format='json',
        )
        if r.status_code != 200:
            print('RESPONSE:', r.status_code, r.data)
        assert r.status_code == 200
        # 1 para el usuario, 1 para otro admin
        notifs_usuario = Notificacion.objects.filter(
            destinatario=comunero_user, tipo='aprobacion_cuenta',
        )
        assert notifs_usuario.count() == 1
        notifs_otro_admin = Notificacion.objects.filter(
            destinatario=otro_admin, referencia_tipo='USUARIO',
        )
        assert notifs_otro_admin.count() == 1
        # El admin que hizo la accion NO recibe su propia notif
        notifs_self = Notificacion.objects.filter(
            destinatario=admin_user, referencia_tipo='USUARIO',
            referencia_id=comunero_user.id,
        )
        assert notifs_self.count() == 0

    def test_bloquear_usuario_crea_notif(self, admin_user, comunero_user):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        Notificacion.objects.all().delete()
        r = client.patch(
            f'/api/v1/usuarios/{comunero_user.id}/',
            {'estado': 'BLOQUEADO'},
            format='json',
        )
        assert r.status_code == 200
        assert Notificacion.objects.filter(
            destinatario=comunero_user, tipo='cuenta_bloqueada',
        ).count() == 1

    def test_sin_cambio_estado_no_crea_notif(self, admin_user, comunero_user):
        """Si el estado no cambia, no se crea notificacion."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        Notificacion.objects.all().delete()
        r = client.patch(
            f'/api/v1/usuarios/{comunero_user.id}/',
            {'telefono': '999111222'},
            format='json',
        )
        assert r.status_code == 200
        assert Notificacion.objects.count() == 0


# ============== Noticia / Evento ==============


@pytest.fixture
def admin_activo(db):
    User = get_user_model()
    return User.objects.create_user(
        email='admin@comunidadzapotal.gob.pe',
        password='Admin1234!',
        tipo_usuario='ADMIN',
        estado='ACTIVO',
        is_active=True,
    )


@pytest.fixture
def comunero_activo(db):
    User = get_user_model()
    return User.objects.create_user(
        email='juan@comunidadzapotal.gob.pe',
        password='Juan1234!',
        tipo_usuario='COMUNERO',
        estado='ACTIVO',
        is_active=True,
    )


@pytest.mark.django_db
class TestNotifContenido:
    def test_noticia_publicada_notifica_usuarios(self, admin_activo, comunero_activo):
        from django.test import TestCase
        with TestCase().captureOnCommitCallbacks(execute=True):
            Notificacion.objects.all().delete()
            cat = Categoria.objects.create(nombre='General')
            Noticia.objects.create(
                titulo='Titulo de prueba',
                contenido='Contenido de la noticia de prueba.',
                resumen='Resumen',
                categoria=cat,
                estado='PUBLICADA',
            )
        assert Notificacion.objects.filter(tipo='nueva_noticia').count() >= 2
        notif = Notificacion.objects.filter(tipo='nueva_noticia').first()
        assert '/noticias/' in notif.url_destino
        assert notif.referencia_tipo == 'NOTICIA'

    def test_noticia_borrador_no_notifica(self, admin_activo):
        Notificacion.objects.all().delete()
        cat = Categoria.objects.create(nombre='General2')
        Noticia.objects.create(
            titulo='Borrador',
            contenido='Contenido borrador.',
            categoria=cat,
            estado='BORRADOR',
        )
        assert Notificacion.objects.count() == 0

    def test_evento_creado_notifica_usuarios(self, admin_activo, comunero_activo):
        from datetime import datetime, timezone
        from django.test import TestCase
        with TestCase().captureOnCommitCallbacks(execute=True):
            Notificacion.objects.all().delete()
            Evento.objects.create(
                titulo='Asamblea comunal',
                descripcion='Asamblea general anual.',
                fecha=datetime(2026, 7, 15, 10, 0, tzinfo=timezone.utc),
            )
        assert Notificacion.objects.filter(tipo='nuevo_evento').count() >= 2
        notif = Notificacion.objects.filter(tipo='nuevo_evento').first()
        assert '/eventos/' in notif.url_destino


# ============== Endpoint conteo ==============


@pytest.mark.django_db
class TestNotifConteoEndpoint:
    def test_count_anonimo_retorna_401_o_0(self):
        """Anonimo no esta autenticado, asi que el endpoint retorna 401 (o 200 con 0 si la config lo permite)."""
        client = APIClient()
        r = client.get('/api/v1/notificaciones/no-leidas/count/')
        # IsAuthenticated es estricto: 401 para anonimos
        assert r.status_code == 401

    def test_count_usuario_normal(self, comunero_user):
        Notificacion.objects.create(
            destinatario=comunero_user, titulo='Test', mensaje='X', leido=False,
        )
        Notificacion.objects.create(
            destinatario=comunero_user, titulo='Test2', mensaje='X', leido=True,
        )
        client = APIClient()
        client.force_authenticate(user=comunero_user)
        r = client.get('/api/v1/notificaciones/no-leidas/count/')
        assert r.status_code == 200
        assert r.data == {'count': 1}

    def test_count_admin_ve_solo_las_suyas(self, admin_user, comunero_user):
        """Loop 3.3 (Modelo A): cada admin ve solo SUS notificaciones en el conteo."""
        Notificacion.objects.create(
            destinatario=comunero_user, titulo='T1', mensaje='X', leido=False,
        )
        Notificacion.objects.create(
            destinatario=admin_user, titulo='T2', mensaje='X', leido=False,
        )
        Notificacion.objects.create(
            destinatario=admin_user, titulo='T3', mensaje='X', leido=False,
        )
        client = APIClient()
        client.force_authenticate(user=admin_user)
        r = client.get('/api/v1/notificaciones/no-leidas/count/')
        assert r.status_code == 200
        # El admin ve solo las 2 suyas (no la del comunero)
        assert r.data['count'] == 2
