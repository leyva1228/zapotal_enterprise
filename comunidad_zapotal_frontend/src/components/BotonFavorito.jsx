import React, { useEffect, useState, useCallback } from "react";
import { FaRegStar, FaStar } from "react-icons/fa";
import api from "../api";
import { useAuth } from "../context/AuthContext";
import "./BotonFavorito.css";

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

export default function BotonFavorito({ tipo, itemId, size = 22 }) {
  const { isAuthenticated } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [loading, setLoading] = useState(false);
  const [favId, setFavId] = useState(null);

  const cargarEstado = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const { data } = await api.get(`/favoritos/?tipo=${tipo}`);
      const list = Array.isArray(data) ? data : (data?.results || []);
      const fav = list.find((f) => {
        if (tipo === 'NOTICIA') return f.noticia === itemId;
        return f.evento === itemId;
      });
      setIsFavorite(!!fav);
      setFavId(fav ? fav.id : null);
    } catch (e) {
      setIsFavorite(false);
      setFavId(null);
    }
  }, [isAuthenticated, tipo, itemId]);

  useEffect(() => { cargarEstado(); }, [cargarEstado]);

  const toggle = async (e) => {
    e?.preventDefault();
    e?.stopPropagation();
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    setLoading(true);
    try {
      if (isFavorite && favId) {
        await api.delete(`/favoritos/${favId}/`);
        setIsFavorite(false);
        setFavId(null);
      } else {
        const payload = { tipo };
        if (tipo === 'NOTICIA') payload.noticia = itemId;
        else payload.evento = itemId;
        const { data } = await api.post('/favoritos/', payload);
        setIsFavorite(true);
        setFavId(data.id);
      }
    } catch (err) {
      const d = err.response?.data;
      const msg = typeof d === 'string' ? d : (d?.detail || 'No se pudo actualizar.');
      window.dispatchEvent(new CustomEvent('app-toast', { detail: { type: 'error', text: msg } }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      className={`fav-btn ${isFavorite ? 'fav-btn--active' : ''}`}
      onClick={toggle}
      disabled={loading}
      title={isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
      aria-label={isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
      aria-pressed={isFavorite}
    >
      {isFavorite ? <FaStar size={size} /> : <FaRegStar size={size} />}
    </button>
  );
}
