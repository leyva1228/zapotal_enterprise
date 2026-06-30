from django.db import models
from django.conf import settings
from apps.core.validators import validate_not_empty


class Categoria(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True, validators=[validate_not_empty])
    descripcion = models.TextField('Descripcion', blank=True, default='')
    fecha_creacion = models.DateTimeField('Fecha de creacion', auto_now_add=True)

    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Noticia(models.Model):
    class EstadoNoticia(models.TextChoices):
        PUBLICADA = 'PUBLICADA', 'Publicada'
        BORRADOR = 'BORRADOR', 'Borrador'
        ARCHIVADA = 'ARCHIVADA', 'Archivada'

    titulo = models.CharField('Titulo', max_length=200, validators=[validate_not_empty])
    contenido = models.TextField('Contenido', validators=[validate_not_empty])
    resumen = models.TextField('Resumen', blank=True, default='')
    imagen = models.ImageField('Imagen', upload_to='noticias/', blank=True, null=True)
    imagen_url = models.URLField('URL de imagen externa', max_length=500, blank=True, default='')
    fecha_publicacion = models.DateTimeField('Fecha de publicacion', auto_now_add=True, db_index=True)
    estado = models.CharField(
        'Estado',
        max_length=10,
        choices=EstadoNoticia.choices,
        default=EstadoNoticia.PUBLICADA,
        db_index=True,
    )
    vistas = models.PositiveIntegerField('Vistas', default=0)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Categoria',
        related_name='noticias',
    )

    class Meta:
        db_table = 'noticia'
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo


class Evento(models.Model):
    titulo = models.CharField('Titulo', max_length=200, validators=[validate_not_empty])
    descripcion = models.TextField('Descripcion', blank=True, default='')
    fecha = models.DateTimeField('Fecha del evento', db_index=True)
    lugar = models.CharField('Lugar', max_length=200, blank=True, default='')
    imagen = models.ImageField('Imagen', upload_to='eventos/', blank=True, null=True)
    imagen_url = models.URLField('URL de imagen externa', max_length=500, blank=True, default='')
    vistas = models.PositiveIntegerField('Vistas', default=0)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos',
        verbose_name='Categoria',
    )

    class Meta:
        db_table = 'evento'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo


class Multimedia(models.Model):
    class TipoMultimedia(models.TextChoices):
        IMAGEN = 'IMAGEN', 'Imagen'
        VIDEO = 'VIDEO', 'Video'

    tipo = models.CharField(
        'Tipo',
        max_length=10,
        choices=TipoMultimedia.choices,
        default=TipoMultimedia.IMAGEN,
    )
    archivo = models.FileField('Archivo', upload_to='multimedia/')
    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Noticia',
        related_name='multimedia',
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Evento',
        related_name='multimedia',
    )
    fecha_subida = models.DateTimeField('Fecha de subida', auto_now_add=True)

    class Meta:
        db_table = 'multimedia'
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Multimedias'

    def __str__(self):
        return f'{self.tipo} - {self.archivo.name}'


class Comentario(models.Model):
    class EstadoComentario(models.TextChoices):
        PUBLICADO = 'PUBLICADO', 'Publicado'
        OCULTO = 'OCULTO', 'Oculto'
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ELIMINADO = 'ELIMINADO', 'Eliminado'

    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        verbose_name='Noticia',
        related_name='comentarios',
        null=True,
        blank=True,
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        verbose_name='Evento',
        related_name='comentarios',
        null=True,
        blank=True,
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Autor',
        related_name='comentarios',
    )
    contenido = models.TextField('Contenido')
    fecha = models.DateTimeField('Fecha', auto_now_add=True, db_index=True)
    estado = models.CharField(
        'Estado',
        max_length=10,
        choices=EstadoComentario.choices,
        default=EstadoComentario.PUBLICADO,
    )
    editado = models.BooleanField('Editado', default=False)
    respuesta_a = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Respuesta a',
        related_name='respuestas',
    )

    PALABRAS_PROHIBIDAS = [
        'groseria1', 'groseria2', 'insulto1', 'insulto2',
        'tonto', 'idiota', 'basura', 'malo', 'feo',
    ]

    class Meta:
        db_table = 'comentario'
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['noticia', 'estado']),
        ]

    def __str__(self):
        autor = self.autor.email if self.autor else 'Anónimo'
        if self.noticia:
            return f'{autor} - {self.noticia.titulo}'
        if self.evento:
            return f'{autor} - {self.evento.titulo}'
        return f'{autor} (sin destino #{self.id})'

    def tiene_palabras_prohibidas(self):
        contenido_lower = (self.contenido or '').lower()
        return any(p in contenido_lower for p in self.PALABRAS_PROHIBIDAS)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.tiene_palabras_prohibidas():
            raise ValidationError('El comentario contiene palabras prohibidas.')


