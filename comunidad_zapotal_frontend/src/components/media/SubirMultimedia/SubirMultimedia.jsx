import React, { useState, useRef, useCallback } from "react";
import { FaTrash, FaImage, FaVideo, FaCloudUploadAlt, FaCheck } from "react-icons/fa";
import api from "../../../api";

/**
 * Componente reutilizable para subir multiples archivos multimedia
 * (imagenes y videos) asociados a una noticia o un evento.
 *
 * Props:
 *  - itemId: id de la noticia o evento (null si es nuevo)
 *  - itemType: "noticia" | "evento" (a donde se asocia el FK)
 *  - initialFiles: archivos ya subidos (array de {id, archivo_url, tipo, archivo})
 *  - onChange: callback opcional cuando cambia la lista de archivos
 *  - disabled: si esta deshabilitado
 */
function SubirMultimedia({
  itemId,
  itemType,
  initialFiles = [],
  onChange,
  disabled = false,
}) {
  const [files, setFiles] = useState(
    (initialFiles || []).map((f) => ({
      id: f.id,
      url: f.archivo_url,
      tipo: f.tipo,
      nombre: f.archivo_url ? f.archivo_url.split("/").pop() : "",
      nuevo: false,
      subiendo: false,
    }))
  );
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const inputRef = useRef(null);

  const detectarTipo = (mime) => {
    if (!mime) return "IMAGEN";
    if (mime.startsWith("video/")) return "VIDEO";
    return "IMAGEN";
  };

  const handleFiles = useCallback(
    (fileList) => {
      setError("");
      setInfo("");
      if (!itemId) {
        setError("Guarda primero el item antes de subir archivos.");
        return;
      }
      const nuevos = Array.from(fileList || []).map((f) => ({
        file: f,
        nombre: f.name,
        tamano: f.size,
        tipo: detectarTipo(f.type),
        nuevo: true,
        subiendo: false,
        url: URL.createObjectURL(f),
      }));
      setFiles((prev) => [...prev, ...nuevos]);
    },
    [itemId]
  );

  const handleInputChange = (e) => {
    handleFiles(e.target.files);
    if (inputRef.current) inputRef.current.value = "";
  };

  const subirArchivo = async (item) => {
    if (!item.file) return;
    setFiles((prev) =>
      prev.map((f) =>
        f.file === item.file ? { ...f, subiendo: true, error: null } : f
      )
    );
    try {
      const fd = new FormData();
      fd.append("archivo", item.file);
      fd.append("tipo", item.tipo);
      fd.append(itemType, itemId);
      const { data } = await api.post("/multimedias/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      // Reemplaza el item temporal por el item guardado del backend.
      setFiles((prev) => {
        const replaced = prev.map((f) =>
          f.file === item.file
            ? {
                id: data.id,
                url: data.archivo_url,
                tipo: data.tipo,
                nombre: data.archivo_url
                  ? data.archivo_url.split("/").pop()
                  : item.nombre,
                nuevo: false,
                subiendo: false,
              }
            : f
        );
        if (onChange) onChange(replaced.filter((x) => !x.nuevo || x.id));
        return replaced;
      });
      setInfo(`Subido: ${item.nombre}`);
    } catch (e) {
      console.error("Error al subir", e);
      setError(`No se pudo subir ${item.nombre}`);
      setFiles((prev) =>
        prev.map((f) =>
          f.file === item.file ? { ...f, subiendo: false, error: true } : f
        )
      );
    }
  };

  const eliminarArchivo = async (item) => {
    if (item.nuevo) {
      // Si es nuevo (aun no subido), solo lo quita del estado.
      URL.revokeObjectURL(item.url);
      setFiles((prev) => {
        const next = prev.filter((f) => f !== item);
        if (onChange) onChange(next.filter((x) => !x.nuevo || x.id));
        return next;
      });
      return;
    }
    if (!item.id) return;
    try {
      await api.delete(`/multimedias/${item.id}/`);
      setFiles((prev) => {
        const next = prev.filter((f) => f.id !== item.id);
        if (onChange) onChange(next.filter((x) => !x.nuevo || x.id));
        return next;
      });
      setInfo(`Eliminado: ${item.nombre}`);
    } catch (e) {
      console.error("Error al eliminar", e);
      setError(`No se pudo eliminar ${item.nombre}`);
    }
  };

  const subirTodos = async () => {
    const pendientes = files.filter((f) => f.nuevo && f.file);
    for (const item of pendientes) {
      // eslint-disable-next-line no-await-in-loop
      await subirArchivo(item);
    }
  };

  return (
    <div className="subir-multimedia">
      <div className="subir-multimedia__header">
        <label className="admin-label">
          Archivos multimedia (imágenes y videos)
        </label>
        <div className="subir-multimedia__actions">
          <input
            ref={inputRef}
            type="file"
            multiple
            accept="image/*,video/*"
            onChange={handleInputChange}
            disabled={disabled || !itemId}
            style={{ display: "none" }}
          />
          <button
            type="button"
            className="admin-btn admin-btn--secondary"
            onClick={() => inputRef.current && inputRef.current.click()}
            disabled={disabled || !itemId}
          >
            <FaCloudUploadAlt /> Seleccionar archivos
          </button>
          {files.some((f) => f.nuevo) && (
            <button
              type="button"
              className="admin-btn admin-btn--primary"
              onClick={subirTodos}
              disabled={disabled}
            >
              <FaCheck /> Subir todos
            </button>
          )}
        </div>
      </div>

      {!itemId && (
        <p className="admin-form-hint">
          Guarda primero el {itemType === "noticia" ? "noticia" : "evento"} para poder subir archivos.
        </p>
      )}

      {error && <p className="admin-form-error">{error}</p>}
      {info && <p className="admin-form-info">{info}</p>}

      {files.length > 0 && (
        <ul className="subir-multimedia__list">
          {files.map((f, i) => (
            <li
              key={f.id || f.nombre + i}
              className={`subir-multimedia__item subir-multimedia__item--${
                f.tipo === "VIDEO" ? "video" : "imagen"
              }`}
            >
              {f.tipo === "VIDEO" ? (
                <video src={f.url} muted className="subir-multimedia__preview" />
              ) : (
                <img src={f.url} alt={f.nombre} className="subir-multimedia__preview" />
              )}
              <div className="subir-multimedia__info">
                <span className="subir-multimedia__tipo">
                  {f.tipo === "VIDEO" ? <FaVideo /> : <FaImage />}
                  {f.tipo}
                </span>
                <span className="subir-multimedia__nombre" title={f.nombre}>
                  {f.nombre}
                </span>
                {f.tamano && (
                  <span className="subir-multimedia__tamano">
                    {(f.tamano / 1024).toFixed(1)} KB
                  </span>
                )}
                {f.subiendo && <span className="subir-multimedia__estado">Subiendo...</span>}
                {f.id && <span className="subir-multimedia__estado">#{f.id}</span>}
              </div>
              <button
                type="button"
                className="subir-multimedia__delete"
                onClick={() => eliminarArchivo(f)}
                title="Eliminar"
                disabled={f.subiendo}
              >
                <FaTrash />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SubirMultimedia;
