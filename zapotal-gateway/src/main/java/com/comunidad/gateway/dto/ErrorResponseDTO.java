package com.comunidad.gateway.dto;

public record ErrorResponseDTO(
        String timestamp,
        int status,
        String error,
        String message,
        String path
) {
}