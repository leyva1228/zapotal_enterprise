package com.comunidad.gateway.dto;

public record PagedResponseDTO<T>(
        T data,
        Object meta
) {
}