import React, { useEffect, useState, useCallback, useRef } from "react";
import { FaEdit, FaTrash, FaKey, FaLock, FaLockOpen, FaBan, FaUserSlash, FaUndo } from "react-icons/fa";
import api, { extractList } from "../../api";
import AdminModal from "../../components/Admin/AdminModal";
import FiltersBar from "../../components/Admin/FiltersBar";
import Pagination from "../../components/Admin/Pagination";
import { useConfirm } from "../../components/Admin/AdminConfirmDialog";
import { useUrlFilters, parseIntParam } from "../../hooks/useUrlFilters";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";

const ESTADOS = ["ACTIVO", "INACTIVO", "BLOQUEADO", "RECHAZADO", "DE_BAJA", "PENDIENTE_OTP", "PENDIENTE_APROBACION"];

function colorEstado(estado) {
  if (estado === "ACTIVO") return "admin-badge--success";
  if (estado === "BLOQUEADO") return "admin-badge--danger";
  if (estado === "RECHAZADO") return "admin-badge--danger";
  if (estado === "PENDIENTE_APROBACION" || estado === "PENDIENTE_OTP") return "admin-badge--warning";
  if (estado === "INACTIVO") return "admin-badge--gray";
  if (estado === "DE_BAJA") return "admin-badge--danger";
  return "admin-badge--gray";
}

const EMPTY = {
  email: "", password: "", tipo_usuario: "COMUNERO", estado: "ACTIVO",
  comunero: "",
};

