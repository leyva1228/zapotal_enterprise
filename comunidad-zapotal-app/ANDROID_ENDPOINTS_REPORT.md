# Android App - API Endpoints Report

## Información General
- **Framework:** Retrofit 2.11.0 + OkHttp
- **Base URL:** `http://192.168.0.6:8000/` (hardcodeada en `RetrofitClient.kt`)
- **Formato de datos:** JSON (Gson converter)

## Endpoints Detectados

### 1. Noticias
| Método | Endpoint | Uso | Archivo |
|--------|----------|-----|---------|
| GET | `api/noticias/` | Listar noticias | `NoticiasFragment.kt`, `HomeFragment.kt` |

### 2. Eventos
| Método | Endpoint | Uso | Archivo |
|--------|----------|-----|---------|
| GET | `api/eventos/` | Listar eventos | `EventosFragment.kt`, `HomeFragment.kt` |

### 3. Autoridades
| Método | Endpoint | Uso | Archivo |
|--------|----------|-----|---------|
| GET | `api/autoridades/` | Listar autoridades | `AutoridadesFragment.kt`, `HomeFragment.kt` |

### 4. Autenticación
| Método | Endpoint | Uso | Archivo |
|--------|----------|-----|---------|
| POST | `api/login/` | Iniciar sesión | `LoginActivity.kt` |
| POST | `api/register/` | Registrar usuario | `RegisterActivity.kt` |
| POST | `api/password_reset/` | Recuperar contraseña | `ForgotPasswordActivity.kt` |

### 5. Usuarios
| Método | Endpoint | Uso | Archivo |
|--------|----------|-----|---------|
| GET | `api/usuarios/{id}/` | Obtener usuario por ID | `InformacionUsuarioActivity.kt` |
| PUT | `api/usuarios/{id}/` | Actualizar usuario | `ApiService.kt` |
| POST | `api/usuarios/{id}/upload_photo/` | Subir foto de perfil | `ApiService.kt` |

### 6. Reacciones (Likes)
| Método | Endpoint | Uso | Archivo |
|--------|----------|-----|---------|
| POST | `api/reacciones/` | Crear/actualizar reacción | `NoticiaDetalleActivity.kt`, `EventoDetalleActivity.kt` |
| GET | `api/reacciones/conteo/{noticiaId}/` | Obtener conteo de reacciones | `NoticiaDetalleActivity.kt` |

## Resumen por Método

| Método | Cantidad |
|--------|----------|
| GET | 5 |
| POST | 4 |
| PUT | 1 |
| **Total** | **10** |

## Configuración de Red
- **Timeout:** No configurado explícitamente (usa defaults de Retrofit)
- **Interceptores:** Ninguno (no se maneja autenticación con token)
- **SSL:** No configurado (solo HTTP)

## Observaciones

1. **URL hardcodeada:** `http://192.168.0.6:8000/` - cambiar para producción
2. **Sin autenticación JWT:** No se envía token en headers
3. **Seguridad:** Usa HTTP, no HTTPS
4. **Endpoints no implementados en app:**
   - `/api/comentarios/` (aunque existe en backend)
   - `/api/categorias/`
   - `/api/mensajes/`
   - `/api/notificaciones/`
   - `/api/multimedia/`
   - `/api/contacto/`
   - `/api/libro-reclamaciones/`

## Archivos Clave
- `network/RetrofitClient.kt` - Configuración base URL
- `network/ApiService.kt` - Definición de interfaces Retrofit
- `ui/auth/LoginActivity.kt` - Login
- `ui/auth/RegisterActivity.kt` - Registro
- `ui/noticias/NoticiasFragment.kt` - Noticias
- `ui/eventos/EventosFragment.kt` - Eventos
- `ui/autoridades/AutoridadesFragment.kt` - Autoridades

---
*Reporte generado automáticamente por análisis de código fuente*