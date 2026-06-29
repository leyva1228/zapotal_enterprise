# 04 — App Android Kotlin (Futura): Dockerización

## Contexto

La app móvil `zapotal_app_kotlin` **aún no existe** como proyecto. Está listada en `docs/VERSIONING.md` como `🔄 Pendiente`. Este documento es una **guía de planificación** para cuando se cree el proyecto Android nativo con Kotlin, y cómo se relaciona con la infraestructura Docker.

## Consideración fundamental: una app Android NO se dockeriza como servicio

A diferencia del backend, frontend web y BFF, **una app Android nativa no se ejecuta dentro de un contenedor Docker**. Sin embargo, la dockerización es relevante para:

| Componente | Dockerizable | Propósito |
|------------|-------------|----------|
| **Build de la app** (APK/AAB) | ✅ Sí | CI/CD reproducible |
| **Servicio de backend que la app consume** | ✅ Sí (BFF ya documentado) | Ya cubierto en [03-mobile-bff.md](./03-mobile-bff.md) |
| **Servidor de notificaciones push** | ✅ Sí | Futuro: Firebase Cloud Messaging o servicio propio |
| **Emulador Android en CI** | ✅ Sí | Tests instrumentados en pipelines |
| **La app en el teléfono del usuario** | ❌ No | Se instala como APK/AAB vía Play Store |

## Stack tecnológico recomendado

| Tecnología | Versión | Rol |
|-----------|---------|-----|
| Kotlin | 2.0+ | Lenguaje principal |
| Jetpack Compose | BOM 2024+ | UI declarativa |
| Material Design 3 | - | Diseño visual |
| Kotlin Coroutines + Flow | - | Async/reactive |
| Hilt (Dagger) | - | Inyección de dependencias |
| Retrofit + OkHttp | - | Cliente HTTP → BFF |
| Coil | - | Carga de imágenes |
| DataStore (Preferences) | - | Storage local |
| Room | - | Base de datos local (SQLite) |
| Navigation Compose | - | Routing in-app |
| Ktor o Retrofit | - | Comunicación con BFF :8080 |
| Gradle Kotlin DSL | 8.x | Build tool |

## Estructura de proyecto propuesta

```
zapotal_app_kotlin/
├── app/
│   ├── src/main/
│   │   ├── java/com/zapotal/app/
│   │   │   ├── MainActivity.kt
│   │   │   ├── ui/                    # Compose screens
│   │   │   │   ├── auth/              # Login, registro, OTP
│   │   │   │   ├── home/              # Dashboard
│   │   │   │   ├── noticias/          # Noticia list + detail
│   │   │   │   ├── eventos/            # Evento list + detail
│   │   │   │   ├── mensajes/           # Mensajería
│   │   │   │   ├── perfil/            # Perfil, 2FA
│   │   │   │   └── reclamos/          # Libro reclamaciones
│   │   │   ├── data/                  # Repository pattern
│   │   │   │   ├── remote/             # Retrofit API service
│   │   │   │   ├── local/             # Room DAO, DataStore
│   │   │   │   └── repository/         # Repository impl
│   │   │   ├── domain/                # Use cases, models
│   │   │   ├── di/                    # Hilt modules
│   │   │   └── navigation/            # NavHost, routes
│   │   ├── res/                        # Resources Android
│   │   └── AndroidManifest.xml
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── build.gradle.kts                   # Root
├── settings.gradle.kts
├── gradle.properties
└── gradle/
    └── wrapper/
```

## Dockerfile para build de la app

Este Dockerfile permite compilar el APK/AAB dentro de un contenedor Docker, útil para CI/CD:

```dockerfile
# ── Build de APK en contenedor (CI/CD) ──
FROM ubuntu:24.04 AS builder

ENV ANDROID_HOME=/opt/android-sdk

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://dl.google.com/android/commandlinetools/latest/commandlinetools-linux-11047088_latest.zip \
    -O /tmp/cmd-tools.zip \
    && mkdir -p ${ANDROID_HOME}/cmdline-tools \
    && unzip -q /tmp/cmd-tools.zip -d ${ANDROID_HOME}/cmdline-tools \
    && mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest \
    && rm /tmp/cmd-tools.zip

ENV PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${PATH}"

RUN yes | sdkmanager --licenses > /dev/null 2>&1 \
    && sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

WORKDIR /app
COPY . .

RUN chmod +x gradlew \
    && ./gradlew assembleRelease --no-daemon --stacktrace

# ── Etapa de salida: solo el APK ──
FROM alpine:3.20 AS release
COPY --from=builder /app/app/build/outputs/apk/release/*.apk /output/
```

