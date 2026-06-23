"""Tests del módulo reports (contacto y libro de reclamaciones)."""
import pytest


@pytest.mark.django_db
class TestContactoMensajeViewSet:
    """Tests del ViewSet de mensajes de contacto."""

    def test_create_public(self, api_client):
        """POST /contacto-mensajes/ es público (cualquier visitante)."""
        response = api_client.post(
            '/api/v1/contacto-mensajes/',
            {
                'nombre': 'Visitante',
                'email': 'visitante@example.com',
                'asunto': 'Consulta',
                'mensaje': 'Quisiera más información sobre...',
            },
            format='json',
        )
        assert response.status_code == 201

    def test_list_requires_admin(self, api_client, regular_user):
        """GET /contacto-mensajes/ requiere ser admin."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/v1/contacto-mensajes/')
        assert response.status_code == 403

    def test_list_as_admin_returns_200(self, api_client, admin_user):
        """GET /contacto-mensajes/ como admin retorna 200."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/v1/contacto-mensajes/')
        assert response.status_code == 200

    def test_list_unauthenticated_returns_401(self, api_client):
        """GET /contacto-mensajes/ sin autenticacion retorna 401."""
        response = api_client.get('/api/v1/contacto-mensajes/')
        assert response.status_code == 401

    def test_create_public_still_works(self, api_client):
        """POST /contacto-mensajes/ sigue siendo publico."""
        response = api_client.post(
            '/api/v1/contacto-mensajes/',
            {
                'nombre': 'Otro Visitante',
                'email': 'otro@example.com',
                'asunto': 'Otra consulta',
                'mensaje': 'Otra consulta con suficiente detalle.',
            },
            format='json',
        )
        assert response.status_code == 201


@pytest.mark.django_db
class TestLibroReclamacionViewSet:
    """Tests del libro de reclamaciones (INDECOPI)."""

    def test_create_public(self, api_client):
        """POST /libro-reclamaciones/ es público (Libro de Reclamaciones)."""
        response = api_client.post(
            '/api/v1/libro-reclamaciones/',
            {
                'nombre': 'Consumidor',
                'email': 'consumidor@example.com',
                'telefono': '987654321',
                'direccion': 'Av. Test 123',
                'tipo': 'QUEJA',
                'descripcion': 'Detalle de la queja con suficiente detalle',
            },
            format='json',
        )
        assert response.status_code == 201

    def test_list_requires_admin(self, api_client, regular_user):
        """Solo admin puede listar/ver/editar reclamos."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/v1/libro-reclamaciones/')
        assert response.status_code == 403

    def test_list_as_admin_returns_200(self, api_client, admin_user):
        """GET /libro-reclamaciones/ como admin retorna 200."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/v1/libro-reclamaciones/')
        assert response.status_code == 200

    def test_list_unauthenticated_returns_401(self, api_client):
        """GET /libro-reclamaciones/ sin autenticacion retorna 401."""
        response = api_client.get('/api/v1/libro-reclamaciones/')
        assert response.status_code == 401

    def test_create_public_still_works(self, api_client):
        """POST /libro-reclamaciones/ sigue siendo publico (INDECOPI)."""
        response = api_client.post(
            '/api/v1/libro-reclamaciones/',
            {
                'nombre': 'Otro Consumidor',
                'email': 'otro@example.com',
                'telefono': '987654321',
                'direccion': 'Av. Test 456',
                'tipo': 'QUEJA',
                'descripcion': 'Otra queja con suficiente detalle para validar.',
            },
            format='json',
        )
        assert response.status_code == 201

    def test_retrieve_requires_admin(self, api_client, regular_user, admin_user):
        """GET /libro-reclamaciones/{id}/ requiere admin."""
        from apps.reports.models import LibroReclamacion
        reclamo = LibroReclamacion.objects.create(
            nombre='X', email='x@x.com', tipo='QUEJA', descripcion='Detalle',
        )
        api_client.force_authenticate(user=regular_user)
        response = api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/')
        assert response.status_code == 403

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/v1/libro-reclamaciones/{reclamo.id}/')
        assert response.status_code == 200

    def test_cambiar_estado_only_admin(self, api_client, admin_user, regular_user):
        """Solo admin puede cambiar estado de un reclamo."""
        from apps.reports.models import LibroReclamacion
        reclamo = LibroReclamacion.objects.create(
            nombre='X', email='x@x.com', tipo='QUEJA', descripcion='Detalle',
        )
        # Regular user no puede
        api_client.force_authenticate(user=regular_user)
        response = api_client.post(
            f'/api/v1/libro-reclamaciones/{reclamo.id}/cambiar_estado/',
            {'estado': 'EN_PROCESO'},
            format='json',
        )
        assert response.status_code == 403

        # Admin puede
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            f'/api/v1/libro-reclamaciones/{reclamo.id}/cambiar_estado/',
            {'estado': 'EN_PROCESO'},
            format='json',
        )
        assert response.status_code == 200
        assert response.json()['estado'] == 'EN_PROCESO'
