package com.comunidad.comunidadapi.dto;

public class ReaccionResponseDTO {

    private Long id;
    private ReaccionTipo tipo;
    private Long usuario;
    private Long noticia;
    private Long evento;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public ReaccionTipo getTipo() {
        return tipo;
    }

    public void setTipo(ReaccionTipo tipo) {
        this.tipo = tipo;
    }

    public Long getUsuario() {
        return usuario;
    }

    public void setUsuario(Long usuario) {
        this.usuario = usuario;
    }

    public Long getNoticia() {
        return noticia;
    }

    public void setNoticia(Long noticia) {
        this.noticia = noticia;
    }

    public Long getEvento() {
        return evento;
    }

    public void setEvento(Long evento) {
        this.evento = evento;
    }
}