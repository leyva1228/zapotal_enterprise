"""Modelos institucionales (Fase 5): ConfiguracionComunidad, MarcoLegalItem,
PaginaLegal, HitoHistorico, GaleriaImagen, MensajeContacto.

Estos modelos permiten que toda la informacion del sitio venga de la DB
en lugar de estar hardcoded en el frontend.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class ConfiguracionComunidad(models.Model):
    """Configuracion institucional singleton - solo 1 registro (pk=1)."""

    # Identidad
    nombre_oficial = models.CharField(
        'Nombre oficial', max_length=200,
        default='Comunidad Campesina Niño Dios de Zapotal',
    )
    nombre_corto = models.CharField(
        'Nombre corto', max_length=100, default='Comunidad Zapotal',
    )
    eslogan = models.CharField('Eslogan', max_length=200, blank=True, default='')
    descripcion_corta = models.TextField('Descripcion corta', blank=True, default='')
    descripcion_larga = models.TextField('Descripcion larga', blank=True, default='')

    # Historia / identidad
    historia_html = models.TextField(
        'Historia (HTML/Markdown)', blank=True, default='',
        help_text='Texto largo sobre la historia de la Comunidad.',
    )
    mision = models.TextField('Mision', blank=True, default='')
    vision = models.TextField('Vision', blank=True, default='')
    valores = models.JSONField(
        'Valores', default=list, blank=True,
        help_text='Lista de {nombre, descripcion, icono}.',
    )

    # Ubicacion
    distrito = models.CharField('Distrito', max_length=100, default='Huarango')
    provincia = models.CharField('Provincia', max_length=100, default='San Ignacio')
    region = models.CharField('Region', max_length=100, default='Cajamarca')
    ubigeo = models.CharField('Ubigeo', max_length=10, default='060903')
    direccion_casa_comunal = models.CharField(
        'Direccion Casa Comunal', max_length=300,
        default='Centro Poblado Zapotal, Distrito Huarango, San Ignacio, Cajamarca',
    )
    coordenadas_lat = models.DecimalField(
        'Latitud', max_digits=10, decimal_places=7, default=-5.3983,
    )
    coordenadas_lng = models.DecimalField(
        'Longitud', max_digits=10, decimal_places=7, default=-78.7055,
    )
    codigo_postal = models.CharField('Codigo postal', max_length=10, default='06860')

    # Contacto
    telefono_fijo = models.CharField(
        'Telefono fijo', max_length=20, blank=True, default='+51 931 757 530',
    )
    telefono_emergencias = models.CharField(
        'Telefono emergencias', max_length=20, blank=True, default='',
    )
    whatsapp_numero = models.CharField(
        'WhatsApp (con prefijo pais)', max_length=20, blank=True, default='',
        help_text='Ej: +51931757530',
    )
    email_contacto = models.EmailField(
        'Email de contacto', default='contacto@comunidadzapotal.gob.pe',
    )
    email_privacidad = models.EmailField(
        'Email privacidad / DPO', default='privacidad@comunidadzapotal.gob.pe',
    )
    email_denuncias = models.EmailField(
        'Email de denuncias', default='denuncias@comunidadzapotal.gob.pe',
    )
    horario_atencion = models.CharField(
        'Horario de atencion', max_length=200,
        default='Lun a Vie, 8:00 a 17:00',
    )

    # Multimedia
    logo_url = models.URLField('Logo URL', blank=True, default='')
    foto_casa_comunal_url = models.URLField(
        'Foto Casa Comunal URL', blank=True, default='',
    )

    # Metadata
    actualizado_en = models.DateTimeField('Actualizado en', auto_now=True)

    # ============================================================
    # Modulos (Loop 1 v2 — flags para activar/desactivar modulos
    # del sistema desde el panel admin sin redeploy).
    # ============================================================
    modulo_donaciones_activo = models.BooleanField(
        'Modulo Donaciones activo', default=True,
        help_text='Permite mostrar/ocultar la seccion de donaciones en el sitio publico.',
    )
    modulo_favoritos_activo = models.BooleanField(
        'Modulo Favoritos activo', default=True,
        help_text='Permite mostrar/ocultar el boton de favoritos en noticias/eventos.',
    )
    modulo_registro_abierto = models.BooleanField(
        'Registro publico de usuarios abierto', default=True,
        help_text='Permite bloquear el registro de nuevos usuarios.',
    )
    modulo_comentarios_activo = models.BooleanField(
        'Modulo Comentarios activo', default=True,
        help_text='Permite deshabilitar comentarios en noticias y eventos.',
    )
    moderacion_comentarios_previa = models.BooleanField(
        'Moderacion previa de comentarios', default=False,
        help_text='Si esta activo, los comentarios quedan PENDIENTES hasta aprobacion admin.',
    )
    notificaciones_email_activas = models.BooleanField(
        'Notificaciones por email activas', default=True,
        help_text='Envia emails de notificacion al admin (bienvenida, alertas, etc).',
    )
    tiempo_sesion_minutos = models.PositiveIntegerField(
        'Tiempo de sesion en minutos', default=60,
        help_text='Duracion del access token JWT.',
    )
    actualizado_por = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='configuraciones_modificadas',
        verbose_name='Actualizado por',
    )

    class Meta:
        verbose_name = 'Configuracion de la Comunidad'
        verbose_name_plural = 'Configuracion de la Comunidad'

    def save(self, *args, **kwargs):
        # Singleton: forzar pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.nombre_oficial


class MarcoLegalItem(models.Model):
    """Items editables del Marco Legal de la Comunidad."""
    titulo = models.CharField('Titulo', max_length=200)
    norma = models.CharField('Norma legal', max_length=200, help_text='Ej: Ley 24656 + D.S. 008-91-TR')
    descripcion = models.TextField('Descripcion')
    icono = models.CharField(
        'Icono (react-icons)', max_length=50, default='FaGavel',
        help_text='Nombre del icono Fa de react-icons/fa.',
    )
    url_externa = models.URLField('URL externa', blank=True, default='')
    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'Item de Marco Legal'
        verbose_name_plural = 'Items de Marco Legal'

    def __str__(self):
        return f'{self.titulo} ({self.norma})'


class PaginaLegal(models.Model):
    """Paginas legales editables: Terminos, Privacidad, Cookies."""
    SLUG_CHOICES = [
        ('terminos',   'Terminos y Condiciones'),
        ('privacidad', 'Politica de Privacidad'),
        ('cookies',    'Politica de Cookies'),
    ]
    slug = models.SlugField('Slug', choices=SLUG_CHOICES, unique=True)
    titulo = models.CharField('Titulo', max_length=200)
    resumen_corto = models.TextField('Resumen corto', blank=True, default='')
    contenido = models.TextField(
        'Contenido (HTML/Markdown)',
        help_text='Texto legal completo de la pagina.',
    )
    version = models.CharField('Version', max_length=20, default='1.0')
    fecha_vigencia = models.DateField('Fecha de vigencia', default=timezone.now)
    activo = models.BooleanField('Activo', default=True)
    fecha_actualizacion = models.DateTimeField('Actualizado en', auto_now=True)

    class Meta:
        ordering = ['slug']
        verbose_name = 'Pagina Legal'
        verbose_name_plural = 'Paginas Legales'

    def __str__(self):
        return self.titulo


class HitoHistorico(models.Model):
    """Linea de tiempo historica de la Comunidad."""
    fecha = models.DateField('Fecha exacta', null=True, blank=True)
    anio = models.PositiveIntegerField(
        'Anio', null=True, blank=True,
        help_text='Usar cuando no se conoce mes/dia exacto.',
    )
    titulo = models.CharField('Titulo', max_length=200)
    descripcion = models.TextField('Descripcion', blank=True, default='')
    imagen = models.ImageField(
        'Imagen', upload_to='hitos/', blank=True, null=True,
    )
    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        ordering = ['orden', '-anio', '-fecha']
        verbose_name = 'Hito Historico'
        verbose_name_plural = 'Hitos Historicos'

    def __str__(self):
        fecha_str = ''
        if self.fecha:
            fecha_str = self.fecha.strftime('%Y-%m-%d')
        elif self.anio:
            fecha_str = str(self.anio)
        return f'{fecha_str} - {self.titulo}'


class GaleriaImagen(models.Model):
    """Galeria de imagenes de la Comunidad."""
    class Categoria(models.TextChoices):
        COMUNIDAD       = 'COMUNIDAD',       'Comunidad'
        AUTORIDADES     = 'AUTORIDADES',     'Autoridades'
        FESTIVIDADES    = 'FESTIVIDADES',    'Festividades'
        INFRAESTRUCTURA = 'INFRAESTRUCTURA', 'Infraestructura'
        NATURALEZA      = 'NATURALEZA',      'Naturaleza'
        PATRIMONIO      = 'PATRIMONIO',      'Patrimonio Cultural'
        OTRO            = 'OTRO',            'Otro'

    titulo = models.CharField('Titulo', max_length=200)
    descripcion = models.TextField('Descripcion', blank=True, default='')
    imagen = models.ImageField('Imagen', upload_to='galeria/')
    categoria = models.CharField(
        'Categoria', max_length=20, choices=Categoria.choices,
        default=Categoria.COMUNIDAD,
    )
    fecha = models.DateField('Fecha', null=True, blank=True)
    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        ordering = ['orden', '-fecha']
        verbose_name = 'Imagen de Galeria'
        verbose_name_plural = 'Imagenes de Galeria'

    def __str__(self):
        return f'{self.titulo} ({self.get_categoria_display()})'


class MensajeContacto(models.Model):
    """Mensajes recibidos desde el formulario de contacto publico."""
    class Prioridad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'

    nombre = models.CharField('Nombre', max_length=200)
    email = models.EmailField('Email')
    telefono = models.CharField('Telefono', max_length=20, blank=True, default='')
    asunto = models.CharField('Asunto', max_length=200)
    mensaje = models.TextField('Mensaje')
    ip_origen = models.GenericIPAddressField('IP de origen', null=True, blank=True)
    user_agent = models.CharField('User agent', max_length=500, blank=True, default='')
    leido = models.BooleanField('Leido', default=False)
    respondido = models.BooleanField('Respondido', default=False)
    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    # Campos administrativos (Loop 1.2)
    prioridad = models.CharField(
        'Prioridad', max_length=10,
        choices=Prioridad.choices, default=Prioridad.MEDIA,
    )
    nota_admin = models.TextField('Nota interna del admin', blank=True, default='')
    nota_admin_at = models.DateTimeField('Nota interna - fecha', null=True, blank=True)
    nota_admin_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notas_mensajes_contacto',
    )
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='respuestas_mensajes_contacto',
    )
    respondido_at = models.DateTimeField('Respondido en', null=True, blank=True)
    respondido_texto = models.TextField('Texto de la respuesta enviada', blank=True, default='')
    respondido_desde_panel = models.BooleanField('Respondido desde el panel', default=False)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Mensaje de Contacto'
        verbose_name_plural = 'Mensajes de Contacto'
        indexes = [
            models.Index(fields=['leido', '-fecha']),
            models.Index(fields=['prioridad', '-fecha']),
        ]

    def __str__(self):
        return f'{self.nombre} - {self.asunto} ({self.fecha:%Y-%m-%d})'
