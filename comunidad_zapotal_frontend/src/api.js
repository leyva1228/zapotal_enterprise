import axios from "axios";

const API_BASE_URL =
  (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_URL) ||
  "http://127.0.0.1:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * El backend usa `StandardPagination`, cuya respuesta es
 *   { data: [...], meta: { page, page_size, total_items, ... } }
 * Esta helper acepta:
 *   - arrays crudos (compat)
 *   - { data: [...] }
 *   - { results: [...] } (DRF default, por si algún endpoint no usa paginación custom)
 *   - { data: { data: [...] } } (anidado, no debería pasar)
 */
export const extractList = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.data)) return payload.data;
  if (payload && Array.isArray(payload.results)) return payload.results;
  return [];
};

export { API_BASE_URL };
export default api;
