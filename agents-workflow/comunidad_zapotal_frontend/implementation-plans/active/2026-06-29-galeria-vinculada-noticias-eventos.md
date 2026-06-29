# Plan: Galeria vinculada a noticias y eventos (frontend)

> **Para Hermes:** Usar `subagent-driven-development` para ejecutar este
> plan tarea por tarea, con revision de spec-compliance y code-quality
> entre tareas.

**Goal:** Hacer que la galeria publica `/nosotros/galeria` muestre un
boton "Ver noticia completa" / "Ver evento completo" en el lightbox
cuando la imagen este asociada a una noticia o evento, y que el panel
admin `/admin/galeria` permita vincular cada imagen a una noticia o
evento al crearla/editarla.

**Architecture:** Cambios aditivos en el JSX existente. El componente
lightbox detecta los nuevos campos `noticia`/`evento` del serializer y
renderiza el boton correspondiente. El modal del admin agrega dos
`<select>` para asociar FKs.

**Tech Stack:** React 19, Vite 7, react-router-dom 7, react-icons 4.

---

## Estado

- Estado: DRAFT (esperando aprobacion humana)
- Requiere aprobacion humana: SI
- Fecha: 2026-06-29
- Tecnologia: frontend React (Vite)
- Audit relacionado: `audits/active/2026-06-29-galeria-vinculada-noticias-eventos.md` (backend)
- Plan backend: `implementation-plans/active/2026-06-29-galeria-vinculada-noticias-eventos.md`

## Skills obligatorias

- `writing-plans`
- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Archivos permitidos

- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.jsx`
- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.css`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminGaleria.jsx`
- `comunidad_zapotal_frontend/src/hooks/useGaleria.js` (solo si requiere ajuste menor)

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_frontend/src/api.js` (NO se toca)
- `comunidad_zapotal_frontend/src/context/` (NO se toca)
- `comunidad_zapotal_frontend/src/App.jsx` (NO se cambia; las rutas
  `/noticias/:id` y `/eventos/:id` ya existen)
- `comunidad_zapotal_frontend/src/components/Require*`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx` (NO se toca)
- Cualquier page distinta a Galeria.jsx, Galeria.css y AdminGaleria.jsx

## Micro-tareas

### Task 1: Anadir boton de redireccion en el lightbox (Galeria.jsx)

**Objetivo:** Mostrar un boton en el lightbox que navegue al detalle
de la noticia o evento asociado, cuando la imagen tenga esa asociacion.

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.jsx`

**Pasos:**
1. Importar `useNavigate` de `react-router-dom`:
   ```jsx
   import { useNavigate } from 'react-router-dom';
   ```
2. Dentro de la funcion `Galeria`, agregar:
   ```jsx
   const navigate = useNavigate();
   ```
3. En el bloque del lightbox (donde esta `<div className="galeria-lightbox__caption">`),
   agregar condicionalmente un boton de redireccion **antes** del caption,
   solo si la imagen tiene `noticia` o `evento`:
   ```jsx
   {(lightbox.noticia || lightbox.evento) && (
     <div className="galeria-lightbox__action">
       {lightbox.noticia && (
         <button
           type="button"
           className="galeria-lightbox__btn"
           onClick={(e) => {
             e.stopPropagation();
             navigate(`/noticias/${lightbox.noticia}`);
           }}
         >
           <FaNewspaper style={{ marginRight: 6 }} />
           Ver noticia completa
           {lightbox.noticia_titulo && (
             <span className="galeria-lightbox__btn-sub">
               {lightbox.noticia_titulo}
             </span>
           )}
         </button>
       )}
       {lightbox.evento && (
         <button
           type="button"
           className="galeria-lightbox__btn"
           onClick={(e) => {
             e.stopPropagation();
             navigate(`/eventos/${lightbox.evento}`);
           }}
         >
           <FaCalendarAlt style={{ marginRight: 6 }} />
           Ver evento completo
           {lightbox.evento_titulo && (
             <span className="galeria-lightbox__btn-sub">
               {lightbox.evento_titulo}
             </span>
           )}
         </button>
       )}
     </div>
   )}
   ```
4. Importar `FaNewspaper` (de `react-icons/fa`) si no esta. Usar
   `FaCalendarAlt` que ya viene de `react-icons/fa` (verificar que
   la importacion actual de `Galeria.jsx` lo incluya o agregarlo).
5. NO modificar el resto del componente. NO cambiar el manejo del
   Escape o click-fuera. NO romper el `role="dialog" aria-modal="true"`.

