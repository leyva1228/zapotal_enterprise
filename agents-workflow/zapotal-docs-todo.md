# To-Do: Documentacion del proyecto Zapotal Enterprise

## Estado actual (auditado 2026-06-27)

### Backend Django (comunidad_zapotal_backend) - PRINCIPAL - ✅ 100%
- [x] apps/accounts (27/27 source files)
- [x] apps/cms (11/11)
- [x] apps/comunidad (44/44)
- [x] apps/content (18/18)
- [x] apps/core (27/27)
- [x] apps/donaciones (13/13)
- [x] apps/messaging (18/18)
- [x] apps/reports (19/19)
- [x] root-level files (6/6)
- [x] zapotal_config (5/5)
- **Total: 188/188 source files (100%)**

### Frontend React (comunidad_zapotal_frontend) - ✅ 100%
- [x] 122/122 source files (.js, .jsx, .css)
- Docs totales: 170 (incluye 25 index.md de seccion)

### Mobile BFF + Android + Legacy Backend (comunidad_zapotal_mobilebff_and_mobile_old) - ✅ 100% cobertura

#### zapotal-gateway (Spring Boot Mobile BFF)
- [x] 84/84 .java + 1/1 .xml = 85/85 source files
- Critical files mejorados: Application, Config (3), Security, Exception, Util, Controllers (12), Services (12), Clients (12), Favoritos module (5), DTOs (20+), pom.xml.

#### ComunidadZapotal3 (Android app)
- [x] 109/109 .kt + 3/3 .kts + 1/1 AndroidManifest.xml = 113/113 code files
- (159 archivos .xml de res/drawable/layout/values son assets visuales - no requieren per-file docs)
- Critical files mejorados: MainActivity, ApiService, RetrofitClient, AuthInterceptor, TokenAuthenticator, SessionManager, ApiConstants, NetworkErrorHandler, ReaccionCache, build.gradle.kts, AndroidManifest.xml.
- index.md para cada subfolder de UI/data.
- 9 docs >= 60 lineas, 48 docs medium (20-59).

#### comunidad_zapotal_backend (Legacy - NO usar como fuente principal)
- [x] 95/95 .py source files
- 161 docs (incluyen algunos archivos que NO existen en el legacy, son restos historicos)
- SEGUN AGENTS.md: no se mejora mas, se conserva como referencia.

## Resumen total

| Arbol | Source files | Docs | Estado |
|-------|-------------|------|--------|
| comunidad_zapotal_backend | 188 | 188 | ✅ 100% |
| comunidad_zapotal_frontend | 122 | 170 (con index.md) | ✅ 100% |
| zapotal-gateway | 85 | 114 (con index.md) | ✅ 100% |
| ComunidadZapotal3 | 113 code + 159 assets | 169 (con index.md) | ✅ 100% code |
| comunidad_zapotal_backend (legacy) | 95 | 161 (historico) | ✅ referencia |

## To-do cerrado

Todos los items del to-do original (cms, comunidad, content, core, donaciones, messaging, reports, root-level, zapotal_config) estan completados al 100%. No quedan items pendientes en el alcance del to-do del usuario.
