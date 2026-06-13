package com.comunidad.gateway.dto;

public record ContactoMensajeResponseDTO(
        Long id,
        String nombre,
        String email,
        String asunto,
        String mensaje,
        String fecha
) {
}