**Comando de verificacion:**
```bash
cd comunidad_zapotal_frontend
# Buscar la nueva cadena:
grep -n "Ver noticia completa" src/pages/Nosotros/Galeria.jsx
grep -n "Ver evento completo"  src/pages/Nosotros/Galeria.jsx
grep -n "useNavigate"          src/pages/Nosotros/Galeria.jsx
```

**Criterio de exito:** los 3 grep devuelven al menos 1 linea.

**Criterio de rollback:** revertir `Galeria.jsx`.

---

### Task 2: Estilos del boton de redireccion (Galeria.css)

**Objetivo:** Darle estilo al nuevo boton del lightbox, consistente
con la paleta del navbar (verde/dorado), responsive.

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.css`

**Pasos:**
1. Abrir `Galeria.css`. Al final, antes de los media queries, agregar:
   ```css
   .galeria-lightbox__action {
     display: flex;
     flex-direction: column;
     gap: 8px;
     align-items: center;
     margin-bottom: 12px;
   }
   .galeria-lightbox__btn {
     display: inline-flex;
     align-items: center;
     gap: 6px;
     padding: 10px 20px;
     background: var(--nb-verde, #1a3209);
     color: #fff;
     border: 1px solid var(--nb-verde, #1a3209);
     border-radius: 999px;
     font-family: inherit;
     font-size: 14px;
     font-weight: 600;
     cursor: pointer;
     transition: background 0.2s, transform 0.1s;
     text-decoration: none;
   }
   .galeria-lightbox__btn:hover {
     background: var(--nb-verde-med, #0f2206);
     transform: translateY(-1px);
   }
   .galeria-lightbox__btn:active {
     transform: translateY(0);
   }
   .galeria-lightbox__btn-sub {
     display: block;
     margin-left: 8px;
     font-weight: 400;
     font-size: 12px;
     opacity: 0.85;
   }
   ```
2. En el bloque `@media (max-width: 640px)`, reducir el padding del
   boton:
   ```css
   .galeria-lightbox__btn { padding: 8px 14px; font-size: 13px; }
   ```
3. NO modificar el resto del CSS. NO eliminar las clases
   `.galeria-modal-*` existentes (queda como CSS legado, fuera de
   alcance limpiarlas en este ticket).

**Comando de verificacion:**
```bash
cd comunidad_zapotal_frontend
grep -n "galeria-lightbox__btn" src/pages/Nosotros/Galeria.css
```

**Criterio de exito:** aparecen referencias a la nueva clase.

**Criterio de rollback:** revertir `Galeria.css`.

---

### Task 3: Selectores de noticia/evento en AdminGaleria (AdminGaleria.jsx)

**Objetivo:** Permitir que el admin asocie una imagen de galeria con
una noticia o evento al crearla/editarla.

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Admin/AdminGaleria.jsx`

**Pasos:**
1. En el estado `EMPTY` (linea ~49), agregar los campos:
   ```jsx
   const EMPTY = {
     titulo: "",
     descripcion: "",
     categoria: "COMUNIDAD",
     fecha: "",
     orden: 0,
     activo: true,
     imagen: null,
     imagen_url_externa: "",
     noticia: "",
     evento: "",
   };
   ```
2. Agregar dos `useState` para las listas de noticias y eventos:
   ```jsx
   const [noticias, setNoticias] = useState([]);
   const [eventos, setEventos] = useState([]);
   ```
3. Agregar un `useEffect` (o dentro de `cargar`) que traiga las listas
   al montar:
   ```jsx
   useEffect(() => {
     Promise.all([
       api.get('/noticias/', { params: { page_size: 100, estado: 'PUBLICADA' } })
         .then(r => setNoticias(extractList(r.data)))
         .catch(() => setNoticias([])),
       api.get('/eventos/', { params: { page_size: 100 } })
         .then(r => setEventos(extractList(r.data)))
         .catch(() => setEventos([])),
     ]);
   }, []);
   ```
4. En `abrirEditar` (linea ~120), popular los nuevos campos:
   ```jsx
   noticia: it.noticia || "",
   evento: it.evento || "",
   imagen_url_externa: it.imagen_url_externa || "",
   ```
5. En `guardar` (linea ~142), antes del POST/PATCH, agregar al
   FormData:
   ```jsx
   if (form.imagen_url_externa) data.append("imagen_url_externa", form.imagen_url_externa);
   if (form.noticia) data.append("noticia", form.noticia);
   if (form.evento) data.append("evento", form.evento);
   ```
6. En el JSX del modal, agregar un bloque nuevo con dos `<select>`
   justo despues del bloque de "Categoria / Fecha":
   ```jsx
   <div className="admin-form-row">
     <div className="admin-form-group">
       <label className="admin-form-group__label">Noticia asociada (opcional)</label>
       <select
         className="admin-select"
         value={form.noticia || ""}
         onChange={(e) => setForm({ ...form, noticia: e.target.value })}
       >
         <option value="">(Sin noticia)</option>
         {noticias.map(n => (
           <option key={n.id} value={n.id}>#{n.id} - {n.titulo}</option>
         ))}
       </select>
     </div>
     <div className="admin-form-group">
       <label className="admin-form-group__label">Evento asociado (opcional)</label>
       <select
         className="admin-select"
         value={form.evento || ""}
         onChange={(e) => setForm({ ...form, evento: e.target.value })}
       >
         <option value="">(Sin evento)</option>
         {eventos.map(ev => (
           <option key={ev.id} value={ev.id}>#{ev.id} - {ev.titulo}</option>
         ))}
       </select>
     </div>
   </div>
   ```
7. En la grilla de imagenes (donde se muestra cada `it`), agregar
   un badge opcional con la asociacion:
   ```jsx
   {(it.noticia || it.evento) && (
     <div className="text-[10px] text-gray-500">
       {it.noticia && <span>Noticia #{it.noticia}</span>}
       {it.noticia && it.evento && ' · '}
       {it.evento && <span>Evento #{it.evento}</span>}
     </div>
   )}
   ```
8. NO modificar la grilla ni el modal en su estructura mayor. NO
   cambiar la logica de `eliminar`, `abrirNuevo`, `cerrar`.

**Comando de verificacion:**
```bash
cd comunidad_zapotal_frontend
grep -n "Noticia asociada" src/pages/Admin/AdminGaleria.jsx
grep -n "Evento asociado"  src/pages/Admin/AdminGaleria.jsx
grep -n "imagen_url_externa" src/pages/Admin/AdminGaleria.jsx
```

**Criterio de exito:** los 3 grep devuelven al menos 1 linea.

**Criterio de rollback:** revertir `AdminGaleria.jsx`.

---

### Task 4: Verificacion final frontend

**Objetivo:** Confirmar que el frontend compila, lintea y se ve
correcto en el navegador.

**Comandos:**
```bash
cd comunidad_zapotal_frontend
npm run lint
npm run build
```

**Verificacion manual (Playwright o browser):**
1. Login como admin en `/login`.
2. Ir a `/admin/institucional` -> tab "Galeria" o a `/admin/galeria`
   (donde este registrado `AdminGaleria`).
3. Click en "Agregar nueva imagen".
4. Verificar que aparecen los selectores "Noticia asociada" y
   "Evento asociado" con opciones.
5. Crear una imagen asociandola a una noticia.
6. Verificar que en la grilla aparece el badge "Noticia #N".
7. Ir a `/nosotros/galeria` (logout primero).
8. Click en la imagen recien creada.
9. Verificar que en el lightbox aparece el boton "Ver noticia completa".
10. Click en el boton: debe navegar a `/noticias/<id>`.
11. Repetir para un evento.
12. Verificar responsive en mobile (320px y 768px).

**Criterio de exito:**
- `npm run build` sin errores ni warnings nuevos.
- `npm run lint` sin errores nuevos.
- Verificacion manual PASS en los 12 pasos.

**Criterio de rollback:** revertir Tasks 1-3. Los cambios son aditivos,
asi que un revert de los 3 archivos devuelve el frontend al estado
anterior sin efectos colaterales.

---

## Notas finales

- El backend debe estar implementado **antes** de este plan. Las nuevas
  tareas del frontend dependen de que el serializer exponga
  `noticia`, `noticia_titulo`, `evento`, `evento_titulo`,
  `imagen_url_externa`.
- Si el backend no esta listo, los selects del admin estaran vacios
  y el boton del lightbox no aparecera (no rompe la UI, solo no
  muestra nada porque las imagenes no tienen FK).
- El frontend NO modifica el contrato de la API ni los hooks
  existentes. El nuevo `useNavigate` se usa solo localmente en
  `Galeria.jsx`.
- Si en el futuro hay miles de noticias, se deberia cambiar
  `page_size=100` por un endpoint `/noticias/select/?q=...` con
  busqueda. **Fuera de alcance de este ticket**.
