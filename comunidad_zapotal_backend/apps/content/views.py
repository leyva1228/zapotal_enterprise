from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly, IsComuneroOrAdmin, IsAdminUser
from .models import Noticia, Categoria, Evento, Multimedia, Comentario, Reaccion
from .serializers import (
    NoticiaSerializer, NoticiaEscrituraSerializer, NoticiaRelacionadaSerializer,
    NoticiaRelacionadaAgrupadaSerializer,
    CategoriaSerializer, EventoSerializer, EventoEscrituraSerializer,
    EventoRelacionadoSerializer, EventoRelacionadoAgrupadoSerializer,
    MultimediaSerializer, ComentarioSerializer, ReaccionSerializer,
)


def _agrupar_por_categoria(items, item_serializer, sin_categoria_label="General", request=None):
    """Agrupa una lista de objetos (Noticia/Evento) por su FK categoria.

    Devuelve un dict con clave `grupos` que contiene la lista
    [{categoria: {id, nombre} | None, items: [...]}, ...].
    Los items sin categoria caen en un unico grupo etiquetado como
    `sin_categoria_label`. Los grupos se ordenan por nombre de categoria;
    el grupo "General" va al final.

    `request` se propaga al sub-serializer para que pueda resolver
    URLs absolutas cuando el `imagen_url` externo no este disponible.
    """
    grupos_map = {}
    fallback_items = []
    for obj in items:
        if obj.categoria_id:
            cid = obj.categoria_id
            grupos_map.setdefault(cid, {"categoria": {"id": cid, "nombre": obj.categoria.nombre}, "items": []})
            grupos_map[cid]["items"].append(obj)
        else:
            fallback_items.append(obj)

    grupos = list(grupos_map.values())
    grupos.sort(key=lambda g: (g["categoria"]["nombre"] or "").lower())

    if fallback_items:
        grupos.append({
            "categoria": None,
            "items": fallback_items,
            "label": sin_categoria_label,
        })

    sub_context = {"request": request} if request is not None else None

    return {
        "grupos": [
            {
                "categoria": g.get("categoria"),
                "label": g.get("label") or (g["categoria"]["nombre"] if g["categoria"] else sin_categoria_label),
                "items": item_serializer(
                    g["items"], many=True, context=sub_context
                ).data,
            }
            for g in grupos
        ]
    }


def _parse_categoria_filtro(request, default_label="General"):
    """Lee el query param `?cat=<id>` (filtro opcional del endpoint
    de relacionadas/relacionados).

    Usamos `cat` (no `categoria`) para NO chocar con
    `filterset_fields = [..., 'categoria', ...]` del viewset: si el
    cliente envia `?categoria=<id>`, el filter backend lo aplicaria
    al queryset base antes de `get_object()` y la entidad base
    dejaria de encontrarse.

    Retorna (categoria_id, categoria_obj|None). Si el parametro no viene
    o no es un entero valido, retorna (None, None) para indicar "sin
    filtro". Esto es seguro contra valores basura (None, '', 'abc', etc).
    """
    raw = request.query_params.get("cat")
    if raw is None or str(raw).strip() == "":
        return None, None
    try:
        cid = int(str(raw).strip())
    except (TypeError, ValueError):
        return None, None
    from .models import Categoria
    cat = Categoria.objects.filter(pk=cid).first()
    if cat is None:
        return cid, None
    return cid, cat


