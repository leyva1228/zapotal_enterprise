package com.comunidad.comunidadapi.service;

import com.comunidad.comunidadapi.dto.NoticiaDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Service
public class NoticiaService {

    private final WebClient webClient;

    @Value("${django.api.url}")
    private String djangoUrl;

    public NoticiaService(WebClient webClient) {
        this.webClient = webClient;
    }

    public List<NoticiaDTO> obtenerNoticias() {

        return webClient.get()
                .uri(djangoUrl + "/api/noticias/")
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<List<NoticiaDTO>>() {})
                .block();
    }
}