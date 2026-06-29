$docsRoot = "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\docs\comunidad_zapotal_backend"

function Write-Doc($relPath, $content) {
    $fullPath = Join-Path $docsRoot "$relPath.py.md"
    $dir = Split-Path $fullPath -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $fullPath -Value $content -Encoding UTF8
    Write-Output "OK: $relPath.py.md"
}

# === All __init__.py files (17) ===
$inits = @(
    "apps\__init__", "apps\accounts\__init__", "apps\accounts\factories\__init__",
    "apps\accounts\management\__init__", "apps\accounts\management\commands\__init__", "apps\accounts\migrations\__init__",
    "apps\cms\__init__", "apps\cms\management\__init__", "apps\cms\management\commands\__init__", "apps\cms\migrations\__init__",
    "apps\comunidad\__init__", "apps\comunidad\management\__init__", "apps\comunidad\management\commands\__init__", "apps\comunidad\migrations\__init__",
    "apps\content\__init__", "apps\content\migrations\__init__",
    "apps\core\__init__", "apps\core\management\__init__", "apps\core\management\commands\__init__", "apps\core\migrations\__init__",
    "apps\donaciones\__init__", "apps\donaciones\migrations\__init__",
    "apps\messaging\__init__", "apps\messaging\management\__init__", "apps\messaging\management\commands\__init__", "apps\messaging\migrations\__init__",
    "apps\reports\__init__", "apps\reports\management\__init__", "apps\reports\management\commands\__init__", "apps\reports\migrations\__init__",
    "zapotal_config\__init__"
)

foreach ($fp in $inits) {
    $p = $fp -replace '\\', '/'
    Write-Doc $fp "# $p/__init__.py`n`n- **Ruta original:** comunidad_zapotal_backend/$p/__init__.py`n- **Tecnologia:** Python / Django`n- **Tipo:** Package init`n- **Proposito:** Marca el directorio como paquete Python"
}

# === migrations ===
Write-Doc "apps\accounts\migrations\0001_initial" @"
# apps/accounts/migrations/0001_initial.py

**Proposito:** Creacion del modelo Usuario (AbstractUser custom)
**Modelos:** Usuario (AbstractUser), Comunero (OneToOne con Usuario)
**Dependencias:** auth 0012, contenttypes 0002, core 0001, comunidad 0001
**Campos Usuario:** id, password, last_login, is_superuser, groups, user_permissions, username (unique 150), first_name, last_name, email (unique 254), is_staff, is_active, date_joined, tipo_usuario, telefono, foto_perfil, direccion, fecha_nacimiento, is_email_verified, email_verification_token, notification_token, updated_at, created_at
**Campos Comunero:** usuario_ptr (OneToOne PK), dni (unique 8), nombres, apellidos, fecha_nacimiento, direccion
"@

Write-Doc "apps\accounts\migrations\0002_usuario_aprobado_por_usuario_canal_verificacion_and_more" @"
# apps/accounts/migrations/0002

**Operaciones:** AddField aprobado_por (FK Usuario null), canal_verificacion, email_verificado, fecha_aprobacion, moderado (BooleanField default=True), necesita_revision (BooleanField default=False), motivo_rechazo, razon_social (FK null), rol (CharField default=comunero), tipo_documento
**Dependencias:** accounts 0001
"@

Write-Doc "apps\accounts\migrations\0003_usuario_two_factor_confirmed_at_and_more" @"
# apps/accounts/migrations/0003

**Operaciones:** AddField two_factor_confirmed_at, two_factor_enabled, two_factor_secret, updated_at (alter field), created_at (alter field)
**Dependencias:** accounts 0002
"@

Write-Doc "apps\accounts\migrations\0004_remove_usuario_facebook_id" @"
# apps/accounts/migrations/0004

**Operaciones:** RemoveField facebook_id de Usuario
**Dependencias:** accounts 0003
"@

