package com.comunidad.gateway.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record MensajeRequestDTO(
        @NotNull Long destinatario,
        @NotBlank String contenido
) {
}