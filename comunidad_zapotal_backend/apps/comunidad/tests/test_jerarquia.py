"""
Tests de jerarquia administrativa.
"""
import pytest
from datetime import date, timedelta

from apps.accounts.models import Usuario, Comunero
from apps.comunidad.models import Autoridad


@pytest.mark.django_db
class TestJerarquia:
    def _make_comunero(self, dni='11111111'):
        return Comunero.objects.create(
            dni=dni, nombres='Test', apellidos='User',
        )

    def _make_comunero_user(self, dni='11111111', email=None):
        """Crea un usuario COMUNERO con autoridad opcional."""
        com = self._make_comunero(dni)
        user = Usuario.objects.create_user(
            email=email or f'user_{dni}@zapotal.pe',
            password='testpass123',
            tipo_usuario=Usuario.TipoUsuario.COMUNERO,
            estado=Usuario.EstadoUsuario.ACTIVO,
            comunero=com,
        )
        return user, com

    def test_cargo_tipo_presidente_da_es_admin(self):
        user, com = self._make_comunero_user('11111111')
        Autoridad.objects.create(
            comunero=com,
            cargo=Autoridad.TipoCargo.PRESIDENTE,
            cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
            usuario=user,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=365),
            es_admin=True,
            activo=True,
            fecha_inicio=date.today(),
        )
        # Ahora el usuario COMUNERO con autoridad PRESIDENTE vigente es admin
        assert user.es_admin_efectivo

    def test_autoridad_inactiva_no_es_admin(self):
        user, com = self._make_comunero_user('22222222')
        Autoridad.objects.create(
            comunero=com,
            cargo=Autoridad.TipoCargo.PRESIDENTE,
            cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
            usuario=user,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=365),
            es_admin=True,
            activo=False,  # desactivada
            fecha_inicio=date.today(),
        )
        assert not user.es_admin_efectivo

    def test_autoridad_periodo_vencido_no_es_admin(self):
        user, com = self._make_comunero_user('33333333')
        Autoridad.objects.create(
            comunero=com,
            cargo=Autoridad.TipoCargo.PRESIDENTE,
            cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
            usuario=user,
            periodo_inicio=date(2020, 1, 1),
            periodo_fin=date(2021, 1, 1),  # periodo vencido
            es_admin=True,
            activo=True,
            fecha_inicio=date(2020, 1, 1),
        )
        assert not user.es_admin_efectivo

    def test_is_superuser_es_admin(self, admin_user):
        # admin_user es is_superuser=True
        assert admin_user.es_admin_efectivo

    def test_usuario_sin_autoridad_no_es_admin(self, regular_user):
        # Usuario regular sin autoridad
        assert not regular_user.es_admin_efectivo

    def test_mapear_cargo_legacy(self):
        assert Autoridad._mapear_cargo_a_tipo('Presidente de la Comunidad') == Autoridad.TipoCargo.PRESIDENTE
        assert Autoridad._mapear_cargo_a_tipo('Vicepresidenta') == Autoridad.TipoCargo.VICEPRESIDENTE
        assert Autoridad._mapear_cargo_a_tipo('Tesorero') == Autoridad.TipoCargo.TESORERO
        assert Autoridad._mapear_cargo_a_tipo('Secretario de Actas') == Autoridad.TipoCargo.SECRETARIO
        assert Autoridad._mapear_cargo_a_tipo('') == Autoridad.TipoCargo.OTRO
