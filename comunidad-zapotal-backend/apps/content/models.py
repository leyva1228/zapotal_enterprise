from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')

    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Noticia(models.Model):
    class EstadoNoticia(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    titulo = models.CharField(max_length=200, verbose_name='Título')
    contenido = models.TextField(verbose_name='Contenido')
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE,
        related_name='noticias', verbose_name='Categoría'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='noticias', verbose_name='Usuario responsable'
    )
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')
    estado = models.CharField(
        max_length=10, choices=EstadoNoticia.choices,
        default=EstadoNoticia.ACTIVO, verbose_name='Estado'
    )

    class Meta:
        db_table = 'noticia'
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'
        ordering = ['-fecha_publicacion']
        indexes = [
            models.Index(fields=['estado', '-fecha_publicacion']),
            models.Index(fields=['categoria', 'estado']),
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if not self.titulo or not self.titulo.strip():
            raise ValidationError({'titulo': 'El título no puede estar vacío.'})
        if not self.contenido or not self.contenido.strip():
            raise ValidationError({'contenido': 'El contenido no puede estar vacío.'})


class Evento(models.Model):
    class EstadoEvento(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE,
        related_name='eventos', verbose_name='Categoría'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='eventos', verbose_name='Usuario responsable'
    )
    fecha_evento = models.DateTimeField(verbose_name='Fecha del evento')
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')
    estado = models.CharField(
        max_length=10, choices=EstadoEvento.choices,
        default=EstadoEvento.ACTIVO, verbose_name='Estado'
    )

    class Meta:
        db_table = 'evento'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_evento']
        indexes = [
            models.Index(fields=['estado', 'fecha_evento']),
        ]

    def __str__(self):
        return self.titulo

    def clean(self):
        if not self.titulo or not self.titulo.strip():
            raise ValidationError({'titulo': 'El título no puede estar vacío.'})
        if not self.descripcion or not self.descripcion.strip():
            raise ValidationError({'descripcion': 'La descripción no puede estar vacía.'})


class Multimedia(models.Model):
    class TipoMultimedia(models.TextChoices):
        IMAGEN = 'IMAGEN', 'IMAGEN'
        VIDEO = 'VIDEO', 'VIDEO'

    archivo = models.FileField(upload_to='multimedia/', verbose_name='Archivo')
    tipo = models.CharField(
        max_length=10, choices=TipoMultimedia.choices, verbose_name='Tipo'
    )
    noticia = models.ForeignKey(
        Noticia, on_delete=models.CASCADE,
        related_name='multimedia', null=True, blank=True,
        verbose_name='Noticia'
    )
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE,
        related_name='multimedia', null=True, blank=True,
        verbose_name='Evento'
    )
    orden = models.IntegerField(default=1, verbose_name='Orden')
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')

    class Meta:
        db_table = 'multimedia'
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Multimedia'
        ordering = ['orden', '-fecha_subida']

    def __str__(self):
        return str(self.archivo)

    def clean(self):
        if self.noticia and self.evento:
            raise ValidationError(
                'No puede asociarse a noticia y evento al mismo tiempo.'
            )
        if not self.noticia and not self.evento:
            raise ValidationError(
                'Debe asociarse a una noticia o a un evento.'
            )


class Comentario(models.Model):
    class EstadoComentario(models.TextChoices):
        APROBADO = 'APROBADO', 'APROBADO'
        PENDIENTE = 'PENDIENTE', 'PENDIENTE'
        RECHAZADO = 'RECHAZADO', 'RECHAZADO'

    contenido = models.TextField(verbose_name='Contenido')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='comentarios', verbose_name='Usuario'
    )
    noticia = models.ForeignKey(
        Noticia, on_delete=models.CASCADE,
        related_name='comentarios', null=True, blank=True,
        verbose_name='Noticia'
    )
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE,
        related_name='comentarios', null=True, blank=True,
        verbose_name='Evento'
    )
    comentario_padre = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name='respuestas', null=True, blank=True,
        verbose_name='Comentario padre'
    )
    estado = models.CharField(
        max_length=10, choices=EstadoComentario.choices,
        default=EstadoComentario.PENDIENTE
    )
    tiene_palabras_prohibidas = models.BooleanField(default=False)
    editado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comentario'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['noticia', '-fecha']),
            models.Index(fields=['usuario', '-fecha']),
        ]

    def __str__(self):
        return f'Comentario #{self.id} - {self.usuario}'

    def clean(self):
        if not self.contenido or not self.contenido.strip():
            raise ValidationError({'contenido': 'El comentario no puede estar vacío.'})
        if self.noticia and self.evento:
            raise ValidationError(
                'No puede estar en noticia y evento al mismo tiempo.'
            )
        if not self.noticia and not self.evento:
            raise ValidationError(
                'Debe pertenecer a una noticia o a un evento.'
            )


class Reaccion(models.Model):
    class TipoReaccion(models.TextChoices):
        LIKE = 'LIKE', 'LIKE'
        LOVE = 'LOVE', 'LOVE'
        ENOJO = 'ENOJO', 'ENOJO'

    tipo = models.CharField(
        max_length=10, choices=TipoReaccion.choices, verbose_name='Tipo'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reacciones', verbose_name='Usuario'
    )
    noticia = models.ForeignKey(
        Noticia, on_delete=models.CASCADE,
        related_name='reacciones', null=True, blank=True,
        verbose_name='Noticia'
    )
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE,
        related_name='reacciones', null=True, blank=True,
        verbose_name='Evento'
    )

    class Meta:
        db_table = 'reaccion'
        verbose_name = 'Reacción'
        verbose_name_plural = 'Reacciones'

    def __str__(self):
        destino = self.noticia if self.noticia else self.evento
        return f'{self.usuario} - {self.tipo} - {destino}'

    def clean(self):
        if self.noticia and self.evento:
            raise ValidationError(
                'Una reacción no puede estar asociada a noticia y evento al mismo tiempo.'
            )
        if not self.noticia and not self.evento:
            raise ValidationError(
                'Una reacción debe estar asociada a una noticia o a un evento.'
            )
