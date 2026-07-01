# Sesión: Admin Responsive Redesign

## Commit
`3c27da0` — `feat(admin): responsive layout redesign + hamburger + fotoperfil fix`

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `AdminLayout.css` | Rediseño visual completo (variables CSS, colores, sombras, radios) + breakpoints responsive 1100/900/768/600/480 + corrección orden media queries |
| `AdminLayout.jsx` | Agregado `<FaBars>` hamburger icon en logo-toggle |
| `AdminDonaciones.css` | Nuevo breakpoint 480px (stats 1 columna, modales full-width, tabla compacta, wrap reducido) |
| `Perfil.jsx` | Guarda `foto_perfil_url` en auth context para que sidebar renderice la foto |

## Qué se logró

- ✅ Layout admin completamente responsivo en 5 breakpoints
- ✅ Sidebar se convierte en overlay a ≤900px con hamburguesa
- ✅ Tablas con `overflow-x: auto` + `min-width: 600px` a ≤768px (cubre Usuarios, Noticias, etc.)
- ✅ Modales full-width en mobile con esquinas redondeadas
- ✅ Stats grids se apilan a 1 columna en mobile
- ✅ AdminDonaciones aislado con su propio responsive 640px + 480px
- ✅ Build verificado (0 errores)

## No incluido en este commit (workflow docs)
- `agents-workflow/auditorias/*.md`
- `agents-workflow/comunidad_zapotal_frontend/*`
- `comunidad_zapotal_backend/apps/reports/migrations/0004_*.py`
