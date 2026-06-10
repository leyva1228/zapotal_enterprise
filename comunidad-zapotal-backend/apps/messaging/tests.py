from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Mensaje, Notificacion

User = get_user_model()


class MensajeModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com', password='test123',
            dni='11111111', first_name='User', last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com', password='test123',
            dni='22222222', first_name='User', last_name='Two'
        )

    def test_crear_mensaje(self):
        m = Mensaje.objects.create(
            remitente=self.user1, destinatario=self.user2,
            asunto='Hola', cuerpo='Mensaje de prueba'
        )
        self.assertEqual(m.estado, Mensaje.EstadoMensaje.ENVIADO)
        self.assertFalse(m.leido)
        self.assertIsNone(m.fecha_lectura)

    def test_auto_mensaje_rechazado(self):
        m = Mensaje(
            remitente=self.user1, destinatario=self.user1,
            asunto='Test', cuerpo='A mi mismo'
        )
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_cuerpo_vacio(self):
        m = Mensaje(
            remitente=self.user1, destinatario=self.user2,
            asunto='Vacio', cuerpo=''
        )
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_str_representation(self):
        m = Mensaje.objects.create(
            remitente=self.user1, destinatario=self.user2,
            asunto='Saludo', cuerpo='Que tal'
        )
        self.assertIn('Saludo', str(m))


class NotificacionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='notif@test.com', password='test123',
            dni='33333333', first_name='Not', last_name='If'
        )

    def test_crear_notificacion(self):
        n = Notificacion.objects.create(
            usuario=self.user,
            tipo=Notificacion.TipoNotificacion.SISTEMA,
            titulo='Bienvenido', mensaje='Bienvenido al sistema'
        )
        self.assertFalse(n.leido)
        self.assertEqual(str(n), 'Bienvenido - Not If')

    def test_titulo_vacio(self):
        n = Notificacion(
            usuario=self.user,
            tipo=Notificacion.TipoNotificacion.SISTEMA,
            titulo='', mensaje='Algo'
        )
        with self.assertRaises(ValidationError):
            n.full_clean()

    def test_mensaje_vacio(self):
        n = Notificacion(
            usuario=self.user,
            tipo=Notificacion.TipoNotificacion.GENERAL,
            titulo='Titulo', mensaje=''
        )
        with self.assertRaises(ValidationError):
            n.full_clean()


class MessagingAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='a@test.com', password='test123',
            dni='44444444', first_name='A', last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='b@test.com', password='test123',
            dni='55555555', first_name='B', last_name='Two'
        )
        self.mensaje = Mensaje.objects.create(
            remitente=self.user1, destinatario=self.user2,
            asunto='Test', cuerpo='Prueba'
        )

    def test_enviar_mensaje(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/mensajes/', {
            'destinatario': self.user2.id,
            'asunto': 'Nuevo', 'cuerpo': 'Contenido'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_listar_mensajes(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/mensajes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_marcar_mensaje_leido(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/mensajes/{self.mensaje.id}/marcar_leido/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mensaje.refresh_from_db()
        self.assertTrue(self.mensaje.leido)
        self.assertEqual(self.mensaje.estado, Mensaje.EstadoMensaje.LEIDO)

    def test_create_notificacion(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/notificaciones/', {
            'usuario': self.user2.id,
            'tipo': 'SISTEMA',
            'titulo': 'Alerta', 'mensaje': 'Alerta test'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_marcar_notificacion_leido(self):
        n = Notificacion.objects.create(
            usuario=self.user2,
            tipo=Notificacion.TipoNotificacion.GENERAL,
            titulo='T', mensaje='M'
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/notificaciones/{n.id}/marcar_leido/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        n.refresh_from_db()
        self.assertTrue(n.leido)

    def test_marcar_todas_notificaciones_leido(self):
        for i in range(3):
            Notificacion.objects.create(
                usuario=self.user2,
                tipo=Notificacion.TipoNotificacion.GENERAL,
                titulo=f'T{i}', mensaje=f'M{i}'
            )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/notificaciones/marcar_todas_leido/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Notificacion.objects.filter(usuario=self.user2, leido=False).count(), 0
        )

    def test_usuario_no_ve_mensajes_ajenos(self):
        user3 = User.objects.create_user(
            email='c@test.com', password='test123',
            dni='66666666', first_name='C', last_name='Three'
        )
        self.client.force_authenticate(user=user3)
        response = self.client.get(f'/api/mensajes/{self.mensaje.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
