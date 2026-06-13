package com.comunidad.gateway.dto;

import java.util.List;
import java.util.Map;

public record NoticiaResponseDTO(
        Long id,
        String titulo,
        String contenido,
        String resumen,
        String imagen_url,
        String categoria_nombre,
        List<Object> multimedia,
        List<Object> comentarios,
        List<Object> reacciones,
        Map<String, Integer> total_reacciones
) {
}