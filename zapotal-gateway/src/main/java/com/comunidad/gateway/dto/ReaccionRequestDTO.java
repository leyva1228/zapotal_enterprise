package com.comunidad.gateway.dto;

import jakarta.validation.constraints.NotBlank;

public record ReaccionRequestDTO(
        Long noticia,
        Long evento,
        Long comentario,

        @NotBlank(message = "El tipo de reacción es obligatorio")
        String tipo
) {
}