package com.comunidad.comunidadapi.service;

import com.comunidad.comunidadapi.dto.AutoridadDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Service
public class AutoridadService {

    private final WebClient webClient;

    @Value("${django.api.url}")
    private String djangoUrl;

    public AutoridadService(WebClient webClient) {
        this.webClient = webClient;
    }

    public List<AutoridadDTO> obtenerAutoridades() {

        return webClient.get()
                .uri(djangoUrl + "/api/autoridades/")
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<List<AutoridadDTO>>() {})
                .block();
    }
}