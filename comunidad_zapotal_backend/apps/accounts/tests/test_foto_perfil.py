"""
Tests del upload de foto de perfil.

Cubre el flujo completo:
- PATCH /api/v1/usuarios/<id>/ con FormData (foto_perfil)
- Verifica que el archivo se guarda y se devuelve foto_perfil_url
- Verifica que foto_perfil=null limpia el campo
- Verifica que el storage genera URLs validas (no rutas internas)
- Verifica que un usuario solo puede editar SU propio perfil
"""
import io
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.accounts.models import Usuario, Comunero


def _crear_imagen_png(color=(200, 50, 50), size=(40, 40), nombre='perrito.png'):
    """Genera un PNG valido en memoria como SimpleUploadedFile.
    Usar SimpleUploadedFile (no BytesIO) porque DRF lo necesita para
    detectar el nombre y content-type del archivo en multipart.
    """
    img = Image.new('RGB', size, color)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return SimpleUploadedFile(nombre, buf.read(), content_type='image/png')


@pytest.fixture
def usuario_test(db):
    comunero = Comunero.objects.create(
        dni='12345678',
        nombres='Foto',
        apellidos='Test',
    )
    return Usuario.objects.create_user(
        email='foto@zapotal.pe',
        password='Test1234',
        tipo_usuario='COMUNERO',
        estado='ACTIVO',
        comunero=comunero,
    )


@pytest.fixture
def usuario_otro(db):
    comunero = Comunero.objects.create(
        dni='87654321',
        nombres='Otro',
        apellidos='User',
    )
    return Usuario.objects.create_user(
        email='otro@zapotal.pe',
        password='Test1234',
        tipo_usuario='COMUNERO',
        estado='ACTIVO',
        comunero=comunero,
    )


@pytest.mark.django_db
class TestFotoPerfilUpload:
    """Tests del endpoint PATCH /usuarios/<id>/ con FormData."""

    def _login(self, client, user):
        # Login con JWT (es el flujo que usa el frontend)
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client

    def test_upload_foto_perfil_retorna_url_valida(self, usuario_test):
        client = self._login(APIClient(), usuario_test)
        img = _crear_imagen_png()
        data = {'foto_perfil': ('perrito.png', img, 'image/png')}

        response = client.patch(
            f'/api/v1/usuarios/{usuario_test.id}/',
            data=data,
            format='multipart',
        )

        assert response.status_code == 200, response.content
        body = response.json()
        assert body.get('foto_perfil'), 'foto_perfil no viene en la respuesta'
        assert body.get('foto_perfil_url'), 'foto_perfil_url no viene en la respuesta'

        # La URL NO debe ser una ruta de filesystem local
        url = body['foto_perfil_url']
        assert not url.startswith('/media/'), \
            f'La URL no debe ser una ruta local: {url}'
        assert '://' in url, f'La URL debe ser absoluta: {url}'

    def test_upload_persiste_en_db(self, usuario_test):
        client = self._login(APIClient(), usuario_test)
        img = _crear_imagen_png(color=(50, 200, 50))
        data = {'foto_perfil': ('perrito.png', img, 'image/png')}

        response = client.patch(
            f'/api/v1/usuarios/{usuario_test.id}/',
            data=data,
            format='multipart',
        )
        assert response.status_code == 200

        usuario_test.refresh_from_db()
        assert usuario_test.foto_perfil
        # El nombre se guarda con un sufijo aleatorio de Django
        assert 'perrito' in usuario_test.foto_perfil.name
        assert usuario_test.foto_perfil.storage.exists(usuario_test.foto_perfil.name)

    def test_foto_perfil_null_limpia_campo(self, usuario_test):
        """Cuando el usuario elige 'avatar predeterminado', la API debe aceptar null/'' y limpiar."""
        # Primero subimos una imagen
        usuario_test.foto_perfil.save(
            'vieja.png', _crear_imagen_png(color=(10, 10, 10)), save=True
        )
        assert usuario_test.foto_perfil

        client = self._login(APIClient(), usuario_test)
        response = client.patch(
            f'/api/v1/usuarios/{usuario_test.id}/',
            data={'foto_perfil': ''},
            format='multipart',
        )
        assert response.status_code == 200, response.content

        usuario_test.refresh_from_db()
        # El campo debe estar vacio o None
        assert not usuario_test.foto_perfil, \
            f'foto_perfil no se limpio: {usuario_test.foto_perfil!r}'

    def test_storage_url_no_es_endpoint_s3_interno(self, usuario_test):
        """El storage no debe devolver URLs al endpoint S3 interno (requieren firma)."""
        from apps.core.storage_backends import CloudflareR2Storage
        storage = CloudflareR2Storage()
        url = storage.url('usuarios/perfiles/test.png')
        # Si el storage se inicializo (USE_CLOUDFLARE_R2=True), debe usar
        # el dominio publico. Si no, cae al fallback. En cualquier caso,
        # NO debe ser el endpoint S3 interno a menos que el public domain
        # no este configurado.
        if hasattr(storage, 'bucket_name') and storage.bucket_name:
            from django.conf import settings
            if getattr(settings, 'CLOUDFLARE_R2_PUBLIC_DOMAIN', ''):
                assert 'r2.cloudflarestorage.com' not in url, \
                    f'La URL usa el endpoint S3 interno (requiere firma): {url}'
                assert 'r2.dev' in url or 'cdn.' in url, \
                    f'La URL no usa el dominio publico: {url}'

    def test_usuario_no_puede_editar_otro_perfil(self, usuario_test, usuario_otro):
        """Aislamiento: user A no puede cambiar la foto de user B."""
        client = self._login(APIClient(), usuario_test)
        img = _crear_imagen_png(color=(255, 0, 0))
        data = {'foto_perfil': ('hack.png', img, 'image/png')}

        response = client.patch(
            f'/api/v1/usuarios/{usuario_otro.id}/',
            data=data,
            format='multipart',
        )
        # 403 (PermissionDenied) o 404 (get_object)
        assert response.status_code in (403, 404), \
            f'Se esperaba 403/404, recibio {response.status_code}'

        usuario_otro.refresh_from_db()
        assert not usuario_otro.foto_perfil, 'Foto fue modificada por otro usuario!'

    def test_sin_auth_no_puede_subir(self, usuario_test):
        client = APIClient()
        img = _crear_imagen_png()
        data = {'foto_perfil': ('perrito.png', img, 'image/png')}

        response = client.patch(
            f'/api/v1/usuarios/{usuario_test.id}/',
            data=data,
            format='multipart',
        )
        assert response.status_code == 401, response.content

    def test_get_propio_perfil_funciona_sin_ser_admin(self, usuario_test):
        """Un comunero puede hacer GET de su propio perfil.
        Esto es critico porque Perfil.jsx hace api.get('/usuarios/<id>/')
        al cargar la pagina para obtener datos frescos.
        """
        client = self._login(APIClient(), usuario_test)
        response = client.get(f'/api/v1/usuarios/{usuario_test.id}/')
        assert response.status_code == 200, response.content
        body = response.json()
        assert body['id'] == usuario_test.id
        assert body['email'] == usuario_test.email

    def test_get_otro_usuario_bloqueado(self, usuario_test, usuario_otro):
        """Un comunero NO puede ver el perfil de OTRO usuario."""
        client = self._login(APIClient(), usuario_test)
        response = client.get(f'/api/v1/usuarios/{usuario_otro.id}/')
        # 403 por get_object (PermissionDenied) o 404 si get_object no lo encuentra
        assert response.status_code in (403, 404), \
            f'Se esperaba 403/404, recibio {response.status_code}'

    def test_sin_auth_no_puede_get(self, usuario_test):
        """Sin token, GET /usuarios/<id>/ debe ser 401."""
        client = APIClient()
        response = client.get(f'/api/v1/usuarios/{usuario_test.id}/')
        assert response.status_code == 401, response.content


