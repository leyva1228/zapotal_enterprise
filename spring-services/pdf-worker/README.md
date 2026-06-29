# Comunidad Zapotal - PDF Worker (Spring Boot)

Microservicio asincrono para generar y enviar boletas de donacion en PDF.

## Por que existe

El backend Django actual (`apps/donaciones/views.py`) genera el PDF de la
boleta con `xhtml2pdf` y lo envia por email **sincronicamente** dentro del
endpoint `POST /donaciones/procesar-simulado/`. Esto bloquea el response HTTP
3-10 segundos y degrada la UX (el usuario espera para ver el modal de resultado).

Este worker es el **mini-cerebro** que recibe la peticion de Django, responde
inmediatamente con un `job_id`, y procesa el PDF + email en background con
un thread pool dedicado.

## Arquitectura

```
React (browser)
   |
   v
Django (Render)  <-- autenticacion JWT, validacion, persistencia
   |                |
   |                +---> MySQL/Postgres (Render)
   |
   v (HTTP POST con X-Internal-API-Key)
PDF Worker (este)  <-- encola job, responde <100ms con job_id
   |
   +---> thread pool (4 workers, cola 100)
   |
   +---> OpenPDF genera el PDF
   |
   +---> SMTP (Resend) envia el email
```

## Endpoints

Todos los endpoints `/api/v1/internal/*` requieren el header
`X-Internal-API-Key: <INTERNAL_API_KEY>` (configurado via env var).

| Metodo | Path | Body | Response |
|---|---|---|---|
| `POST` | `/api/v1/internal/render-boleta` | `BoletaRequest` (JSON) | `202 Accepted {job_id, status: "queued", created_at}` |
| `GET`  | `/api/v1/internal/health`      | (none) | `200 "OK"` (sin auth, lo usa Render healthcheck) |

### BoletaRequest

```json
{
  "donacion_id": 18,
  "numero_boleta": "2026-000018",
  "monto": "50.00",
  "moneda": "PEN",
  "email_destinatario": "donante@ejemplo.com",
  "nombre_donante": "Mofren Perez",
  "documento_donante": "12345678",
  "destino": "Comunidad general",
  "mensaje": "Apoyo a la comunidad",
  "ultimos_4": "6176",
  "tipo_tarjeta": "credito",
  "anonima": false
}
```

## Como lo invoca Django

En `apps/donaciones/views.py:ProcesarPagoSimuladoView`, justo despues de actualizar
el estado a APROBADO, en lugar de generar el PDF sincronamente, Django hace:

```python
import requests
requests.post(
    "https://pdf-worker.comunidadzapotal.org/api/v1/internal/render-boleta",
    json=boleta_payload,
    headers={"X-Internal-API-Key": settings.INTERNAL_API_KEY},
    timeout=2,  # el worker responde en <100ms, esto solo espera el 202
)
```

Django ya no espera la generacion del PDF ni el envio del email. Solo persiste
el estado APROBADO, encola el job, y devuelve el modal al usuario.

## Como se desplega en Render

Crear un nuevo "Web Service" en Render:
- **Runtime**: Docker (Render detecta el Dockerfile automaticamente)
- **Dockerfile Path**: `spring-services/pdf-worker/Dockerfile`
- **Context**: el repo
- **Region**: Oregon (mismo que Django)
- **Plan**: Starter ($7/mes, suficiente)
- **Instance Type**: 512 MB o 1 GB

Variables de entorno requeridas:
- `INTERNAL_API_KEY` (mismo valor que en Django, 32+ chars)
- `SMTP_HOST` (ej: `smtp.resend.com`)
- `SMTP_PORT` (587)
- `SMTP_USER` (ej: `resend`)
- `SMTP_PASSWORD` (API key de Resend)
- `EMAIL_FROM` (ej: `noreply@comunidadzapotal.org`)
- `PORT` (Render lo inyecta automaticamente, no setearlo)

## Variables de entorno en Django

Adicional a las ya existentes (`MERCADO_PAGO_*`, `CLOUDFLARE_R2_*`, etc),
agregar en Render:

- `INTERNAL_API_KEY` (mismo valor que en el PDF worker)
- `PDF_WORKER_URL` = `https://pdf-worker.comunidadzapotal.org`

## Como se desarrolla local

```bash
cd spring-services/pdf-worker
mvn spring-boot:run
```

Levanta el servicio en `http://localhost:8081`. La API key por default
es `dev-only-internal-key-change-me-in-prod-please-32-chars` (solo para dev).

Para probarlo:
```bash
curl -X POST http://localhost:8081/api/v1/internal/render-boleta \
  -H "Content-Type: application/json" \
  -H "X-Internal-API-Key: dev-only-internal-key-change-me-in-prod-please-32-chars" \
  -d '{"donacion_id": 18, "numero_boleta": "2026-000018", "monto": "50.00", "email_destinatario": "tu@email.com", "nombre_donante": "Test User"}'
```

Deberia responder 202 con un job_id en <100ms.

## Por que OpenPDF y no xhtml2pdf / flying-saucer / Playwright

| Libreria | Pros | Contras | Decision |
|---|---|---|---|
| **OpenPDF** (usada) | LGPL, sin deps nativas, control total | HTML simple (sin flex/grid) | Ideal para plantillas estructuradas (la boleta) |
| flying-saucer | CSS mas completo | Depende de iText | Igual de bien, mas viejo |
| Playwright/Chromium | HTML+CSS completo, full fidelity | Pesado (1GB+ imagen), latencia alta | Para boletas no vale la pena |
| xhtml2pdf (Python) | Ya lo usa Django | Duplicar logica, no async | Solo si Django lo necesitara sync |

## Roadmap

- [ ] **v0.2**: webhook de Django -> worker para tracking de jobs
- [ ] **v0.3**: retry automatico con backoff exponencial (Spring Retry)
- [ ] **v0.4**: dead-letter queue (Redis Streams o RabbitMQ) para boletas que no se pudieron enviar
- [ ] **v0.5**: validacion de DNI contra RENIEC (microservicio dedicado)
- [ ] **v1.0**: gateway unico (BFF) que enruta Django, PDF worker, RENIEC, etc

## Troubleshooting

| Error | Causa | Solucion |
|---|---|---|
| `401 unauthorized` en `/render-boleta` | `X-Internal-API-Key` falta o no coincide | Verificar que el valor en Django y el worker sea EXACTAMENTE igual (sin espacios) |
| `Connection refused` a SMTP | Credenciales mal o puerto bloqueado | Verificar `SMTP_HOST` y `SMTP_PORT`. Para Resend usar `smtp.resend.com:587` con TLS |
| PDF sale en blanco | Thymeleaf no encontro la plantilla | Verificar que `templates/boleta.html` esta en `src/main/resources/` |
| Job queda en "queued" para siempre | Thread pool saturado | Aumentar `app.async.core-pool-size` en `application.yml` o ver si hay un error en logs |
