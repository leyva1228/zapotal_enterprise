package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.LibroReclamacionRequestDTO;
import com.comunidad.gateway.dto.LibroReclamacionResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@RequiredArgsConstructor
public class LibroReclamacionClient {

    private final WebClient djangoWebClient;

    public LibroReclamacionResponseDTO crearReclamo(
            LibroReclamacionRequestDTO request
    ) {
        return djangoWebClient.post()
                .uri("/api/v1/libro-reclamaciones/")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(LibroReclamacionResponseDTO.class)
                .block();
    }
}