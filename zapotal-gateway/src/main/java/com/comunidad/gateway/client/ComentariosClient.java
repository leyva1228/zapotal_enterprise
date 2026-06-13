package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.ComentarioRequestDTO;
import com.comunidad.gateway.dto.ComentarioResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class ComentariosClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<ComentarioResponseDTO>> obtenerComentarios(
            String authorizationHeader,
            String queryString
    ) {
        String uri = "/api/v1/comentarios/";
        if (queryString != null && !queryString.isBlank()) {
            uri = uri + "?" + queryString;
        }

        return djangoWebClient.get()
                .uri(uri)
                .headers(headers -> {
                    if (authorizationHeader != null) {
                        headers.set(HttpHeaders.AUTHORIZATION, authorizationHeader);
                    }
                })
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<ComentarioResponseDTO>>>() {})
                .block();
    }

    public ComentarioResponseDTO crearComentario(
            ComentarioRequestDTO request,
            String authorizationHeader
    ) {
        return djangoWebClient.post()
                .uri("/api/v1/comentarios/")
                .headers(headers -> {
                    if (authorizationHeader != null) {
                        headers.set(HttpHeaders.AUTHORIZATION, authorizationHeader);
                    }
                })
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ComentarioResponseDTO.class)
                .block();
    }
}