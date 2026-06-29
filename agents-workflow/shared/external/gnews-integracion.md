# Integración detallada de GNews en Zapotal Enterprise

> Proyecto: **Zapotal Enterprise — Comunidad Zapotal**  
> Stack detectado: **Django REST Framework + React**  
> Objetivo: integrar noticias externas de forma segura, cacheada y útil para el portal.

---

## 1. ¿Qué es GNews y por qué puede servir aquí?

**GNews** es una API de noticias que permite buscar y recuperar artículos por:

- palabra clave,
- idioma,
- país,
- fuente,
- tema,
- fecha.

### Ventajas para Zapotal Enterprise

- Puede alimentar la sección de **noticias** con contenido fresco.
- Sirve para mostrar **titulares relacionados** en eventos, comunidad o temas institucionales.
- Ayuda a tener un **feed automático** sin depender de carga manual constante.
- Puede complementar la parte editorial del CMS con contenido externo curado.

---

## 2. Importante: límites del plan gratuito

Antes de integrarlo, hay que tener claro que el plan gratuito de GNews es útil para **desarrollo y pruebas**, pero **no está pensado para uso comercial**.

### Lo que incluye el plan gratis

- **100 requests por día**
- **Hasta 10 artículos por request**
- **Retraso de 12 horas** frente a contenido real-time
- **30 días de histórico**
- **CORS habilitado para localhost**
- Acceso a todas las fuentes

### Consecuencia práctica

Si Zapotal Enterprise va a ser un producto público/comercial, lo correcto es:

- usar el plan gratis solo en **desarrollo**, **demo** o **validación interna**,
- y para producción evaluar un plan pago o una alternativa libre.

---

## 3. Dónde encaja en este proyecto

Por la estructura actual, GNews encaja mejor en la capa **backend Django** y luego se expone al frontend React mediante API propia.

### Componentes detectados en el proyecto

- **Backend:** `comunidad_zapotal_backend`
- **Frontend:** `comunidad_zapotal_frontend`
- Ya existe una sección de **noticias** en el admin:
  - `src/pages/Admin/AdminNoticias.jsx`
  - ruta: `/noticias`
- El backend ya tiene recursos de contenido en:
  - `apps.content.urls`
  - endpoint base: `/api/v1/noticias/`

Eso significa que puedes integrar GNews como una **fuente externa adicional** dentro del módulo de contenido existente, sin inventar una arquitectura nueva desde cero.

---

## 4. Casos de uso recomendados dentro de Zapotal Enterprise

### 4.1. Titulares automáticos en la página principal

Mostrar una pequeña sección de noticias externas tipo:

- “Últimas noticias del día”
- “Noticias relacionadas con tu comunidad”
- “Actualidad del sector”

**Beneficio:** la web se ve viva aunque el equipo editorial no publique todos los días.

---

### 4.2. Noticias relacionadas con eventos

Cuando un usuario entra a un evento, se pueden mostrar artículos relacionados por tema o palabra clave.

Ejemplos:

- Evento de medio ambiente → noticias sobre reciclaje, clima, sostenibilidad.
- Evento cultural → noticias sobre festivales, arte, patrimonio.
- Evento institucional → noticias de gestión pública o comunidad.

**Beneficio:** aumenta el tiempo de permanencia y aporta contexto.

---

### 4.3. Panel administrativo de curación

El equipo admin puede usar GNews para:

- descubrir temas relevantes,
- seleccionar artículos para publicar manualmente,
- importar un artículo externo como borrador interno,
- ocultar noticias irrelevantes.

**Beneficio:** GNews no reemplaza el CMS, lo complementa.

---

### 4.4. Feed temático por categoría

Puedes agrupar los resultados por temas como:

- comunidad
- tecnología
- educación
- medio ambiente
- eventos
- cultura
- Perú / región

**Beneficio:** convierte GNews en una capa de enriquecimiento de contenido.

---

### 4.5. Alertas y notificaciones internas

Usar GNews para detectar artículos con palabras clave específicas y generar alertas:

- “nuevo artículo sobre Zapotal”
- “noticia sobre el distrito/región”
- “tema sensible detectado”

**Beneficio:** útil para moderación, monitoreo y comunicación.

---

## 5. Arquitectura recomendada

### Opción recomendada: integrar GNews solo en el backend

### Flujo

1. **React** solicita datos al backend.
2. **Django** consulta GNews.
3. **Django cachea** la respuesta.
4. **Django devuelve** JSON ya normalizado.
5. **React** renderiza tarjetas o listas.

