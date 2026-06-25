from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import Usuario, Comunero


class ComiteComunal(models.Model):
    """Comites Especializados (Ley 24656 Art. 16.c + D.S. 008-91-TR Art. 79).

    Tercer organo de gobierno de la Comunidad Campesina. Incluye:
    - Comite Electoral (elegido a mas tardar 15 de octubre)
    - Comite Revisor de Cuentas (3 miembros: Pres, Sec, Vocal)
    - Rondas Campesinas (justicia consuetudinaria)
    - Comite de Gestion (proyectos, obras)
    """
    class TipoComite(models.TextChoices):
        ELECTORAL         = 'ELECTORAL',         'Comite Electoral'
        REVISOR_CUENTAS   = 'REVISOR_CUENTAS',   'Comite Revisor de Cuentas'
        RONDAS_CAMPESINAS = 'RONDAS',            'Rondas Campesinas'
        COMITE_GESTION    = 'GESTION',           'Comite de Gestion'
        COMITE_OBRAS      = 'OBRAS',             'Comite de Obras'
        COMITE_EDUCACION  = 'EDUCACION',         'Comite de Educacion'
        OTRO              = 'OTRO',              'Otro'

    class NivelComite(models.TextChoices):
        COMUNAL   = 'COMUNAL',   'Nivel Comunal'
        ANEXO     = 'ANEXO',     'Anexo/Sector'
        DISTRITAL = 'DISTRITAL', 'Nivel Distrital'

    nombre = models.CharField(
        'Nombre del comite',
        max_length=150,
        help_text='Ej. "Comite Electoral 2026", "Comite Revisor de Cuentas 2026".',
    )
    tipo = models.CharField(
        'Tipo de comite',
        max_length=20,
        choices=TipoComite.choices,
        db_index=True,
    )
    nivel = models.CharField(
        'Nivel',
        max_length=20,
        choices=NivelComite.choices,
        default=NivelComite.COMUNAL,
        db_index=True,
    )
    descripcion = models.TextField(
        'Descripcion / funciones',
        blank=True,
        default='',
        help_text='Funciones del comite y marco legal aplicable.',
    )

    # Miembros: presidente, secretario, vocal (3 tipicos)
    presidente = models.ForeignKey(
        'Autoridad', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
        verbose_name='Presidente del comite',
    )
    secretario = models.ForeignKey(
        'Autoridad', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
        verbose_name='Secretario del comite',
    )
    vocal = models.ForeignKey(
        'Autoridad', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
        verbose_name='Vocal del comite',
    )

    fecha_constitucion = models.DateField(
        'Fecha de constitucion',
        null=True, blank=True,
        help_text='Fecha en que se eligio al comite en Asamblea.',
    )
    periodo_inicio = models.DateField('Inicio del periodo', null=True, blank=True)
    periodo_fin = models.DateField('Fin del periodo', null=True, blank=True)
    activo = models.BooleanField(default=True)
    acta_pdf = models.FileField(
        'Acta de constitucion (PDF)',
        upload_to='comites/actas/',
        blank=True, null=True,
        help_text='Acta firmada en formato PDF.',
    )

    class Meta:
        verbose_name = 'Comite Comunal'
        verbose_name_plural = 'Comites Comunales'
        ordering = ['-fecha_constitucion', 'tipo']
        constraints = [
            models.UniqueConstraint(
                fields=['tipo', 'periodo_inicio'],
                name='unique_comite_por_tipo_y_periodo',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()})'

    def clean(self):
        errores = {}
        if self.periodo_inicio and self.periodo_fin and self.periodo_inicio > self.periodo_fin:
            errores['periodo_fin'] = 'La fecha de fin no puede ser anterior a la fecha de inicio.'
        if errores:
            raise ValidationError(errores)


