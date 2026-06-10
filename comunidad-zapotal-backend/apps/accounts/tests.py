from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Usuario

User = get_user_model()


class UsuarioModelTests(TestCase):
    def test_crear_usuario_normal(self):
        user = User.objects.create_user(
            email='test@test.com', password='test123456',
            dni='12345678', first_name='Juan', last_name='Perez'
        )
        self.assertEqual(user.email, 'test@test.com')
        self.assertEqual(user.dni, '12345678')
        self.assertEqual(user.first_name, 'Juan')
        self.assertEqual(user.last_name, 'Perez')
        self.assertEqual(user.tipo_usuario, Usuario.TipoUsuario.USUARIO)
        self.assertFalse(user.dni_verificado)
        self.assertTrue(user.check_password('test123456'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_crear_superusuario(self):
        admin = User.objects.create_superuser(
            email='admin@test.com', password='admin123456',
            dni='87654321', first_name='Admin', last_name='Root'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.tipo_usuario, Usuario.TipoUsuario.ADMIN)

    def test_email_obligatorio(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='test123')

    def test_dni_invalido_rechazado(self):
        with self.assertRaises(ValidationError):
            user = User(
                email='bad@test.com', dni='1234abcd',
                first_name='Bad', last_name='User'
            )
            user.full_clean()

    def test_str_representation(self):
        user = User.objects.create_user(
            email='str@test.com', password='test123',
            dni='11111111', first_name='Carlos', last_name='Lopez'
        )
        self.assertEqual(str(user), 'Carlos Lopez')

    def test_properties(self):
        user = User.objects.create_user(
            email='prop@test.com', password='test123',
            dni='22222222', first_name='Ana', last_name='Maria'
        )
        self.assertEqual(user.nombres, 'Ana')
        self.assertEqual(user.apellidos, 'Maria')
        self.assertIsNotNone(user.fecha_registro)

    def test_email_unico(self):
        User.objects.create_user(
            email='dupe@test.com', password='test123',
            dni='33333333', first_name='A', last_name='B'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='dupe@test.com', password='test456',
                dni='44444444', first_name='C', last_name='D'
            )


class LoginAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='login@test.com', password='password123',
            dni='55555555', first_name='Login', last_name='Test'
        )
        self.login_url = '/api/login/'

    def test_login_exitoso(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com', 'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['ok'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['usuario']['email'], 'login@test.com')

    def test_login_credenciales_incorrectas(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com', 'password': 'wrongpass'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['ok'])

    def test_login_email_inexistente(self):
        response = self.client.post(self.login_url, {
            'email': 'noexiste@test.com', 'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_datos_invalidos(self):
        response = self.client.post(self.login_url, {
            'email': 'no-es-email', 'password': ''
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_jwt_token_valido(self):
        response = self.client.post(self.login_url, {
            'email': 'login@test.com', 'password': 'password123'
        }, format='json')
        access = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        me_response = self.client.get('/api/usuarios/', format='json')
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)


class UsuarioAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='test123456',
            dni='66666666', first_name='User', last_name='Test'
        )
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='admin123',
            dni='77777777', first_name='Admin', last_name='Root'
        )

    def test_listar_usuarios_autenticado(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/usuarios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_listar_usuarios_anonimo(self):
        response = self.client.get('/api/usuarios/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_usuario(self):
        response = self.client.post('/api/usuarios/', {
            'nombres': 'Nuevo', 'apellidos': 'Usuario',
            'email': 'nuevo@test.com', 'password': 'nuevo123',
            'dni': '88888888', 'tipo_usuario': 'COMUNERO'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='nuevo@test.com').exists())

    def test_crear_usuario_sin_password(self):
        response = self.client.post('/api/usuarios/', {
            'nombres': 'No', 'apellidos': 'Pass',
            'email': 'nopass@test.com',
            'dni': '99999999'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ver_detalle_usuario(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/usuarios/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@test.com')

    def test_actualizar_usuario(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/usuarios/{self.user.id}/', {
            'nombres': 'Actualizado'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Actualizado')

    def test_eliminar_usuario(self):
        self.client.force_authenticate(user=self.admin)
        temp = User.objects.create_user(
            email='temp@test.com', password='temp123',
            dni='12121212', first_name='Temp', last_name='User'
        )
        response = self.client.delete(f'/api/usuarios/{temp.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
