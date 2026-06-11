# Frontend Architecture — React SPA

```mermaid
graph TB
    subgraph App["React 18 + TypeScript + Vite"]
        R[Router<br/>react-router-dom]
        
        subgraph Layout
            H[Header / Navbar]
            F[Footer]
            L[LoadingScreen]
        end

        subgraph Pages
            Home[Home]
            Login[Login]
            Registro[Registro]
            Perfil[Perfil]
            Noticias[Noticias<br/>DetalleNoticia]
            Eventos[Eventos<br/>DetalleEvento]
            Nosotros[Conocenos<br/>NuestraHistoria]
            Donaciones[Donaciones]
            Admin[Admin<br/>Dashboard, Usuarios, Noticias,<br/>Eventos, Categorias,<br/>Comentarios, Autoridades]
        end

        subgraph Services["API Services"]
            S1[authService<br/>login / register / refresh]
            S2[contentService<br/>noticias / eventos]
            S3[comentarioService]
            S4[reaccionService]
            S5[comunidadService]
            S6[messagingService]
            S7[reportService]
            S8[adminService]
            AX[Axios Instance<br/>+ JWT Interceptor]
        end

        subgraph Context
            CX[AuthContext<br/>user + tokens]
        end

        subgraph UI["Shared UI"]
            C1[Common Components<br/>Cards, Buttons, Forms]
            C2[Admin Components<br/>Tables, CRUD Forms]
        end
    end

    subgraph Backend["Django REST API"]
        B1[/api/v1/]
    end

    R --> Login
    R --> Home
    R --> Noticias
    R --> Eventos
    R --> Nosotros
    R --> Donaciones
    R --> Perfil
    R --> Admin

    Pages --> Services
    Services --> AX
    AX -->|HTTP / JWT| Backend

    Services --> CX
    Pages --> CX
```

## Page-to-API Map

| Page | Route | API Endpoints |
|------|-------|--------------|
| Login | /login | POST accounts/login/ |
| Registro | /register | POST accounts/register/ |
| Home | / | GET content/noticias/, content/eventos/ |
| Noticias | /noticias | GET content/noticias/, content/categorias/ |
| DetalleNoticia | /noticias/:id | GET content/noticias/:id, content/comentarios/ |
| Eventos | /eventos | GET content/eventos/ |
| DetalleEvento | /eventos/:id | GET content/eventos/:id |
| Conocenos | /nosotros | GET comunidad/autoridades/ |
| Perfil | /perfil | GET/PUT accounts/profile/ |
| Admin | /admin/* | CRUD content/*, accounts/*, comunidad/* |
| Donaciones | /donaciones | Redirect externo (Paga.pe) |

## Routing Tree

```
<App>
  <AuthProvider>
    <BrowserRouter>
      <Routes>
        /               → Home
        /login          → Login
        /register       → Registro
        /noticias       → Noticias
        /noticias/:id   → DetalleNoticia
        /eventos        → Eventos
        /eventos/:id    → DetalleEvento
        /nosotros       → Conocenos
        /nuestra-historia → NuestraHistoria
        /donaciones     → Donaciones
        /perfil         → Perfil (protected)
        /admin/*        → AdminLayout (protected, admin)
          /dashboard    → AdminDashboard
          /usuarios     → AdminUsuarios
          /noticias     → AdminNoticias
          /eventos      → AdminEventos
          /categorias   → AdminCategorias
          /comentarios  → AdminComentarios
          /autoridades  → AdminAutoridades
      </Routes>
    </BrowserRouter>
  </AuthProvider>
</App>
```