Write-Doc "apps\cms\migrations\0001_initial" @"
# apps/cms/migrations/0001_initial.py

**Proposito:** Creacion del modelo PaginaEstatica
**Modelos:** PaginaEstatica (id BigAutoField, titulo, slug unique, contenido HTML, meta_descripcion, orden IntegerField default=0, activa BooleanField default=True, created_at, updated_at)
**Dependencias:** Ninguna
"@

Write-Doc "apps\comunidad\migrations\0001_initial" @"
# apps/comunidad/migrations/0001_initial.py

**Modelos:** Autoridad (BigAutoField, nombre, cargo, foto, activo default=True), Categoria (id, nombre unique, descripcion, color_hex, icono)
**Dependencias:** Ninguna
"@

Write-Doc "apps\comunidad\migrations\0002_autoridad_activo_autoridad_cargo_tipo_and_more" @"
# apps/comunidad/migrations/0002

**Operaciones:** AddField activo, cargo_tipo; AlterField cargo (max_length 200); CreateModel JuntaDirectiva, CargoJunta
**Dependencias:** comunidad 0001
"@

Write-Doc "apps\comunidad\migrations\0003_autoridad_foto" @"
# apps/comunidad/migrations/0003

**Operaciones:** AddField foto a Autoridad
**Dependencias:** comunidad 0002
"@

Write-Doc "apps\comunidad\migrations\0004_autoridad_descripcion_autoridad_dni_and_more" @"
# apps/comunidad/migrations/0004

**Operaciones:** AddField descripcion, dni, email, telefono a Autoridad; alter cargo_tipo choices, remove field cargo
**Dependencias:** comunidad 0003
"@

Write-Doc "apps\comunidad\migrations\0005_alter_autoridad_cargo_alter_autoridad_cargo_tipo" @"
# apps/comunidad/migrations/0005

**Operaciones:** AlterField cargo (max_length 255), cargo_tipo (max_length 50)
**Dependencias:** comunidad 0004
"@

Write-Doc "apps\comunidad\migrations\0006_autoridad_authoridad_anterior_and_more" @"
# apps/comunidad/migrations/0006

**Operaciones:** Autoridad add periodo_inicio, periodo_fin, autoridad_anterior (FK self); JuntaDirectiva add fecha_inicio, fecha_fin
**Dependencias:** comunidad 0005
"@

Write-Doc "apps\comunidad\migrations\0007_configuracioncomunidad_galeriaimagen_hitohistorico_and_more" @"
# apps/comunidad/migrations/0007

**Operaciones:** CreateModel ConfiguracionComunidad, GaleriaImagen, HitoHistorico, MarcoLegal, PaginaLegal, ComiteComunal
**Dependencias:** comunidad 0006
"@

Write-Doc "apps\comunidad\migrations\0008_mensaje_contacto_campos_admin" @"
# apps/comunidad/migrations/0008

**Operaciones:** CreateModel MensajeContacto (id, nombre, email, asunto, mensaje, leido, respondido, respuesta_admin, respondido_por FK Usuario null, created_at, updated_at)
**Dependencias:** comunidad 0007
"@

Write-Doc "apps\comunidad\migrations\0009_configuracioncomunidad_actualizado_por_and_more" @"
# apps/comunidad/migrations/0009

**Operaciones:** AddField actualizado_por, ultima_actualizacion a ConfiguracionComunidad
**Dependencias:** comunidad 0008
"@

Write-Doc "apps\content\migrations\0001_initial" @"
# apps/content/migrations/0001_initial.py

**Modelos:** Noticia (id, titulo, contenido, resumen, imagen, categoria FK, video, galeria JSON, fecha_publicacion, fecha_actualizacion, estado, fuente URL, vistas PositiveIntegerField), Evento (id, titulo, descripcion, fecha_evento, lugar, imagen), Comentario (id, contenido, noticia FK, autor FK Usuario, fecha_creacion, estado), Reaccion (id, tipo, noticia FK, autor FK Usuario, created_at)
**Dependencias:** comunidad 0001, accounts 0001
"@

