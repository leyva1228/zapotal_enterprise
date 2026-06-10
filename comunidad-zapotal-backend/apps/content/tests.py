from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion

User = get_user_model()


class CategoriaModelTests(TestCase):
    def test_crear_categoria(self):
        cat = Categoria.objects.create(
            nombre='Noticias', descripcion='Categoría de noticias'
        )
        self.assertEqual(str(cat), 'Noticias')

    def test_nombre_unico(self):
        Categoria.objects.create(nombre='Unica', descripcion='Test')
        with self.assertRaises(Exception):
            Categoria.objects.create(nombre='Unica', descripcion='Otra')


class NoticiaModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='noticia@test.com', password='test123',
            dni='12345678', first_name='Per', last_name='Son'
        )
        self.cat = Categoria.objects.create(
            nombre='Test Cat', descripcion='Desc'
        )

    def test_crear_noticia(self):
        n = Noticia.objects.create(
            titulo='Titulo Test', contenido='Contenido test',
            categoria=self.cat, usuario=self.user
        )
        self.assertEqual(str(n), 'Titulo Test')
        self.assertEqual(n.estado, Noticia.EstadoNoticia.ACTIVO)

    def test_clean_titulo_vacio(self):
        n = Noticia(
            titulo='', contenido='algo',
            categoria=self.cat, usuario=self.user
        )
        with self.assertRaises(ValidationError):
            n.full_clean()

    def test_clean_contenido_vacio(self):
        n = Noticia(
            titulo='Titulo', contenido='',
            categoria=self.cat, usuario=self.user
        )
        with self.assertRaises(ValidationError):
            n.full_clean()


class EventoModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='evento@test.com', password='test123',
            dni='23456789', first_name='Eve', last_name='Ntus'
        )
        self.cat = Categoria.objects.create(
            nombre='Eventos', descripcion='Cat eventos'
        )

    def test_crear_evento(self):
        from datetime import datetime
        e = Evento.objects.create(
            titulo='Evento Test', descripcion='Desc test',
            categoria=self.cat, usuario=self.user,
            fecha_evento=datetime.now()
        )
        self.assertEqual(str(e), 'Evento Test')


class MultimediaModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='multi@test.com', password='test123',
            dni='34567890', first_name='Mul', last_name='Ti'
        )
        self.cat = Categoria.objects.create(nombre='M', descripcion='D')
        self.noticia = Noticia.objects.create(
            titulo='N', contenido='C',
            categoria=self.cat, usuario=self.user
        )

    def test_multimedia_noticia_asociada(self):
        m = Multimedia(archivo='test.jpg', tipo='IMAGEN', noticia=self.noticia)
        m.full_clean()

    def test_multimedia_sin_referencia(self):
        m = Multimedia(archivo='test.jpg', tipo='IMAGEN')
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_multimedia_doble_referencia(self):
        from datetime import datetime
        evento = Evento.objects.create(
            titulo='E', descripcion='D',
            categoria=self.cat, usuario=self.user,
            fecha_evento=datetime.now()
        )
        m = Multimedia(
            archivo='test.jpg', tipo='IMAGEN',
            noticia=self.noticia, evento=evento
        )
        with self.assertRaises(ValidationError):
            m.full_clean()


class ComentarioModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='com@test.com', password='test123',
            dni='45678901', first_name='Com', last_name='En'
        )
        self.cat = Categoria.objects.create(nombre='C', descripcion='D')
        self.noticia = Noticia.objects.create(
            titulo='N', contenido='C',
            categoria=self.cat, usuario=self.user
        )

    def test_comentario_en_noticia(self):
        c = Comentario(
            contenido='Buen articulo', usuario=self.user,
            noticia=self.noticia
        )
        c.full_clean()
        c.save()
        self.assertEqual(c.contenido, 'Buen articulo')

    def test_comentario_sin_referencia(self):
        c = Comentario(contenido='Hola', usuario=self.user)
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_comentario_vacio(self):
        c = Comentario(
            contenido='', usuario=self.user,
            noticia=self.noticia
        )
        with self.assertRaises(ValidationError):
            c.full_clean()


class ReaccionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reac@test.com', password='test123',
            dni='56789012', first_name='Re', last_name='Ac'
        )
        self.cat = Categoria.objects.create(nombre='R', descripcion='D')
        self.noticia = Noticia.objects.create(
            titulo='N', contenido='C',
            categoria=self.cat, usuario=self.user
        )

    def test_reaccion_like(self):
        r = Reaccion(
            tipo=Reaccion.TipoReaccion.LIKE,
            usuario=self.user, noticia=self.noticia
        )
        r.full_clean()
        r.save()
        self.assertIn('LIKE', str(r))

    def test_reaccion_sin_referencia(self):
        r = Reaccion(
            tipo=Reaccion.TipoReaccion.LOVE,
            usuario=self.user
        )
        with self.assertRaises(ValidationError):
            r.full_clean()


class ContentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='api@test.com', password='test123',
            dni='67890123', first_name='Api', last_name='Test'
        )
        self.cat = Categoria.objects.create(
            nombre='General', descripcion='Cat general'
        )

    def test_listar_categorias(self):
        response = self.client.get('/api/categorias/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_noticia_autenticado(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/noticias/', {
            'titulo': 'Nueva Noticia', 'contenido': 'Contenido noticia',
            'categoria': self.cat.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titulo'], 'Nueva Noticia')

    def test_crear_noticia_anonimo(self):
        response = self.client.post('/api/noticias/', {
            'titulo': 'No Auth', 'contenido': 'No content',
            'categoria': self.cat.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filtrar_noticias_por_estado(self):
        self.client.force_authenticate(user=self.user)
        Noticia.objects.create(
            titulo='Activa', contenido='Contenido',
            categoria=self.cat, usuario=self.user
        )
        response = self.client.get('/api/noticias/?estado=ACTIVO')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_crear_evento(self):
        self.client.force_authenticate(user=self.user)
        from datetime import datetime
        response = self.client.post('/api/eventos/', {
            'titulo': 'Evento Test', 'descripcion': 'Desc',
            'categoria': self.cat.id,
            'fecha_evento': datetime.now().isoformat()
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_crear_comentario_en_noticia(self):
        self.client.force_authenticate(user=self.user)
        n = Noticia.objects.create(
            titulo='Com', contenido='Contenido',
            categoria=self.cat, usuario=self.user
        )
        response = self.client.post('/api/comentarios/', {
            'contenido': 'Mi comentario', 'noticia': n.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_crear_reaccion(self):
        self.client.force_authenticate(user=self.user)
        n = Noticia.objects.create(
            titulo='Reacc', contenido='Contenido',
            categoria=self.cat, usuario=self.user
        )
        response = self.client.post('/api/reacciones/', {
            'tipo': 'LIKE', 'noticia': n.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
