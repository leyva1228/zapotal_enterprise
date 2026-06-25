from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly, IsComuneroOrAdmin, IsAdminUser
from .models import Noticia, Categoria, Evento, Multimedia, Comentario, Reaccion
from .serializers import (
    NoticiaSerializer, NoticiaEscrituraSerializer, NoticiaRelacionadaSerializer,
    CategoriaSerializer, EventoSerializer, EventoEscrituraSerializer,
    MultimediaSerializer, ComentarioSerializer, ReaccionSerializer,
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

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def incrementar_vistas(self, request, pk=None):
        """Incrementa el contador de vistas de forma atomica.

        Usa F('vistas') + 1 para evitar condiciones de carrera.
        Es publico (AllowAny) porque solo registra metricas de lectura.
        """
        Noticia.objects.filter(pk=pk).update(vistas=F('vistas') + 1)
        noticia = Noticia.objects.filter(pk=pk).values('id', 'vistas').first()
        if not noticia:
            return Response({'detail': 'Noticia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'id': noticia['id'], 'vistas': noticia['vistas']}, status=status.HTTP_200_OK)


class EventoViewSet(viewsets.ModelViewSet):
    """
    Eventos de la comunidad.
    - Lectura pública.
    - Escritura solo ADMIN o COMUNERO.
    - Endpoint personalizado: /eventos/{id}/comentarios/
    """
    queryset = Evento.objects.prefetch_related('multimedia', 'reacciones', 'comentarios')
    serializer_class = EventoSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['fecha', 'lugar']
    search_fields = ['titulo', 'descripcion', 'lugar']
    ordering_fields = ['fecha', 'titulo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventoEscrituraSerializer
        return EventoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsComuneroOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def comentarios(self, request, pk=None):
        """Lista los comentarios públicos de un evento."""
        evento = self.get_object()
        comentarios = evento.comentarios.filter(
            estado=Comentario.EstadoComentario.PUBLICADO
        ).order_by('-fecha')
        serializer = ComentarioSerializer(comentarios, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def incrementar_vistas(self, request, pk=None):
        """Incrementa el contador de vistas del evento de forma atomica."""
        Evento.objects.filter(pk=pk).update(vistas=F('vistas') + 1)
        evento = Evento.objects.filter(pk=pk).values('id', 'vistas').first()
        if not evento:
            return Response({'detail': 'Evento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'id': evento['id'], 'vistas': evento['vistas']}, status=status.HTTP_200_OK)


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
    Comentarios en noticias o eventos.
    - Lectura pública (solo PUBLICADO; ADMIN ve también OCULTO/ELIMINADO).
    - Crear: solo COMUNERO o ADMIN activos.
    - Editar/eliminar: solo el autor o ADMIN.
    - Acción especial `cambiar_estado` solo para ADMIN (PUBLICADO/OCULTO/ELIMINADO).
    """
    queryset = Comentario.objects.select_related('noticia', 'evento', 'respuesta_a', 'autor')
    serializer_class = ComentarioSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['noticia', 'evento', 'estado']
    search_fields = ['contenido', 'autor__email']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and getattr(user, 'tipo_usuario', None) == 'ADMIN':
            return qs
        return qs.filter(estado=Comentario.EstadoComentario.PUBLICADO)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsComuneroOrAdmin()]
        if self.action in ['cambiar_estado']:
            return [IsAdminUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        comentario = serializer.save(autor=self.request.user)
        # Moderacion automatica: si el comentario contiene palabras prohibidas,
        # se envia a PENDIENTE en lugar de PUBLICADO para revision administrativa.
        if comentario.tiene_palabras_prohibidas():
            comentario.estado = Comentario.EstadoComentario.PENDIENTE
            comentario.save(update_fields=['estado'])

    def perform_update(self, serializer):
        # Solo el autor del comentario o un ADMIN puede editarlo.
        instance = self.get_object()
        user = self.request.user
        if instance.autor_id != user.id and getattr(user, 'tipo_usuario', None) != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Solo el autor o un administrador pueden editar este comentario.')
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.autor_id != user.id and getattr(user, 'tipo_usuario', None) != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Solo el autor o un administrador pueden eliminar este comentario.')
        instance.delete()

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Solo ADMIN: cambia el estado del comentario (PUBLICADO/OCULTO/ELIMINADO)."""
        comentario = self.get_object()
        nuevo = request.data.get('estado')
        if nuevo not in dict(Comentario.EstadoComentario.choices):
            return Response(
                {'detail': f'Estado inválido. Use uno de: {list(dict(Comentario.EstadoComentario.choices).keys())}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        comentario.estado = nuevo
        comentario.save(update_fields=['estado'])
        return Response(ComentarioSerializer(comentario, context={'request': request}).data)


class ReaccionViewSet(viewsets.ModelViewSet):
    """
    Reacciones (LIKE / DISLIKE) a noticias, eventos o comentarios.
    - Lectura pública.
    - Crear/eliminar: solo COMUNERO o ADMIN activos.
    - Toggle: si ya existe la misma reacción, se elimina; si es diferente, se actualiza.
    """
    queryset = Reaccion.objects.select_related('noticia', 'evento', 'comentario', 'autor')
    serializer_class = ReaccionSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['noticia', 'evento', 'comentario', 'tipo', 'autor']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsComuneroOrAdmin()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        """
        Crear o toggle una reacción.

        - Acepta payload con `noticia` O `evento` O `comentario` (uno es obligatorio).
        - Si el usuario ya tiene la misma reacción al mismo objetivo, se elimina.
        - Si el usuario tiene una reacción diferente al mismo objetivo, se actualiza.
        - Si no tiene, se crea.
        """
        autor = request.user
        noticia_id  = request.data.get('noticia')
        evento_id   = request.data.get('evento')
        comentario_id = request.data.get('comentario')
        tipo = request.data.get('tipo')

        qs = Reaccion.objects.filter(autor=autor)
        if noticia_id:
            qs = qs.filter(noticia_id=noticia_id)
        elif evento_id:
            qs = qs.filter(evento_id=evento_id)
        elif comentario_id:
            qs = qs.filter(comentario_id=comentario_id)
        else:
            return Response(
                {'detail': 'Debe especificar noticia, evento o comentario.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existente = qs.first()
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
