"""
Tests de AuditLog.
"""
import pytest
from apps.core.models import AuditLog
from apps.core.utils import log_audit_event, sanitize_metadata


@pytest.mark.django_db
class TestAuditLog:
    def test_crear_entrada(self, admin_user):
        entry = log_audit_event(
            accion='LOGIN',
            usuario=admin_user,
            descripcion='Login OK',
        )
        assert AuditLog.objects.filter(accion='LOGIN', usuario=admin_user).count() == 1

    def test_sanitize_quita_passwords(self):
        limpio = sanitize_metadata({
            'email': 'a@b.com',
            'password': 'secreto',
            'token': 'jwt',
            'code': '123',
            'motivo': 'ok',
        })
        assert 'password' not in limpio
        assert 'token' not in limpio
        assert 'code' not in limpio
        assert limpio['email'] == 'a@b.com'
        assert limpio['motivo'] == 'ok'

    def test_sanitize_trunca_valores_largos(self):
        limpio = sanitize_metadata({'x': 'a' * 2000})
        assert len(limpio['x']) < 2000
        assert 'truncated' in limpio['x']
