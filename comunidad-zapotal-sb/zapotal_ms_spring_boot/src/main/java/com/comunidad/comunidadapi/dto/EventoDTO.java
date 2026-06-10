package com.comunidad.comunidadapi.dto;

import java.util.List;

public class EventoDTO {

    private Integer id;
    private String titulo;
    private String descripcion;
    private String fecha_evento;
    private String fecha_publicacion;
    private String estado;
    private Integer categoria;
    private UsuarioDTO usuario;
    private List<MultimediaDTO> multimedia;

    public EventoDTO() {
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getTitulo() {
        return titulo;
    }

    public void setTitulo(String titulo) {
        this.titulo = titulo;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getFecha_evento() {
        return fecha_evento;
    }

    public void setFecha_evento(String fecha_evento) {
        this.fecha_evento = fecha_evento;
    }

    public String getFecha_publicacion() {
        return fecha_publicacion;
    }

    public void setFecha_publicacion(String fecha_publicacion) {
        this.fecha_publicacion = fecha_publicacion;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public Integer getCategoria() {
        return categoria;
    }

    public void setCategoria(Integer categoria) {
        this.categoria = categoria;
    }

    public UsuarioDTO getUsuario() {
        return usuario;
    }

    public void setUsuario(UsuarioDTO usuario) {
        this.usuario = usuario;
    }

    public List<MultimediaDTO> getMultimedia() {
        return multimedia;
    }

    public void setMultimedia(List<MultimediaDTO> multimedia) {
        this.multimedia = multimedia;
    }
}