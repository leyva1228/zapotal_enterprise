package com.comunidad.gateway.dto;

public record LibroReclamacionResponseDTO(
        Long id,
        String nombre,
        String email,
        String telefono,
        String direccion,
        String tipo,
        String descripcion,
        String fecha,
        String estado
) {
}