"""
Tests de OTP service.
"""
import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import OTPVerification
from apps.accounts.services import OTPService


def _generar(usuario, tipo=OTPVerification.TipoOTP.REGISTRO, destinatario=None):
    result = OTPService.generar_y_enviar(
        usuario=usuario,
        tipo=tipo,
        destinatario=destinatario or usuario.email,
    )
    return result


@pytest.mark.django_db
class TestOTPService:
    def test_generar_crea_registro(self, regular_user):
        result = _generar(regular_user)
        otp = result['otp']
        assert otp.usuario == regular_user
        assert otp.tipo == OTPVerification.TipoOTP.REGISTRO
        assert otp.usado is False
        assert otp.expira_en > timezone.now()

    def test_verificar_otp_exitoso(self, regular_user):
        result = _generar(regular_user)
        codigo = result['codigo']
        # Verificar el codigo generado
        OTPService.verificar(regular_user, OTPVerification.TipoOTP.REGISTRO, codigo)
        # Segundo intento debe fallar (ya esta usado)
        with pytest.raises(ValidationError):
            OTPService.verificar(regular_user, OTPVerification.TipoOTP.REGISTRO, codigo)

    def test_verificar_otp_incorrecto(self, regular_user):
        _generar(regular_user)
        with pytest.raises(ValidationError):
            OTPService.verificar(
                regular_user, OTPVerification.TipoOTP.REGISTRO, '000000'
            )

    def test_sin_otp_pendiente(self, regular_user):
        with pytest.raises(ValidationError):
            OTPService.verificar(
                regular_user, OTPVerification.TipoOTP.REGISTRO, '123456'
            )

    def test_otp_expirado(self, regular_user):
        result = _generar(regular_user)
        otp = result['otp']
        otp.expira_en = timezone.now() - timedelta(minutes=1)
        otp.save()
        with pytest.raises(ValidationError) as exc:
            OTPService.verificar(
                regular_user, OTPVerification.TipoOTP.REGISTRO, '123456'
            )
        assert 'expirado' in str(exc.value).lower()

    def test_max_intentos(self, regular_user):
        result = _generar(regular_user)
        otp = result['otp']
        otp.intentos = 3
        otp.save()
        with pytest.raises(ValidationError) as exc:
            OTPService.verificar(
                regular_user, OTPVerification.TipoOTP.REGISTRO, '123456'
            )
        assert 'intentos' in str(exc.value).lower()

    def test_invalidar_otp_anterior(self, regular_user):
        result1 = _generar(regular_user)
        otp1 = result1['otp']
        # Forzar que el cooldown de 60s haya expirado
        otp1.creado_en = timezone.now() - timedelta(seconds=120)
        otp1.save()
        result2 = _generar(regular_user)
        otp2 = result2['otp']
        otp1.refresh_from_db()
        assert otp1.usado is True
        assert otp2.usado is False

    def test_generar_devuelve_codigo_en_dev(self, regular_user, settings):
        settings.DEBUG = True
        result = _generar(regular_user)
        assert 'codigo' in result
        assert len(result['codigo']) == 6
        assert result['codigo'].isdigit()
