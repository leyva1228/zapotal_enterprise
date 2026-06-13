package com.comunidad.gateway.client;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@RequiredArgsConstructor
public class DjangoHealthClient {

    private final WebClient djangoWebClient;

    public String probarConexion() {
        return djangoWebClient
                .get()
                .uri("/api/v1/noticias/")
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }
}