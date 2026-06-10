import re
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Usuario(models.Model):
    class TipoUsuario(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        COMUNERO = 'COMUNERO', 'COMUNERO'
        USUARIO = 'USUARIO', 'USUARIO'

    class EstadoUsuario(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    password = models.CharField(max_length=255, verbose_name="Contraseña")
    dni = models.CharField(max_length=8, unique=True, verbose_name="DNI")

    tipo_usuario = models.CharField(
        max_length=10,
        choices=TipoUsuario.choices,
        verbose_name="Tipo de usuario"
    )

    estado = models.CharField(
        max_length=10,
        choices=EstadoUsuario.choices,
        default=EstadoUsuario.ACTIVO,
        verbose_name="Estado"
    )

    dni_verificado = models.BooleanField(
        default=False,
        verbose_name="DNI verificado"
    )

    foto_perfil = models.ImageField(
        upload_to='usuarios/perfiles/',
        blank=True,
        null=True,
        verbose_name="Foto de perfil"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    class Meta:
        db_table = 'usuario'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def nombre_completo(self):
        if self.nombres and self.apellidos:
            return f"{self.nombres} {self.apellidos}"
        return self.nombres or self.email

    @property
    def iniciales(self):
        iniciales = ""
        if self.nombres and len(self.nombres) > 0:
            iniciales += self.nombres[0].upper()
        if self.apellidos and len(self.apellidos) > 0:
            iniciales += self.apellidos[0].upper()
        if not iniciales and self.email:
            iniciales = self.email[0].upper()
        if not iniciales:
            iniciales = "U"
        return iniciales

    def clean(self):
        errores = {}

        if not self.nombres or not self.nombres.strip():
            errores['nombres'] = "El nombre no puede estar vacío."

        if not self.apellidos or not self.apellidos.strip():
            errores['apellidos'] = "El apellido no puede estar vacío."

        if not re.fullmatch(r'\d{8}', self.dni or ''):
            errores['dni'] = "El DNI debe tener exactamente 8 dígitos numéricos."

        if not self.password or len(self.password) < 6:
            errores['password'] = "La contraseña debe tener mínimo 6 caracteres."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Comunero(models.Model):
    class EstadoComunero(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    dni = models.CharField(
        max_length=8,
        unique=True,
        verbose_name="DNI oficial"
    )

    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")

    estado = models.CharField(
        max_length=10,
        choices=EstadoComunero.choices,
        default=EstadoComunero.ACTIVO,
        verbose_name="Estado"
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='comuneros',
        verbose_name="Usuario asociado"
    )

    class Meta:
        db_table = 'comunero'
        verbose_name = "Comunero"
        verbose_name_plural = "Comuneros"
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def clean(self):
        errores = {}

        if not re.fullmatch(r'\d{8}', self.dni or ''):
            errores['dni'] = "El DNI debe tener exactamente 8 dígitos."

        if not self.nombres.strip():
            errores['nombres'] = "El nombre no puede estar vacío."

        if not self.apellidos.strip():
            errores['apellidos'] = "El apellido no puede estar vacío."

        if self.usuario and self.usuario.tipo_usuario != Usuario.TipoUsuario.COMUNERO:
            errores['usuario'] = "El usuario debe ser de tipo COMUNERO."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Categoria(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre"
    )
    descripcion = models.TextField(
        verbose_name="Descripción"
    )

    class Meta:
        db_table = 'categoria'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def clean(self):
        errores = {}

        if not self.nombre or not self.nombre.strip():
            errores['nombre'] = "El nombre de la categoría no puede estar vacío."

        if not self.descripcion or not self.descripcion.strip():
            errores['descripcion'] = "La descripción no puede estar vacía."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Noticia(models.Model):
    class EstadoNoticia(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    titulo = models.CharField(max_length=200, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='noticias',
        verbose_name="Categoría"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='noticias',
        verbose_name="Usuario responsable"
    )
    fecha_publicacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de publicación"
    )
    estado = models.CharField(
        max_length=10,
        choices=EstadoNoticia.choices,
        default=EstadoNoticia.ACTIVO,
        verbose_name="Estado"
    )

    class Meta:
        db_table = 'noticia'
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo

    def clean(self):
        errores = {}

        if not self.titulo or not self.titulo.strip():
            errores['titulo'] = "El título no puede estar vacío."

        if not self.contenido or not self.contenido.strip():
            errores['contenido'] = "El contenido no puede estar vacío."

        if self.usuario and self.usuario.tipo_usuario != Usuario.TipoUsuario.ADMIN:
            errores['usuario'] = "Solo un usuario ADMIN puede publicar noticias."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Evento(models.Model):
    class EstadoEvento(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='eventos',
        verbose_name="Categoría"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='eventos',
        verbose_name="Usuario responsable"
    )
    fecha_evento = models.DateTimeField(verbose_name="Fecha del evento")
    fecha_publicacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de publicación"
    )
    estado = models.CharField(
        max_length=10,
        choices=EstadoEvento.choices,
        default=EstadoEvento.ACTIVO,
        verbose_name="Estado"
    )

    class Meta:
        db_table = 'evento'
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-fecha_evento']

    def __str__(self):
        return self.titulo

    def clean(self):
        errores = {}

        if not self.titulo or not self.titulo.strip():
            errores['titulo'] = "El título no puede estar vacío."

        if not self.descripcion or not self.descripcion.strip():
            errores['descripcion'] = "La descripción no puede estar vacía."

        if self.usuario and self.usuario.tipo_usuario != Usuario.TipoUsuario.ADMIN:
            errores['usuario'] = "Solo un usuario ADMIN puede publicar eventos."

        if self.fecha_evento and self.fecha_evento < timezone.now():
            errores['fecha_evento'] = "No se puede crear un evento con fecha pasada."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Comentario(models.Model):
    class EstadoComentario(models.TextChoices):
        APROBADO = 'APROBADO', 'APROBADO'
        PENDIENTE = 'PENDIENTE', 'PENDIENTE'
        RECHAZADO = 'RECHAZADO', 'RECHAZADO'
        ELIMINADO = 'ELIMINADO', 'ELIMINADO'  # NUEVO ESTADO

    contenido = models.TextField(verbose_name="Contenido")
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name="Usuario"
    )
    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        related_name='comentarios',
        null=True,
        blank=True,
        verbose_name="Noticia"
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='comentarios',
        null=True,
        blank=True,
        verbose_name="Evento"
    )
    comentario_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='respuestas',
        null=True,
        blank=True,
        verbose_name="Comentario padre"
    )
    estado = models.CharField(
        max_length=10,
        choices=EstadoComentario.choices,
        default=EstadoComentario.PENDIENTE
    )
    tiene_palabras_prohibidas = models.BooleanField(default=False)
    editado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(null=True, blank=True)  # NUEVO

    class Meta:
        db_table = 'comentario'
        ordering = ['-fecha']

    def __str__(self):
        return f"Comentario #{self.id} - {self.usuario}"

    def es_respuesta(self):
        return self.comentario_padre is not None

    def puede_eliminar(self, usuario):
        return usuario == self.usuario or usuario.tipo_usuario == 'ADMIN'

    def clean(self):
        errores = {}

        if not self.contenido or not self.contenido.strip():
            errores['contenido'] = "El comentario no puede estar vacío."

        if self.noticia and self.evento:
            errores['noticia'] = "No puede estar en noticia y evento al mismo tiempo."

        if not self.noticia and not self.evento:
            errores['noticia'] = "Debe pertenecer a una noticia o a un evento."

        if self.comentario_padre:
            if self.noticia and self.comentario_padre.noticia != self.noticia:
                errores['comentario_padre'] = "Debe responder a la misma noticia."

            if self.evento and self.comentario_padre.evento != self.evento:
                errores['comentario_padre'] = "Debe responder al mismo evento."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Reaccion(models.Model):
    class TipoReaccion(models.TextChoices):
        LIKE = 'LIKE', 'LIKE'
        LOVE = 'LOVE', 'LOVE'
        ANGRY = 'ANGRY', 'ANGRY'  # Cambiado de ENOJO a ANGRY para consistencia

    tipo = models.CharField(
        max_length=10,
        choices=TipoReaccion.choices,
        verbose_name="Tipo"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reacciones',
        verbose_name="Usuario"
    )
    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        related_name='reacciones',
        null=True,
        blank=True,
        verbose_name="Noticia"
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='reacciones',
        null=True,
        blank=True,
        verbose_name="Evento"
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")  # NUEVO

    class Meta:
        db_table = 'reaccion'
        verbose_name = "Reacción"
        verbose_name_plural = "Reacciones"
        unique_together = ['usuario', 'noticia', 'evento']  # NUEVO

    def __str__(self):
        destino = self.noticia if self.noticia else self.evento
        return f"{self.usuario} - {self.tipo} - {destino}"

    def clean(self):
        errores = {}

        if self.noticia and self.evento:
            errores['noticia'] = "Una reacción no puede estar asociada a noticia y evento al mismo tiempo."

        if not self.noticia and not self.evento:
            errores['noticia'] = "Una reacción debe estar asociada a una noticia o a un evento."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Mensaje(models.Model):
    emisor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        verbose_name="Emisor"
    )
    receptor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_recibidos',
        verbose_name="Receptor"
    )
    contenido = models.TextField(verbose_name="Contenido")
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha"
    )
    leido = models.BooleanField(default=False)  # NUEVO
    fecha_lectura = models.DateTimeField(null=True, blank=True)  # NUEVO

    class Meta:
        db_table = 'mensaje'
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['-fecha']

    def __str__(self):
        return f"Mensaje de {self.emisor} a {self.receptor}"

    def clean(self):
        errores = {}

        if not self.contenido or not self.contenido.strip():
            errores['contenido'] = "El mensaje no puede estar vacío."

        if self.emisor and self.receptor and self.emisor == self.receptor:
            errores['receptor'] = "El usuario no puede enviarse un mensaje a sí mismo."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Notificacion(models.Model):
    class TipoNotificacion(models.TextChoices):
        GLOBAL = 'GLOBAL', 'GLOBAL'
        COMUNEROS = 'COMUNEROS', 'COMUNEROS'
        PERSONAL = 'PERSONAL', 'PERSONAL'

    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    mensaje = models.TextField(
        verbose_name="Mensaje"
    )
    tipo = models.CharField(
        max_length=15,
        choices=TipoNotificacion.choices,
        verbose_name="Tipo"
    )
    usuario_destino = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        null=True,
        blank=True,
        verbose_name="Usuario destino"
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha"
    )
    leido = models.BooleanField(default=False)  # NUEVO

    class Meta:
        db_table = 'notificacion'
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo

    def clean(self):
        errores = {}

        if not self.titulo or not self.titulo.strip():
            errores['titulo'] = "El título no puede estar vacío."

        if not self.mensaje or not self.mensaje.strip():
            errores['mensaje'] = "El mensaje no puede estar vacío."

        if self.tipo == self.TipoNotificacion.PERSONAL and not self.usuario_destino:
            errores['usuario_destino'] = "La notificación PERSONAL debe tener un usuario destino."

        if self.tipo in [
            self.TipoNotificacion.GLOBAL,
            self.TipoNotificacion.COMUNEROS
        ] and self.usuario_destino:
            errores['usuario_destino'] = "Solo la notificación PERSONAL debe tener usuario destino."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Multimedia(models.Model):

    class TipoMultimedia(models.TextChoices):
        IMAGEN = 'IMAGEN', 'IMAGEN'
        VIDEO = 'VIDEO', 'VIDEO'

    archivo = models.FileField(
        upload_to='multimedia/',
        null=True,
        blank=True,  
        verbose_name="Archivo (imagen o video)"
    )

    tipo = models.CharField(
        max_length=10,
        choices=TipoMultimedia.choices,
        verbose_name="Tipo"
    )

    noticia = models.ForeignKey(
        'Noticia',
        on_delete=models.CASCADE,
        related_name='multimedia',
        null=True,
        blank=True,
        verbose_name="Noticia"
    )

    evento = models.ForeignKey(
        'Evento',
        on_delete=models.CASCADE,
        related_name='multimedia',
        null=True,
        blank=True,
        verbose_name="Evento"
    )

    orden = models.IntegerField(
        default=1,
        verbose_name="Orden"
    )

    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de subida"
    )

    class Meta:
        db_table = 'multimedia'
        verbose_name = "Multimedia"
        verbose_name_plural = "Multimedia"
        ordering = ['orden', '-fecha_subida']

    def __str__(self):
        return str(self.archivo) if self.archivo else "Multimedia"

    def clean(self):
        errores = {}

        if not self.archivo:
            errores['archivo'] = "Debe subir un archivo."

        if self.noticia and self.evento:
            errores['noticia'] = "No puede asociarse a noticia y evento al mismo tiempo."

        if not self.noticia and not self.evento:
            errores['noticia'] = "Debe asociarse a una noticia o a un evento."

        if self.orden < 1:
            errores['orden'] = "El orden debe ser mayor o igual a 1."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Autoridad(models.Model):
    class EstadoAutoridad(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=120)
    descripcion = models.TextField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    foto = models.ImageField(upload_to="autoridades/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=1)
    estado = models.CharField(
        max_length=10,
        choices=EstadoAutoridad.choices,
        default=EstadoAutoridad.ACTIVO
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "autoridad"
        verbose_name = "Autoridad"
        verbose_name_plural = "Autoridades"
        ordering = ["orden", "cargo", "apellidos"]

    def __str__(self):
        return f"{self.cargo} - {self.nombres} {self.apellidos}"

    def clean(self):
        errores = {}

        if not self.nombres or not self.nombres.strip():
            errores["nombres"] = "Los nombres son obligatorios."

        if not self.apellidos or not self.apellidos.strip():
            errores["apellidos"] = "Los apellidos son obligatorios."

        if not self.cargo or not self.cargo.strip():
            errores["cargo"] = "El cargo es obligatorio."

        if not self.descripcion or not self.descripcion.strip():
            errores["descripcion"] = "La descripción es obligatoria."

        if self.telefono and not re.fullmatch(r"\d{6,15}", self.telefono):
            errores["telefono"] = "El teléfono debe tener entre 6 y 15 dígitos."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ContactoMensaje(models.Model):
    class EstadoMensaje(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ATENDIDO = "ATENDIDO", "Atendido"
        ARCHIVADO = "ARCHIVADO", "Archivado"

    nombres = models.CharField(max_length=120)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    estado = models.CharField(
        max_length=10,
        choices=EstadoMensaje.choices,
        default=EstadoMensaje.PENDIENTE
    )
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contacto_mensaje"
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"{self.asunto} - {self.nombres}"

    def clean(self):
        errores = {}

        if not self.nombres or not self.nombres.strip():
            errores["nombres"] = "Los nombres son obligatorios."

        if not self.asunto or not self.asunto.strip():
            errores["asunto"] = "El asunto es obligatorio."

        if not self.mensaje or not self.mensaje.strip():
            errores["mensaje"] = "El mensaje es obligatorio."

        if self.telefono and not re.fullmatch(r"\d{6,15}", self.telefono):
            errores["telefono"] = "El teléfono debe tener entre 6 y 15 dígitos."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class LibroReclamacion(models.Model):

    class TipoSolicitud(models.TextChoices):
        RECLAMO = "RECLAMO", "Reclamo"
        QUEJA = "QUEJA", "Queja"
        SUGERENCIA = "SUGERENCIA", "Sugerencia"

    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_REVISION = "EN_REVISION", "En revisión"
        ATENDIDO = "ATENDIDO", "Atendido"

    nombres = models.CharField(
        max_length=120,
        verbose_name="Nombres"
    )

    apellidos = models.CharField(
        max_length=120,
        verbose_name="Apellidos"
    )

    dni = models.CharField(
        max_length=8,
        verbose_name="DNI"
    )

    correo = models.EmailField(
        verbose_name="Correo electrónico"
    )

    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )

    tipo_solicitud = models.CharField(
        max_length=15,
        choices=TipoSolicitud.choices,
        verbose_name="Tipo de solicitud"
    )

    asunto = models.CharField(
        max_length=200,
        verbose_name="Asunto"
    )

    descripcion = models.TextField(
        verbose_name="Descripción"
    )

    pedido = models.TextField(
        blank=True,
        null=True,
        verbose_name="Pedido del usuario"
    )

    estado = models.CharField(
        max_length=15,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.PENDIENTE,
        verbose_name="Estado"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    class Meta:
        db_table = "libro_reclamacion"
        verbose_name = "Libro de reclamación"
        verbose_name_plural = "Libro de reclamaciones"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.tipo_solicitud} - {self.nombres} {self.apellidos}"

    def clean(self):
        errores = {}

        if not self.nombres or not self.nombres.strip():
            errores["nombres"] = "Los nombres son obligatorios."

        if not self.apellidos or not self.apellidos.strip():
            errores["apellidos"] = "Los apellidos son obligatorios."

        if not re.fullmatch(r"\d{8}", self.dni or ""):
            errores["dni"] = "El DNI debe tener exactamente 8 dígitos."

        if not self.asunto or not self.asunto.strip():
            errores["asunto"] = "El asunto es obligatorio."

        if not self.descripcion or not self.descripcion.strip():
            errores["descripcion"] = "La descripción es obligatoria."

        if self.telefono:
            if not re.fullmatch(r"\d{6,15}", self.telefono):
                errores["telefono"] = "El teléfono debe tener entre 6 y 15 dígitos."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)