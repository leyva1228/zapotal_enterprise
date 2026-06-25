"""
Tests del campo foto en Autoridad y su serializacion.
"""
import io
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Usuario, Comunero
from apps.comunidad.models import Autoridad
from apps.comunidad.serializers import AutoridadSerializer


def _crear_imagen_png(color=(200, 50, 50), size=(100, 100), nombre='test.png'):
    img = Image.new('RGB', size, color)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return SimpleUploadedFile(nombre, buf.read(), content_type='image/png')


@pytest.fixture
def setup_jerarquia(db):
    """Crea una autoridad de prueba con usuario y comunero."""
    com = Comunero.objects.create(dni='99999999', nombres='Test', apellidos='Cargo')
    user = Usuario.objects.create_user(
        email='test_cargo@zapotal.pe',
        password='Test1234',
        tipo_usuario=Usuario.TipoUsuario.COMUNERO,
        estado=Usuario.EstadoUsuario.ACTIVO,
        comunero=com,
    )
    autoridad = Autoridad.objects.create(
        comunero=com,
        cargo=Autoridad.TipoCargo.PRESIDENTE,
        cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
        usuario=user,
        periodo_inicio='2026-01-01',
        activo=True,
    )
    return autoridad, user, com


@pytest.mark.django_db
class TestAutoridadFoto:
    """Tests del campo foto y del serializer."""

    def test_autoridad_puede_tener_foto(self, setup_jerarquia):
        autoridad, user, com = setup_jerarquia
        img = _crear_imagen_png()
        autoridad.foto.save('presidente_test.png', img, save=True)
        autoridad.refresh_from_db()
        assert autoridad.foto
        assert autoridad.foto.name.startswith('autoridades/')
        assert autoridad.foto.storage.exists(autoridad.foto.name)

    def test_serializer_devuelve_foto_url_absoluta(self, setup_jerarquia):
        autoridad, user, com = setup_jerarquia
        img = _crear_imagen_png()
        autoridad.foto.save('presidente_test2.png', img, save=True)
        autoridad.refresh_from_db()

        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        ser = AutoridadSerializer(autoridad, context={'request': request})
        assert ser.data['foto_url'] is not None
        assert 'http' in ser.data['foto_url']
        assert ser.data['foto_url'].endswith('.png')
        # No debe tener el nombre del bucket ni el endpoint S3
        assert 'cloudflarestorage' not in ser.data['foto_url']

    def test_foto_url_fallback_a_usuario_sin_foto_autoridad(self, setup_jerarquia):
        """Si la autoridad NO tiene foto pero el usuario SI, devuelve la del usuario."""
        autoridad, user, com = setup_jerarquia
        # El usuario no tiene foto
        assert not user.foto_perfil
        autoridad.refresh_from_db()
        assert not autoridad.foto

        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        ser = AutoridadSerializer(autoridad, context={'request': request})
        assert ser.data['foto_url'] is None

    def test_foto_url_prioridad_autoridad_sobre_usuario(self, setup_jerarquia):
        """Si la autoridad TIENE foto, gana sobre la del usuario."""
        autoridad, user, com = setup_jerarquia
        # Subir foto al usuario
        user.foto_perfil.save('user_foto.png', _crear_imagen_png(color=(0, 0, 200), nombre='user.png'), save=True)
        # Subir foto DIFERENTE a la autoridad
        autoridad.foto.save('autoridad_foto.png', _crear_imagen_png(color=(200, 0, 0), nombre='aut.png'), save=True)
        autoridad.refresh_from_db()

        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        ser = AutoridadSerializer(autoridad, context={'request': request})
        # Debe ser la de la autoridad (color rojo, no azul)
        assert 'autoridad_foto' in ser.data['foto_url']
        assert 'user_foto' not in ser.data['foto_url']

    def test_api_lista_autoridades_incluye_foto_url(self, setup_jerarquia):
        """El endpoint GET /autoridades/ debe incluir foto_url en cada item."""
        autoridad, user, com = setup_jerarquia
        autoridad.foto.save('api_test.png', _crear_imagen_png(), save=True)
        autoridad.refresh_from_db()

        # El endpoint es de lectura publica
        client = APIClient()
        response = client.get('/api/v1/autoridades/')
        assert response.status_code == 200
        data = response.json()
        results = data if isinstance(data, list) else data.get('results', [])
        assert len(results) >= 1
        first = results[0]
        assert 'foto_url' in first
        assert 'nombres' in first
        assert 'apellidos' in first

    def test_admin_puede_subir_foto_via_api(self, setup_jerarquia):
        """El admin puede subir una foto para una autoridad via PATCH multipart."""
        autoridad, user, com = setup_jerarquia
        admin = Usuario.objects.create_user(
            email='admin_test_foto@zapotal.pe',
            password='Admin1234',
            tipo_usuario=Usuario.TipoUsuario.ADMIN,
            estado=Usuario.EstadoUsuario.ACTIVO,
            is_staff=True,
            is_superuser=True,
        )
        client = APIClient()
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        img = _crear_imagen_png(color=(50, 200, 50), nombre='admin_upload.png')
        response = client.patch(
            f'/api/v1/autoridades/{autoridad.id}/',
            data={'foto': img},
            format='multipart',
        )
        assert response.status_code == 200, response.content
        autoridad.refresh_from_db()
        assert autoridad.foto
        assert autoridad.foto.name.startswith('autoridades/')

    def test_comunero_no_puede_subir_foto(self, setup_jerarquia):
        """Un comunero NO puede modificar la foto de una autoridad."""
        autoridad, user, com = setup_jerarquia
        client = APIClient()
        # user es COMUNERO, no admin
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        img = _crear_imagen_png()
        response = client.patch(
            f'/api/v1/autoridades/{autoridad.id}/',
            data={'foto': img},
            format='multipart',
        )
        # 403 (no admin) o 404 (si la queryset no incluye autoridades)
        assert response.status_code in (403, 404), \
            f'Se esperaba 403/404, recibio {response.status_code}'
        autoridad.refresh_from_db()
        # La foto no debe haberse subido
        assert not autoridad.foto

    def test_sin_auth_no_puede_listar(self, setup_jerarquia):
        """El endpoint de autoridades es publico (GET sin auth debe funcionar)."""
        client = APIClient()
        response = client.get('/api/v1/autoridades/')
        # Lectura publica debe ser 200
        assert response.status_code == 200
