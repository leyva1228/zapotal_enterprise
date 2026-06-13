package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.MultimediaResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class MultimediaClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<MultimediaResponseDTO>> obtenerMultimedia() {
        return djangoWebClient.get()
                .uri("/api/v1/multimedias/")
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<MultimediaResponseDTO>>>() {})
                .block();
    }
}