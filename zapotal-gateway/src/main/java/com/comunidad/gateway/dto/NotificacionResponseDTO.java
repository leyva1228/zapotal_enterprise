package com.comunidad.gateway.dto;

public record NotificacionResponseDTO(
        Long id,
        String titulo,
        String mensaje,
        Long destinatario,
        String destinatario_email,
        String fecha,
        Boolean leido,
        String tipo
) {
}