### Por qué hacerlo así

- No expones la API key en el frontend.
- Puedes controlar rate limits.
- Puedes cachear por categoría o término.
- Puedes unificar el formato con tus noticias internas.

---

## 6. Estructura técnica sugerida en Django

Como el proyecto ya usa `apps.content`, una integración limpia sería una de estas dos opciones:

### Opción A: Reutilizar `apps.content`

Crear dentro de `apps.content`:

- `services/gnews_service.py`
- `views_gnews.py`
- `urls_gnews.py`
- `serializers_gnews.py` si hace falta normalizar

### Opción B: Crear una app nueva

Crear una app dedicada, por ejemplo:

- `apps.integrations`
- `apps.newsfeed`
- `apps.external_news`

**Recomendación:** para este proyecto, empezar con **Opción A** suele ser mejor porque ya existe la estructura de contenidos.

---

## 7. Variables de entorno recomendadas

Guardar la clave en `.env` o en el gestor de secretos del servidor:

```env
GNEWS_API_KEY=tu_api_key_aqui
GNEWS_BASE_URL=https://gnews.io/api/v4
GNEWS_DEFAULT_LANG=es
GNEWS_DEFAULT_COUNTRY=pe
GNEWS_TIMEOUT=10
GNEWS_CACHE_TTL=900
```

### Reglas

- Nunca hardcodear la API key en React.
- Nunca subir la key al repositorio.
- En producción, limitar acceso al backend.

---

## 8. Endpoints sugeridos en tu backend

Puedes exponer endpoints internos como estos:

### 8.1. Buscar noticias externas

`GET /api/v1/gnews/noticias/?q=...&lang=es&country=pe&page=1`

### 8.2. Noticias por categoría temática

`GET /api/v1/gnews/categoria/?tema=medio-ambiente`

### 8.3. Titulares destacados

`GET /api/v1/gnews/destacadas/`

### 8.4. Noticias relacionadas con un evento

`GET /api/v1/gnews/relacionadas/?q=evento+palabra-clave`

---

## 9. Ejemplo de servicio backend

### 9.1. Servicio base

```python
# apps/content/services/gnews_service.py

import requests
from django.conf import settings
from django.core.cache import cache

GNEWS_URL = getattr(settings, "GNEWS_BASE_URL", "https://gnews.io/api/v4")
GNEWS_KEY = getattr(settings, "GNEWS_API_KEY", "")
GNEWS_TIMEOUT = getattr(settings, "GNEWS_TIMEOUT", 10)
GNEWS_CACHE_TTL = getattr(settings, "GNEWS_CACHE_TTL", 900)


def buscar_noticias(query, lang="es", country="pe", max_results=10):
    cache_key = f"gnews:{query}:{lang}:{country}:{max_results}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "q": query,
        "lang": lang,
        "country": country,
        "max": max_results,
        "token": GNEWS_KEY,
    }

    response = requests.get(
        f"{GNEWS_URL}/search",
        params=params,
        timeout=GNEWS_TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()
    cache.set(cache_key, data, GNEWS_CACHE_TTL)
    return data
```

### 9.2. Vista DRF

```python
# apps/content/views_gnews.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .services.gnews_service import buscar_noticias


@api_view(["GET"])
@permission_classes([AllowAny])
def gnews_buscar(request):
    q = request.query_params.get("q", "")
    if not q:
        return Response({"detail": "Falta el parámetro q"}, status=status.HTTP_400_BAD_REQUEST)

    lang = request.query_params.get("lang", "es")
    country = request.query_params.get("country", "pe")
    max_results = int(request.query_params.get("max", 10))

    try:
        data = buscar_noticias(q, lang=lang, country=country, max_results=max_results)
        return Response(data)
    except Exception:
        return Response(
            {"detail": "No se pudieron obtener noticias externas en este momento."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
```

---

## 10. Recomendaciones de cache

Como el plan gratis es limitado, el cache es obligatorio.

### Estrategia sugerida

- **TTL corto** para búsquedas generales: 10 a 20 minutos
- **TTL más largo** para categorías estables: 1 a 3 horas
- **TTL largo** para resultados de portadas: 30 a 60 minutos

### Claves de cache útiles

- `gnews:portada:es:pe`
- `gnews:eventos:es:pe`
- `gnews:medio-ambiente:es:pe`

### Beneficios

- ahorras requests,
- evitas errores por límite diario,
- mejoras tiempo de respuesta.

---

## 11. Cómo normalizar los datos para tu frontend

