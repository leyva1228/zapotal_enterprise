$docsRoot = "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\docs\comunidad_zapotal_backend"

function Write-Doc($relPath, $content) {
    $fullPath = Join-Path $docsRoot "$relPath.py.md"
    $dir = Split-Path $fullPath -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $fullPath -Value $content -Encoding UTF8
    Write-Output "OK: $relPath.py.md"
}

Write-Doc "apps\accounts\models" @"
# apps/accounts/models.py

- **Ruta original:** comunidad_zapotal_backend/apps/accounts/models.py
- **Tecnologia:** Python / Django
- **Tipo:** Modelos de dominio
- **Proposito:** Define Usuario (AbstractBaseUser), Comunero, OTPVerification, PendingApproval

## Comunero
| Campo | Tipo | Constraints |
|-------|------|-------------|
| dni | CharField(8) | unique, db_index |
| nombres | CharField(100) | required |
| apellidos | CharField(100) | required |
| estado | CharField(10) | choices: ACTIVO/INACTIVO, default=ACTIVO, db_index |

**Propiedades:** nombre_completo. **Validacion:** clean() valida dni 8 digitos, nombres/apellidos no vacios. save() llama full_clean().

## UsuarioManager
- create_user(email, password, **extra_fields): normaliza email, set_password
- create_superuser(email, password, **extra_fields): is_staff=is_superuser=True, tipo_usuario=ADMIN

## OTPVerification
| Campo | Tipo | Constraints |
|-------|------|-------------|
| usuario | FK(Usuario) | CASCADE, related_name=otps |
| tipo | CharField(20) | choices: REGISTRO, RESET_PASSWORD, TWO_FA, CAMBIO_EMAIL, CAMBIO_TELEFONO |
| canal | CharField(10) | choices: EMAIL, SMS |
| codigo_hash | CharField(128) | SHA256 del codigo |
| destinatario | CharField(255) | |
| creado_en | DateTimeField | auto_now_add |
| expira_en | DateTimeField | |
| usado | BooleanField | default=False |
| intentos | PositiveIntegerField | default=0 |
| ip_solicitud | GenericIPAddressField | nullable |

**Metodos estaticos:** hash_codigo(codigo) -> sha256 hex. verificar_codigo(codigo_ingresado) -> bool.
**Meta:** db_table=otp_verification, indexes: (usuario,tipo,-creado_en), (expira_en)

## PendingApproval
| Campo | Tipo | Constraints |
|-------|------|-------------|
| usuario | OneToOneField(Usuario) | CASCADE, related_name=pending_approval |
| datos_registro | JSONField | default=dict |
| ip_registro | GenericIPAddressField | |
| user_agent_registro | CharField(255) | blank |
| oauth_provider | CharField(20) | blank |
| fecha_solicitud | DateTimeField | auto_now_add |
| revisado_por | FK(Usuario) | SET_NULL, null, related_name=aprobaciones_revisadas |
| fecha_revision | DateTimeField | null |
| notas_admin | TextField | blank |

**Meta:** db_table=pending_approval, ordering=[-fecha_solicitud]

