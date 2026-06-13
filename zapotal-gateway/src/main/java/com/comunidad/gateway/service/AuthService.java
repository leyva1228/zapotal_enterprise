package com.comunidad.gateway.service;

import com.comunidad.gateway.client.AuthClient;
import com.comunidad.gateway.dto.LoginRequestDTO;
import com.comunidad.gateway.dto.LoginResponseDTO;
import com.comunidad.gateway.dto.RegisterRequestDTO;
import com.comunidad.gateway.dto.UsuarioDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthClient authClient;

    public UsuarioDTO register(RegisterRequestDTO request) {
        return authClient.register(request);
    }

    public LoginResponseDTO login(LoginRequestDTO request) {
        return authClient.login(request);
    }
}