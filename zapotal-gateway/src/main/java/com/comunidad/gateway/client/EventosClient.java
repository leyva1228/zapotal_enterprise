package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.EventoResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class EventosClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<EventoResponseDTO>> obtenerEventos(String authorizationHeader) {
        return djangoWebClient
                .get()
                .uri("/api/v1/eventos/")
                .headers(headers -> {
                    if (authorizationHeader != null) {
                        headers.set(HttpHeaders.AUTHORIZATION, authorizationHeader);
                    }
                })
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<EventoResponseDTO>>>() {})
                .block();
    }
}