## Usuario (AbstractBaseUser, PermissionsMixin)
| Campo | Tipo | Constraints |
|-------|------|-------------|
| comunero | OneToOneField(Comunero) | CASCADE, null, related_name=usuario |
| email | EmailField | unique, db_index, USERNAME_FIELD |
| tipo_usuario | CharField(10) | choices: ADMIN/COMUNERO/USUARIO, db_index |
| estado | CharField(20) | choices: PENDIENTE_OTP/PENDIENTE_APROBACION/ACTIVO/INACTIVO/BLOQUEADO/RECHAZADO, default=ACTIVO |
| foto_perfil | ImageField | upload_to=usuarios/perfiles/, nullable |
| fecha_registro | DateTimeField | auto_now_add |
| is_active | BooleanField | default=True |
| is_staff | BooleanField | default=False |
| email_verificado | BooleanField | default=False |
| telefono | CharField(15) | nullable |
| telefono_verificado | BooleanField | default=False |
| canal_verificacion | CharField(10) | choices: EMAIL, nullable |
| google_id | CharField(255) | nullable, db_index |
| proveedor_oauth | CharField(20) | nullable |
| two_factor_enabled | BooleanField | default=False |
| two_factor_secret | CharField(64) | nullable |
| two_factor_backup_codes | JSONField | default=list |
| two_factor_confirmed_at | DateTimeField | nullable |
| failed_login_attempts | PositiveIntegerField | default=0 |
| failed_otp_attempts | PositiveIntegerField | default=0 |
| locked_until | DateTimeField | nullable |
| last_password_change | DateTimeField | nullable |
| password_reset_required | BooleanField | default=False |
| aprobado_por | FK(self) | SET_NULL, null, related_name=usuarios_aprobados |
| fecha_aprobacion | DateTimeField | nullable |
| motivo_rechazo | TextField | blank |

**Propiedades:** nombre_completo, dni, iniciales, es_admin_efectivo
**Metodos:** get_autoridad_vigente() -> Autoridad|None (valida periodo)
**Meta:** db_table=usuario, ordering=[-fecha_registro]
"@

Write-Doc "apps\accounts\serializers" @"
# apps/accounts/serializers.py

## ComuneroSerializer (ModelSerializer)
| Campo | Tipo |
|-------|------|
| id, dni, nombres, apellidos, estado | directo |
| nombre_completo | CharField(read_only) |

## UsuarioSerializer (ModelSerializer)
| Campo | Tipo | Source |
|-------|------|--------|
| foto_perfil_url | SerializerMethodField | build_absolute_uri |
| nombre_completo, iniciales, nombres, apellidos, dni | SerializerMethodField | comunero asociado |
| es_admin | SerializerMethodField | es_admin_efectivo |
| es_autoridad | SerializerMethodField | get_autoridad_vigente |
| autoridad_cargo | SerializerMethodField | autoridad.cargo |

**Read only:** id, fecha_registro, is_active, is_staff, is_superuser

## UsuarioEscrituraSerializer (ModelSerializer)
| Campo | Tipo |
|-------|------|
| password | CharField(write_only, min_length=6) |
| foto_perfil_url | SerializerMethodField |

**create:** set_password antes de guardar. **update:** set_password si cambia.

## LoginSerializer (Serializer)
- **Campos:** email, password
- **validate:** authenticate -> LOGIN_FAILED audit si falla

## LoginResponseSerializer
- **Campos:** access, refresh, usuario(UsuarioSerializer), requiere_otp

## PendingApprovalSerializer
- **Campos:** id, usuario, usuario_email, usuario_nombre, usuario_dni, datos_registro, ip_registro, user_agent_registro, oauth_provider, fecha_solicitud, revisado_por, fecha_revision, notas_admin
"@

Write-Doc "apps\accounts\services" @"
# apps/accounts/services.py

## AuthService
| Metodo | Params | Returns | Description |
|--------|--------|---------|-------------|
| authenticate_user | email, password | Usuario|None | Autentica por email/password, valida estado activo/pendiente |
| issue_tokens | user | (access, refresh) | Genera JWT tokens via SimpleJWT |
| issue_short_token | user | str | Token temporal 5 min para paso 2FA (scope=pre_2fa) |
| validate_pre_2fa_token | token | Usuario|None | Valida token pre-2FA |

## UsuarioService (todos @transaction.atomic)
- create_user_with_comunero(email, password, tipo_usuario, comunero_data): Crea Comunero + Usuario
- change_password(user, new_password): min 6 chars
- activate/deactivate(user): Cambia estado/ACTIVO INACTIVO

## ComuneroService
- create_comunero(dni, nombres, apellidos, **extra): Crea Comunero

