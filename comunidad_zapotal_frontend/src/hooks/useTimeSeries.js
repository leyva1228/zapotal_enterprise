import { useMemo } from "react";

/**
 * useTimeSeries - Convierte items con timestamp+value en buckets agregados.
 *
 * Opciones:
 * - dateKey: nombre del campo de fecha (default "timestamp")
 * - valueKey: nombre del campo de valor (default "value")
 * - bucketMs: tamano del bucket en ms (default 3600000 = 1h)
 * - windowSecs: ventana en segundos (default 86400 = 24h)
 *
 * Retorna array de {timestamp, value} ordenados ascendente por timestamp.
 */
export function useTimeSeries(items, options = {}) {
  const {
    dateKey = "timestamp",
    valueKey = "value",
    bucketMs = 3600000,
    windowSecs = 86400,
  } = options;

  return useMemo(() => {
    if (!Array.isArray(items) || items.length === 0) return [];

    const now = Date.now();
    const windowStart = now - windowSecs * 1000;

    // Crear buckets vacios en la ventana
    const buckets = new Map();
    for (let t = windowStart; t <= now; t += bucketMs) {
      buckets.set(t, { timestamp: t, value: 0, count: 0 });
    }

    // Agregar items a buckets
    for (const item of items) {
      const ts = item[dateKey];
      const ms = typeof ts === "number" ? ts * (ts < 1e12 ? 1000 : 1) : new Date(ts).getTime();
      if (ms < windowStart || ms > now) continue;
      // Snap al bucket mas cercano
      const bucketTs = Math.floor((ms - windowStart) / bucketMs) * bucketMs + windowStart;
      const bucket = buckets.get(bucketTs);
      if (bucket) {
        const v = item[valueKey];
        if (typeof v === "number") {
          bucket.value += v;
        }
        bucket.count += 1;
      }
    }

    return Array.from(buckets.values());
  }, [items, dateKey, valueKey, bucketMs, windowSecs]);
}

/**
 * useTimeSeriesByCategory - Agrupa por categoria, retorna array de series.
 *
 * Espera items: [{timestamp, value, category}]
 * Retorna: [{id, label, color, data: [{timestamp, value}]}]
 */
export function useTimeSeriesByCategory(items, categoryColors, options = {}) {
  const {
    dateKey = "timestamp",
    valueKey = "value",
    categoryKey = "category",
    bucketMs = 3600000,
    windowSecs = 86400,
  } = options;

  return useMemo(() => {
    if (!Array.isArray(items) || items.length === 0) return [];

    const now = Date.now();
    const windowStart = now - windowSecs * 1000;

    // Agrupar por categoria
    const byCategory = new Map();
    for (const item of items) {
      const cat = item[categoryKey] || "OTRO";
      if (!byCategory.has(cat)) byCategory.set(cat, []);
      byCategory.get(cat).push(item);
    }

    const series = [];
    for (const [cat, list] of byCategory.entries()) {
      const buckets = new Map();
      for (let t = windowStart; t <= now; t += bucketMs) {
        buckets.set(t, { timestamp: t, value: 0 });
      }
      for (const item of list) {
        const ts = item[dateKey];
        const ms = typeof ts === "number" ? ts * (ts < 1e12 ? 1000 : 1) : new Date(ts).getTime();
        if (ms < windowStart || ms > now) continue;
        const bucketTs = Math.floor((ms - windowStart) / bucketMs) * bucketMs + windowStart;
        const bucket = buckets.get(bucketTs);
        if (bucket) {
          const v = item[valueKey];
          if (typeof v === "number") bucket.value += v;
        }
      }
      const data = Array.from(buckets.values());
      series.push({
        id: cat,
        label: cat,
        color: categoryColors[cat] || "#6b7280",
        data,
        value: data.length > 0 ? data[data.length - 1].value : 0,
      });
    }
    return series;
  }, [items, dateKey, valueKey, categoryKey, bucketMs, windowSecs, categoryColors]);
}