def _filtrar_por_categoria(items, categoria_id):
    """Filtra una lista de objetos (Noticia/Evento) por categoria_id."""
    if categoria_id is None:
        return items
    return [obj for obj in items if obj.categoria_id == categoria_id]


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
            return NoticiaRelacionadaAgrupadaSerializer
        return NoticiaSerializer

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def relacionadas(self, request, pk=None):
        """Devuelve noticias relacionadas agrupadas por categoria.

        Prioridad:
          1. Si la noticia base tiene categoria: traer hasta 5 de esa categoria.
          2. Si la noticia base no tiene categoria: traer las 5 mas recientes.
        Adicionalmente se devuelven hasta 5 mas por cada otra categoria que
          tenga noticias PUBLICADAS, para que la sidebar pueda mostrar multiples
          grupos (incluyendo el de la categoria de la noticia base).

        Query params opcionales:
          - `cat=<id>`: si se envia, limita los resultados a esa
            categoria. Util para endpoints como
            `/noticia/detalle/<id>/relacionadas/?cat=2`.
            NOTA: usamos `cat` y no `categoria` para no chocar con
            `filterset_fields` del viewset.
        """
        noticia = self.get_object()
        base_qs = Noticia.objects.filter(estado=Noticia.EstadoNoticia.PUBLICADA).exclude(id=noticia.id)

        categoria_filtro, _ = _parse_categoria_filtro(request)

        ids_por_categoria = {}
        if noticia.categoria_id:
            mismas = list(
                base_qs.filter(categoria_id=noticia.categoria_id)
                .order_by('-fecha_publicacion')[:5]
            )
            ids_por_categoria[noticia.categoria_id] = mismas

        otras = list(
            base_qs.exclude(categoria_id=noticia.categoria_id)
            .order_by('-fecha_publicacion')[:30]
        )
        for obj in otras:
            if not obj.categoria_id:
                continue
            bucket = ids_por_categoria.setdefault(obj.categoria_id, [])
            if len(bucket) < 3 and obj.id not in {x.id for x in bucket}:
                bucket.append(obj)

        if not ids_por_categoria:
            recientes = list(base_qs.order_by('-fecha_publicacion')[:5])
            recientes = _filtrar_por_categoria(recientes, categoria_filtro)
            payload = {
                "grupos": [
                    {
                        "categoria": None,
                        "label": "General",
                        "items": NoticiaRelacionadaSerializer(
                            recientes, many=True, context={"request": request}
                        ).data,
                    }
                ]
            }
        else:
            objetos = [n for ns in ids_por_categoria.values() for n in ns]
            objetos = _filtrar_por_categoria(objetos, categoria_filtro)
            if not objetos:
                payload = {"grupos": []}
            else:
                payload = _agrupar_por_categoria(
                    objetos, NoticiaRelacionadaSerializer, request=request
                )
        return Response(payload)

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
    - Endpoint personalizado: /eventos/{id}/comentarios/ y /eventos/{id}/relacionados/
    """
    queryset = Evento.objects.select_related('categoria').prefetch_related('multimedia', 'reacciones', 'comentarios')
    serializer_class = EventoSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['fecha', 'lugar', 'categoria']
    search_fields = ['titulo', 'descripcion', 'lugar']
    ordering_fields = ['fecha', 'titulo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventoEscrituraSerializer
        if self.action == 'relacionados':
            return EventoRelacionadoAgrupadoSerializer
        return EventoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsComuneroOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def relacionados(self, request, pk=None):
        """Devuelve eventos relacionados agrupados por categoria.

        Misma logica que `NoticiaViewSet.relacionadas`: prioriza la
        categoria del evento base, y completa con hasta 3 eventos de
        cada otra categoria. Si el evento no tiene categoria, devuelve
        un grupo "General" con los 5 mas recientes.

        Query params opcionales:
          - `cat=<id>`: si se envia, limita los resultados a esa
            categoria. Usamos `cat` y no `categoria` para no chocar con
            `filterset_fields` del viewset.
        """
        evento = self.get_object()
        base_qs = Evento.objects.exclude(id=evento.id)

        categoria_filtro, _ = _parse_categoria_filtro(request)

        ids_por_categoria = {}
        if evento.categoria_id:
            mismos = list(
                base_qs.filter(categoria_id=evento.categoria_id)
                .order_by('-fecha')[:5]
            )
            ids_por_categoria[evento.categoria_id] = mismos

        otros = list(
            base_qs.exclude(categoria_id=evento.categoria_id)
            .order_by('-fecha')[:30]
        )
        for obj in otros:
            if not obj.categoria_id:
                continue
            bucket = ids_por_categoria.setdefault(obj.categoria_id, [])
            if len(bucket) < 3 and obj.id not in {x.id for x in bucket}:
                bucket.append(obj)

        if not ids_por_categoria:
            recientes = list(base_qs.order_by('-fecha')[:5])
            recientes = _filtrar_por_categoria(recientes, categoria_filtro)
            payload = {
                "grupos": [
                    {
                        "categoria": None,
                        "label": "General",
                        "items": EventoRelacionadoSerializer(
                            recientes, many=True, context={"request": request}
                        ).data,
                    }
                ]
            }
        else:
            objetos = [e for es in ids_por_categoria.values() for e in es]
            objetos = _filtrar_por_categoria(objetos, categoria_filtro)
            if not objetos:
                payload = {"grupos": []}
            else:
                payload = _agrupar_por_categoria(
                    objetos, EventoRelacionadoSerializer, request=request
                )
        return Response(payload)

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