Write-Doc "apps\content\migrations\0002_alter_reaccion_unique_together_comentario_evento_and_more" @"
# apps/content/migrations/0002

**Operaciones:** AlterUniqueTogether reaccion, AddField comentario.evento (FK), evento, alter noticia nullable; AddConstraint UniqueConstraint(tipo, autor, contenido_type+id)
**Dependencias:** content 0001
"@

Write-Doc "apps\content\migrations\0003_solicitudbaja_favorito_novedadvista" @"
# apps/content/migrations/0003

**Modelos nuevos:** SolicitudBaja, Favorito (usuario FK, tipo_contenido, contenido_id, fecha_guardado), NovedadVista (usuario FK, novedad_id, vista)
**Dependencias:** content 0002
"@

Write-Doc "apps\content\migrations\0004_evento_imagen_url_noticia_imagen_url" @"
# apps/content/migrations/0004

**Operaciones:** AddField imagen_url a Evento y Noticia (URLField blank)
**Dependencias:** content 0003
"@

Write-Doc "apps\content\migrations\0005_evento_vistas" @"
# apps/content/migrations/0005

**Operaciones:** AddField vistas a Evento (PositiveIntegerField default=0)
**Dependencias:** content 0004
"@

Write-Doc "apps\core\migrations\0001_initial" @"
# apps/core/migrations/0001_initial.py

**Modelos:** AuditLog (id, usuario FK null, accion, modelo, id_objeto, detalle JSON, direccion_ip, created_at)
**Dependencias:** Ninguna
"@

Write-Doc "apps\core\migrations\0002_alter_auditlog_accion" @"
# apps/core/migrations/0002

**Operaciones:** AlterField accion de AuditLog (max_length 100)
**Dependencias:** core 0001
"@

Write-Doc "apps\donaciones\migrations\0001_initial" @"
# apps/donaciones/migrations/0001_initial.py

**Modelos:** Donacion (id, usuario FK null, monto DecimalField, nombre_completo, email, telefono, tipo_documento, numero_documento, metodo_pago, estado CharField default=PENDIENTE, mp_preference_id, mp_payment_id, mp_payment_url, created_at, updated_at)
**Dependencias:** accounts 0001
"@

Write-Doc "apps\donaciones\migrations\0002_add_mp_notification_id" @"
# apps/donaciones/migrations/0002

**Operaciones:** AddField mp_notification_id a Donacion (CharField max=255 blank)
**Dependencias:** donaciones 0001
"@

Write-Doc "apps\messaging\migrations\0001_initial" @"
# apps/messaging/migrations/0001_initial.py

**Modelos:** Mensaje (id, remitente FK, destinatario FK, asunto, cuerpo, leido, created_at, updated_at), Notificacion (id, usuario FK, titulo, mensaje, tipo, leido, created_at)
**Dependencias:** accounts 0001
"@

Write-Doc "apps\messaging\migrations\0002_notificacion_referencia_id_and_more" @"
# apps/messaging/migrations/0002

**Operaciones:** AddField referencia_id, referencia_tipo a Notificacion
**Dependencias:** messaging 0001
"@

Write-Doc "apps\messaging\migrations\0003_alter_notificacion_tipo_and_more" @"
# apps/messaging/migrations/0003

**Operaciones:** AlterField tipo de Notificacion (max_length 50), alter referencia_tipo choices
**Dependencias:** messaging 0002
"@

Write-Doc "apps\reports\migrations\0001_initial" @"
# apps/reports/migrations/0001_initial.py

