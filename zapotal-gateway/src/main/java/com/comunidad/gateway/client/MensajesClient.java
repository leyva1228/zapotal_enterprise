package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.MensajeRequestDTO;
import com.comunidad.gateway.dto.MensajeResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class MensajesClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<MensajeResponseDTO>> obtenerMensajes(String auth) {
        return djangoWebClient.get()
                .uri("/api/v1/mensajes/")
                .headers(h -> {
                    if (auth != null) h.set(HttpHeaders.AUTHORIZATION, auth);
                })
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<MensajeResponseDTO>>>() {})
                .block();
    }

    public MensajeResponseDTO crearMensaje(MensajeRequestDTO request, String auth) {
        return djangoWebClient.post()
                .uri("/api/v1/mensajes/")
                .headers(h -> {
                    if (auth != null) h.set(HttpHeaders.AUTHORIZATION, auth);
                })
                .bodyValue(request)
                .retrieve()
                .bodyToMono(MensajeResponseDTO.class)
                .block();
    }
}