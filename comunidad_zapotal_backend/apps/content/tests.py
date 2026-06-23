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


@pytest.mark.django_db
class TestModelStrRobustness:
    """El __str__ no debe romper si las FKs son None (comentarios/reacciones huerfanas)."""

    def test_comentario_str_con_noticia(self):
        from apps.content.models import Comentario, Noticia, Categoria
        from django.utils import timezone
        from apps.accounts.factories import UsuarioFactory
        usuario = UsuarioFactory()
        cat = Categoria.objects.create(nombre='Cat', descripcion='x')
        noticia = Noticia.objects.create(
            titulo='Noti', contenido='c', resumen='r',
            categoria=cat, estado='PUBLICADA',
            fecha_publicacion=timezone.now(),
        )
        c = Comentario.objects.create(usuario=usuario, noticia=noticia, contenido='hola')
        s = str(c)
        assert usuario.email in s
        assert 'Noti' in s

    def test_comentario_str_sin_destino_no_crashea(self):
        from apps.content.models import Comentario
        from apps.accounts.factories import UsuarioFactory
        usuario = UsuarioFactory()
        c = Comentario.objects.create(usuario=usuario, contenido='huerfano')
        s = str(c)
        assert usuario.email in s
        assert 'eliminado' in s.lower()

    def test_comentario_str_con_evento(self):
        from apps.content.models import Comentario, Evento
        from django.utils import timezone
        from apps.accounts.factories import UsuarioFactory
        usuario = UsuarioFactory()
        evento = Evento.objects.create(
            titulo='Mi Evento', descripcion='d', lugar='l',
            fecha=timezone.now().date(),
        )
        c = Comentario.objects.create(usuario=usuario, evento=evento, contenido='ok')
        s = str(c)
        assert 'Mi Evento' in s

    def test_reaccion_str_sin_destino_no_crashea(self):
        from apps.content.models import Reaccion
        from apps.accounts.factories import UsuarioFactory
        usuario = UsuarioFactory()
        r = Reaccion.objects.create(usuario=usuario, tipo='LIKE')
        s = str(r)
        assert usuario.email in s
        assert 'LIKE' in s