GNews devuelve campos que conviene estandarizar antes de exponerlos al frontend.

### Campos útiles

- `title` → título
- `description` → resumen
- `content` → contenido
- `url` → enlace original
- `image` → imagen destacada
- `publishedAt` → fecha
- `source.name` → fuente

### Formato sugerido para React

```json
{
  "titulo": "...",
  "resumen": "...",
  "contenido": "...",
  "fuente": "...",
  "url_original": "...",
  "imagen": "...",
  "fecha_publicacion": "..."
}
```

**Beneficio:** tu frontend no depende del formato bruto de GNews.

---

## 12. Integración en el frontend React

### 12.1. Componente de tarjetas

Puedes crear un componente tipo:

- `GNewsCard.jsx`
- `GNewsList.jsx`
- `GNewsSection.jsx`

### 12.2. Hook personalizado

Crear un hook como:

- `useGNews.js`

Ejemplo de comportamiento:

- recibe `query`, `lang`, `country`,
- consulta el endpoint del backend,
- maneja loading/error,
- devuelve resultados listos para pintar.

### 12.3. Lugares para mostrarlo

- Home pública
- página de noticias
- detalle de evento
- dashboard de administrador
- sidebar de actualidad

---

## 13. Uso dentro del admin actual

Ya existe `AdminNoticias.jsx`, que administra noticias propias.

La integración con GNews podría agregarse como:

### Botón adicional

- “Buscar noticias externas”
- “Importar como borrador”
- “Ver relacionadas”

### Flujo administrativo

1. El admin busca una palabra clave.
2. Se muestran resultados GNews.
3. Selecciona un artículo.
4. Lo importa como borrador interno.
5. Luego lo edita y publica manualmente.

**Beneficio:** mantienes control editorial.

---

## 14. Usos concretos en Zapotal Enterprise

### Para la comunidad

- noticias de interés local,
- seguimiento de temas ciudadanos,
- actualidad regional.

### Para eventos

- artículos relacionados con el evento,
- contexto cultural o temático,
- promoción de actividades vinculadas.

### Para el portal institucional

- sección de actualidad,
- contenido de apoyo para campañas,
- apoyo a comunicación externa.

### Para el equipo interno

- investigación rápida,
- monitoreo de temas,
- curación de contenido.

---

## 15. Riesgos y cómo mitigarlos

### 15.1. Límite diario

**Riesgo:** agotar las 100 requests.

**Mitigación:**

- cache,
- no consultar en cada render,
- usar refresh manual o programado.

### 15.2. Uso no permitido en producción comercial

**Riesgo:** el plan gratis no cubre uso comercial.

**Mitigación:**

- usar el plan gratis solo para pruebas,
- migrar a plan pago o alternativa libre en producción.

### 15.3. Dependencia externa

**Riesgo:** que GNews falle o cambie.

**Mitigación:**

- fallback con contenido propio,
- mostrar cache,
- mensajes amigables.

### 15.4. Contenido duplicado o poco relevante

**Riesgo:** mezclar noticias externas con las propias sin control.

**Mitigación:**

- etiquetar claramente “fuente externa”,
- moderación manual,
- filtros por categoría.

---

## 16. Recomendación de implementación por fases

### Fase 1 — Prueba interna

- crear servicio en backend,
- exponer endpoint propio,
- probar cache,
- mostrar 1 sección pequeña en frontend.

### Fase 2 — Curación editorial

- añadir filtros por tema,
- importar noticias como borradores,
- mostrar fuente y enlace original.

### Fase 3 — Producción

- revisar límites de plan,
- validar licenciamiento/comercial,
- implementar fallback y monitoreo.

---

## 17. Conclusión

GNews encaja bien en Zapotal Enterprise si se usa como **fuente externa complementaria** y no como reemplazo del CMS.

### Lo más recomendable

- consumirlo desde **Django**,
- cachear agresivamente,
- exponerlo por API propia,
- mostrarlo en React como **contenido curado**,
- y usar el plan gratuito solo para **desarrollo o demo**.

Si el proyecto va a producción comercial, el plan gratuito **no debería ser la base final**.

---

## 18. Próximo paso sugerido

Si quieres, el siguiente paso puede ser uno de estos:

1. **Te preparo el código real del backend** para Django.
2. **Te preparo el hook/componente React** para mostrar las noticias.
3. **Te redacto un plan de implementación en el repo** con tareas concretas.
4. **Te adapto este documento a un estilo más técnico o más ejecutivo**.
