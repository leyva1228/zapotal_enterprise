package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.NotificacionResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class NotificacionesClient {

    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<NotificacionResponseDTO>> obtenerNotificaciones(String auth) {
        return djangoWebClient.get()
                .uri("/api/v1/notificaciones/")
                .headers(h -> {
                    if (auth != null) h.set(HttpHeaders.AUTHORIZATION, auth);
                })
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<NotificacionResponseDTO>>>() {})
                .block();
    }
}