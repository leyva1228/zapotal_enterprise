"""Tests del endpoint registro/verificar-otp/ (vista completa)."""
import pytest
from unittest.mock import patch

from apps.accounts.models import (
    Usuario, Comunero, OTPVerification, PendingApproval,
)


@pytest.mark.django_db
class TestRegistroVerificarOtpView:
    """Tests de la vista que verifica el codigo OTP de registro."""

    def _crear_usuario_pendiente(self):
        comunero = Comunero.objects.create(
            dni='12345678',
            nombres='Test',
            apellidos='User',
        )
        usuario = Usuario.objects.create_user(
            email='test@zapotal.pe',
            password='Test1234',
            comunero=comunero,
            estado=Usuario.EstadoUsuario.PENDIENTE_OTP,
        )
        return usuario

    def test_verificar_otp_valido_promueve_usuario_y_crea_pending_approval(self, api_client):
        """Si el codigo es valido, el usuario pasa a PENDIENTE_APROBACION
        y se crea un registro PendingApproval con ip_registro poblado."""
        from rest_framework.test import APIClient
        from apps.accounts.services import OTPService

        usuario = self._crear_usuario_pendiente()
        result = OTPService.generar_y_enviar(usuario, OTPVerification.TipoOTP.REGISTRO)
        codigo = result['codigo']

        client = APIClient()
        client.credentials(HTTP_X_FORWARDED_FOR='192.168.1.100')
        response = client.post(
            '/api/v1/registro/verificar-otp/',
            {'usuario_id': usuario.id, 'codigo': codigo},
            format='json',
        )
        assert response.status_code == 200, response.json()

        usuario.refresh_from_db()
        assert usuario.estado == Usuario.EstadoUsuario.PENDIENTE_APROBACION
        assert usuario.email_verificado is True

        # Verificar que PendingApproval se creo con ip_registro
        pa = PendingApproval.objects.get(usuario=usuario)
        assert pa.ip_registro == '192.168.1.100'
        assert pa.datos_registro['email'] == 'test@zapotal.pe'
        assert pa.datos_registro['dni'] == '12345678'

    def test_verificar_otp_no_promueve_si_codigo_es_incorrecto(self, api_client):
        from rest_framework.test import APIClient
        from apps.accounts.services import OTPService

        usuario = self._crear_usuario_pendiente()
        OTPService.generar_y_enviar(usuario, OTPVerification.TipoOTP.REGISTRO)

        client = APIClient()
        response = client.post(
            '/api/v1/registro/verificar-otp/',
            {'usuario_id': usuario.id, 'codigo': '000000'},
            format='json',
        )
        assert response.status_code == 400
        assert 'incorrecto' in response.json()['detail'].lower()

        usuario.refresh_from_db()
        assert usuario.estado == Usuario.EstadoUsuario.PENDIENTE_OTP  # NO promovido
        assert not PendingApproval.objects.filter(usuario=usuario).exists()

    def test_verificar_otp_no_requiere_autenticacion(self, api_client):
        from rest_framework.test import APIClient
        from apps.accounts.services import OTPService

        usuario = self._crear_usuario_pendiente()
        result = OTPService.generar_y_enviar(usuario, OTPVerification.TipoOTP.REGISTRO)

        client = APIClient()  # sin credenciales
        response = client.post(
            '/api/v1/registro/verificar-otp/',
            {'usuario_id': usuario.id, 'codigo': result['codigo']},
            format='json',
        )
        assert response.status_code == 200