export default function AdminUsuarios() {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [comuneros, setComuneros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const { confirm, ConfirmDialog } = useConfirm();
  const [actionModal, setActionModal] = useState({ open: false, item: null, accion: null });
  const [motivo, setMotivo] = useState("");

  const [filters, setFilters, clearFilters] = useUrlFilters({
    estado: { defaultValue: "" },
    tipo_usuario: { defaultValue: "" },
    search: { defaultValue: "" },
    page: { defaultValue: 1, parser: parseIntParam },
  });

  const debouncedSearch = useDebouncedValue(filters.search, 350);
  const abortRef = useRef(null);

  const cargar = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(""); setOk("");
    try {
      const params = { page: filters.page, page_size: 15 };
      if (filters.estado) params.estado = filters.estado;
      if (filters.tipo_usuario) params.tipo_usuario = filters.tipo_usuario;
      if (debouncedSearch) params.search = debouncedSearch;
      const [u, c] = await Promise.all([
        api.get("/usuarios/", { params, signal: controller.signal }),
        api.get("/comuneros/", { signal: controller.signal }).catch(() => ({ data: { data: [] } })),
      ]);
      const data = u.data;
      const list = extractList(data);
      setItems(list);
      setTotalItems(data.count || list.length);
      setComuneros(extractList(c.data));
    } catch (e) {
      if (e.name !== "CanceledError" && e.name !== "AbortError") {
        setError("No se pudieron cargar los usuarios.");
      }
    } finally {
      setLoading(false);
    }
  }, [filters.page, filters.estado, filters.tipo_usuario, debouncedSearch]);

  useEffect(() => { cargar(); }, [cargar]);

  // Resetea a pagina 1 cuando cambia cualquier filtro (excepto page).
  useEffect(() => {
    if (filters.page !== 1) {
      setFilters({ page: 1 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.estado, filters.tipo_usuario, debouncedSearch]);

  const abrirNuevo = () => { setEditItem(null); setForm(EMPTY); setModalOpen(true); };
  const abrirEditar = (u) => {
    setEditItem(u);
    setForm({
      email: u.email,
      password: "",
      tipo_usuario: u.tipo_usuario,
      estado: u.estado,
      comunero: u.comunero || "",
    });
    setModalOpen(true);
  };
  const cerrar = () => { setModalOpen(false); setEditItem(null); setForm(EMPTY); };

  const guardar = async (e) => {
    e?.preventDefault?.();
    setSaving(true); setError(""); setOk("");
    try {
      const payload = { ...form };
      if (!payload.comunero) delete payload.comunero;
      if (!payload.password) delete payload.password;
      if (editItem) {
        await api.patch(`/usuarios/${editItem.id}/`, payload);
        setOk("Usuario actualizado.");
      } else {
        if (!payload.password) { setError("La contrasena es obligatoria al crear."); setSaving(false); return; }
        await api.post("/usuarios/", payload);
        setOk("Usuario creado.");
      }
      cerrar(); cargar();
    } catch (err) {
      const d = err.response?.data;
      setError(typeof d === "string" ? d : (d?.detail || d?.email?.[0] || JSON.stringify(d) || "Error al guardar."));
    } finally { setSaving(false); }
  };

  const eliminar = async (u) => {
    if (!await confirm({
      title: "Eliminar usuario",
      message: `Eliminar al usuario "${u.email}"? Esta acción no se puede deshacer.`,
    })) return;
    setError(""); setOk("");
    try { await api.delete(`/usuarios/${u.id}/`); setOk("Usuario eliminado."); cargar(); }
    catch (e) { setError("No se pudo eliminar. Puede tener contenido asociado."); }
  };

  const abrirAccion = (item, accion) => {
    setActionModal({ open: true, item, accion });
    setMotivo("");
  };
  const cerrarAccion = () => {
    if (saving) return;
    setActionModal({ open: false, item: null, accion: null });
    setMotivo("");
  };

  const ejecutarAccion = async () => {
    if (!actionModal.item || !actionModal.accion) return;
    setSaving(true);
    setError(""); setOk("");
    try {
      const id = actionModal.item.id;
      const endpoint = {
        aprobar: `/usuarios/${id}/aprobar/`,
        rechazar: `/usuarios/${id}/rechazar/`,
        bloquear: `/usuarios/${id}/bloquear/`,
        desbloquear: `/usuarios/${id}/desbloquear/`,
        dar_baja: `/usuarios/${id}/dar-baja/`,
      }[actionModal.accion];
      const body = (actionModal.accion === "rechazar" || actionModal.accion === "bloquear")
        ? { motivo }
        : (actionModal.accion === "aprobar" ? { notas_admin: motivo } : {});
      await api.post(endpoint, body);
      const labels = {
        aprobar: "aprobado",
        rechazar: "rechazado",
        bloquear: "bloqueado",
        desbloquear: "desbloqueado",
        dar_baja: "dado de baja",
      };
      setOk(`Usuario ${actionModal.item.email} ${labels[actionModal.accion]}.`);
      cerrarAccion();
      cargar();
    } catch (err) {
      const d = err.response?.data;
      setError(typeof d === "string" ? d : (d?.detail || JSON.stringify(d) || "No se pudo completar la accion."));
    } finally {
      setSaving(false);
    }
  };

  const accionConfig = {
    aprobar: { title: "Aprobar usuario", label: "Notas internas (opcional)", color: "admin-btn-success", btn: "Confirmar aprobacion" },
    rechazar: { title: "Rechazar usuario", label: "Motivo del rechazo", color: "admin-btn-danger", btn: "Confirmar rechazo" },
    bloquear: { title: "Bloquear usuario", label: "Motivo del bloqueo", color: "admin-btn-danger", btn: "Confirmar bloqueo" },
    desbloquear: { title: "Desbloquear usuario", label: "Notas (opcional)", color: "admin-btn-primary", btn: "Confirmar desbloqueo" },
    dar_baja: { title: "Dar de baja usuario", label: "Motivo de la baja", color: "admin-btn-danger", btn: "Confirmar baja definitiva" },
  };

  // Chips de filtro rapido por estado.
  const chipsEstado = [
    { key: "estado", value: "", label: "Todos" },
    { key: "estado", value: "PENDIENTE", label: "Pendientes" },
    { key: "estado", value: "ACTIVO", label: "Activos" },
    { key: "estado", value: "BLOQUEADO", label: "Bloqueados" },
    { key: "estado", value: "INACTIVO", label: "Inactivos" },
    { key: "estado", value: "RECHAZADO", label: "Rechazados" },
    { key: "estado", value: "DE_BAJA", label: "De baja" },
  ];
  const chipsRol = [
    { key: "tipo_usuario", value: "", label: "Todos los roles" },
    { key: "tipo_usuario", value: "ADMIN", label: "Admins" },
    { key: "tipo_usuario", value: "COMUNERO", label: "Comuneros" },
    { key: "tipo_usuario", value: "USUARIO", label: "Usuarios" },
  ];

  const totalPages = Math.max(1, Math.ceil(totalItems / 15));

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {ok && <div className="admin-success">{ok}</div>}

      <div className="admin-card mt-4">
        <div className="admin-card__header">
          <h3 className="admin-card__title">Usuarios</h3>
        </div>
        <div className="admin-card__body">
          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            clearFilters={clearFilters}
            chips={chipsEstado}
            searchKey="search"
            searchPlaceholder="Buscar por email, nombre o DNI..."
            extra={
              <select
                className="admin-select"
                value={filters.tipo_usuario || ""}
                onChange={(e) => setFilters({ tipo_usuario: e.target.value, page: 1 })}
                aria-label="Filtrar por rol"
              >
                {chipsRol.map((c) => (
                  <option key={c.value || "__all__"} value={c.value}>{c.label}</option>
                ))}
              </select>
            }
          />

          {loading ? (
            <div className="admin-loading">Cargando...</div>
          ) : items.length === 0 ? (
            <div className="admin-empty">
              {Object.values(filters).some((v) => v && v !== 1)
                ? "No hay usuarios con los filtros aplicados."
                : "No hay usuarios."}
            </div>
          ) : (
            <>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Nombre</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th>Registro</th>
                    <th className="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map(u => (
                    <tr key={u.id}>
                      <td className="font-semibold">{u.email}</td>
                      <td>{u.nombre_completo || "-"}</td>
                      <td>
                        <span className={"admin-badge " + (
                          u.tipo_usuario === "ADMIN"    ? "admin-badge--danger" :
                          u.tipo_usuario === "COMUNERO" ? "admin-badge--info" :
                                                          "admin-badge--gray"
                        )}>
                          {u.tipo_usuario}
                        </span>
                      </td>
                      <td>
                        <span className={"admin-badge " + colorEstado(u.estado)}>
                          {u.estado}
                        </span>
                      </td>
                      <td className="text-mute">
                        {u.fecha_registro ? new Date(u.fecha_registro).toLocaleDateString("es-PE") : "-"}
                      </td>
                      <td className="actions justify-end">
                        {(u.estado === "PENDIENTE_OTP" || u.estado === "PENDIENTE_APROBACION") && (
                          <>
                            <button
                              className="admin-btn admin-btn-sm admin-btn-success"
                              onClick={() => abrirAccion(u, "aprobar")}
                              title="Aprobar"
                            >
                              <FaUserSlash /> Aprobar
                            </button>
                            <button
                              className="admin-btn admin-btn-sm admin-btn-danger"
                              onClick={() => abrirAccion(u, "rechazar")}
                              title="Rechazar"
                            >
                              <FaBan /> Rechazar
                            </button>
                          </>
                        )}
                        {u.estado === "ACTIVO" && (
                          <>
                            <button
                              className="admin-btn admin-btn-sm admin-btn-danger"
                              onClick={() => abrirAccion(u, "bloquear")}
                              title="Bloquear"
                            >
                              <FaLock /> Bloquear
                            </button>
                            <button
                              className="admin-btn admin-btn-sm admin-btn-danger"
                              onClick={() => abrirAccion(u, "dar_baja")}
                              title="Dar de baja"
                            >
                              <FaUserSlash /> Dar de baja
                            </button>
                          </>
                        )}
                        {u.estado === "BLOQUEADO" && (
                          <button
                            className="admin-btn admin-btn-sm admin-btn-success"
                            onClick={() => abrirAccion(u, "desbloquear")}
                            title="Desbloquear"
                          >
                            <FaLockOpen /> Desbloquear
                          </button>
                        )}
                        <button className="admin-btn admin-btn-sm" onClick={() => abrirEditar(u)} title="Editar">
                          <FaEdit />
                        </button>
                        <button className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => eliminar(u)} title="Eliminar">
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <Pagination
                page={filters.page}
                totalPages={totalPages}
                totalItems={totalItems}
                onPageChange={(p) => setFilters({ page: p })}
              />
            </>
          )}
        </div>
      </div>

      <div className="mt-3">
        <button className="admin-btn admin-btn-primary" onClick={abrirNuevo}>
          Crear nuevo usuario
        </button>
      </div>

      <AdminModal
        open={modalOpen}
        title={editItem ? "Editar usuario" : "Crear usuario"}
        onClose={cerrar}
        footer={
          <>
            <button className="admin-btn" onClick={cerrar} disabled={saving}>Cancelar</button>
            <button className="admin-btn admin-btn-primary" onClick={guardar} disabled={saving}>
              {saving ? "Guardando..." : "Guardar"}
            </button>
          </>
        }
      >
        <form onSubmit={guardar}>
          <div className="admin-form-group">
            <label className="admin-form-group__label admin-form-group__label--required">Email</label>
            <input
              type="email" className="admin-input"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              disabled={!!editItem}
              required
            />
            {editItem && <div className="admin-form-hint">El email no se puede modificar.</div>}
          </div>
          <div className="admin-form-group">
            <label className="admin-form-group__label">
              <FaKey className="mr-1" /> Contrasena
            </label>
            <input
              type="password" className="admin-input"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder={editItem ? "Dejar vacio para no cambiar" : "Minimo 6 caracteres"}
              minLength={6}
            />
          </div>
          <div className="admin-form-row">
            <div className="admin-form-group">
              <label className="admin-form-group__label admin-form-group__label--required">Rol</label>
              <select
                className="admin-select" value={form.tipo_usuario}
                onChange={(e) => setForm({ ...form, tipo_usuario: e.target.value })} required
              >
                <option value="COMUNERO">COMUNERO</option>
                <option value="ADMIN">ADMIN</option>
                <option value="USUARIO">USUARIO</option>
              </select>
            </div>
            <div className="admin-form-group">
              <label className="admin-form-group__label">Estado</label>
              <select
                className="admin-select" value={form.estado}
                onChange={(e) => setForm({ ...form, estado: e.target.value })}
              >
                {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
              </select>
            </div>
          </div>
          {form.tipo_usuario === "COMUNERO" && (
            <div className="admin-form-group">
              <label className="admin-form-group__label">Comunero asociado</label>
              <select
                className="admin-select" value={form.comunero}
                onChange={(e) => setForm({ ...form, comunero: e.target.value })}
              >
                <option value="">- Sin comunero -</option>
                {comuneros.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.nombre_completo || `${c.nombres} ${c.apellidos}`} (DNI {c.dni})
                  </option>
                ))}
              </select>
            </div>
          )}
        </form>
      </AdminModal>

      <AdminModal
        open={actionModal.open}
        title={actionModal.accion ? accionConfig[actionModal.accion].title : ""}
        onClose={cerrarAccion}
        footer={
          <>
            <button className="admin-btn" onClick={cerrarAccion} disabled={saving}>
              <FaUndo /> Cancelar
            </button>
            <button
              className={"admin-btn " + (actionModal.accion ? accionConfig[actionModal.accion].color : "")}
              onClick={ejecutarAccion}
              disabled={saving}
            >
              {saving ? "Procesando..." : (actionModal.accion ? accionConfig[actionModal.accion].btn : "")}
            </button>
          </>
        }
      >
        <p className="text-mute">
          {actionModal.accion === "bloquear" && "Esta accion revocara todos los tokens del usuario y le impedira iniciar sesion."}
          {actionModal.accion === "desbloquear" && "El usuario podra volver a iniciar sesion."}
          {actionModal.accion === "aprobar" && "El usuario recibira un correo de bienvenida."}
          {actionModal.accion === "rechazar" && "El usuario sera marcado como RECHAZADO y no podra iniciar sesion."}
          {actionModal.accion === "dar_baja" && "ATENCION: Esta accion es permanente. El usuario sera marcado como DE_BAJA y no podra volver a iniciar sesion. Se revocaran todos sus tokens."}
        </p>
        <div className="admin-form-group">
          <label className="admin-form-group__label">
            {actionModal.accion ? accionConfig[actionModal.accion].label : ""}
          </label>
          <textarea
            className="admin-textarea"
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            rows={3}
            placeholder={actionModal.accion === "rechazar" || actionModal.accion === "bloquear" ? "Describe el motivo..." : "Opcional..."}
          />
        </div>
      </AdminModal>
      {ConfirmDialog}
    </div>
  );
}
