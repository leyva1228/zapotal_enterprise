"""pytest configuration for comunidad_zapotal_backend."""
import os
import django
from pathlib import Path

import pytest


def pytest_configure(config):
    """Configure Django settings for tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
    os.environ.setdefault('DJANGO_DEBUG', 'False')
    os.environ.setdefault('DJANGO_SECRET_KEY', 'test-secret-key-for-testing-only')
    os.environ.setdefault('DB_ENGINE', 'django.db.backends.sqlite3')
    os.environ.setdefault('DB_NAME', ':memory:')

    django.setup()


@pytest.fixture
def api_client():
    """Return a DRF APIClient instance."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    from apps.accounts.models import Usuario
    return Usuario.objects.create_user(
        email='admin@zapotal.pe',
        password='testpass123',
        tipo_usuario='ADMIN',
        estado='ACTIVO',
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def comunero_user(db):
    """Create a comunero user."""
    from apps.accounts.models import Usuario, Comunero
    comunero = Comunero.objects.create(
        dni='12345678',
        nombres='Juan',
        apellidos='Pérez',
    )
    return Usuario.objects.create_user(
        email='juan@zapotal.pe',
        password='testpass123',
        tipo_usuario='COMUNERO',
        estado='ACTIVO',
        comunero=comunero,
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user."""
    from apps.accounts.models import Usuario
    return Usuario.objects.create_user(
        email='user@zapotal.pe',
        password='testpass123',
        tipo_usuario='USUARIO',
        estado='ACTIVO',
    )
