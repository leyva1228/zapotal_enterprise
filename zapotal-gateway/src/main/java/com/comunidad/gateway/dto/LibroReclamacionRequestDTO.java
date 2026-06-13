package com.comunidad.gateway.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record LibroReclamacionRequestDTO(
        @NotBlank String nombre,
        @Email @NotBlank String email,
        String telefono,
        String direccion,
        @NotBlank String tipo,
        @NotBlank @Size(min = 10) String descripcion
) {
}