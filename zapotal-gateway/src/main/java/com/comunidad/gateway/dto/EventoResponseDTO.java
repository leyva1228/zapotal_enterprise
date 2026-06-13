package com.comunidad.gateway.dto;

import java.util.List;
import java.util.Map;

public record EventoResponseDTO(
        Long id,
        String titulo,
        String descripcion,
        String fecha_inicio,
        String fecha_fin,
        String lugar,
        String imagen_url,
        String categoria_nombre,
        List<Object> multimedia,
        List<Object> comentarios,
        List<Object> reacciones,
        Map<String, Integer> total_reacciones
) {
}