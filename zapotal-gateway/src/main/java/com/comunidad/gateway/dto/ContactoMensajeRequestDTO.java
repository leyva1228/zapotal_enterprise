package com.comunidad.gateway.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record ContactoMensajeRequestDTO(
        @NotBlank String nombre,
        @Email @NotBlank String email,
        @NotBlank String asunto,
        @NotBlank String mensaje
) {
}