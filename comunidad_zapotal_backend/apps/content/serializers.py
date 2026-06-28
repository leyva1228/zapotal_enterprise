"""
Serializers para el módulo de contenido.

Incluye campos explícitos (sin `__all__`) y serializa con nested
para recursos relacionados.
"""
from rest_framework import serializers
from .models import (
    Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion,
)


def _resolver_imagen_url(obj, request=None):
    """Devuelve la URL publica de la imagen de un objeto (Noticia/Evento).

    Prioriza `imagen_url` (URL externa, ej. R2/CDN). Si no existe,
    intenta resolver el `ImageField` local usando el `request` para
    construir una URL absoluta. Como ultimo recurso (sin request o si
    el storage backend no esta disponible) devuelve `None` en lugar de
    explotar, para que la respuesta del endpoint nunca quede en 500.
    """
    url_externa = (getattr(obj, "imagen_url", "") or "").strip()
    if url_externa:
        return url_externa
    imagen = getattr(obj, "imagen", None)
    if not imagen:
        return None
    nombre = getattr(imagen, "name", None)
    if not nombre:
        return None
    if request is not None:
        try:
            return request.build_absolute_uri(imagen.url)
        except Exception:
            pass
    try:
        return imagen.url
    except Exception:
        return None


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer de categorías de noticias."""
    total_noticias = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion', 'total_noticias']
        read_only_fields = ['id', 'fecha_creacion', 'total_noticias']

    def get_total_noticias(self, obj):
        return obj.noticias.count()


class MultimediaSerializer(serializers.ModelSerializer):
    """Serializer de archivos multimedia."""
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Multimedia
        # `archivo` (FileField) NO se incluye a proposito: si el storage
        # backend (R2) no esta disponible, DRF intenta resolver
        # `FieldFile.url` y el endpoint entero devuelve 500. El frontend
        # consume `archivo_url` (string URL externa), asi que no perdemos
        # informacion para el cliente.
        fields = [
            'id', 'tipo', 'archivo_url',
            'noticia', 'evento', 'fecha_subida',
        ]
        read_only_fields = ['id', 'fecha_subida', 'archivo_url']

    def get_archivo_url(self, obj):
        request = self.context.get('request')
        url_externa = (getattr(obj, "archivo_url", "") or "").strip() if False else ""
        try:
            archivo = getattr(obj, "archivo", None)
            nombre = getattr(archivo, "name", None) if archivo else None
            if not nombre:
                return None
            if request is not None:
                return request.build_absolute_uri(archivo.url)
            return archivo.url
        except Exception:
            return None


class ComentarioSerializer(serializers.ModelSerializer):
    """Serializer de comentarios."""
    autor_email = serializers.CharField(source='autor.email', read_only=True, default=None)
    autor_nombre = serializers.SerializerMethodField()
    autor_foto = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = [
            'id', 'noticia', 'evento', 'autor', 'autor_email',
            'autor_nombre', 'autor_foto',
            'contenido', 'fecha', 'estado', 'editado', 'respuesta_a',
        ]
        read_only_fields = ['id', 'fecha', 'autor', 'autor_email', 'autor_nombre', 'autor_foto']

    def get_autor_nombre(self, obj):
        if not obj.autor:
            return "Anónimo"
        if hasattr(obj.autor, 'comunero') and obj.autor.comunero:
            return f"{obj.autor.comunero.nombres} {obj.autor.comunero.apellidos}".strip()
        # Para usuarios sin comunero (ADMIN), usar la parte antes del @ del email
        email = obj.autor.email or ""
        return email.split('@')[0].replace('.', ' ').title() or email

    def get_autor_foto(self, obj):
        if not obj.autor or not obj.autor.foto_perfil:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.autor.foto_perfil.url)
        return obj.autor.foto_perfil.url


class ReaccionSerializer(serializers.ModelSerializer):
    """Serializer de reacciones."""
    autor_email = serializers.CharField(source='autor.email', read_only=True, default=None)

    class Meta:
        model = Reaccion
        fields = ['id', 'noticia', 'evento', 'comentario', 'autor', 'autor_email', 'tipo', 'fecha']
        read_only_fields = ['id', 'fecha', 'autor', 'autor_email']

    def validate(self, data):
        """Al menos uno de noticia/evento/comentario debe estar presente."""
        targets = [data.get('noticia'), data.get('evento'), data.get('comentario')]
        if not any(targets):
            raise serializers.ValidationError(
                'Debe especificar noticia, evento o comentario.'
            )
        if sum(1 for t in targets if t) > 1:
            raise serializers.ValidationError(
                'Solo puede especificar un objetivo (noticia, evento o comentario).'
            )
        return data


class NoticiaSerializer(serializers.ModelSerializer):
    """
    Serializer completo de noticia con nested de multimedia, comentarios y reacciones.

    Usado para GET. Para escritura se usa `NoticiaEscrituraSerializer`.
    """
    multimedia = MultimediaSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)
    reacciones = ReaccionSerializer(many=True, read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True, default=None)
    total_reacciones = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Noticia
        # NOTA: `imagen` (ImageField) NO se incluye a proposito: si el
        # storage backend (R2) no esta disponible, DRF intenta resolver
        # `FieldFile.url` y el endpoint entero devuelve 500. El frontend
        # consume `imagen_url` (string URL externa), asi que no perdemos
        # informacion para el cliente.
        fields = [
            'id', 'titulo', 'contenido', 'resumen', 'imagen_url',
            'fecha_publicacion', 'estado', 'vistas', 'categoria',
            'categoria_nombre', 'multimedia', 'comentarios',
            'reacciones', 'total_reacciones',
        ]
        read_only_fields = ['id', 'fecha_publicacion', 'vistas']

    def get_total_reacciones(self, obj):
        from collections import Counter
        return dict(Counter(r.tipo for r in obj.reacciones.all()))

    def get_imagen_url(self, obj):
        return _resolver_imagen_url(obj, self.context.get("request"))


class NoticiaEscrituraSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar noticias (sin nested).

    Devuelve `imagen_url` ademas de `imagen` para que el frontend
    (AdminNoticias.jsx) reciba la URL absoluta del archivo subido
    en la misma respuesta del POST/PATCH y pueda previsualizar
    sin tener que recargar la lista.
    """
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'contenido', 'resumen', 'imagen',
            'imagen_url', 'estado', 'categoria',
        ]
        read_only_fields = ['id']

    def get_imagen_url(self, obj):
        return _resolver_imagen_url(obj, self.context.get("request"))


class EventoEscrituraSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar eventos (sin nested).

    Mismo patron que NoticiaEscrituraSerializer: incluye `imagen_url`
    en la respuesta del POST/PATCH para que el admin panel pueda
    mostrar la URL absoluta de la imagen recien subida.
    """
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'descripcion', 'fecha', 'lugar',
            'imagen', 'imagen_url', 'categoria',
        ]
        read_only_fields = ['id']

    def get_imagen_url(self, obj):
        return _resolver_imagen_url(obj, self.context.get("request"))


class EventoSerializer(serializers.ModelSerializer):
    """Serializer de eventos con nested de multimedia."""
    multimedia = MultimediaSerializer(many=True, read_only=True)
    imagen_url = serializers.SerializerMethodField()
    fecha_evento = serializers.DateTimeField(source='fecha', read_only=True)
    ubicacion = serializers.CharField(source='lugar', read_only=True)
    total_reacciones = serializers.SerializerMethodField()
    total_comentarios = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True, default=None)

    class Meta:
        model = Evento
        # Ver nota en NoticiaSerializer: `imagen` se omite para no
        # depender del storage backend. El frontend usa `imagen_url`.
        fields = [
            'id', 'titulo', 'descripcion', 'fecha', 'fecha_evento',
            'lugar', 'ubicacion', 'imagen_url', 'multimedia',
            'total_reacciones', 'total_comentarios', 'categoria', 'categoria_nombre',
        ]
        read_only_fields = ['id', 'fecha_evento', 'ubicacion', 'total_reacciones', 'total_comentarios', 'categoria_nombre']

    def get_imagen_url(self, obj):
        return _resolver_imagen_url(obj, self.context.get("request"))

    def get_total_reacciones(self, obj):
        from collections import Counter
        return dict(Counter(r.tipo for r in obj.reacciones.all()))

    def get_total_comentarios(self, obj):
        return obj.comentarios.filter(estado='PUBLICADO').count()


class NoticiaRelacionadaSerializer(serializers.ModelSerializer):
    """Serializer minimalista para noticias relacionadas (en endpoint custom)."""
    reacciones = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    categoria = serializers.PrimaryKeyRelatedField(read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True, default=None)

    class Meta:
        model = Noticia
        # NOTA: NO se incluye el campo `imagen` (ImageField) a proposito.
        # Si el storage backend (R2) no esta disponible, DRF intenta
        # resolver `FieldFile.url` y revienta el endpoint entero. Como el
        # frontend consume `imagen_url` (string URL externa), exponer el
        # FileField no aporta valor y rompe la serializacion.
        fields = [
            'id', 'titulo', 'resumen', 'imagen_url',
            'fecha_publicacion', 'estado', 'vistas', 'reacciones',
            'categoria', 'categoria_nombre',
        ]

    def get_reacciones(self, obj):
        from collections import Counter
        return dict(Counter(r.tipo for r in obj.reacciones.all()))

    def get_imagen_url(self, obj):
        return _resolver_imagen_url(obj, self.context.get("request"))


class EventoRelacionadoSerializer(serializers.ModelSerializer):
    """Serializer minimalista para eventos relacionados (en endpoint custom)."""
    imagen_url = serializers.SerializerMethodField()
    fecha_evento = serializers.DateTimeField(source='fecha', read_only=True)
    ubicacion = serializers.CharField(source='lugar', read_only=True)
    categoria = serializers.PrimaryKeyRelatedField(read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True, default=None)

    class Meta:
        model = Evento
        # Ver nota en NoticiaRelacionadaSerializer: omitimos `imagen` para
        # evitar la llamada a `FieldFile.url` que depende del storage backend.
        fields = [
            'id', 'titulo', 'descripcion', 'fecha', 'fecha_evento',
            'lugar', 'ubicacion', 'imagen_url',
            'categoria', 'categoria_nombre',
        ]

    def get_imagen_url(self, obj):
        return _resolver_imagen_url(obj, self.context.get("request"))


class NoticiaRelacionadaAgrupadaSerializer(serializers.Serializer):
    """Agrupa las noticias relacionadas por categoria.

    Shape:
        { "grupos": [ { "categoria": {"id": 1, "nombre": "Cultura"}, "items": [...] } ] }
    Si la noticia base no tiene categoria, se devuelve un unico grupo
    "General" con todas las relacionadas.
    """
    grupos = serializers.ListField(child=serializers.DictField())


class EventoRelacionadoAgrupadoSerializer(serializers.Serializer):
    """Agrupa los eventos relacionados por categoria. Mismo shape que
    `NoticiaRelacionadaAgrupadaSerializer`."""
    grupos = serializers.ListField(child=serializers.DictField())
