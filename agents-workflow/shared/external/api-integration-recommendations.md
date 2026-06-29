# Recomendaciones de APIs Públicas para Integración

> Proyecto: Zapotal Enterprise — Plataforma de Noticias y Eventos
> Fuente: [public-apis/public-apis](https://github.com/public-apis/public-apis)
> Fecha: Junio 2026

---

## 1. News — Noticias

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [GNews](https://gnews.io/) | 100 req/día | `apiKey` | Sí | Sí | Búsqueda por palabra clave, 30+ idiomas. Ideal para agregar noticias nacionales e internacionales. |
| [Mediastack](https://mediastack.com) | 500 req/mes | `apiKey` | Sí | ? | API simple y rápida para noticias en vivo y artículos de blog. |
| [NewsAPI](https://newsapi.org/) | 100 req/día | `apiKey` | Sí | ? | El estándar de facto. Headlines, fuentes, búsqueda. |
| [Currents](https://currentsapi.services/) | 100 req/día | `apiKey` | Sí | Sí | Soporte multilingüe, noticias en tiempo real e históricas. |
| [The Guardian](http://open-platform.theguardian.com/) | Ilimitado (personal) | `apiKey` | Sí | ? | Contenido curado, secciones y etiquetas. Periodismo de calidad. |
| [New York Times](https://developer.nytimes.com/) | 5 req/min, 500/día | `apiKey` | Sí | ? | Article Search, Top Stories, Popular. APIs clásicas. |
| [TheNews](https://www.thenewsapi.com/) | 100 req/día | `apiKey` | Sí | Sí | Headlines, top stories, live news JSON API. |

**Stack recomendado:** `GNews` (principal, gratis 100/día) + `NewsAPI` (fallback) + `The Guardian` (contenido editorial de calidad).

---

## 2. Events — Eventos

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [Ticketmaster](http://developer.ticketmaster.com/) | 50 req/día | `apiKey` | Sí | ? | Eventos, atracciones, venues. Cobertura global, ideal para conciertos, teatro, deportes. |
| [Eventbrite](https://www.eventbrite.com/platform/api/) | Ilimitado (eventos propios) | `OAuth` | Sí | ? | Eventos locales, conferencias, talleres. |
| [SeatGeek](https://platform.seatgeek.com/) | Ilimitado | `apiKey` | Sí | ? | Búsqueda de eventos, venues y performers. |

**Stack recomendado:** `Ticketmaster` (50 req/día gratuitos, ideal para agenda cultural) + `Eventbrite` (eventos comunitarios y conferencias).

---

## 3. Calendar / Holidays — Calendario y Feriados

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [Calendarific](https://calendarific.com/) | 1000 req/mes | `apiKey` | Sí | ? | Feriados mundiales. Ideal para Perú: feriados nacionales, regionales y religiosos. |
| [Nager.Date](https://date.nager.at) | Ilimitado | No | Sí | No | Feriados públicos para 90+ países. Sin API key. |
| [Abstract Public Holidays](https://www.abstractapi.com/holidays-api) | 5000 req/año | `apiKey` | Sí | Sí | Feriados nacionales, regionales y religiosos. |

**Recomendado:** `Nager.Date` (sin auth, ideal para mostrar feriados peruanos) + `Calendarific` (más datos, soporte para feriados regionales de Perú).

---

## 4. Weather — Clima

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [Open-Meteo](https://open-meteo.com/) | Ilimitado (no comercial) | No | Sí | Sí | Sin API key. Pronóstico global, histórico, calidad del aire. Perfecto para clima local. |
| [Weatherstack](https://weatherstack.com) | 500 req/mes | `apiKey` | Sí | ? | Tiempo real e histórico. |
| [AQICN](https://aqicn.org/api/) | Ilimitado | `apiKey` | Sí | ? | Calidad del aire para 1000+ ciudades. |

**Recomendado:** `Open-Meteo` (sin key, 100% gratis para proyectos no comerciales, ideal para sidebar de clima).

---

## 5. Images / Photography — Imágenes de Stock

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [Pexels](https://www.pexels.com/api/) | 200 req/hora | `apiKey` | Sí | Sí | Fotos y videos de stock gratuitos. Ideal para ilustrar noticias y eventos. |
| [Unsplash](https://unsplash.com/developers) | 50 req/hora | `OAuth` | Sí | ? | Banco de imágenes de alta calidad. |
| [Pixabay](https://pixabay.com/api/docs/) | Ilimitado | `apiKey` | Sí | ? | Imágenes, vectores, videos. API generosa. |
| [Lorem Picsum](https://picsum.photos/) | Ilimitado | No | Sí | ? | Placeholders aleatorios de Unsplash. Sin auth. |

**Recomendado:** `Pexels` (200 req/hora, calidad excelente) + `Lorem Picsum` (placeholders sin auth).

---

## 6. Geolocation / Maps — Ubicación de Eventos

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [OpenStreetMap (Nominatim)](https://nominatim.org/release-docs/develop/api/Overview/) | Ilimitado (1 req/seg) | No | Sí | — | Geocoding gratuito, datos abiertos. |
| [CountryStateCity](https://countrystatecity.in/) | 1000 req/día | `apiKey` | Sí | Sí | Países, estados, ciudades del mundo en JSON. |
| [Bing Maps](https://www.microsoft.com/maps/) | 125,000 req/año | `apiKey` | Sí | ? | Mapas, geocoding, rutas. |
| [IPstack](https://ipstack.com) | 100 req/mes | `apiKey` | Sí | ? | Geolocalización por IP del visitante. |

**Recomendado:** `Nominatim` (geocoding gratis para ubicar eventos en mapa) + `CountryStateCity` (datos de ubicación para filtros por ciudad/región).

---

## 7. Social — Redes Sociales

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [Reddit](https://www.reddit.com/dev/api) | Ilimitado | `OAuth` | Sí | ? | Contenido viral, tendencias, comunidades. Fuente de noticias y discusión. |
| [Bluesky](https://docs.bsky.app/) | Ilimitado | No | Sí | Sí | Red social descentralizada. Feed público sin auth. |
| [HackerNews](https://github.com/HackerNews/API) | Ilimitado | No | Sí | ? | Noticias de tecnología y emprendimiento. |
| [Disqus](https://disqus.com/api/docs/auth/) | Ilimitado | `OAuth` | Sí | ? | Sistema de comentarios para artículos. |

**Recomendado:** `Reddit` (tendencias y contenido generado por usuarios) + `Disqus` (comentarios en artículos de noticias).

---

## 8. Text Analysis — Análisis de Texto

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [Detect Language](https://detectlanguage.com/) | 3500 req/día | `apiKey` | Sí | ? | Detección de idioma para artículos multilingües. |
| [LibreTranslate](https://libretranslate.com/docs) | Ilimitado | No | Sí | ? | Traducción automática gratuita, auto-hosteable. |
| [Cloudmersive NLP](https://www.cloudmersive.com/nlp-api) | 800 req/mes | `apiKey` | Sí | Sí | NLP: sentiment, entidades, clasificación. |
| [Aylien Text Analysis](https://docs.aylien.com/textapi/) | 1000 req/mes | `apiKey` | Sí | ? | News API + análisis de texto. |

**Recomendado:** `LibreTranslate` (traducción automática gratuita, sin auth) + `Detect Language` (multilingüe para artículos).

---

## 9. Video — Contenido Multimedia

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [YouTube Data API](https://developers.google.com/youtube/v3) | 10,000 unidades/día | `OAuth` | Sí | ? | Buscar videos, listas de reproducción, canales. |
| [Dailymotion](https://developer.dailymotion.com/) | Limitado | `OAuth` | Sí | ? | Videos alternativos. |
| [Hyperserve](https://hyperserve.io/) | Gratuito | `apiKey` | Sí | Sí | Subida, transcodificación y CDN de video. |

**Recomendado:** `YouTube Data API` (para incrustar videos de noticias y eventos).

---

## 10. Government — Datos Abiertos Perú

| API | Plan Gratuito | Auth | HTTPS | CORS | ¿Por qué usarla? |
|-----|--------------|------|-------|------|------------------|
| [Datos Abiertos Perú](https://www.datosabiertos.gob.pe/) | Ilimitado | No | Sí | ? | Portal de datos abiertos del gobierno peruano. |
| [SENAMHI](https://www.senamhi.gob.pe/) | Ilimitado | No | Sí | ? | Datos meteorológicos oficiales del Perú. |
| [INEI](https://www.inei.gob.pe/) | Ilimitado | No | Sí | ? | Estadísticas demográficas y económicas del Perú. |

**Nota:** Muchas APIs gubernamentales peruanas son REST sin auth. Verificar disponibilidad actual.

---

## Prioridad de Integración

| Prioridad | API | Categoría | Esfuerzo | Impacto |
|-----------|-----|-----------|----------|---------|
| 🔴 Alta | GNews | News | Bajo | Alto — contenido principal |
| 🔴 Alta | Ticketmaster | Events | Bajo | Alto — agenda cultural |
| 🔴 Alta | Open-Meteo | Weather | Muy bajo | Medio — sidebar informativo |
| 🟡 Media | Pexels | Images | Bajo | Medio — ilustrar artículos |
| 🟡 Media | Calendarific | Calendar | Bajo | Medio — feriados |
| 🟡 Media | Disqus | Social | Bajo | Alto — engagement |
| 🟢 Baja | LibreTranslate | Text | Medio | Bajo — contenido multilingüe |
| 🟢 Baja | Reddit | Social | Bajo | Bajo — tendencias |
| 🟢 Baja | Nominatim | Geocoding | Medio | Bajo — mapa de eventos |

---

## Consideraciones de integración técnica

- **Backend (Laravel):** Usar `Http` facade para consumir APIs. Cachear respuestas con `Cache::remember()` para evitar sobrepasar límites gratuitos.
- **Frontend (React):** Llamadas desde el backend (no exponer API keys en el frontend). Para mapas, considerar Leaflet con OpenStreetMap tiles.
- **Rate limiting:** Respetar límites de cada API. Implementar backoff exponencial y colas con `Queue` de Laravel.
- **Fallo graceful:** Mostrar datos cacheados o mensajes amigables cuando una API no responda.
- **Perú:** Priorizar contenido en español. Verificar que las APIs seleccionadas tengan cobertura para Perú (latam).

> Documento generado automáticamente vía [public-apis](https://github.com/public-apis/public-apis)