## EmailService
- _is_dev(): DEBUG=True sin API key Resend -> True (loguea en consola)
- _add_deliverability_headers(msg, destinatario): Reply-To, List-Unsubscribe, X-Mailer
- enviar_otp(destinatario, codigo, tipo): Email HTML con branding, codigo 36px Courier, 10 min validez
- enviar_notificacion(destinatario, asunto, cuerpo, html): Transaccional generico
- enviar_bienvenida(destinatario, nombre): Email aprobacion de cuenta con boton login
- enviar_rechazo(destinatario, motivo): Email de rechazo

## OTPService
| Constante | Valor |
|-----------|-------|
| LONGITUD_CODIGO | 6 |
| VALIDEZ_MINUTOS | 5 |
| MAX_INTENTOS | 5 |
| COOLDOWN_REENVIO_SEGUNDOS | 60 |

- generar_y_enviar(usuario, tipo, destinatario, ip): Cooldown 60s, SHA256 hash, crea OTP + envia email
- verificar(usuario, tipo, codigo_ingresado, ip): Match contra CUALQUIER OTP activo (race condition de emails lentos), marca todos usados, incrementa intentos

## TurnstileService
- verify(token, ip): POST a Cloudflare Turnstile siteverify. Fail-open en dev (secret placeholder)

## TwoFAService
- generar_secreto(): pyotp.random_base32(32)
- otpauth_url(usuario, secreto): provisioning_uri con issuer
- qr_code_base64(otpauth_url): QR via qrcode library, base64 PNG
- verificar_codigo(secreto, codigo, ventana=1): TOTP verify
- backup_codes_plain/generar_backup_codes(): tokens hex 4 bytes
- iniciar_setup(usuario): secreto + QR + backup_codes (no activa)
- confirmar_setup(usuario, secreto, codigo, ip): Verifica codigo TOTP, activa 2FA, guarda backup codes hasheados
- validar(usuario, codigo, ip): TOTP o backup code, consume backup code usado
- desactivar(usuario, password_actual, ip): Requiere password actual
"@

Write-Doc "apps\accounts\views" @"
# apps/accounts/views.py

## ComuneroViewSet (ModelViewSet)
- **queryset:** Comunero.objects.all()
- **serializer:** ComuneroSerializer
- **permisos:** IsAdminUser (escritura), lectura publica via override
- **filtros:** estado, search(dni, nombres, apellidos), ordering(apellidos, nombres, dni)

## UsuarioViewSet (ModelViewSet)
- **queryset:** Usuario.objects.select_related('comunero')
- **permisos variables:**
  - list/destroy: IsAdminUser
  - retrieve/update/partial_update: IsAuthenticated (self-service OK)
- **get_permissions:** retrieve/update/partial_update relaja a IsAuthenticated
- **get_serializer_class:** create/update -> UsuarioEscrituraSerializer, lectura -> UsuarioSerializer
- **get_queryset:** Admin ve todos, usuarios normales solo su propio id
- **filter_queryset (LOOP 1):** Magic value PENDIENTE mapea a PENDIENTE_OTP + PENDIENTE_APROBACION. Search extends a comunero__nombres, comunero__apellidos, comunero__dni.
- **get_object:** Usuario autenticado puede ver SU propio perfil; otro usuario -> PermissionDenied
- **partial_update:** Bloquea activacion de PENDIENTE_OTP (debe verificar email primero), notifica cambios de estado

## Funciones helper
- **login_usuario** (POST, AllowAny, LoginThrottle): Login con JWT. Chequea estados BLOQUEADO/RECHAZADO/INACTIVO/PENDIENTE_OTP. Si 2FA, delega a login_usuario_v2. Retorna access, refresh, usuario, requiere_otp.
- **register_usuario** (POST, IsAdminUser, RegisterThrottle): Registro administrativo. Solo ADMIN. Crea via UsuarioEscrituraSerializer.
"@

Write-Doc "apps\accounts\views_auth" @"
# apps/accounts/views_auth.py