class Autoridad(models.Model):
    class TipoCargo(models.TextChoices):
        # Cargos de la Directiva Comunal (Ley 24656, D.S. 008-91-TR Art. 19)
        PRESIDENTE = 'PRESIDENTE', 'Presidente'
        VICEPRESIDENTE = 'VICEPRESIDENTE', 'Vicepresidente'
        SECRETARIO = 'SECRETARIO', 'Secretario'
        TESORERO = 'TESORERO', 'Tesorero'
        FISCAL = 'FISCAL', 'Fiscal'
        VOCAL = 'VOCAL', 'Vocal'
        # Cargos Municipales (Ley 28440) - se representan con cargo_tipo
        # PRESIDENTE o VOCAL segun el contexto. Se distinguen por nivel_gobierno.
        REGIDOR = 'REGIDOR', 'Regidor'
        OTRO = 'OTRO', 'Otro'

    CARGO_CHOICES = TipoCargo.choices

    comunero = models.OneToOneField(
        Comunero,
        on_delete=models.CASCADE,
        verbose_name='Comunero',
        related_name='autoridad',
    )
    cargo = models.CharField(
        'Cargo',
        max_length=100,
        choices=TipoCargo.choices,
        default=TipoCargo.OTRO,
        db_index=True,
    )
    cargo_tipo = models.CharField(
        'Tipo de cargo',
        max_length=20,
        choices=TipoCargo.choices,
        default=TipoCargo.OTRO,
        db_index=True,
        help_text='Version normalizada del cargo para el sistema de jerarquia.',
    )
    periodo = models.CharField('Periodo', max_length=50, blank=True, default='')
    comunero_info = models.CharField(
        'Comunero (texto legacy)',
        max_length=200,
        blank=True,
        default='',
        help_text='Snapshot textual del nombre previo a la migracion.',
    )
    reporta_a = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados',
        verbose_name='Reporta a',
    )
    es_admin = models.BooleanField(
        default=False,
        verbose_name='¿Tiene acceso al panel admin?',
        help_text='Solo presidente y cargos con permisos administrativos.',
    )
    periodo_inicio = models.DateField(
        'Inicio del periodo',
        null=True,
        blank=True,
    )
    periodo_fin = models.DateField(
        'Fin del periodo',
        null=True,
        blank=True,
    )
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField('Fecha de inicio (legacy)', null=True, blank=True)
    fecha_fin = models.DateField('Fecha de fin (legacy)', null=True, blank=True)
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='autoridad',
    )
    foto = models.ImageField(
        'Foto de la autoridad',
        upload_to='autoridades/',
        blank=True,
        null=True,
        help_text='Foto oficial. Si esta vacia, se usa la foto del usuario asociado.',
    )

    # ────────────────────────────────────────────────────────────
    # Campos extendidos (jun-2026): niveles de gobierno peruano
    # Comunidad Campesina + Municipalidad de C.P. + Autoridad Politica
    # ────────────────────────────────────────────────────────────
    class NivelGobierno(models.TextChoices):
        """Marco legal peruano (Ley 24656 + Ley 27972 + Ley 28440 + D.Leg. 370)."""
        COMUNAL   = 'COMUNAL',   'Directiva Comunal'
        MUNICIPAL = 'MUNICIPAL', 'Municipalidad de Centro Poblado'
        POLITICO  = 'POLITICO',  'Autoridad Politica'

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO  = 'F', 'Femenino'
        OTRO      = 'O', 'Otro'

    nivel_gobierno = models.CharField(
        'Nivel de gobierno',
        max_length=20,
        choices=NivelGobierno.choices,
        default=NivelGobierno.COMUNAL,
        db_index=True,
        help_text='Nivel al que pertenece la autoridad: Comunal / Municipal / Politico.',
    )
    descripcion = models.TextField(
        'Descripcion del cargo',
        blank=True,
        default='',
        help_text='Funciones y responsabilidades del cargo (segun Ley 24656, 27972 o 28440).',
    )
    orden = models.PositiveIntegerField(
        'Orden de visualizacion',
        default=0,
        db_index=True,
        help_text='Orden dentro del mismo nivel. Presidente=1, Vice=2, etc.',
    )
    sexo = models.CharField(
        'Sexo',
        max_length=1,
        choices=Sexo.choices,
        blank=True,
        default='',
        help_text='Para validar cuota 30% (Ley 30982).',
    )
    dni = models.CharField(
        'DNI',
        max_length=8,
        blank=True,
        default='',
        help_text='DNI desnormalizado (puede no tener Comunero asociado, ej. Gobernador).',
    )
    duracion_mandato_anos = models.PositiveSmallIntegerField(
        'Duracion del mandato (anos)',
        default=2,
        help_text='2 para Comunal, 4 para Municipal, variable para Politico.',
    )
    telefono = models.CharField(
        'Telefono de contacto',
        max_length=15,
        blank=True,
        default='',
    )
    email_institucional = models.EmailField(
        'Email institucional',
        blank=True,
        default='',
    )
    nro_partida_sunarp = models.CharField(
        'Partida SUNARP',
        max_length=50,
        blank=True,
        default='',
        help_text='Numero de partida registral donde esta inscrita la autoridad.',
    )

    # SUNARP extendido (Fase 4A) - inscripcion obligatoria Ley 24656
    sede_inscripcion = models.CharField(
        'Oficina registral (SUNARP)',
        max_length=100,
        blank=True,
        default='',
        help_text='Oficina registral donde se inscribio (ej. Oficina Registral de Jaen).',
    )
    resolucion_inscripcion = models.CharField(
        'Resolucion de inscripcion',
        max_length=50,
        blank=True,
        default='',
        help_text='Numero de la resolucion regional/ministerial de inscripcion.',
    )
    fecha_inscripcion = models.DateField(
        'Fecha de inscripcion',
        null=True,
        blank=True,
        help_text='Fecha en que se inscribio en SUNARP.',
    )
    estado_inscripcion = models.CharField(
        'Estado de inscripcion',
        max_length=20,
        choices=[
            ('', 'Sin tramite'),
            ('INSCRITO', 'Inscrito'),
            ('EN_TRAMITE', 'En tramite'),
            ('OBSERVADO', 'Observado'),
            ('PENDIENTE', 'Pendiente'),
            ('VENCIDO', 'Vencido'),
        ],
        blank=True,
        default='',
        help_text='Estado del tramite ante SUNARP.',
    )
    fecha_vencimiento_inscripcion = models.DateField(
        'Vencimiento de vigencia registral',
        null=True,
        blank=True,
        help_text='Vencimiento de la vigencia de la partida.',
    )

    # Cargos tradicionales (Fase 4C) - Ley 24656 Art. 19
    es_cargo_tradicional = models.BooleanField(
        'Es cargo tradicional',
        default=False,
        db_index=True,
        help_text='Cargo tradicional andino (Varayoc, Mayordomo, Padrino, etc.).',
    )
    nombre_tradicional = models.CharField(
        'Nombre tradicional',
        max_length=100,
        blank=True,
        default='',
        help_text='Nombre del cargo en idioma nativo o tradicional (ej. "Varayoc", "Alcalde Vara").',
    )

    # Reeleccion (Fase 4E) - Ley 24656 Art. 20 + D.S. 008-91-TR Art. 88
    reelegido = models.BooleanField(
        'Reelegido',
        default=False,
        help_text='Es reelegido por un segundo periodo consecutivo? (max 1 reelecion)',
    )
    autoridad_anterior = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reelecciones_sucesivas',
        verbose_name='Autoridad anterior (periodo previo)',
        help_text='Vinculo a la autoridad que precede a esta (en caso de reelecion).',
    )

    # Requisito de idioma (Fase 4F) - Ley 24656 Art. 20.d
    LENGUA_CHOICES = [
        ('', 'No especificado'),
        ('ES', 'Espanol'),
        ('QU', 'Quechua (Chinchaysuyo)'),
        ('AW', 'Awajun'),
        ('WP', 'Wampis'),
        ('OT', 'Otro'),
    ]
    lengua_materna = models.CharField(
        'Lengua materna',
        max_length=2,
        choices=LENGUA_CHOICES,
        blank=True,
        default='',
        help_text='Idioma nativo predominante de la Comunidad (requisito Ley 24656 Art. 20.d).',
    )

    class Meta:
        verbose_name = 'Autoridad'
        verbose_name_plural = 'Autoridades'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.comunero} - {self.cargo}'

    def clean(self):
        errores = {}
        if self.periodo_inicio and self.periodo_fin and self.periodo_inicio > self.periodo_fin:
            errores['periodo_fin'] = 'La fecha de fin no puede ser anterior a la fecha de inicio.'
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        # Compatibilidad hacia atras: si vienen fechas legacy, propagarlas a las nuevas.
        if not self.periodo_inicio and self.fecha_inicio:
            self.periodo_inicio = self.fecha_inicio
        if not self.periodo_fin and self.fecha_fin:
            self.periodo_fin = self.fecha_fin
        # Mapear cargo a cargo_tipo si cargo_tipo no fue seteado
        if not self.cargo_tipo or self.cargo_tipo == self.TipoCargo.OTRO:
            self.cargo_tipo = self._mapear_cargo_a_tipo(self.cargo)
        super().save(*args, **kwargs)

    @staticmethod
    def _mapear_cargo_a_tipo(texto):
        if not texto:
            return Autoridad.TipoCargo.OTRO
        t = texto.upper()
        if 'PRESIDENTE' in t or 'ALCALDE' in t:
            return Autoridad.TipoCargo.PRESIDENTE
        if 'VICE' in t:
            return Autoridad.TipoCargo.VICEPRESIDENTE
        if 'TESORER' in t:
            return Autoridad.TipoCargo.TESORERO
        if 'SECRETAR' in t:
            return Autoridad.TipoCargo.SECRETARIO
        if 'FISCAL' in t:
            return Autoridad.TipoCargo.FISCAL
        if 'REGIDOR' in t or 'GOBERNADOR' in t:
            return Autoridad.TipoCargo.REGIDOR
        if 'VOCAL' in t or 'TENIENTE' in t:
            return Autoridad.TipoCargo.VOCAL
        return Autoridad.TipoCargo.OTRO


# Importar modelos institucionales (Fase 5) al final para evitar ciclos
from .models_institucionales import (  # noqa: E402
    ConfiguracionComunidad,
    MarcoLegalItem,
    PaginaLegal,
    HitoHistorico,
    GaleriaImagen,
    MensajeContacto,
)
