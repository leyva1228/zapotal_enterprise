import React, { useEffect, useRef, useState } from "react";
import { FaCamera, FaRedo, FaTimes, FaExclamationTriangle, FaCheckCircle } from "react-icons/fa";

/**
 * Captura de foto con la camara del navegador (getUserMedia).
 *
 * Props:
 *   onCapture(blob, previewUrl) -> llamada cuando el usuario acepta la captura
 *   onCancel()                  -> llamada cuando cierra o rechaza
 *
 * Estados posibles:
 *   - starting: pidiendo permiso y arrancando stream
 *   - live: video en vivo, listo para capturar
 *   - captured: foto tomada, mostrando preview + botones Repetir/Usar esta
 *   - error: permiso denegado, sin camara, error de hardware, etc.
 *
 * Notas:
 *   - Requiere HTTPS o localhost (getUserMedia no funciona en HTTP).
 *   - Limpia el stream en unmount para no dejar la camara encendida.
 *   - El blob se entrega como File-ready (mime type image/jpeg, q=0.92).
 */
export default function CameraCapture({ onCapture, onCancel }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [phase, setPhase] = useState("starting"); // starting | live | captured | error
  const [errorMsg, setErrorMsg] = useState("");
  const [previewUrl, setPreviewUrl] = useState(null);
  const [capturedBlob, setCapturedBlob] = useState(null);

  // Arrancar camara al montar
  useEffect(() => {
    let cancelled = false;
    let activeStream = null;

    async function start() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (!cancelled) {
          setErrorMsg("Tu navegador no soporta captura de camara. Actualiza o usa otro browser.");
          setPhase("error");
        }
        return;
      }
      try {
        const s = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });
        if (cancelled) {
          s.getTracks().forEach((t) => t.stop());
          return;
        }
        activeStream = s;
        streamRef.current = s;
        if (videoRef.current) {
          videoRef.current.srcObject = s;
          // Algunos browsers necesitan esperar al evento
          try { await videoRef.current.play(); } catch (_) { /* ignore */ }
        }
        setPhase("live");
      } catch (e) {
        if (cancelled) return;
        setPhase("error");
        if (e && e.name === "NotAllowedError") {
          setErrorMsg(
            "Permiso de camara denegado. Habilitalo en la configuracion del navegador (icono de candado en la barra de direccion) y vuelve a intentar."
          );
        } else if (e && e.name === "NotFoundError") {
          setErrorMsg("No se detecto ninguna camara. Conecta una camara y vuelve a intentar.");
        } else if (e && e.name === "NotReadableError") {
          setErrorMsg("La camara esta siendo usada por otra aplicacion. Cierrala y reintenta.");
        } else {
          setErrorMsg(
            (e && e.message) ||
              "No se pudo acceder a la camara. Revisa los permisos del navegador."
          );
        }
      }
    }

    start();
    return () => {
      cancelled = true;
      if (activeStream) {
        activeStream.getTracks().forEach((t) => t.stop());
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Capturar frame actual del video
  const capture = () => {
    const v = videoRef.current;
    if (!v || !v.videoWidth) return;
    const canvas = document.createElement("canvas");
    canvas.width = v.videoWidth;
    canvas.height = v.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setErrorMsg("No se pudo capturar la imagen. Reintenta.");
          setPhase("error");
          return;
        }
        const url = URL.createObjectURL(blob);
        setCapturedBlob(blob);
        setPreviewUrl(url);
        setPhase("captured");
        // Apagar el stream: ya no necesitamos el video en vivo
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
        }
      },
      "image/jpeg",
      0.92
    );
  };

  const retake = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setCapturedBlob(null);
    setPhase("starting");
    // Re-arrancar la camara
    (async () => {
      try {
        const s = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });
        streamRef.current = s;
        if (videoRef.current) {
          videoRef.current.srcObject = s;
          try { await videoRef.current.play(); } catch (_) { /* ignore */ }
        }
        setPhase("live");
      } catch (e) {
        setErrorMsg("No se pudo reiniciar la camara.");
        setPhase("error");
      }
    })();
  };

  const accept = () => {
    if (capturedBlob) {
      onCapture?.(capturedBlob, previewUrl);
    }
  };

  // ────────────── RENDERS ──────────────
  if (phase === "error") {
    return (
      <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-center">
        <FaExclamationTriangle className="text-4xl text-rose-500 mx-auto mb-3" />
        <p className="text-rose-800 font-semibold mb-2">No se pudo abrir la camara</p>
        <p className="text-sm text-rose-700 mb-4 leading-relaxed">{errorMsg}</p>
        <div className="flex gap-2 justify-center">
          <button
            type="button"
            onClick={() => {
              setPhase("starting");
              setErrorMsg("");
              // reintentar
              (async () => {
                try {
                  const s = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: "user" },
                    audio: false,
                  });
                  streamRef.current = s;
                  if (videoRef.current) {
                    videoRef.current.srcObject = s;
                    try { await videoRef.current.play(); } catch (_) { /* ignore */ }
                  }
                  setPhase("live");
                } catch (e) {
                  setErrorMsg("Sigue sin poder acceder a la camara.");
                  setPhase("error");
                }
              })();
            }}
            className="px-4 py-2 bg-rose-600 text-white rounded-lg text-sm font-semibold hover:bg-rose-700"
          >
            Reintentar
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-white border border-rose-300 text-rose-700 rounded-lg text-sm font-semibold hover:bg-rose-50"
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  }

  if (phase === "captured" && previewUrl) {
    return (
      <div className="text-center">
        <div className="relative inline-block">
          <img
            src={previewUrl}
            alt="Captura de camara"
            className="w-56 h-56 sm:w-64 sm:h-64 rounded-full object-cover border-4 border-emerald-500 shadow-lg"
          />
          <FaCheckCircle className="absolute -top-1 -right-1 text-emerald-600 bg-white rounded-full text-3xl" />
        </div>
        <p className="text-sm text-gray-600 mt-3 mb-4">Tu foto esta lista para guardar</p>
        <div className="flex flex-col sm:flex-row gap-2 justify-center">
          <button
            type="button"
            onClick={retake}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-sm font-semibold transition"
          >
            <FaRedo /> Repetir
          </button>
          <button
            type="button"
            onClick={accept}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold transition"
          >
            <FaCheckCircle /> Usar esta foto
          </button>
        </div>
        <button
          type="button"
          onClick={onCancel}
          className="mt-3 text-xs text-gray-500 hover:text-gray-700 inline-flex items-center gap-1"
        >
          <FaTimes /> Cancelar
        </button>
      </div>
    );
  }

  // starting | live
  return (
    <div className="text-center">
      <div className="relative bg-black rounded-xl overflow-hidden aspect-video mb-4 mx-auto max-w-2xl">
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          playsInline
          muted
          autoPlay
        />
        {phase === "starting" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 text-white gap-3">
            <div className="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin" />
            <p className="text-sm">Solicitando acceso a la camara...</p>
            <p className="text-xs text-white/60">Acepta el permiso en tu navegador</p>
          </div>
        )}
        {phase === "live" && (
          <div className="absolute top-3 left-3 bg-rose-500 text-white text-xs font-bold px-2.5 py-1 rounded-full flex items-center gap-1.5 shadow-lg">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
            EN VIVO
          </div>
        )}
        <div className="absolute bottom-3 right-3 bg-black/60 text-white text-[10px] uppercase tracking-wider px-2 py-1 rounded">
          Camara frontal
        </div>
      </div>
      <button
        type="button"
        onClick={capture}
        disabled={phase !== "live"}
        className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-full transition shadow-lg"
      >
        <FaCamera /> Capturar foto
      </button>
      <p className="text-xs text-gray-500 mt-3">
        Tu foto se subira a tu perfil y quedara guardada en nuestro almacenamiento seguro.
      </p>
      <button
        type="button"
        onClick={onCancel}
        className="mt-2 text-xs text-gray-500 hover:text-gray-700"
      >
        Cancelar
      </button>
    </div>
  );
}
