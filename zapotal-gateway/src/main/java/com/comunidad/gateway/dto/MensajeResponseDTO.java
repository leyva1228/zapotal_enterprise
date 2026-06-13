package com.comunidad.gateway.dto;

public record MensajeResponseDTO(
        Long id,
        Long remitente,
        Long destinatario,
        String remitente_email,
        String destinatario_email,
        String contenido,
        String fecha,
        Boolean leido
) {
}