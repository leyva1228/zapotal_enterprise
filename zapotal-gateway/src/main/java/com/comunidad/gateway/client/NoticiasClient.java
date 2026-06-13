package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.NoticiaResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class NoticiasClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<NoticiaResponseDTO>> obtenerNoticias(String authorizationHeader) {
        return djangoWebClient
                .get()
                .uri("/api/v1/noticias/")
                .headers(headers -> {
                    if (authorizationHeader != null) {
                        headers.set(HttpHeaders.AUTHORIZATION, authorizationHeader);
                    }
                })
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<NoticiaResponseDTO>>>() {})
                .block();
    }
}