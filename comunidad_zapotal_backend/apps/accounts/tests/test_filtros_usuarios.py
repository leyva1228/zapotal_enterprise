"""
Tests para el fix del bug de filtros en AdminUsuarios (LOOP 1).

Cubre:
- Filtro PENDIENTE mapea a PENDIENTE_OTP + PENDIENTE_APROBACION.
- Search por email, nombre, apellido, DNI del comunero.
- Combinacion de filtros (estado + search).
- Paginacion (?page=).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_user(
        email='admin@zapotal.pe', password='Admin1234!',
        tipo_usuario='ADMIN', estado='ACTIVO', is_active=True,
    )


@pytest.fixture
def comunero_user(db):
    User = get_user_model()
    from apps.accounts.models import Comunero
    c = Comunero.objects.create(
        dni='12345678', nombres='Juan', apellidos='Perez', estado='ACTIVO',
    )
    return User.objects.create_user(
        email='juan@zapotal.pe', password='Comunero123!',
        tipo_usuario='COMUNERO', estado='ACTIVO', is_active=True,
        comunero=c,
    )


@pytest.fixture
def usuario_pendiente_otp(db):
    User = get_user_model()
    return User.objects.create_user(
        email='pendiente1@zapotal.pe', password='Test1234!',
        tipo_usuario='COMUNERO', estado='PENDIENTE_OTP', is_active=False,
    )


@pytest.fixture
def usuario_pendiente_aprobacion(db):
    User = get_user_model()
    return User.objects.create_user(
        email='pendiente2@zapotal.pe', password='Test1234!',
        tipo_usuario='COMUNERO', estado='PENDIENTE_APROBACION', is_active=False,
    )


@pytest.fixture
def usuario_bloqueado(db):
    User = get_user_model()
    return User.objects.create_user(
        email='bloqueado@zapotal.pe', password='Test1234!',
        tipo_usuario='COMUNERO', estado='BLOQUEADO', is_active=False,
    )


@pytest.fixture
def usuario_inactivo(db):
    User = get_user_model()
    return User.objects.create_user(
        email='inactivo@zapotal.pe', password='Test1234!',
        tipo_usuario='COMUNERO', estado='INACTIVO', is_active=False,
    )


@pytest.fixture
def usuario_rechazado(db):
    User = get_user_model()
    return User.objects.create_user(
        email='rechazado@zapotal.pe', password='Test1234!',
        tipo_usuario='COMUNERO', estado='RECHAZADO', is_active=False,
    )


@pytest.fixture
def api_client(admin_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    token = RefreshToken.for_user(admin_user).access_token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.mark.django_db
class TestFiltroEstadoPendiente:
    """LOOP 1.1: el magic value 'PENDIENTE' filtra ambos estados pendientes."""

    def test_pendiente_devuelve_otp_y_aprobacion(
        self, api_client,
        usuario_pendiente_otp, usuario_pendiente_aprobacion,
        comunero_user, admin_user, usuario_bloqueado
    ):
        r = api_client.get('/api/v1/usuarios/?estado=PENDIENTE')
        assert r.status_code == 200
        emails = [u['email'] for u in r.json()['results']]
        assert 'pendiente1@zapotal.pe' in emails
        assert 'pendiente2@zapotal.pe' in emails
        # NO debe incluir activos/bloqueados
        assert 'bloqueado@zapotal.pe' not in emails
        assert 'juan@zapotal.pe' not in emails
        assert 'admin@zapotal.pe' not in emails

    def test_pendiente_otp_solo(
        self, api_client,
        usuario_pendiente_otp, usuario_pendiente_aprobacion
    ):
        r = api_client.get('/api/v1/usuarios/?estado=PENDIENTE_OTP')
        assert r.status_code == 200
        emails = [u['email'] for u in r.json()['results']]
        assert 'pendiente1@zapotal.pe' in emails
        assert 'pendiente2@zapotal.pe' not in emails

    def test_pendiente_aprobacion_solo(
        self, api_client,
        usuario_pendiente_otp, usuario_pendiente_aprobacion
    ):
        r = api_client.get('/api/v1/usuarios/?estado=PENDIENTE_APROBACION')
        emails = [u['email'] for u in r.json()['results']]
        assert 'pendiente2@zapotal.pe' in emails
        assert 'pendiente1@zapotal.pe' not in emails

    def test_bloqueado(
        self, api_client, usuario_bloqueado,
        usuario_pendiente_otp, comunero_user
    ):
        r = api_client.get('/api/v1/usuarios/?estado=BLOQUEADO')
        emails = [u['email'] for u in r.json()['results']]
        assert 'bloqueado@zapotal.pe' in emails
        assert 'pendiente1@zapotal.pe' not in emails

    def test_activo(
        self, api_client, comunero_user, admin_user,
        usuario_bloqueado, usuario_pendiente_otp
    ):
        r = api_client.get('/api/v1/usuarios/?estado=ACTIVO')
        emails = [u['email'] for u in r.json()['results']]
        assert 'juan@zapotal.pe' in emails
        assert 'admin@zapotal.pe' in emails
        assert 'bloqueado@zapotal.pe' not in emails


@pytest.mark.django_db
class TestSearchPorNombre:
    """LOOP 1.2: el search incluye email, nombres, apellidos, DNI."""

    def test_search_por_email(self, api_client, comunero_user, admin_user):
        r = api_client.get('/api/v1/usuarios/?search=admin@zapotal')
        emails = [u['email'] for u in r.json()['results']]
        assert 'admin@zapotal.pe' in emails
        assert 'juan@zapotal.pe' not in emails

    def test_search_por_dni(self, api_client, comunero_user):
        # comunero_user fixture ya tiene DNI 12345678.
        r = api_client.get('/api/v1/usuarios/?search=12345678')
        emails = [u['email'] for u in r.json()['results']]
        # juan@zapotal.pe debe estar si tiene DNI
        assert 'juan@zapotal.pe' in emails

    def test_search_sin_match(self, api_client, comunero_user, admin_user):
        r = api_client.get('/api/v1/usuarios/?search=xyzzz_no_existe')
        # Solo devuelve vacio, no error
        assert r.status_code == 200
        assert r.json()['count'] == 0

    def test_search_con_acentos(self, api_client, comunero_user):
        from apps.accounts.models import Comunero
        Comunero.objects.filter(pk=comunero_user.comunero_id).update(
            nombres='María', apellidos='García',
        )
        r = api_client.get('/api/v1/usuarios/?search=Maria')
        # icontains es case-insensitive
        emails = [u['email'] for u in r.json()['results']]
        assert 'juan@zapotal.pe' in emails


@pytest.mark.django_db
class TestCombinacionFiltros:
    """LOOP 1.3: filtros combinables (estado + search + tipo_usuario)."""

    def test_estado_mas_search(
        self, api_client,
        usuario_pendiente_otp, usuario_pendiente_aprobacion,
        admin_user
    ):
        r = api_client.get('/api/v1/usuarios/?estado=PENDIENTE&search=pendiente1')
        emails = [u['email'] for u in r.json()['results']]
        assert 'pendiente1@zapotal.pe' in emails
        assert 'pendiente2@zapotal.pe' not in emails

    def test_tipo_usuario_comunero(
        self, api_client,
        comunero_user, admin_user, usuario_pendiente_otp
    ):
        r = api_client.get('/api/v1/usuarios/?tipo_usuario=COMUNERO')
        emails = [u['email'] for u in r.json()['results']]
        assert 'juan@zapotal.pe' in emails
        assert 'admin@zapotal.pe' not in emails

    def test_tipo_usuario_admin(
        self, api_client,
        comunero_user, admin_user
    ):
        r = api_client.get('/api/v1/usuarios/?tipo_usuario=ADMIN')
        emails = [u['email'] for u in r.json()['results']]
        assert 'admin@zapotal.pe' in emails
        assert 'juan@zapotal.pe' not in emails


@pytest.mark.django_db
class TestPaginacion:
    """LOOP 1.4: paginacion real (?page=)."""

    def test_paginacion_devuelve_count_y_next(
        self, api_client,
        admin_user, comunero_user, usuario_bloqueado, usuario_inactivo,
        usuario_rechazado, usuario_pendiente_otp, usuario_pendiente_aprobacion,
    ):
        r = api_client.get('/api/v1/usuarios/')
        data = r.json()
        assert 'count' in data
        assert 'results' in data
        assert data['count'] == 7  # admin + comunero + 5 estados

    def test_paginacion_page_size_20(self, api_client, admin_user):
        # page_size=20 del StandardPagination.
        r = api_client.get('/api/v1/usuarios/?page_size=20')
        assert len(r.json()['results']) <= 20

    def test_paginacion_page_invalido_retorna_404_o_ultima(
        self, api_client, admin_user
    ):
        # DRF retorna 404 para paginas fuera de rango.
        r = api_client.get('/api/v1/usuarios/?page=9999')
        assert r.status_code in (200, 404)
