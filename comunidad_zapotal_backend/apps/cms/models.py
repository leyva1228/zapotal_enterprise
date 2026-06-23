from django.db import models


class ContenidoEstatico(models.Model):
    class Seccion(models.TextChoices):
        HISTORIA = 'HISTORIA', 'Nuestra Historia'
        MISION = 'MISION', 'Mision'
        VISION = 'VISION', 'Vision'
        VALORES = 'VALORES', 'Valores'
        INICIO_HERO = 'INICIO_HERO', 'Inicio - Hero'
        INICIO_SUBTITULO = 'INICIO_SUBTITULO', 'Inicio - Subtitulo'
        CONTACTO_INFO = 'CONTACTO_INFO', 'Informacion de contacto'
        FOOTER = 'FOOTER', 'Pie de pagina'
        AUTORIDADES_INTRO = 'AUTORIDADES_INTRO', 'Autoridades - Introduccion'
        DONACIONES_INTRO = 'DONACIONES_INTRO', 'Donaciones - Introduccion'

    seccion = models.CharField(
        'Seccion',
        max_length=30,
        choices=Seccion.choices,
        unique=True,
        db_index=True,
    )
    titulo = models.CharField('Titulo', max_length=200)
    contenido = models.TextField('Contenido (texto plano)')
    contenido_html = models.TextField(
        'Contenido HTML (opcional)',
        blank=True,
        default='',
        help_text='HTML enriquecido que se sanitizara en backend antes de servir.',
    )
    imagen = models.ImageField(
        'Imagen',
        upload_to='cms/',
        blank=True,
        null=True,
    )
    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualizacion', auto_now=True)

    class Meta:
        db_table = 'contenido_estatico'
        verbose_name = 'Contenido estatico'
        verbose_name_plural = 'Contenidos estaticos'
        ordering = ['orden', 'seccion']

    def __str__(self):
        return f'{self.get_seccion_display()}: {self.titulo}'
