"""
Tests del modelo Donacion.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.accounts.factories import UsuarioFactory
from apps.donaciones.models import Donacion


class DonacionModelTest(TestCase):
    def setUp(self):
        self.usuario = UsuarioFactory()

    def test_crear_donacion_minima(self):
        d = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('1.00'), email_donante=self.usuario.email,
        )
        self.assertEqual(d.monto, Decimal('1.00'))
        self.assertEqual(d.estado, 'PENDIENTE')
        self.assertEqual(d.moneda, 'PEN')
        self.assertFalse(d.anonima)
        self.assertFalse(d.esta_aprobada)

    def test_donacion_anonima_no_muestra_email(self):
        d = Donacion.objects.create(
            monto=Decimal('10.00'),
            nombre_donante='Juan',
            email_donante='juan@x.com',
            anonima=True,
        )
        self.assertEqual(d.nombre_display, 'Anonimo')

    def test_donacion_no_anonima_muestra_nombre(self):
        d = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('10.00'),
        )
        self.assertIn('@', d.nombre_display)

    def test_str_representation(self):
        d = Donacion.objects.create(usuario=self.usuario, monto=Decimal('5.00'))
        s = str(d)
        self.assertIn('S/ 5.00', s)
        self.assertIn('PENDIENTE', s)

    def test_monto_no_puede_ser_cero(self):
        d = Donacion(monto=Decimal('0.00'), email_donante='x@x.com')
        with self.assertRaises(ValidationError):
            d.full_clean()

    def test_donacion_tiene_default_destinatario(self):
        d = Donacion.objects.create(monto=Decimal('5.00'), email_donante='x@x.com')
        self.assertEqual(d.destinatario, 'COMUNIDAD')

    def test_email_display_con_usuario(self):
        d = Donacion.objects.create(usuario=self.usuario, monto=Decimal('5.00'))
        self.assertEqual(d.email_display, self.usuario.email)

    def test_email_display_sin_usuario(self):
        d = Donacion.objects.create(
            monto=Decimal('5.00'), email_donante='visitante@x.com',
        )
        self.assertEqual(d.email_display, 'visitante@x.com')


class MercadoPagoServiceTest(TestCase):
    """Tests del wrapper del SDK de Mercado Pago."""

    def test_get_sdk_sin_access_token_falla(self):
        from django.test import override_settings
        from apps.donaciones.services import MercadoPagoService, MercadoPagoError
        MercadoPagoService.reset_sdk()
        with override_settings(MERCADO_PAGO_ACCESS_TOKEN=''):
            MercadoPagoService.reset_sdk()
            with self.assertRaises(MercadoPagoError):
                MercadoPagoService.get_sdk()

    def test_mapear_estado_mp(self):
        from apps.donaciones.services import MercadoPagoService
        self.assertEqual(MercadoPagoService.mapear_estado_mp('approved'), 'APROBADO')
        self.assertEqual(MercadoPagoService.mapear_estado_mp('in_process'), 'EN_PROCESO')
        self.assertEqual(MercadoPagoService.mapear_estado_mp('pending'), 'EN_PROCESO')
        self.assertEqual(MercadoPagoService.mapear_estado_mp('rejected'), 'RECHAZADO')
        self.assertEqual(MercadoPagoService.mapear_estado_mp('cancelled'), 'CANCELADO')
        self.assertEqual(MercadoPagoService.mapear_estado_mp('refunded'), 'REEMBOLSADO')
        self.assertEqual(MercadoPagoService.mapear_estado_mp('otro'), 'EN_PROCESO')


class IniciarDonacionAPITest(TestCase):
    """Tests del endpoint POST /donaciones/iniciar/ (requiere auth)."""

    def _client_auth(self, usuario):
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        client = APIClient()
        refresh = RefreshToken.for_user(usuario)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client

    def test_iniciar_sin_auth_devuelve_401(self):
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.post('/api/v1/donaciones/iniciar/', {
            'monto': '25.00',
            'mensaje': 'Apoyo a la comunidad',
            'anonima': True,
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_crear_donacion_anonima_con_usuario_logueado(self):
        usuario = UsuarioFactory()
        client = self._client_auth(usuario)
        response = client.post('/api/v1/donaciones/iniciar/', {
            'monto': '25.00',
            'mensaje': 'Apoyo a la comunidad',
            'anonima': True,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('donation_id', data)
        self.assertIn('public_key', data)
        self.assertEqual(data['monto'], '25.00')
        self.assertEqual(data['status'], 'ready_for_brick')

        d = Donacion.objects.get(id=data['donation_id'])
        self.assertEqual(d.estado, 'PENDIENTE')
        self.assertTrue(d.anonima)
        self.assertEqual(d.usuario, usuario)

    def test_crear_donacion_con_usuario_logueado(self):
        usuario = UsuarioFactory()
        client = self._client_auth(usuario)
        response = client.post('/api/v1/donaciones/iniciar/', {
            'monto': '50.00', 'mensaje': 'Obras para la escuela',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        d = Donacion.objects.get(id=response.json()['donation_id'])
        self.assertEqual(d.usuario, usuario)
        self.assertEqual(d.email_donante, usuario.email)
        self.assertFalse(d.anonima)

    def test_monto_menor_al_minimo_rechazado(self):
        usuario = UsuarioFactory()
        client = self._client_auth(usuario)
        response = client.post('/api/v1/donaciones/iniciar/', {
            'monto': '0.50',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_monto_mayor_al_maximo_rechazado(self):
        usuario = UsuarioFactory()
        client = self._client_auth(usuario)
        response = client.post('/api/v1/donaciones/iniciar/', {
            'monto': '10000.00',
        }, format='json')
        self.assertEqual(response.status_code, 400)


class ProcesarPagoAPITest(TestCase):
    """Tests del endpoint POST /donaciones/procesar/ (requiere auth)."""

    def setUp(self):
        from apps.donaciones.services import MercadoPagoService
        MercadoPagoService.reset_sdk()
        self.usuario = UsuarioFactory()

    def _client_auth(self):
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        client = APIClient()
        refresh = RefreshToken.for_user(self.usuario)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client

    def test_procesar_sin_auth_devuelve_401(self):
        from rest_framework.test import APIClient
        donacion = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('25.00'), email_donante=self.usuario.email,
        )
        client = APIClient()
        response = client.post('/api/v1/donaciones/procesar/', {
            'donation_id': donacion.id, 'token': 'fake',
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_procesar_otro_usuario_devuelve_403(self):
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        donacion = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('25.00'), email_donante=self.usuario.email,
        )
        otro = UsuarioFactory()
        client = APIClient()
        refresh = RefreshToken.for_user(otro)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.post('/api/v1/donaciones/procesar/', {
            'donation_id': donacion.id, 'token': 'fake',
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_pago_aprobado_actualiza_donacion(self):
        from unittest.mock import patch
        from apps.donaciones.services import MercadoPagoService

        donacion = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('25.00'), email_donante=self.usuario.email,
        )

        fake_payment = {
            'id': 1234567890,
            'status': 'approved',
            'status_detail': 'accredited',
            'payment_method_id': 'visa',
            'payment_type_id': 'credit_card',
            'installments': 1,
        }
        with patch.object(MercadoPagoService, 'crear_pago', return_value=fake_payment):
            client = self._client_auth()
            response = client.post('/api/v1/donaciones/procesar/', {
                'donation_id': donacion.id,
                'token': 'fake_token_abc',
                'payment_method_id': 'visa',
                'installments': 1,
                'payer': {'email': self.usuario.email, 'identification': {'type': 'DNI', 'number': '12345678'}},
            }, format='json')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'aprobado')
            self.assertEqual(data['mp_payment_id'], 1234567890)

        donacion.refresh_from_db()
        self.assertEqual(donacion.estado, 'APROBADO')
        self.assertEqual(donacion.mp_payment_id, 1234567890)
        self.assertEqual(donacion.mp_payment_method, 'visa')
        self.assertIsNotNone(donacion.aprobado_at)

    def test_pago_rechazado_marca_donacion(self):
        from unittest.mock import patch
        from apps.donaciones.services import MercadoPagoService, MercadoPagoError

        donacion = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('10.00'), email_donante=self.usuario.email,
        )

        with patch.object(MercadoPagoService, 'crear_pago',
                          side_effect=MercadoPagoError('Tarjeta rechazada')):
            client = self._client_auth()
            response = client.post('/api/v1/donaciones/procesar/', {
                'donation_id': donacion.id, 'token': 'fake',
            }, format='json')
            self.assertEqual(response.status_code, 400)

        donacion.refresh_from_db()
        self.assertEqual(donacion.estado, 'RECHAZADO')

    def test_pago_pendiente_queda_en_proceso(self):
        from unittest.mock import patch
        from apps.donaciones.services import MercadoPagoService

        donacion = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('50.00'), email_donante=self.usuario.email,
        )

        fake_payment = {
            'id': 9999, 'status': 'in_process', 'status_detail': 'pending_review',
            'payment_method_id': 'visa', 'payment_type_id': 'credit_card', 'installments': 1,
        }
        with patch.object(MercadoPagoService, 'crear_pago', return_value=fake_payment):
            client = self._client_auth()
            response = client.post('/api/v1/donaciones/procesar/', {
                'donation_id': donacion.id, 'token': 'fake',
            }, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['status'], 'en_proceso')

        donacion.refresh_from_db()
        self.assertEqual(donacion.estado, 'EN_PROCESO')

    def test_donacion_ya_aprobada_no_se_reprocesa(self):
        donacion = Donacion.objects.create(
            usuario=self.usuario, monto=Decimal('10.00'), email_donante=self.usuario.email,
            estado='APROBADO', mp_payment_id=111,
        )
        client = self._client_auth()
        response = client.post('/api/v1/donaciones/procesar/', {
            'donation_id': donacion.id, 'token': 'fake',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('APROBADO', response.json()['detail'])

    def test_donacion_inexistente_404(self):
        client = self._client_auth()
        response = client.post('/api/v1/donaciones/procesar/', {
            'donation_id': 999999, 'token': 'fake',
        }, format='json')
        self.assertEqual(response.status_code, 404)


class WebhookAPITest(TestCase):
    def test_webhook_tipo_invalido_ignora(self):
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.post('/api/v1/donaciones/webhook/', {
            'type': 'plan', 'data': {'id': 1}
        }, format='json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_actualiza_donacion_aprobada(self):
        from unittest.mock import patch
        from rest_framework.test import APIClient
        from apps.donaciones.services import MercadoPagoService

        donacion = Donacion.objects.create(
            monto=Decimal('10.00'), email_donante='x@x.com',
            estado='EN_PROCESO', mp_payment_id=555,
        )

        fake_payment = {
            'id': 555, 'status': 'approved', 'status_detail': 'accredited',
            'payment_method_id': 'master', 'payment_type_id': 'credit_card', 'installments': 1,
        }
        with patch.object(MercadoPagoService, 'obtener_pago', return_value=fake_payment):
            client = APIClient()
            response = client.post('/api/v1/donaciones/webhook/', {
                'type': 'payment', 'data': {'id': 555}
            }, format='json')
            self.assertEqual(response.status_code, 200)

        donacion.refresh_from_db()
        self.assertEqual(donacion.estado, 'APROBADO')
        self.assertEqual(donacion.mp_payment_method, 'master')

    def test_webhook_pago_no_encontrado_ignora(self):
        from unittest.mock import patch
        from rest_framework.test import APIClient
        from apps.donaciones.services import MercadoPagoService, MercadoPagoError

        with patch.object(MercadoPagoService, 'obtener_pago',
                          side_effect=MercadoPagoError('No encontrado')):
            client = APIClient()
            response = client.post('/api/v1/donaciones/webhook/', {
                'type': 'payment', 'data': {'id': 999999}
            }, format='json')
            self.assertEqual(response.status_code, 200)

    def test_webhook_donacion_no_encontrada_ignora(self):
        from unittest.mock import patch
        from rest_framework.test import APIClient
        from apps.donaciones.services import MercadoPagoService

        fake_payment = {'id': 999999, 'status': 'approved', 'status_detail': 'accredited',
                         'payment_method_id': 'visa', 'payment_type_id': 'credit_card', 'installments': 1}
        with patch.object(MercadoPagoService, 'obtener_pago', return_value=fake_payment):
            client = APIClient()
            response = client.post('/api/v1/donaciones/webhook/', {
                'type': 'payment', 'data': {'id': 999999}
            }, format='json')
            self.assertEqual(response.status_code, 200)


class EstadisticasAPITest(TestCase):
    def test_estadisticas_sin_donaciones(self):
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.get('/api/v1/donaciones/estadisticas/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['cantidad_donaciones'], 0)
        self.assertEqual(data['total_recaudado'], '0.00')

    def test_estadisticas_con_donaciones_aprobadas(self):
        from rest_framework.test import APIClient
        Donacion.objects.create(monto=Decimal('10.00'), email_donante='a@x.com', estado='APROBADO')
        Donacion.objects.create(monto=Decimal('25.00'), email_donante='b@x.com', estado='APROBADO')
        Donacion.objects.create(monto=Decimal('5.00'), email_donante='c@x.com', estado='PENDIENTE')
        client = APIClient()
        response = client.get('/api/v1/donaciones/estadisticas/')
        data = response.json()
        self.assertEqual(data['cantidad_donaciones'], 2)
        self.assertEqual(data['total_recaudado'], '35.00')


class MisDonacionesAPITest(TestCase):
    """Tests del endpoint GET /donaciones/mis-donaciones/ (requiere auth)."""

    def test_mis_donaciones_sin_auth_devuelve_401(self):
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.get('/api/v1/donaciones/mis-donaciones/')
        self.assertEqual(response.status_code, 401)

    def test_mis_donaciones_solo_del_usuario_logueado(self):
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        usuario = UsuarioFactory()
        otro = UsuarioFactory()
        Donacion.objects.create(usuario=usuario, monto=Decimal('10.00'), email_donante=usuario.email, estado='APROBADO')
        Donacion.objects.create(usuario=usuario, monto=Decimal('20.00'), email_donante=usuario.email, estado='EN_PROCESO')
        Donacion.objects.create(usuario=otro, monto=Decimal('5.00'), email_donante=otro.email)

        client = APIClient()
        refresh = RefreshToken.for_user(usuario)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.get('/api/v1/donaciones/mis-donaciones/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 2)
        montos = sorted([float(d['monto']) for d in results])
        self.assertEqual(montos, [10.0, 20.0])


class AdminDonacionesAPITest(TestCase):
    def test_lista_donaciones_requiere_admin(self):
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.get('/api/v1/donaciones/admin/lista/')
        self.assertEqual(response.status_code, 401)

    def test_lista_donaciones_como_admin(self):
        from rest_framework.test import APIClient
        admin = UsuarioFactory(is_staff=True, is_superuser=True)
        client = APIClient()
        client.force_authenticate(user=admin)
        Donacion.objects.create(monto=Decimal('10.00'), email_donante='a@x.com')
        response = client.get('/api/v1/donaciones/admin/lista/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_reembolso_solo_donacion_aprobada(self):
        from rest_framework.test import APIClient
        from unittest.mock import patch
        from apps.donaciones.services import MercadoPagoService

        admin = UsuarioFactory(is_staff=True, is_superuser=True)
        d = Donacion.objects.create(
            monto=Decimal('10.00'), email_donante='a@x.com',
            estado='PENDIENTE', mp_payment_id=None,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.post(f'/api/v1/donaciones/admin/{d.id}/reembolsar/')
        self.assertEqual(response.status_code, 400)

    def test_admin_lista_con_filtros_y_paginacion(self):
        from rest_framework.test import APIClient
        admin = UsuarioFactory(is_staff=True, is_superuser=True)
        for i in range(25):
            Donacion.objects.create(
                monto=Decimal('5.00'),
                email_donante=f'user{i}@x.com',
                estado='APROBADO' if i % 2 else 'RECHAZADO',
                destinatario='COMUNIDAD' if i % 3 else 'EMERGENCIA',
            )
        client = APIClient()
        client.force_authenticate(user=admin)

        # Sin filtros: 25, default page_size=20
        r = client.get('/api/v1/donaciones/admin/lista/')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body['count'], 25)
        self.assertEqual(len(body['results']), 20)

        # Filtro estado (i%2=1 => APROBADO, i de 1..23 step 2 = 12 elementos)
        r = client.get('/api/v1/donaciones/admin/lista/?estado=APROBADO')
        body = r.json()
        self.assertEqual(body['count'], 12)

        # Filtro destinatario
        r = client.get('/api/v1/donaciones/admin/lista/?destinatario=EMERGENCIA')
        body = r.json()
        self.assertEqual(body['count'], sum(1 for i in range(25) if i % 3 == 0))

        # Search por email
        r = client.get('/api/v1/donaciones/admin/lista/?search=user5@x.com')
        body = r.json()
        self.assertEqual(body['count'], 1)

        # Paginacion
        r = client.get('/api/v1/donaciones/admin/lista/?page=2&page_size=20')
        body = r.json()
        self.assertEqual(len(body['results']), 5)
        self.assertEqual(body['page'], 2)
        self.assertEqual(body['total_pages'], 2)

    def test_admin_lista_search_por_mp_payment_id(self):
        from rest_framework.test import APIClient
        admin = UsuarioFactory(is_staff=True, is_superuser=True)
        Donacion.objects.create(monto=Decimal('5.00'), email_donante='a@x.com', mp_payment_id=9876543210)
        Donacion.objects.create(monto=Decimal('5.00'), email_donante='b@x.com', mp_payment_id=1234567890)
        client = APIClient()
        client.force_authenticate(user=admin)
        r = client.get('/api/v1/donaciones/admin/lista/?search=9876543')
        self.assertEqual(r.json()['count'], 1)