### Uso en CI/CD

```bash
# Build del APK en contenedor
docker build -t zapotal-android-build . -f Dockerfile.android

# Extraer el APK
docker create --name extract zapotal-android-build
docker cp extract:/output app-release.apk
docker rm extract
```

## .dockerignore

```
.gradle/
build/
app/build/
*.apk
*.aab
local.properties
.idea/
*.iml
```

## Comunicación con la infraestructura Docker

La app Android se conecta al **Mobile BFF** (Spring Boot en puerto 8080), no directamente al backend Django:

```
┌──────────────┐      HTTPS       ┌───────────────────┐     HTTP      ┌───────────────┐
│ App Android   │ ───────────────▶ │ Mobile BFF :8080  │ ───────────▶ │ Django :8000  │
│ (Kotlin)      │ ◀─────────────── │ (Spring Boot)     │ ◀─────────── │ (API REST)    │
└──────────────┘                   └───────────────────┘              └───────┬───────┘
                                                                             │
                                                                     ┌───────▼───────┐
                                                                     │ MySQL :3306    │
                                                                     └───────────────┘
```

### Configuración en la app

```kotlin
// En BuildConfig o un objeto de configuración
object ApiConfig {
    // Desarrollo: apunta al BFF local
    const val DEV_BASE_URL = "http://10.0.2.2:8080"  // emulador → host

    // Producción: apunta al BFF expuesto
    const val PROD_BASE_URL = "https://bff.zapotal.app"
}
```

## Variables de entorno de la app (en el dispositivo)

| Variable | Uso |
|----------|-----|
| `BASE_URL` | URL del Mobile BFF |
| `TURNSTILE_SITE_KEY` | Clave pública de Cloudflare Turnstile (si se usa en app) |
| `FIREBASE_API_KEY` | Para notificaciones push |
| `FIREBASE_PROJECT_ID` | Proyecto Firebase |
| `FIREBASE_APP_ID` | App ID Firebase |

> Estas variables se configuran en `build.gradle.kts` como `buildConfigField`, no como env vars del sistema. Se "cuecen" en el APK al compilar.

## Consideraciones críticas

### 1. Firma del APK
En CI/CD dentro de Docker, se necesita el keystore de firma:

```groovy
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
}
```

En el Dockerfile de CI, montar el keystore como volumen o usar BuildKit secrets:
```dockerfile
RUN --mount=type=secret,id=keystore \
    cp /run/secrets/keystore release.keystore \
    && ./gradlew assembleRelease \
    && rm release.keystore
```

### 2. Emulador Android en Docker para tests
Si se quieren ejecutar tests instrumentados (UI tests) en CI:

```dockerfile
FROM us-docker.pkg.dev/android-emulator-2687195653688137701/aem-image/emulator:latest
# Imagen oficial de Google para emulador Android en Docker
# Ver: https://github.com/google/android-emulator-container-scripts
```

Requisitos: KVM habilitado en el host (limitado en algunos Cloud providers).

### 3. Tamaño de la imagen de build Android
La imagen de build es pesada (~2-3 GB) por el SDK de Android. Esto solo se usa en CI/CD, no en producción. La "imagen de producción" de la app es el APK generado.

### 4. Google Play Store deployment
El APK/AAB generado en Docker se sube a Google Play Console vía API (`google-play-publisher` Gradle plugin o `fastlane`). No se distribuye desde un contenedor.

### 5. ProGuard / R8
La app debe ofuscar y optimizar el código en release:
```groovy
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

## Notas para escalabilidad futura

1. **Notificaciones push**: si se implementa FCM (Firebase Cloud Messaging), se puede crear un contenedor Docker que ejecute un servidor de push (o usar Firebase directamente, serverless).
2. **Feature flags**: Remote Config de Firebase permite habilitar/deshabilitar features sin publicar nueva versión.
3. **Actualizaciones in-app**: si se implementa Play Core Library, la app puede descargar módulos bajo demanda.
4. **CI/CD pipeline recomendado**: GitHub Actions + Docker build + Firebase Test Lab + Google Play Publisher.

## Resumen: ¿qué se dockeriza de la app Android?

| Componente | Docker | Tipo |
|-----------|--------|------|
| Build del APK/AAB | ✅ | `Dockerfile.android` en CI/CD |
| Tests unitarios | ✅ | Contenedor de Gradle, sin emulador |
| Tests instrumentados (UI) | ⚠️ | Posible con emulador Docker + KVM |
| Distribución al usuario | ❌ | Play Store / sideloading |
| Servicios que consume la app | ✅ | BFF, backend, MySQL (ya documentados) |
