package com.comunidad.gateway.dto;

public record AutoridadResponseDTO(
        Long id,
        String cargo,
        String periodo,
        String fecha_inicio,
        String fecha_fin,
        String nombres,
        String apellidos,
        String foto_url
) {
}