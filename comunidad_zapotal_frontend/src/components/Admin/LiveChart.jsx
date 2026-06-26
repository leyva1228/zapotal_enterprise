import React, { useMemo } from "react";
import { Liveline } from "liveline";

/**
 * LiveChart - Wrapper sobre la libreria Liveline.
 *
 * Encapsula la API v0.0.x para que un upgrade de version afecte 1 solo archivo.
 *
 * Props:
 * - data: [{timestamp, value}] o [{date, value}] para single-line
 * - series: [{id, label, color, data, value}] para multi-series
 * - windowSecs: number (obligatorio, default 86400 = 24h)
 * - windows: array opcional de {label, secs} para selector
 * - title: string
 * - color: string (default "#16a34a" success)
 * - height: number (default 180)
 * - valueFormatter: (v) => string
 * - variant: "default" | "compact" (tamaños)
 */
export default function LiveChart({
  data = [],
  series = null,
  windowSecs = 86400,
  windows = null,
  title = null,
  color = "#16a34a",
  height = 180,
  valueFormatter = (v) => v.toFixed(0),
  variant = "default",
  badge = null,
  fill = true,
  scrub = true,
  grid = true,
  emptyText = "Sin datos en este periodo",
}) {
  // Normalizar data: {timestamp,value} o {date,value} -> {date: ISO ms, value}
  const normalizedData = useMemo(() => {
    if (!data || data.length === 0) return [];
    return data.map((d) => {
      const ts = d.timestamp || d.date;
      const ms = typeof ts === "number" ? ts * (ts < 1e12 ? 1000 : 1) : new Date(ts).getTime();
      return { date: ms, value: d.value };
    });
  }, [data]);

  const normalizedSeries = useMemo(() => {
    if (!series || series.length === 0) return null;
    return series.map((s) => ({
      ...s,
      data: (s.data || []).map((d) => {
        const ts = d.timestamp || d.date;
        const ms = typeof ts === "number" ? ts * (ts < 1e12 ? 1000 : 1) : new Date(ts).getTime();
        return { date: ms, value: d.value };
      }),
      value: s.value ?? ((s.data && s.data[s.data.length - 1]?.value) || 0),
    }));
  }, [series]);

  // Calcular value (último valor) si no se pasa explícitamente
  const currentValue = useMemo(() => {
    if (normalizedSeries) {
      return normalizedSeries[0]?.value ?? 0;
    }
    if (normalizedData.length > 0) {
      return normalizedData[normalizedData.length - 1].value;
    }
    return 0;
  }, [normalizedData, normalizedSeries]);

  // Estilos segun variant
  const containerStyle = variant === "compact" ? {
    background: "white", borderRadius: 12, padding: 12,
    boxShadow: "0 2px 8px rgba(0,0,0,0.06)", border: "1px solid #e5e7eb",
  } : {
    background: "white", borderRadius: 12, padding: 16,
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
  };

  if ((!normalizedData || normalizedData.length === 0) && (!normalizedSeries || normalizedSeries.length === 0)) {
    return (
      <div style={containerStyle}>
        {title && (
          <h3 style={{ margin: "0 0 8px 0", fontSize: 14, fontWeight: 700, color: "#14532d" }}>
            {title}
          </h3>
        )}
        <div style={{ height, display: "flex", alignItems: "center", justifyContent: "center", color: "#9ca3af", fontSize: 13 }}>
          {emptyText}
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {(title || badge != null) && (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          {title && (
            <h3 style={{ margin: 0, fontSize: variant === "compact" ? 12 : 14, fontWeight: 700, color: "#14532d" }}>
              {title}
            </h3>
          )}
          {badge != null && (
            <span style={{ fontSize: variant === "compact" ? 13 : 18, fontWeight: 700, color }}>
              {typeof badge === "function" ? badge(currentValue) : valueFormatter(badge)}
            </span>
          )}
        </div>
      )}
      <div style={{ height }}>
        {normalizedSeries ? (
          <Liveline
            data={[]}
            value={0}
            series={normalizedSeries}
            color={color}
            theme="light"
            window={windowSecs}
            windows={windows || undefined}
            windowStyle="rounded"
            height={height}
            grid={grid}
            scrub={scrub}
            fill={fill}
          />
        ) : (
          <Liveline
            data={normalizedData}
            value={currentValue}
            color={color}
            theme="light"
            window={windowSecs}
            windows={windows || undefined}
            height={height}
            grid={grid}
            scrub={scrub}
            fill={fill}
            badge={false}
          />
        )}
      </div>
    </div>
  );
}
