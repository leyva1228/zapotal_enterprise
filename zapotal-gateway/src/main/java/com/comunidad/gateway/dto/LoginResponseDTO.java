package com.comunidad.gateway.dto;

public record LoginResponseDTO(
        String access,
        String refresh,
        UsuarioDTO usuario
) {
}