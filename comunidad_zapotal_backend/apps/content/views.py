from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly, IsComuneroOrAdmin
from .models import Noticia, Categoria, Evento, Multimedia, Comentario, Reaccion
from .serializers import (
    NoticiaSerializer, NoticiaEscrituraSerializer, NoticiaRelacionadaSerializer,
    CategoriaSerializer, EventoSerializer, MultimediaSerializer,
    ComentarioSerializer, ReaccionSerializer,
)


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    Categorías de noticias.
    - Lectura pública.
    - Escritura solo ADMIN.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['nombre']
    search_fields = ['nombre', 'descripcion']


class NoticiaViewSet(viewsets.ModelViewSet):
    """
    Noticias de la comunidad.
    - Lectura pública.
    - Escritura solo ADMIN o COMUNERO.
    - Endpoint personalizado: /noticias/{id}/relacionadas/
    """
    queryset = Noticia.objects.select_related('categoria').prefetch_related(
        'multimedia', 'comentarios', 'reacciones'
    )
    serializer_class = NoticiaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['estado', 'categoria', 'fecha_publicacion']
    search_fields = ['titulo', 'contenido', 'resumen']
    ordering_fields = ['fecha_publicacion', 'vistas', 'titulo']
    ordering = ['-fecha_publicacion']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsComuneroOrAdmin()]
        if self.action == 'comentarios':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NoticiaEscrituraSerializer
        if self.action == 'relacionadas':
            return NoticiaRelacionadaSerializer
        return NoticiaSerializer

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def relacionadas(self, request, pk=None):
        noticia = self.get_object()
        if noticia.categoria:
            relacionadas = Noticia.objects.filter(
                categoria=noticia.categoria
            ).exclude(id=noticia.id).order_by('-fecha_publicacion')[:5]
        else:
            relacionadas = Noticia.objects.exclude(id=noticia.id).order_by('-fecha_publicacion')[:5]
        serializer = NoticiaRelacionadaSerializer(relacionadas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def comentarios(self, request, pk=None):
        """Lista los comentarios públicos de una noticia."""
        noticia = self.get_object()
        comentarios = noticia.comentarios.filter(
            estado=Comentario.EstadoComentario.PUBLICADO
        ).order_by('-fecha')
        serializer = ComentarioSerializer(comentarios, many=True, context={'request': request})
        return Response(serializer.data)


class EventoViewSet(viewsets.ModelViewSet):
    """
    Eventos de la comunidad.
    - Lectura pública.
    - Escritura solo ADMIN o COMUNERO.
    """
    queryset = Evento.objects.prefetch_related('multimedia')
    serializer_class = EventoSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['fecha', 'lugar']
    search_fields = ['titulo', 'descripcion', 'lugar']
    ordering_fields = ['fecha', 'titulo']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsComuneroOrAdmin()]
        return super().get_permissions()


class MultimediaViewSet(viewsets.ModelViewSet):
    """
    Archivos multimedia asociados a noticias o eventos.
    - Lectura pública.
    - Escritura solo ADMIN o COMUNERO.
    """
    queryset = Multimedia.objects.select_related('noticia', 'evento')
    serializer_class = MultimediaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['tipo', 'noticia', 'evento']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsComuneroOrAdmin()]
        return super().get_permissions()


class ComentarioViewSet(viewsets.ModelViewSet):
    """
    Comentarios en noticias.
    - Lectura pública (solo PUBLICADO).
    - Crear: usuario autenticado.
    - Editar/eliminar: solo el autor o ADMIN.
    """
    queryset = Comentario.objects.select_related('noticia', 'respuesta_a', 'autor')
    serializer_class = ComentarioSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['noticia', 'estado']
    search_fields = ['contenido', 'autor__email']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and getattr(user, 'tipo_usuario', None) == 'ADMIN':
            return qs
        return qs.filter(estado=Comentario.EstadoComentario.PUBLICADO)

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)


class ReaccionViewSet(viewsets.ModelViewSet):
    """
    Reacciones a noticias (LIKE, DISLIKE, LOVE, ANGRY).
    - Lectura pública.
    - Crear/actualizar: usuario autenticado.
    - Toggle: si ya existe la misma reacción, se elimina; si es diferente, se actualiza.
    """
    queryset = Reaccion.objects.select_related('noticia')
    serializer_class = ReaccionSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['noticia', 'tipo', 'autor']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if self.action == 'list':
                return qs.filter(autor=user)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        """
        Crear o toggle una reacción.

        - Si el usuario ya tiene la misma reacción a la misma noticia, se elimina.
        - Si el usuario tiene una reacción diferente, se actualiza.
        - Si no tiene, se crea.
        """
        noticia_id = request.data.get('noticia')
        tipo = request.data.get('tipo')
        autor = request.user

        existente = Reaccion.objects.filter(noticia_id=noticia_id, autor=autor).first()
        if existente:
            if existente.tipo == tipo:
                existente.delete()
                return Response(
                    {'detail': 'Reacción eliminada.', 'toggled': True},
                    status=status.HTTP_200_OK,
                )
            existente.tipo = tipo
            existente.save()
            serializer = ReaccionSerializer(existente, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = ReaccionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(autor=autor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
