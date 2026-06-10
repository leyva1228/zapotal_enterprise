package com.comunidad.comunidadapi.service;

import com.comunidad.comunidadapi.dto.ReaccionConteoDTO;
import com.comunidad.comunidadapi.dto.ReaccionRequestDTO;
import com.comunidad.comunidadapi.dto.ReaccionResponseDTO;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class ReaccionService {

    private final WebClient webClient;

    @Value("${django.api.url}")
    private String djangoUrl;

    public ReaccionService(WebClient webClient) {
        this.webClient = webClient;
    }

    public ReaccionResponseDTO crearReaccion(
            ReaccionRequestDTO reaccionDTO
    ) {

        return webClient.post()
                .uri(djangoUrl + "/api/reacciones/")
                .bodyValue(reaccionDTO)
                .retrieve()
                .bodyToMono(ReaccionResponseDTO.class)
                .block();
    }

    public ReaccionConteoDTO obtenerConteo(
            Long noticiaId
    ) {

        return webClient.get()
                .uri(
                        djangoUrl +
                        "/api/reacciones/conteo/" +
                        noticiaId +
                        "/"
                )
                .retrieve()
                .bodyToMono(ReaccionConteoDTO.class)
                .block();
    }
}