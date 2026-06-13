package com.comunidad.gateway.dto;

public record ComentarioResponseDTO(
        Long id,
        Long noticia,
        Long evento,
        Long autor,
        String autor_email,
        String autor_nombre,
        String autor_foto,
        String contenido,
        String fecha,
        String estado,
        Boolean editado,
        Long respuesta_a
) {
}