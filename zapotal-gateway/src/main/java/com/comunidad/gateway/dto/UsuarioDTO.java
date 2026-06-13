package com.comunidad.gateway.dto;

public record UsuarioDTO(
        Long id,
        String email,
        String tipo_usuario,
        String estado,
        String foto_perfil,
        String foto_perfil_url,
        String nombre_completo,
        String iniciales,
        String nombres,
        String apellidos,
        String dni,
        String fecha_registro,
        Boolean is_active,
        Long comunero
) {
}