# Data Model — Entity Relationships

```mermaid
erDiagram
    Usuario {
        int id PK
        string email UK
        string password
        string nombres
        string apellidos
        string telefono
        bool is_active
        bool is_admin
        bool is_comunero
        date registered_at
        datetime last_login
    }

    Comunero {
        int id PK
        int usuario_id FK
        string direccion
        string ocupacion
        string foto_perfil
        date fecha_nacimiento
    }

    Categoria {
        int id PK
        string nombre
        string slug UK
        string descripcion
        int tenant_id FK
    }

    Noticia {
        int id PK
        string titulo
        string slug UK
        text contenido
        string resumen
        string estado
        int autor_id FK
        int categoria_id FK
        int vistas
        datetime created_at
        datetime updated_at
        int tenant_id FK
    }

    Evento {
        int id PK
        string titulo
        string slug UK
        text descripcion
        date fecha_evento
        string lugar
        int organizador_id FK
        datetime created_at
        int tenant_id FK
    }

    Multimedia {
        int id PK
        string titulo
        string archivo
        string tipo
        int noticia_id FK
        int tenant_id FK
    }

    Comentario {
        int id PK
        text contenido
        int autor_id FK
        int noticia_id FK
        datetime created_at
        datetime updated_at
        int tenant_id FK
    }

    Reaccion {
        int id PK
        string tipo
        int usuario_id FK
        int noticia_id FK
        datetime created_at
        int tenant_id FK
    }

    Autoridad {
        int id PK
        string nombre
        string cargo
        string descripcion
        string foto
        int orden
        int tenant_id FK
    }

    Mensaje {
        int id PK
        text contenido
        int remitente_id FK
        int destinatario_id FK
        bool leido
        datetime created_at
        int tenant_id FK
    }

    Notificacion {
        int id PK
        string titulo
        text mensaje
        int usuario_id FK
        bool leida
        datetime created_at
        int tenant_id FK
    }

    Contacto {
        int id PK
        string nombre
        string email
        string asunto
        text mensaje
        datetime created_at
        int tenant_id FK
    }

    Reclamacion {
        int id PK
        string nombre
        string email
        string asunto
        text descripcion
        string estado
        datetime created_at
        datetime updated_at
        int tenant_id FK
    }

    Tenant {
        int id PK
        string schema_name UK
        string name
        bool is_active
    }

%% Relationships
    Usuario ||--o| Comunero : "has"
    Usuario ||--o{ Noticia : "authored"
    Usuario ||--o{ Comentario : "wrote"
    Usuario ||--o{ Reaccion : "reacted"
    Usuario ||--o{ Mensaje : "sent"
    Usuario ||--o{ Mensaje : "received"
    Usuario ||--o{ Notificacion : "has"
    Usuario ||--o{ Evento : "organized"
    Categoria ||--o{ Noticia : "contains"
    Noticia ||--o{ Multimedia : "has"
    Noticia ||--o{ Comentario : "has"
    Noticia ||--o{ Reaccion : "has"
    Tenant ||--o{ Noticia : "scoped"
    Tenant ||--o{ Categoria : "scoped"
    Tenant ||--o{ Autoridad : "scoped"
    Tenant ||--o{ Mensaje : "scoped"
    Tenant ||--o{ Contacto : "scoped"
    Tenant ||--o{ Reclamacion : "scoped"
```

## Model Summary

| App | Models | Purpose |
|-----|--------|---------|
| accounts | Usuario | User auth, admin flags |
| accounts | Comunero | Extended profile (1:1) |
| content | Categoria | News categories |
| content | Noticia | News articles with estado workflow |
| content | Evento | Community events |
| content | Multimedia | Image/video attachments |
| content | Comentario | User comments on news |
| content | Reaccion | Like/dislike on news |
| comunidad | Autoridad | Community authorities |
| messaging | Mensaje | Direct messages between users |
| messaging | Notificacion | System notifications |
| reports | Contacto | Public contact form |
| reports | Reclamacion | Public complaints with estado |
