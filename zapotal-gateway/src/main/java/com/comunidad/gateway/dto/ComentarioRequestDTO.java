package com.comunidad.gateway.dto;

import jakarta.validation.constraints.NotBlank;

public record ComentarioRequestDTO(
        Long noticia,
        Long evento,

        @NotBlank(message = "El contenido es obligatorio")
        String contenido,

        Long respuesta_a
) {
}