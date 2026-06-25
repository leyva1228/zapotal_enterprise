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
        assert 'expir' in str(exc.value).lower()

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

    def test_otp_anterior_no_se_invalida_al_generar_nuevo(self, regular_user):
        """Antes se invalidaban todos los OTPs al generar uno nuevo (causaba race
        condition con emails lentos). Ahora el anterior permanece valido hasta
        que el usuario lo use o expire solo."""
        result1 = _generar(regular_user)
        otp1 = result1['otp']
        # Forzar que el cooldown de 60s haya expirado
        otp1.creado_en = timezone.now() - timedelta(seconds=120)
        otp1.save()
        result2 = _generar(regular_user)
        otp2 = result2['otp']
        otp1.refresh_from_db()
        # El primero NO se marca como usado al generar el segundo
        assert otp1.usado is False
        # El segundo es el unico nuevo y activo
        assert otp2.usado is False
        # Ambos coexisten hasta que uno se use o expire
        assert otp1.id != otp2.id

    def test_codigo_de_otp_anterior_tambien_valida(self, regular_user):
        """Si el usuario tiene multiples OTPs (race condition de email lento),
        puede usar CUALQUIERA de los codigos recibidos, no solo el ultimo."""
        result1 = _generar(regular_user)
        codigo1 = result1['codigo']
        # Forzar cooldown expirado
        result1['otp'].creado_en = timezone.now() - timedelta(seconds=120)
        result1['otp'].save()
        result2 = _generar(regular_user)
        codigo2 = result2['codigo']

        # Verificar con el codigo del primer OTP (mas viejo)
        assert OTPService.verificar(regular_user, OTPVerification.TipoOTP.REGISTRO, codigo1) is True

        # El segundo OTP ya debe estar marcado como usado (cascade al verificar)
        result2['otp'].refresh_from_db()
        assert result2['otp'].usado is True

    def test_codigo_incorrecto_no_consume_otros_otps(self, regular_user):
        """Si el codigo es incorrecto, solo incrementa intentos del mas reciente.
        Los demas OTPs siguen siendo usables."""
        result1 = _generar(regular_user)
        result1['otp'].creado_en = timezone.now() - timedelta(seconds=120)
        result1['otp'].save()
        result2 = _generar(regular_user)
        codigo2 = result2['codigo']

        # 1 intento fallido
        with pytest.raises(ValidationError) as exc:
            OTPService.verificar(regular_user, OTPVerification.TipoOTP.REGISTRO, '000000')
        assert 'incorrecto' in str(exc.value).lower()

        # El OTP 1 sigue valido y sin intentos incrementados
        result1['otp'].refresh_from_db()
        assert result1['otp'].intentos == 0
        assert result1['otp'].usado is False

        # Pero el codigo 2 aun funciona
        assert OTPService.verificar(regular_user, OTPVerification.TipoOTP.REGISTRO, codigo2) is True

    def test_generar_devuelve_codigo_en_dev(self, regular_user, settings):
        settings.DEBUG = True
        result = _generar(regular_user)
        assert 'codigo' in result
        assert len(result['codigo']) == 6
        assert result['codigo'].isdigit()