## Endpoints de Registro Publico
- **registro_iniciar** (POST, AllowAny, RegisterThrottle): Flujo: ZeroBounce -> Turnstile -> valida password (min length, mayuscula, digito) -> crea Comunero+Usuario PENDIENTE_OTP -> envia OTP email. Si email existe y esta PENDIENTE_OTP, re-envia OTP.
- **registro_verificar_otp** (POST, AllowAny, OTPThrottle): Verifica OTP -> estado PENDIENTE_APROBACION -> crea PendingApproval -> notifica a admines via Notificacion in-app.
- **registro_reenviar_otp** (POST, AllowAny, OTPThrottle): Re-envia OTP con cooldown 60s.

## Login + 2FA
- **login_usuario_v2** (POST, AllowAny): Si 2FA desactivado -> tokens directos. Si 2FA activado -> {requires_2fa:true, token_temp, usuario_id} (202).
- **auth_verify_2fa_login** (POST, AllowAny): Valida token_temp + TOTP o backup code -> emite JWT reales.
- **auth_logout** (POST, IsAuthenticated): Blacklist refresh token.

## 2FA Setup
- **twofa_setup** (POST, IsAuthenticated): Inicia setup -> secreto, QR, backup codes. NO activa.
- **twofa_confirm** (POST, IsAuthenticated): Body {secret, codigo}. Activa 2FA si codigo TOTP correcto.
- **twofa_disable** (POST, IsAuthenticated): Body {password}. Requiere password actual.

## Password Reset
- **password_reset_request** (POST, AllowAny, ResetPasswordThrottle): ZeroBounce -> OTP reset password. Anti-enumeracion: siempre responde 200.
- **password_reset_confirm** (POST, AllowAny, ResetPasswordThrottle): OTP + nueva_password. Revoca tokens previos.

## Cambio Password
- **cambiar_password** (POST, IsAuthenticated): Body {password_actual, password_nueva}. Actualiza last_password_change, resetea password_reset_required.
"@

Write-Doc "apps\accounts\views_admin" @"
# apps/accounts/views_admin.py

## Endpoints
- **pending_users** (GET, IsAdminUser): Lista usuarios PENDIENTE_APROBACION con datos de pending_approval.
- **approve_user** (POST, IsAdminUser, user_id): Valida estado, atomic: ACTIVO + is_active + aprobado_por + fecha_aprobacion. Envia email bienvenida + notificacion in-app.
- **reject_user** (POST, IsAdminUser, user_id): RECHAZADO + motivo_rechazo. Email rechazo + notificacion.
- **block_user** (POST, IsAdminUser, user_id): BLOQUEADO + revoca tokens. Notificacion.
- **unblock_user** (POST, IsAdminUser, user_id): ACTIVO + resetea failed_login_attempts + locked_until. Notificacion.
"@

Write-Doc "apps\accounts\urls" @"
# apps/accounts/urls.py

## Router
- /api/v1/usuarios/ (UsuarioViewSet)
- /api/v1/comuneros/ (ComuneroViewSet)

## URL Patterns
| Ruta | View | Metodo |
|------|------|--------|
| login/ | login_usuario | POST |
| register/ | register_usuario | POST |
| token/refresh/ | TokenRefreshView | POST |
| token/blacklist/ | TokenBlacklistView | POST |
| auth/login/ | login_usuario_v2 | POST |
| auth/2fa/verify-login/ | auth_verify_2fa_login | POST |
| auth/2fa/setup/ | twofa_setup | POST |
| auth/2fa/confirm/ | twofa_confirm | POST |
| auth/2fa/disable/ | twofa_disable | POST |
| auth/logout/ | auth_logout | POST |
| registro/iniciar/ | registro_iniciar | POST |
| registro/verificar-otp/ | registro_verificar_otp | POST |
| registro/reenviar-otp/ | registro_reenviar_otp | POST |
| password-reset/request/ | password_reset_request | POST |
| password-reset/confirm/ | password_reset_confirm | POST |
| usuarios/<id>/cambiar-password/ | cambiar_password | POST |
| usuarios/pendientes/ | pending_users | GET |
| usuarios/<id>/aprobar/ | approve_user | POST |
| usuarios/<id>/rechazar/ | reject_user | POST |
| usuarios/<id>/bloquear/ | block_user | POST |
| usuarios/<id>/desbloquear/ | unblock_user | POST |
"@