@pytest.mark.django_db
class TestStorageBackendURL:
    """Tests unitarios del backend CloudflareR2Storage.url()."""

    def test_url_con_public_domain(self, settings):
        settings.CLOUDFLARE_R2_PUBLIC_DOMAIN = 'https://pub-xxx.r2.dev'
        settings.AWS_S3_ENDPOINT_URL = 'https://internal.r2.cloudflarestorage.com'
        settings.AWS_STORAGE_BUCKET_NAME = 'zapotal-storage'

        from apps.core.storage_backends import CloudflareR2Storage
        storage = CloudflareR2Storage()
        url = storage.url('usuarios/perfiles/perrito.png')
        assert url == 'https://pub-xxx.r2.dev/usuarios/perfiles/perrito.png'
        assert 'cloudflarestorage.com' not in url

    def test_url_sin_public_domain_cae_a_s3_endpoint(self, settings):
        settings.CLOUDFLARE_R2_PUBLIC_DOMAIN = ''
        settings.AWS_S3_ENDPOINT_URL = 'https://internal.r2.cloudflarestorage.com'
        settings.AWS_STORAGE_BUCKET_NAME = 'zapotal-storage'

        from apps.core.storage_backends import CloudflareR2Storage
        storage = CloudflareR2Storage()
        url = storage.url('noticias/imagen.jpg')
        assert 'cloudflarestorage.com' in url
        assert 'zapotal-storage' in url
        assert url.endswith('noticias/imagen.jpg')

    def test_url_con_public_domain_sin_protocol(self, settings):
        """Acepta dominio sin https:// y lo agrega."""
        settings.CLOUDFLARE_R2_PUBLIC_DOMAIN = 'pub-xxx.r2.dev'
        from apps.core.storage_backends import CloudflareR2Storage
        storage = CloudflareR2Storage()
        url = storage.url('test.png')
        assert url.startswith('https://')
        assert url.endswith('test.png')

    def test_url_con_public_domain_con_slash_final(self, settings):
        """Limpia slash final del public domain."""
        settings.CLOUDFLARE_R2_PUBLIC_DOMAIN = 'https://pub-xxx.r2.dev/'
        from apps.core.storage_backends import CloudflareR2Storage
        storage = CloudflareR2Storage()
        url = storage.url('test.png')
        # No debe haber doble slash
        assert '//' not in url.replace('https://', ''), f'Doble slash en {url}'