class Reaccion(models.Model):
    class TipoReaccion(models.TextChoices):
        LIKE = 'LIKE', 'Like'
        DISLIKE = 'DISLIKE', 'Dislike'

    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        verbose_name='Noticia',
        related_name='reacciones',
        null=True,
        blank=True,
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        verbose_name='Evento',
        related_name='reacciones',
        null=True,
        blank=True,
    )
    comentario = models.ForeignKey(
        'Comentario',
        on_delete=models.CASCADE,
        verbose_name='Comentario',
        related_name='reacciones',
        null=True,
        blank=True,
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Autor',
        related_name='reacciones',
    )
    tipo = models.CharField(
        'Tipo de reaccion',
        max_length=10,
        choices=TipoReaccion.choices,
    )
    fecha = models.DateTimeField('Fecha', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'reaccion'
        verbose_name = 'Reaccion'
        verbose_name_plural = 'Reacciones'
        constraints = [
            models.UniqueConstraint(
                fields=['noticia', 'autor'],
                name='uniq_reaccion_noticia_autor',
                condition=models.Q(noticia__isnull=False),
            ),
            models.UniqueConstraint(
                fields=['evento', 'autor'],
                name='uniq_reaccion_evento_autor',
                condition=models.Q(evento__isnull=False),
            ),
            models.UniqueConstraint(
                fields=['comentario', 'autor'],
                name='uniq_reaccion_comentario_autor',
                condition=models.Q(comentario__isnull=False),
            ),
        ]
        ordering = ['-fecha']

    def __str__(self):
        autor = self.autor.email if self.autor else 'Anónimo'
        destino = self.noticia or self.evento or self.comentario
        destino_label = getattr(destino, 'titulo', None) or getattr(destino, 'id', 'eliminado')
        return f'{autor} - {self.tipo} en {destino_label}'


# =====================================================================
# FAVORITOS
# =====================================================================

class Favorito(models.Model):
    class TipoFavorito(models.TextChoices):
        NOTICIA = 'NOTICIA', 'Noticia'
        EVENTO = 'EVENTO', 'Evento'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoritos',
        verbose_name='Usuario',
    )
    tipo = models.CharField(
        'Tipo',
        max_length=10,
        choices=TipoFavorito.choices,
        db_index=True,
    )
    noticia = models.ForeignKey(
        'content.Noticia',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='favoritos',
        verbose_name='Noticia',
    )
    evento = models.ForeignKey(
        'content.Evento',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='favoritos',
        verbose_name='Evento',
    )
    fecha_agregado = models.DateTimeField('Fecha agregado', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'favorito'
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        ordering = ['-fecha_agregado']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'noticia'],
                name='uniq_favorito_usuario_noticia',
                condition=models.Q(noticia__isnull=False),
            ),
            models.UniqueConstraint(
                fields=['usuario', 'evento'],
                name='uniq_favorito_usuario_evento',
                condition=models.Q(evento__isnull=False),
            ),
        ]

    def __str__(self):
        target = self.noticia_id or self.evento_id
        return f'Favorito({self.usuario_id} -> {self.tipo}#{target})'


# =====================================================================
# SOLICITUDES DE BAJA DE CUENTA
# =====================================================================

class SolicitudBaja(models.Model):
    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADA = 'APROBADA', 'Aprobada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        CANCELADA = 'CANCELADA', 'Cancelada por el usuario'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_baja',
        verbose_name='Usuario',
    )
    motivo = models.TextField('Motivo')
    estado = models.CharField(
        max_length=10,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.PENDIENTE,
        db_index=True,
    )
    fecha_solicitud = models.DateTimeField('Fecha de solicitud', auto_now_add=True, db_index=True)
    fecha_revision = models.DateTimeField('Fecha de revision', null=True, blank=True)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_baja_revisadas',
        verbose_name='Revisado por',
    )
    notas_admin = models.TextField('Notas del administrador', blank=True, default='')

    class Meta:
        db_table = 'solicitud_baja'
        verbose_name = 'Solicitud de baja'
        verbose_name_plural = 'Solicitudes de baja'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'SolicitudBaja({self.usuario_id} - {self.estado})'
