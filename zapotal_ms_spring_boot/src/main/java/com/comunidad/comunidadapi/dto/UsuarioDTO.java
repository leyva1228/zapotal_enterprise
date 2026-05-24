package com.comunidad.comunidadapi.dto;

public class UsuarioDTO {

    private Long id;
    private String nombres;
    private String apellidos;
    private String email;
    private String foto_perfil_url;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNombres() {
        return nombres;
    }

    public void setNombres(String nombres) {
        this.nombres = nombres;
    }

    public String getApellidos() {
        return apellidos;
    }

    public void setApellidos(String apellidos) {
        this.apellidos = apellidos;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getFoto_perfil_url() {
        return foto_perfil_url;
    }

    public void setFoto_perfil_url(String foto_perfil_url) {
        this.foto_perfil_url = foto_perfil_url;
    }
}