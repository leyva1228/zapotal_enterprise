"""Tests del módulo content (noticias, comentarios, reacciones)."""
import pytest


@pytest.mark.django_db
class TestNoticiaViewSet:
    """Tests del ViewSet de noticias."""

    def test_list_noticias_public(self, api_client, admin_user):
        """GET /noticias/ es público."""
        from apps.content.models import Noticia
        Noticia.objects.create(titulo='Test', contenido='Test content')
        response = api_client.get('/api/v1/noticias/')
        assert response.status_code == 200

    def test_create_noticia_requires_auth(self, api_client):
        """POST /noticias/ requiere autenticación."""
        response = api_client.post(
            '/api/v1/noticias/',
            {'titulo': 'Test', 'contenido': 'Test content'},
            format='json',
        )
        assert response.status_code == 401

    def test_relacionadas_endpoint(self, api_client, admin_user):
        """Endpoint /noticias/{id}/relacionadas/ debe ser público."""
        from apps.content.models import Noticia, Categoria
        cat = Categoria.objects.create(nombre='General')
        n1 = Noticia.objects.create(titulo='Noticia 1', contenido='C', categoria=cat)
        Noticia.objects.create(titulo='Noticia 2', contenido='C', categoria=cat)
        response = api_client.get(f'/api/v1/noticias/{n1.id}/relacionadas/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestReaccionToggle:
    """Tests del toggle de reacciones."""

    def test_create_reaccion(self, api_client, regular_user):
        """POST /reacciones/ crea una reacción."""
        from apps.content.models import Noticia
        noticia = Noticia.objects.create(titulo='N', contenido='C')
        api_client.force_authenticate(user=regular_user)
        response = api_client.post(
            '/api/v1/reacciones/',
            {'noticia': noticia.id, 'tipo': 'LIKE'},
            format='json',
        )
        assert response.status_code == 201

    def test_toggle_same_type_deletes(self, api_client, regular_user):
        """POST con mismo tipo elimina la reacción."""
        from apps.content.models import Noticia, Reaccion
        noticia = Noticia.objects.create(titulo='N', contenido='C')
        api_client.force_authenticate(user=regular_user)
        api_client.post(
            '/api/v1/reacciones/',
            {'noticia': noticia.id, 'tipo': 'LIKE'},
            format='json',
        )
        response = api_client.post(
            '/api/v1/reacciones/',
            {'noticia': noticia.id, 'tipo': 'LIKE'},
            format='json',
        )
        assert response.status_code == 200
        assert response.json()['toggled'] is True
        assert Reaccion.objects.count() == 0


@pytest.mark.django_db
class TestComentarioViewSet:
    """Tests del ViewSet de comentarios."""

    def test_list_comentarios_public_filtered(self, api_client, regular_user):
        """GET /comentarios/ solo retorna PUBLICADO a usuarios no-admin."""
        from apps.content.models import Noticia, Comentario
        noticia = Noticia.objects.create(titulo='N', contenido='C')
        Comentario.objects.create(
            noticia=noticia, autor=regular_user, contenido='A',
            estado='PUBLICADO',
        )
        Comentario.objects.create(
            noticia=noticia, autor=regular_user, contenido='B',
            estado='ELIMINADO',
        )
        response = api_client.get('/api/v1/comentarios/')
        assert response.status_code == 200
        results = response.json()['results']
        assert all(c['estado'] == 'PUBLICADO' for c in results)

    def test_comentario_con_palabra_prohibida_rechazado(self, api_client, regular_user):
        """Comentario con palabras prohibidas se envia a moderacion (PENDIENTE)."""
        from apps.content.models import Noticia
        noticia = Noticia.objects.create(titulo='N', contenido='C')
        api_client.force_authenticate(user=regular_user)
        response = api_client.post(
            '/api/v1/comentarios/',
            {'noticia': noticia.id, 'contenido': 'Eres un tonto'},
            format='json',
        )
        assert response.status_code == 201
        assert response.json()['estado'] == 'PENDIENTE'
