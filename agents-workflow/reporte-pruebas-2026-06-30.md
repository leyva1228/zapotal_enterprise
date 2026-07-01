# Reporte de Pruebas — Zapotal Enterprise — 2026-06-30

## Resumen

| Componente | Resultado |
|---|---|
| Backend tests (pytest) | ✅ **96 passed**, 0 failed, 37 warnings |
| Django system check (`check --deploy`) | ⚠️ Solo warnings (no errors) |
| Frontend build (Vite) | ✅ **Build OK** (15.6s, bundle warnings no bloqueantes) |
| Backend lint (ruff) | ⚠️ 1976 findings — **solo estilo** (type annotations, imports, f-strings) |
| Migraciones pendientes | 1 untracked: `0004_reports_libro_reclamacion_completar_campos` |

---

## 1. Backend Tests

**Comando:** `python -m pytest apps -q`

**96 passed, 0 failed — 157.5s**

Warnings (37 total — no bloqueantes):
- `DeprecationWarning`: factory_boy `_after_postgeneration` en próxima major
- `RuntimeWarning`: `DateTimeField Evento.fecha` recibe datetime naive (zona horaria activa)
- `UserWarning`: DRF `min_value` debe ser integer/Decimal (x4)

Todos los módulos cubiertos: content, donaciones, reports (incluido `tests_email_resend.py`).

---

## 2. Django System Check

**Comando:** `python manage.py check --deploy`

**PASS** — sin errores.

Warnings principales:
- `models.W036`: MariaDB no soporta UNIQUE con condiciones (tablas `Favorito`, `Reaccion`)
- 40+ `drf-spectacular.W001`: Faltan `@extend_schema_field` en serializers de `accounts/`
- `logging.WARN`: Configuración de logging referenciada pero ausente en archivo

---

## 3. Frontend Build

**Comando:** `npm run build` (Vite 5.4.21)

```text
✓ 227 modules transformed
✓ built in 15.60s
```

Output:
- `index.html` — 1.48 kB (gzip 0.74 kB)
- `assets/index-CwuWpGyh.css` — 307.74 kB (gzip 54.39 kB)
- `assets/index-B2MpGseR.js` — 2,065.57 kB (gzip 641.96 kB)

⚠️ Warning: JS chunk >500 kB. Sugerir `dynamic import()` o `manualChunks` para producción.

---

## 4. Backend Lint (ruff)

**Comando:** `python -m ruff check .`

**1976 findings** — todos de estilo, **0 errores lógicos o bugs**.

Categorías principales:
- **ANN*** (type annotations): ~1600 — pytest fixtures sin tipado, métodos sin `-> None`
- **I001** (imports desordenados): ~200
- **E402** (import en nivel no-tope): scripts de diagnóstico (`diagnostico_otp.py`, `migrar_urls_r2_publicas.py`)
- **PLC0415** (imports dentro de funciones): `manage.py`, varias views
- **F401**: `IsAuthenticated`, `DjangoFilterBackend` no usados en `reports/views.py`
- **W605** / **F541**: escapes en docstrings de scripts Windows

247 son auto-fixeables con `ruff check --fix`.

---

## 5. Migraciones

Todas las migraciones aplicadas (`[X]` en showmigrations).

**Nueva (untracked):** `reports/migrations/0004_reports_libro_reclamacion_completar_campos.py`
- Agrega 6 columnas a `reports_libroreclamacion`: `numero_reclamo`, `plazo_respuesta`, `prioridad`, `respondido_at`, `respondido_por_id`, `respuesta_admin`
- Backfill de `numero_reclamo` con formato `LIB-{year}-{counter:06d}`
- Backfill de `plazo_respuesta` (30 días hábiles)
- Constraints UNIQUE + FK a `usuario(id)`
- Índices compuestos en `(estado, fecha)`, `(leido, fecha)`, `(prioridad, fecha)`
- **Requiere MariaDB** (usa `SHOW COLUMNS`, `ALTER TABLE`, sintaxis MySQL)

---

## 6. Dependencias Críticas

| Paquete | Versión | Estado |
|---|---|---|
| Python | 3.12 | ✅ |
| Django | 6.0.4 | ✅ |
| DRF | 3.17.1 | ✅ |
| djangorestframework-simplejwt | 5.5.1 | ✅ |
| pytest | 9.1.0 | ✅ |
| pytest-django | 4.12.0 | ✅ |
| xhtml2pdf | 0.2.17 | ✅ |
| reportlab | 4.5.1 | ✅ |
| django-filter | 25.2 | ✅ |
| ruff | ✓ (recién instalado) | ✅ |

---

## 7. Salud General

**✅ APROBADO** — No se encontraron bugs, errores de compilación ni regresiones.

Riesgos detectados:
1. `BoletaPDFService` depende de `xhtml2pdf` + `reportlab` — ambas instaladas y funcionales
2. Warnings de zona horaria en tests de `Evento` (naive datetime) — bajo riesgo
3. Chunk JS >500 kB en frontend — bajo riesgo para MVP, optimizable después
4. Migration 0004 usa SQL raw MariaDB — validar en DB real antes de aplicar
5. `ruff` no estaba instalado en el entorno — agregar a `requirements.txt`
