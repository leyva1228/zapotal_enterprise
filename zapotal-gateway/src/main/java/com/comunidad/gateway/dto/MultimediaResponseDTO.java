package com.comunidad.gateway.dto;

public record MultimediaResponseDTO(
        Long id,
        String tipo,
        String archivo,
        String archivo_url,
        Long noticia,
        Long evento,
        String fecha_subida
) {
}