**Modelos:** ContactoMensaje (id, nombre, email, asunto, mensaje, leido, created_at), LibroReclamacion (id, tipo_reclamo, nombres, apellidos, dni 8, telefono 15, email, bien_contratado 200, monto_reclamado Decimal, descripcion, pedido, estado default=PENDIENTE, created_at, updated_at)
**Dependencias:** Ninguna
"@

Write-Doc "apps\reports\migrations\0002_libro_reclamacion_campos_legales" @"
# apps/reports/migrations/0002

**Operaciones:** AddField tipo_documento, numero_documento, direccion, departamento, provincia, distrito a LibroReclamacion
**Dependencias:** reports 0001
"@

Write-Doc "apps\reports\migrations\0003_alter_libroreclamacion_estado" @"
# apps/reports/migrations/0003

**Operaciones:** AlterField estado de LibroReclamacion (max_length 20, default=PENDIENTE)
**Dependencias:** reports 0002
"@

# === apps.py files ===
Write-Doc "apps\accounts\apps" @"
# apps/accounts/apps.py

**Nombre:** AccountsConfig (verbose_name: Cuentas)
**Ready:** Importa signals de accounts
"@

Write-Doc "apps\cms\apps" @"
# apps/cms/apps.py

**Nombre:** CmsConfig (verbose_name: CMS)
**Proposito:** Configuracion de la app cms (paginas estaticas)
"@

Write-Doc "apps\comunidad\apps" @"
# apps/comunidad/apps.py

**Nombre:** ComunidadConfig (verbose_name: Comunidad)
**Ready:** Importa signals de comunidad
"@

Write-Doc "apps\content\apps" @"
# apps/content/apps.py

**Nombre:** ContentConfig (verbose_name: Contenido)
**Ready:** Importa signals de content
"@

Write-Doc "apps\core\apps" @"
# apps/core/apps.py

**Nombre:** CoreConfig
**Ready:** Importa signals de core
"@

Write-Doc "apps\donaciones\apps" @"
# apps/donaciones/apps.py

**Nombre:** DonacionesConfig (verbose_name: Donaciones)
**Proposito:** Configuracion de la app donaciones (MercadoPago)
"@

Write-Doc "apps\messaging\apps" @"
# apps/messaging/apps.py

**Nombre:** MessagingConfig (verbose_name: Mensajeria)
**Proposito:** Configuracion de la app messaging
"@

Write-Doc "apps\reports\apps" @"
# apps/reports/apps.py

**Nombre:** ReportsConfig (verbose_name: Reportes)
**Proposito:** Configuracion de la app reports
"@

# === admin.py boilerplate ===
Write-Doc "apps\accounts\admin" @"
# apps/accounts/admin.py

**Proposito:** Admin site registration para Usuario, Comunero, PasswordReset, TipoUsuarioLog (via custom_admin_site de core)
"@

Write-Doc "apps\comunidad\admin" @"
# apps/comunidad/admin.py

**Proposito:** Admin site registration para Autoridad, Categoria, ConfiguracionComunidad, GaleriaImagen, HitoHistorico, MarcoLegal, PaginaLegal, ComiteComunal, MensajeContacto, JuntaDirectiva, CargoJunta
"@

Write-Doc "apps\content\admin" @"
# apps/content/admin.py

**Proposito:** Admin site registration para Noticia, Evento, Comentario, Reaccion, Favorito, SolicitudBaja
"@

Write-Doc "apps\core\admin" @"
# apps/core/admin.py

**Proposito:** Admin site registration para AuditLog y otros modelos core
"@

Write-Doc "apps\donaciones\admin" @"
# apps/donaciones/admin.py

**Proposito:** Admin site registration para Donacion
"@

Write-Doc "apps\messaging\admin" @"
# apps/messaging/admin.py

**Proposito:** Admin site registration para Mensaje, Notificacion
"@

Write-Doc "apps\reports\admin" @"
# apps/reports/admin.py

**Proposito:** Admin site registration para ContactoMensaje, LibroReclamacion
"@

Write-Output "Boilerplate done!"
