package com.comunidad.comunidadapi.service;

import com.comunidad.comunidadapi.dto.LoginRequestDTO;
import com.comunidad.comunidadapi.dto.LoginResponseDTO;
import com.comunidad.comunidadapi.dto.RegisterRequestDTO;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class AuthService {

    private final WebClient webClient;

    @Value("${django.api.url}")
    private String djangoUrl;

    public AuthService(WebClient webClient) {
        this.webClient = webClient;
    }

    // LOGIN
    public LoginResponseDTO login(LoginRequestDTO request) {

        return webClient.post()
                .uri(djangoUrl + "/api/login/")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(LoginResponseDTO.class)
                .block();
    }

    // REGISTER
    public String register(RegisterRequestDTO request) {

        return webClient.post()
                .uri(djangoUrl + "/api/register/")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }
}