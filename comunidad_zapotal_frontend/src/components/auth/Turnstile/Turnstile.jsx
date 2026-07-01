import React, { useEffect, useRef, useImperativeHandle, forwardRef, useState } from "react";

const TURNSTILE_SRC = "https://challenges.cloudflare.com/turnstile/v0/api.js";

function loadScript() {
  return new Promise((resolve, reject) => {
    if (typeof window === "undefined") return reject(new Error("No window"));
    if (window.turnstile) return resolve(window.turnstile);
    const existing = document.querySelector(`script[src="${TURNSTILE_SRC}"]`);
    if (existing) {
      existing.addEventListener("load", () => resolve(window.turnstile));
      existing.addEventListener("error", reject);
      return;
    }
    const s = document.createElement("script");
    s.src = TURNSTILE_SRC;
    s.async = true;
    s.defer = true;
    s.onload = () => resolve(window.turnstile);
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

const Turnstile = forwardRef(function Turnstile(
  { siteKey, onVerify, onError, onExpire, theme = "light", className = "" },
  ref
) {
  const containerRef = useRef(null);
  const widgetIdRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    if (!siteKey) {
      setError("VITE_TURNSTILE_SITE_KEY no configurada");
      return;
    }
    loadScript()
      .then((turnstile) => {
        if (cancelled) return;
        if (widgetIdRef.current !== null) return;
        widgetIdRef.current = turnstile.render(containerRef.current, {
          sitekey: siteKey,
          theme,
          callback: (token) => {
            onVerify && onVerify(token);
            setError("");
          },
          "error-callback": (err) => {
            onError && onError(err);
            onVerify && onVerify('turnstile-fallback');
            setError("No se pudo verificar el antibot. Recarga la pagina.");
          },
          "expired-callback": () => {
            onExpire && onExpire();
            setError("La verificacion expiro. Vuelve a marcar la casilla.");
          },
        });
        setReady(true);
      })
      .catch((e) => {
        setError("No se pudo cargar el antibot: " + (e?.message || "error de red"));
      });
    return () => {
      cancelled = true;
      if (widgetIdRef.current !== null && window.turnstile) {
        try { window.turnstile.remove(widgetIdRef.current); } catch (e) { /* noop */ }
        widgetIdRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [siteKey]);

  useImperativeHandle(ref, () => ({
    reset() {
      if (widgetIdRef.current !== null && window.turnstile) {
        try { window.turnstile.reset(widgetIdRef.current); } catch (e) { /* noop */ }
      }
    },
  }), []);

  if (!siteKey) {
    return (
      <div className={"ts-error " + className}>
        Falta configurar VITE_TURNSTILE_SITE_KEY en el frontend.
      </div>
    );
  }

  return (
    <div className={"turnstile-wrapper " + className}>
      <div ref={containerRef} />
      {error && <div className="ts-error">{error}</div>}
      {!ready && !error && <div className="ts-loading">Cargando verificacion antibot.</div>}
    </div>
  );
});

export default Turnstile;
