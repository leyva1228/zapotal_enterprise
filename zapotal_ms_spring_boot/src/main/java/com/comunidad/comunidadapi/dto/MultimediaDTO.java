package com.comunidad.comunidadapi.dto;

import lombok.Data;

@Data
public class MultimediaDTO {

    private Integer id;
    private String archivo_url;
    private String tipo;
    private Integer orden;
}
