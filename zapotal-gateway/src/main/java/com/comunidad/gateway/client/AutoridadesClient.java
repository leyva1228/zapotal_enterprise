package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.AutoridadResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class AutoridadesClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<AutoridadResponseDTO>> obtenerAutoridades() {

        return djangoWebClient
                .get()
                .uri("/api/v1/autoridades/")
                .retrieve()
                .bodyToMono(
                        new ParameterizedTypeReference<
                                PagedResponseDTO<List<AutoridadResponseDTO>>
                                >() {
                        }
                )
                .block();
    }
}