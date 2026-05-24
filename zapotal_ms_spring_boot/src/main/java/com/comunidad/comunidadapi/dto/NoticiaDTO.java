package com.comunidad.comunidadapi.dto;

import lombok.Data;

import java.util.List;

@Data
public class NoticiaDTO {

    private Integer id;

    private String titulo;

    private String contenido;

    private String fecha_publicacion;

    private String estado;

    private UsuarioDTO usuario;

    private Integer categoria;

    private List<MultimediaDTO> multimedia;
}