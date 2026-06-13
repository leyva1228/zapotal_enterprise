package com.comunidad.gateway.dto;

public record ReaccionResponseDTO(
        Long id,
        Long noticia,
        Long evento,
        Long comentario,
        Long autor,
        String autor_email,
        String tipo,
        String fecha
) {
}