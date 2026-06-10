from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Comunero, Autoridad

User = get_user_model()


class ComuneroModelTests(TestCase):
    def test_crear_comunero(self):
        c = Comunero.objects.create(
            nombres='Juan', apellidos='Perez',
            dni='12345678', correo='juan@test.com',
            telefono='987654321'
        )
        self.assertEqual(str(c), 'Juan Perez')
        self.assertEqual(c.estado, Comunero.EstadoComunero.ACTIVO)

    def test_dni_unico(self):
        Comunero.objects.create(
            nombres='A', apellidos='B', dni='11111111'
        )
        with self.assertRaises(Exception):
            Comunero.objects.create(
                nombres='C', apellidos='D', dni='11111111'
            )

    def test_nombres_obligatorios(self):
        c = Comunero(nombres='', apellidos='B', dni='22222222')
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_apellidos_obligatorios(self):
        c = Comunero(nombres='A', apellidos='', dni='33333333')
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_dni_invalido(self):
        c = Comunero(nombres='A', apellidos='B', dni='1234abcd')
        with self.assertRaises(ValidationError):
            c.full_clean()


class AutoridadModelTests(TestCase):
    def setUp(self):
        self.comunero = Comunero.objects.create(
            nombres='Roberto', apellidos='Huaraca',
            dni='87654321'
        )
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='admin123',
            dni='12345678', first_name='Admin', last_name='Root'
        )

    def test_crear_autoridad(self):
        from datetime import date
        a = Autoridad.objects.create(
            comunero=self.comunero,
            cargo=Autoridad.CargoAutoridad.ALCALDE,
            fecha_inicio=date(2025, 1, 1),
            usuario_registra=self.admin
        )
        self.assertIn('Alcalde', str(a))
        self.assertEqual(a.estado, Autoridad.EstadoAutoridad.ACTIVO)

    def test_autoridad_sin_fecha_inicio(self):
        a = Autoridad(
            comunero=self.comunero,
            cargo=Autoridad.CargoAutoridad.REGIDOR,
            usuario_registra=self.admin
        )
        with self.assertRaises(ValidationError):
            a.full_clean()


class ComunidadAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='comapi@test.com', password='test123',
            dni='99887766', first_name='Com', last_name='Api'
        )
        self.comunero = Comunero.objects.create(
            nombres='Maria', apellidos='Lopez',
            dni='11223344'
        )

    def test_listar_comuneros(self):
        response = self.client.get('/api/comuneros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_comunero_autenticado(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/comuneros/', {
            'nombres': 'Nuevo', 'apellidos': 'Comunero',
            'dni': '55667788', 'correo': 'nuevo@test.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_crear_autoridad(self):
        self.client.force_authenticate(user=self.user)
        from datetime import date
        response = self.client.post('/api/autoridades/', {
            'comunero': self.comunero.id,
            'cargo': 'ALCALDE',
            'fecha_inicio': date(2025, 1, 1).isoformat()
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_buscar_comunero_por_dni(self):
        response = self.client.get('/api/comuneros/?search=11223344')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