Write-Doc "apps\accounts\tests" @"
# apps/accounts/tests.py

## TestLoginEndpoint
- test_login_success_returns_jwt_tokens: 200 + access/refresh
- test_login_invalid_credentials_returns_400: 400, no user enumeration
- test_login_nonexistent_user_returns_400: 400
- test_login_inactive_user_returns_403: 403
- test_login_short_password_rejected: 400 (serializer validation)
- test_password_not_exposed_in_user_serializer: password ausente en GET

## TestUsuarioService
- test_create_user: create_user_with_comunero
- test_create_comunero_requires_comunero_data: ValueError si comunero_data=None
- test_change_password: check_password post cambio
- test_activate_deactivate: estados ACTIVO/INACTIVO
"@

Write-Doc "apps\accounts\tests\test_otp" @"
# apps/accounts/tests/test_otp.py

## TestOTPService
- test_generar_crea_registro: Crea OTP, verifica campos
- test_verificar_otp_exitoso: Codigo valido -> True, segundo uso falla
- test_verificar_otp_incorrecto: ValidationError
- test_sin_otp_pendiente: ValidationError
- test_otp_expirado: ValidationError con 'expir'
- test_max_intentos: ValidationError con 'intentos'
- test_otp_anterior_no_se_invalida_al_generar_nuevo: Race condition fix - OTP previo no se marca usado
- test_codigo_de_otp_anterior_tambien_valida: Multiples OTPs -> cualquiera funciona
- test_codigo_incorrecto_no_consume_otros_otps: Solo incrementa intentos del mas reciente
"@

Write-Doc "apps\accounts\tests\test_registro_verificar_view" @"
# apps/accounts/tests/test_registro_verificar_view.py

## TestRegistroVerificarOtpView
- test_verificar_otp_valido_promueve_usuario_y_crea_pending_approval: PENDIENTE_OTP -> PENDIENTE_APROBACION + PendingApproval con ip_registro
- test_verificar_otp_no_promueve_si_codigo_es_incorrecto: 400, estado no cambia, no PendingApproval
- test_verificar_otp_no_requiere_autenticacion: Endpoint publico, 200 sin credenciales
"@

Write-Doc "apps\accounts\tests\test_zerobounce_auth" @"
# apps/accounts/tests/test_zerobounce_auth.py

## TestRegistroZeroBounce
- test_email_disposable_rechazado_400: disposable@example.com -> 400 EMAIL_INVALID
- test_email_invalid_rechazado_400: invalid@example.com -> 400
- test_email_valid_aceptado_201: valid@example.com -> 201 (o 400 por Turnstile)
- test_email_no_reservado_fail_open_201: unknown -> fail-open
- test_sin_api_key_fail_open: Sin ZEROBOUNCE_API_KEY -> fail-open

## TestPasswordResetZeroBounce
- test_email_disposable_responde_200_sin_otp: 200 anti-enumeracion, sin OTP creado
- test_email_invalid_responde_200_sin_otp: 200, sin OTP
- test_email_valido_intenta_enviar_otp: 200 generico anti-enumeracion

## TestAuditLogZB
- test_registro_bloqueado_registra_audit: AuditLog con accion=REG_ZB_BLOCK
- test_reset_bloqueado_registra_audit: AuditLog con accion=PASSRESET_ZB_BLOCK
"@

