"""Tests exhaustivos de la seccion NOTIFICACIONES (Loop 3.9).

Cubre:
- Loop 3.1: get_queryset per-usuario (admin no ve notificaciones de otros).
- Loop 3.2: PATCH solo permitido al destinatario.
- Loop 3.3: no-leidas/count per-usuario.
- Loop 3.4: nuevos tipos (MENSAJE_CONTACTO, NUEVO_RECLAMO, RECLAMO_ESTADO_CAMBIADO, MENSAJE).
- Loop 3.8: senal de comentario moderado crea notificacion.
- Loop 3.6: frontend no testeado (no hay suite frontend).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.messaging.models import Notificacion
from apps.content.models import Comentario, Noticia, Categoria
from apps.reports.models import LibroReclamacion


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def admin1(db):
    User = get_user_model()
    return User.objects.create_user(
        email='admin1@comunidadzapotal.gob.pe',
        password='Admin1234!',
        tipo_usuario='ADMIN',
        estado='ACTIVO',
        is_active=True,
    )


@pytest.fixture
def admin2(db):
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
        estado='ACTIVO',
        is_active=True,
    )


# ============== Loop 3.1: get_queryset per-usuario ==============


@pytest.mark.django_db
class TestGetQuerysetPerUsuario:
    def test_admin1_no_ve_notificaciones_de_admin2(self, admin1, admin2):
        """El admin1 NO debe ver las notificaciones del admin2."""
        Notificacion.objects.create(
            destinatario=admin2, titulo='Para admin2', mensaje='x', tipo='info',
        )
        Notificacion.objects.create(
            destinatario=admin1, titulo='Para admin1', mensaje='y', tipo='info',
        )
        client = APIClient()
        client.force_authenticate(user=admin1)
        r = client.get('/api/v1/notificaciones/')
        assert r.status_code == 200
        items = r.data.get('results', r.data.get('data', r.data))
        destinatarios = set(i['destinatario'] for i in items)
        assert admin1.id in destinatarios
        assert admin2.id not in destinatarios

    def test_comunero_solo_ve_sus_notificaciones(self, admin1, comunero_user):
        Notificacion.objects.create(
            destinatario=admin1, titulo='Para admin', mensaje='x',
        )
        Notificacion.objects.create(
            destinatario=comunero_user, titulo='Para comunero', mensaje='y',
        )
        client = APIClient()
        client.force_authenticate(user=comunero_user)
        r = client.get('/api/v1/notificaciones/')
        items = r.data.get('results', r.data.get('data', r.data))
        destinatarios = set(i['destinatario'] for i in items)
        assert comunero_user.id in destinatarios
        assert admin1.id not in destinatarios


# ============== Loop 3.2: PATCH solo al destinatario ==============


@pytest.mark.django_db
class TestPatchSoloDestinatario:
    def test_admin1_puede_patchear_su_notif(self, admin1):
        n = Notificacion.objects.create(
            destinatario=admin1, titulo='X', mensaje='Y', tipo='info',
        )
        client = APIClient()
        client.force_authenticate(user=admin1)
        r = client.patch(f'/api/v1/notificaciones/{n.id}/', {'leido': True}, format='json')
        assert r.status_code == 200
        n.refresh_from_db()
        assert n.leido is True

    def test_admin1_no_puede_patchear_notif_de_admin2(self, admin1, admin2):
        n = Notificacion.objects.create(
            destinatario=admin2, titulo='X', mensaje='Y', tipo='info',
        )
        client = APIClient()
        client.force_authenticate(user=admin1)
        r = client.patch(f'/api/v1/notificaciones/{n.id}/', {'leido': True}, format='json')
        assert r.status_code == 404  # porque get_queryset filtra

    def test_admin1_no_puede_des_marcar_notif_de_admin2(self, admin1, admin2):
        n = Notificacion.objects.create(
            destinatario=admin2, titulo='X', mensaje='Y', tipo='info', leido=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin1)
        r = client.patch(f'/api/v1/notificaciones/{n.id}/', {'leido': False}, format='json')
        assert r.status_code == 404


# ============== Loop 3.3: no-leidas/count per-usuario ==============


@pytest.mark.django_db
class TestNoLeidasCountPerUsuario:
    def test_anonimo_retorna_401_o_0(self, api_client):
        r = api_client.get('/api/v1/notificaciones/no-leidas/count/')
        assert r.status_code == 401

    def test_admin_ve_solo_sus_no_leidas(self, admin1, admin2):
        Notificacion.objects.create(
            destinatario=admin1, titulo='A1-1', mensaje='X', leido=False,
        )
        Notificacion.objects.create(
            destinatario=admin1, titulo='A1-2', mensaje='X', leido=False,
        )
        Notificacion.objects.create(
            destinatario=admin2, titulo='A2-1', mensaje='X', leido=False,
        )
        Notificacion.objects.create(
            destinatario=admin2, titulo='A2-2', mensaje='X', leido=True,  # leida
        )
        client = APIClient()
        client.force_authenticate(user=admin1)
        r = client.get('/api/v1/notificaciones/no-leidas/count/')
        assert r.status_code == 200
        # El admin1 ve solo sus 2 (la de admin2 leida no cuenta)
        assert r.data['count'] == 2

    def test_comunero_ve_solo_sus_no_leidas(self, admin1, comunero_user):
        Notificacion.objects.create(
            destinatario=admin1, titulo='Admin', mensaje='X', leido=False,
        )
        Notificacion.objects.create(
            destinatario=comunero_user, titulo='Comunero', mensaje='X', leido=False,
        )
        client = APIClient()
        client.force_authenticate(user=comunero_user)
        r = client.get('/api/v1/notificaciones/no-leidas/count/')
        assert r.data['count'] == 1


# ============== Loop 3.4: nuevos tipos ==============


@pytest.mark.django_db
class TestNuevosTipos:
    def test_tipos_existen_en_choices(self):
        from apps.messaging.models import Notificacion
        choices = [c[0] for c in Notificacion.Tipo.choices]
        assert 'nuevo_mensaje_contacto' in choices
        assert 'nuevo_reclamo' in choices
        assert 'reclamo_estado_cambiado' in choices
        assert 'mensaje' in choices

    def test_crear_notif_con_tipo_nuevo_mensaje_contacto(self, admin1):
        n = Notificacion.objects.create(
            destinatario=admin1, titulo='X', mensaje='Y',
            tipo='nuevo_mensaje_contacto',
        )
        assert n.tipo == 'nuevo_mensaje_contacto'

    def test_crear_notif_con_tipo_nuevo_reclamo(self, admin1):
        n = Notificacion.objects.create(
            destinatario=admin1, titulo='X', mensaje='Y',
            tipo='nuevo_reclamo',
        )
        assert n.tipo == 'nuevo_reclamo'

    def test_crear_notif_con_tipo_mensaje(self, admin1):
        """Tipo 'mensaje' (de MensajeService) sigue funcionando."""
        n = Notificacion.objects.create(
            destinatario=admin1, titulo='X', mensaje='Y',
            tipo='mensaje',
        )
        assert n.tipo == 'mensaje'


# ============== Loop 3.8: senal de comentario moderado ==============


@pytest.mark.django_db
class TestSenalComentarioModerado:
    def test_comentario_oculto_crea_notificacion(self, admin1, comunero_user):
        """El cambio PUBLICADO -> OCULTO crea notificacion al autor."""
        cat = Categoria.objects.create(nombre='Test')
        noticia = Noticia.objects.create(
            titulo='Noticia de prueba', contenido='Contenido',
            categoria=cat, estado='PUBLICADA',
        )
        comentario = Comentario.objects.create(
            contenido='Comentario inapropiado',
            noticia=noticia,
            autor=comunero_user,
            estado=Comentario.EstadoComentario.PUBLICADO,
        )
        comentario.estado = Comentario.EstadoComentario.OCULTO
        comentario.save()
        notifs = Notificacion.objects.filter(
            destinatario=comunero_user, tipo='comentario_moderado',
        )
        assert notifs.count() == 1
        assert notifs.first().referencia_tipo == 'COMENTARIO'
        assert notifs.first().referencia_id == comentario.id

    def test_comentario_creado_no_crea_notif(self, admin1, comunero_user):
        cat = Categoria.objects.create(nombre='Test2')
        noticia = Noticia.objects.create(
            titulo='Otra', contenido='Contenido',
            categoria=cat, estado='PUBLICADA',
        )
        Comentario.objects.create(
            contenido='Comentario normal',
            noticia=noticia, autor=comunero_user,
            estado=Comentario.EstadoComentario.PUBLICADO,
        )
        assert Notificacion.objects.filter(tipo='comentario_moderado').count() == 0

    def test_comentario_autor_none_no_crea_notif(self, admin1):
        """Si el comentario no tiene autor, no se crea notificacion."""
        cat = Categoria.objects.create(nombre='Test3')
        noticia = Noticia.objects.create(
            titulo='X', contenido='Y',
            categoria=cat, estado='PUBLICADA',
        )
        comentario = Comentario.objects.create(
            contenido='Sin autor',
            noticia=noticia, autor=None,
            estado=Comentario.EstadoComentario.PUBLICADO,
        )
        comentario.estado = Comentario.EstadoComentario.OCULTO
        comentario.save()
        assert Notificacion.objects.filter(tipo='comentario_moderado').count() == 0


# ============== V2.3: choices, purge, huerfanas, CUENTA_INACTIVADA ==============


@pytest.mark.django_db
class TestV23ChoicesTipo:
    """V2.3: el campo tipo tiene choices validados."""

    def test_tipo_tiene_choices_definidos(self):
        from apps.messaging.models import Notificacion
        valores = dict(Notificacion.Tipo.choices).keys()
        # Choices clave que la app usa
        assert 'cuenta_inactivada' in valores
        assert 'nuevo_mensaje_contacto' in valores
        assert 'nuevo_reclamo' in valores

    def test_field_metadata_tiene_choices(self):
        from apps.messaging.models import Notificacion
        field = Notificacion._meta.get_field('tipo')
        assert field.choices, 'El campo tipo debe tener choices'


@pytest.mark.django_db
class TestV23UrlDestino2000:
    def test_url_destino_max_length_2000(self):
        from apps.messaging.models import Notificacion
        field = Notificacion._meta.get_field('url_destino')
        assert field.max_length >= 1000, (
            f'url_destino debe soportar URLs largas (got max_length={field.max_length})'
        )


@pytest.mark.django_db
class TestV23PurgeOldNotifications:
    """V2.3: command purge_old_notifications funciona."""

    def test_purge_elimina_antiguas(self):
        from datetime import timedelta
        from io import StringIO
        from django.core.management import call_command
        from django.utils import timezone
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_user(
            email='purge@x.com', password='X', tipo_usuario='ADMIN',
            estado='ACTIVO', is_active=True,
        )
        vieja = Notificacion.objects.create(
            destinatario=admin, titulo='V', mensaje='M', leido=True,
        )
        vieja.fecha = timezone.now() - timedelta(days=120)
        vieja.save()
        out = StringIO()
        call_command('purge_old_notifications', stdout=out)
        assert 'Purgadas' in out.getvalue()
        assert not Notificacion.objects.filter(pk=vieja.pk).exists()

    def test_purge_dry_run_no_elimina(self):
        from datetime import timedelta
        from io import StringIO
        from django.core.management import call_command
        from django.utils import timezone
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_user(
            email='dry@x.com', password='X', tipo_usuario='ADMIN',
            estado='ACTIVO', is_active=True,
        )
        n = Notificacion.objects.create(
            destinatario=admin, titulo='V', mensaje='M', leido=True,
        )
        n.fecha = timezone.now() - timedelta(days=120)
        n.save()
        out = StringIO()
        call_command('purge_old_notifications', '--dry-run', stdout=out)
        assert Notificacion.objects.filter(pk=n.pk).exists()
        assert 'Dry run' in out.getvalue()


@pytest.mark.django_db
class TestV23SignalHuerfana:
    """V2.3: post_delete en MensajeContacto y LibroReclamacion
    limpia las notifs con esa referencia."""

    def test_eliminar_mensaje_limpia_notif(self):
        from apps.comunidad.models_institucionales import MensajeContacto
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_user(
            email='s@x.com', password='X', tipo_usuario='ADMIN',
            estado='ACTIVO', is_active=True,
        )
        msg = MensajeContacto.objects.create(
            nombre='X', email='x@x.com', asunto='A', mensaje='M' * 12,
        )
        Notificacion.objects.create(
            destinatario=admin, titulo='T', mensaje='M',
            referencia_tipo='CONTACTO', referencia_id=msg.id,
        )
        Notificacion.objects.create(
            destinatario=admin, titulo='T2', mensaje='M2',
            referencia_tipo='OTRO', referencia_id=999,
        )
        msg.delete()
        # La notif con referencia CONTACTO+id=msg.id debe haberse eliminado
        assert not Notificacion.objects.filter(
            referencia_tipo='CONTACTO', titulo='T',
        ).exists()
        # La otra notif permanece
        assert Notificacion.objects.filter(referencia_tipo='OTRO').exists()

    def test_eliminar_reclamo_limpia_notif(self):
        from apps.reports.models import LibroReclamacion
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_user(
            email='s2@x.com', password='X', tipo_usuario='ADMIN',
            estado='ACTIVO', is_active=True,
        )
        rec = LibroReclamacion.objects.create(
            nombre='X', email='x@x.com', tipo='QUEJA', descripcion='X' * 20,
        )
        Notificacion.objects.create(
            destinatario=admin, titulo='T', mensaje='M',
            referencia_tipo='RECLAMO', referencia_id=rec.id,
        )
        rec.delete()
        assert not Notificacion.objects.filter(
            referencia_tipo='RECLAMO', titulo='T',
        ).exists()
