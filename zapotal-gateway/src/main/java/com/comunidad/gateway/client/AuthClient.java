package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.LoginRequestDTO;
import com.comunidad.gateway.dto.LoginResponseDTO;
import com.comunidad.gateway.dto.RegisterRequestDTO;
import com.comunidad.gateway.dto.UsuarioDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@RequiredArgsConstructor
public class AuthClient {

    private final WebClient djangoWebClient;

    public UsuarioDTO register(RegisterRequestDTO request) {
        return djangoWebClient.post()
                .uri("/api/v1/register/")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(UsuarioDTO.class)
                .block();
    }

    public LoginResponseDTO login(LoginRequestDTO request) {
        return djangoWebClient.post()
                .uri("/api/v1/login/")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(LoginResponseDTO.class)
                .block();
    }
}