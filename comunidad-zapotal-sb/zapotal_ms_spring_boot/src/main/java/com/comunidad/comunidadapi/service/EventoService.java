package com.comunidad.comunidadapi.service;

import com.comunidad.comunidadapi.dto.EventoDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Service
public class EventoService {

    private final WebClient webClient;

    @Value("${django.api.url}")
    private String djangoUrl;

    public EventoService(WebClient webClient) {
        this.webClient = webClient;
    }

    public List<EventoDTO> obtenerEventos() {

        return webClient.get()
                .uri(djangoUrl + "/api/eventos/")
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<List<EventoDTO>>() {})
                .block();
    }
}