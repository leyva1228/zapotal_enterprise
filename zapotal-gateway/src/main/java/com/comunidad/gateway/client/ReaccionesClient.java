package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.dto.ReaccionRequestDTO;
import com.comunidad.gateway.dto.ReaccionResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class ReaccionesClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<ReaccionResponseDTO>> obtenerReacciones(String authorizationHeader) {
        return djangoWebClient.get()
                .uri("/api/v1/reacciones/")
                .headers(headers -> {
                    if (authorizationHeader != null) {
                        headers.set(HttpHeaders.AUTHORIZATION, authorizationHeader);
                    }
                })
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<ReaccionResponseDTO>>>() {})
                .block();
    }

    public ReaccionResponseDTO crearReaccion(
            ReaccionRequestDTO request,
            String authorizationHeader
    ) {
        return djangoWebClient.post()
                .uri("/api/v1/reacciones/")
                .headers(headers -> {
                    if (authorizationHeader != null) {
                        headers.set(HttpHeaders.AUTHORIZATION, authorizationHeader);
                    }
                })
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ReaccionResponseDTO.class)
                .block();
    }
}