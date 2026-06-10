import logging

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion
from .serializers import (
    CategoriaSerializer, NoticiaSerializer, NoticiaEscrituraSerializer,
    EventoSerializer, EventoEscrituraSerializer, MultimediaSerializer,
    ComentarioSerializer, ReaccionSerializer,
)

logger = logging.getLogger(__name__)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']


class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.select_related('categoria', 'usuario').prefetch_related('multimedia')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'categoria']
    search_fields = ['titulo', 'contenido']
    ordering_fields = ['fecha_publicacion', 'titulo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NoticiaEscrituraSerializer
        return NoticiaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
        logger.info(f'Noticia creada por {self.request.user.email}')


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.select_related('categoria', 'usuario').prefetch_related('multimedia')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'categoria']
    search_fields = ['titulo', 'descripcion']
    ordering_fields = ['fecha_evento', 'titulo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventoEscrituraSerializer
        return EventoSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class MultimediaViewSet(viewsets.ModelViewSet):
    queryset = Multimedia.objects.all()
    serializer_class = MultimediaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo', 'noticia', 'evento']


class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.select_related('usuario', 'noticia', 'evento')
    serializer_class = ComentarioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'noticia', 'evento', 'usuario']
    search_fields = ['contenido']
    ordering_fields = ['fecha']

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ReaccionViewSet(viewsets.ModelViewSet):
    queryset = Reaccion.objects.all()
    serializer_class = ReaccionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'usuario', 'noticia', 'evento']

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