Write-Doc "apps\accounts\tests\test_filtros_usuarios" @"
# apps/accounts/tests/test_filtros_usuarios.py

## TestFiltroEstadoPendiente (LOOP 1.1)
- test_pendiente_devuelve_otp_y_aprobacion: ?estado=PENDIENTE -> ambos estados pendientes
- test_pendiente_otp_solo: ?estado=PENDIENTE_OTP -> solo ese estado
- test_pendiente_aprobacion_solo: ?estado=PENDIENTE_APROBACION -> solo ese estado
- test_bloqueado: filtro normal funciona
- test_activo: filtro normal funciona

## TestSearchPorNombre (LOOP 1.2)
- test_search_por_email: search por email parcial
- test_search_por_dni: search por DNI via comunero
- test_search_sin_match: 200 con count=0
- test_search_con_acentos: icontains funciona con acentos

## TestCombinacionFiltros (LOOP 1.3)
- test_estado_mas_search: ?estado=PENDIENTE&search=pendiente1
- test_tipo_usuario_comunero: ?tipo_usuario=COMUNERO
- test_tipo_usuario_admin: ?tipo_usuario=ADMIN

## TestPaginacion (LOOP 1.4)
- test_paginacion_devuelve_count_y_next: count + results
- test_paginacion_page_size_20: page_size=20
- test_paginacion_page_invalido_retorna_404_o_ultima: 404 para pagina fuera de rango
"@

Write-Doc "apps\accounts\tests\test_foto_perfil" @"
# apps/accounts/tests/test_foto_perfil.py

## TestFotoPerfilUpload
- test_upload_foto_perfil_retorna_url_valida: PATCH multipart -> URL absoluta, no ruta local
- test_upload_persiste_en_db: Archivo guardado en storage
- test_foto_perfil_null_limpia_campo: foto_perfil='' -> None
- test_storage_url_no_es_endpoint_s3_interno: CloudflareR2Storage usa dominio publico
- test_usuario_no_puede_editar_otro_perfil: 403/404 al editar perfil ajeno
- test_sin_auth_no_puede_subir: 401
- test_get_propio_perfil_funciona_sin_ser_admin: GET propio perfil -> 200
- test_get_otro_usuario_bloqueado: GET perfil ajeno -> 403/404
- test_sin_auth_no_puede_get: 401

## TestStorageBackendURL
- test_url_con_public_domain: public domain correcto
- test_url_sin_public_domain_cae_a_s3_endpoint: fallback a S3 endpoint
- test_url_con_public_domain_sin_protocol: agrega https://
- test_url_con_public_domain_con_slash_final: limpia slash final
"@

Write-Doc "apps\accounts\management\commands\cleanup_expired_registrations" @"
# apps/accounts/management/commands/cleanup_expired_registrations.py

**Proposito:** Elimina usuarios PENDIENTE_OTP cuyo OTP expiro hace mas de OTP_CLEANUP_GRACE_MINUTES (default 15) + OTP_VALIDITY_MINUTES (default 10) minutos.
**Flags:** --dry-run (solo muestra)
**Proceso:** Busca ultimo OTP de cada usuario, si expiro -> elimina OTPs + PendingApproval + Usuario (CASCADE borra Comunero). Escribe AuditLog.
"@

Write-Doc "apps\accounts\management\commands\cleanup_otps" @"
# apps/accounts/management/commands/cleanup_otps.py

**Proposito:** Elimina OTPs expirados y usados.
**Flags:** --days N (default 1). No elimina OTPs pendientes activos.
"@

Write-Doc "apps\accounts\management\commands\ensure_admin" @"
# apps/accounts/management/commands/ensure_admin.py

**Proposito:** Crea superusuario por defecto si no existe ninguno.
**Config:** Lee DJANGO_SUPERUSER_EMAIL (default admin@zapotal.com) y DJANGO_SUPERUSER_PASSWORD (default Admin123456) de .env via decouple.
"@

Write-Output "All accounts docs created!"
