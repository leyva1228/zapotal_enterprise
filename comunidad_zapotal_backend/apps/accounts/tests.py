"""Tests del módulo de accounts (autenticación y gestión de usuarios)."""
import pytest


@pytest.mark.django_db
class TestLoginEndpoint:
    """Tests del endpoint POST /api/v1/login/"""

    def test_login_success_returns_jwt_tokens(self, api_client, admin_user):
        """Login exitoso debe retornar access y refresh tokens."""
        response = api_client.post(
            '/api/v1/login/',
            {'email': 'admin@zapotal.pe', 'password': 'testpass123'},
            format='json',
        )
        assert response.status_code == 200
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data
        assert 'usuario' in data
        assert data['usuario']['email'] == 'admin@zapotal.pe'

    def test_login_invalid_credentials_returns_400(self, api_client, admin_user):
        """Credenciales inválidas deben retornar 400 sin distinción user/not-user."""
        response = api_client.post(
            '/api/v1/login/',
            {'email': 'admin@zapotal.pe', 'password': 'wrongpassword'},
            format='json',
        )
        assert response.status_code == 400

    def test_login_nonexistent_user_returns_400(self, api_client):
        """Usuario inexistente debe retornar 400 (no user enumeration)."""
        response = api_client.post(
            '/api/v1/login/',
            {'email': 'nobody@zapotal.pe', 'password': 'whatever123'},
            format='json',
        )
        assert response.status_code == 400

    def test_login_inactive_user_returns_403(self, api_client, admin_user):
        """Usuario inactivo debe retornar 403."""
        admin_user.estado = 'INACTIVO'
        admin_user.is_active = False
        admin_user.save()
        response = api_client.post(
            '/api/v1/login/',
            {'email': 'admin@zapotal.pe', 'password': 'testpass123'},
            format='json',
        )
        assert response.status_code == 403

    def test_login_short_password_rejected(self, api_client):
        """Contraseña corta debe ser rechazada por el serializer."""
        response = api_client.post(
            '/api/v1/login/',
            {'email': 'admin@zapotal.pe', 'password': '123'},
            format='json',
        )
        assert response.status_code == 400

    def test_password_not_exposed_in_user_serializer(self, api_client, admin_user):
        """El campo password no debe estar en respuestas GET."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/v1/usuarios/')
        assert response.status_code == 200
        results = response.json()['results']
        for user in results:
            assert 'password' not in user


@pytest.mark.django_db
class TestUsuarioService:
    """Tests del service layer de accounts."""

    def test_create_user(self):
        from apps.accounts.services import UsuarioService
        user = UsuarioService.create_user_with_comunero(
            email='nuevo@zapotal.pe',
            password='pass1234',
            tipo_usuario='ADMIN',
        )
        assert user.email == 'nuevo@zapotal.pe'
        assert user.tipo_usuario == 'ADMIN'
        assert user.check_password('pass1234')

    def test_create_comunero_requires_comunero_data(self):
        from apps.accounts.services import UsuarioService
        with pytest.raises(ValueError):
            UsuarioService.create_user_with_comunero(
                email='nuevo2@zapotal.pe',
                password='pass1234',
                tipo_usuario='COMUNERO',
                comunero_data=None,
            )

    def test_change_password(self, admin_user):
        from apps.accounts.services import UsuarioService
        UsuarioService.change_password(admin_user, 'newpass1234')
        assert admin_user.check_password('newpass1234')

    def test_activate_deactivate(self, admin_user):
        from apps.accounts.services import UsuarioService
        UsuarioService.deactivate(admin_user)
        assert admin_user.estado == 'INACTIVO'
        assert admin_user.is_active is False
        UsuarioService.activate(admin_user)
        assert admin_user.estado == 'ACTIVO'
        assert admin_user.is_active is True
