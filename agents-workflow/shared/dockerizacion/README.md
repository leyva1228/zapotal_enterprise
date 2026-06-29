# Dockerización Comunidad Zapotal — Visión General

## Índice de documentos

| Archivo | Servicio | Stack |
|---------|----------|-------|
| [01-backend-django.md](./01-backend-django.md) | Backend API | Django 6.0 + DRF + MySQL + Uvicorn |
| [02-frontend-react.md](./02-frontend-react.md) | Frontend Web | React 19 + Vite + Nginx |
| [03-mobile-bff.md](./03-mobile-bff.md) | Mobile BFF | Spring Boot 3.5 + Java 17 + Maven |
| [04-mobile-kotlin.md](./04-mobile-kotlin.md) | App Android | Kotlin + Jetpack Compose (futuro) |
| [05-docker-compose-orquestacion.md](./05-docker-compose-orquestacion.md) | Orquestación | Docker Compose + redes + volúmenes |

---

## Arquitectura actual del proyecto

```
zapotal_enterprise/
├── comunidad_zapotal_backend/      # API REST Django (puerto 8000)
│   ├── apps/
│   │   ├── accounts/              # Usuarios, auth JWT, OTP, OAuth
│   │   ├── content/               # Noticias, eventos, comentarios, reacciones, multimedia
│   │   ├── comunidad/             # Autoridades, jerarquía comunal
│   │   ├── messaging/             # Mensajería privada
│   │   ├── reports/               # Libro de reclamaciones
│   │   ├── cms/                   # Contenido estático, novedades
│   │   └── core/                  # AuditLog, permisos, paginación, healthcheck
│   ├── zapotal_config/            # settings, urls, wsgi, asgi
│   ├── deploy/                    # uvicorn.conf.py
│   └── manage.py
├── comunidad_zapotal_frontend/    # SPA React (puerto 5173 dev, 80 prod)
│   ├── src/                       # Componentes, páginas, context, hooks
│   ├── vite.config.js             # Proxy /api → localhost:8000
│   └── package.json               # React 19, Vite 5, React Router 7
├── comunidad_zapotal_mobile_bff/  # BFF para app móvil (puerto 8080)
│   ├── src/main/java/com/comunidad/bff/
│   │   ├── client/                # 10 Feign-like WebClient clients → Django API
│   │   ├── controller/            # 10 REST controllers
│   │   ├── service/               # Lógica de negocio
│   │   ├── dto/                   # Data Transfer Objects
│   │   ├── config/                # WebClient, DjangoProperties
│   │   └── security/             # SecurityConfig
│   └── pom.xml                    # Spring Boot 3.5.15, Java 17
└── docs/
    └── dockerizacion/             # ← Esta carpeta
```

## Comunicación entre servicios

```
┌─────────────┐    ┌──────────────────┐    ┌────────────┐
│  Navegador   │───▶│  Frontend React  │───▶│  Django    │
│  (usuario)   │◀───│  Nginx (80/443)  │◀───│  API:8000  │
└─────────────┘    └──────────────────┘    └─────┬──────┘
                                                  │
                                          ┌───────▼───────┐
                                          │   MySQL 3306  │
                                          └───────────────┘

┌─────────────┐    ┌──────────────────┐    ┌────────────┐
│  App Android │───▶│  Mobile BFF      │───▶│  Django    │
│  (futura)    │◀───│  Spring :8080    │◀───│  API:8000  │
└─────────────┘    └──────────────────┘    └────────────┘
```

## Principios de dockerización

1. **Un servicio = un contenedor**: cada componente en su propio Dockerfile.
2. **Multi-stage builds**: etapa de build + etapa de runtime (imágenes pequeñas).
3. **No root en producción**: cada contenedor corre con usuario sin privilegios.
4. **Variables de entorno**: toda configuración sensible via `.env` / env vars, nunca hardcodeada.
5. **Healthchecks**: cada servicio expone `/health` para que el orquestador lo monitoree.
6. **Redes aisladas**: frontend↔backend por red interna; solo Nginx expuesto al host.
7. **Volúmenes nombrados**: datos persistentes (MySQL, media) en volúmenes Docker.
8. **Capas de caché**: copiar `requirements.txt` / `package.json` antes del código fuente.
9. **`.dockerignore`**: excluir venv, node_modules, .git, __pycache__, target/, etc.
10. **Escalabilidad horizontal**: cada contenedor es stateless (sin sesiones locales, sin archivos pegados al filesystem del contenedor).

## Estado de implementación

| Servicio | Dockerfile actual | Estado |
|----------|-------------------|--------|
| Backend Django | No existe | 📋 Documentado, listo para implementar |
| Frontend React | No existe | 📋 Documentado, listo para implementar |
| Mobile BFF | No existe | 📋 Documentado, listo para implementar |
| Mobile App Kotlin | No existe (ni el proyecto) | 📋 Documentado como guía futura |
| Docker Compose | No existe | 📋 Documentado, listo para implementar |
