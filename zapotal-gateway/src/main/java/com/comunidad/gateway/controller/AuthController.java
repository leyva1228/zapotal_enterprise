package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.LoginRequestDTO;
import com.comunidad.gateway.dto.LoginResponseDTO;
import com.comunidad.gateway.dto.RegisterRequestDTO;
import com.comunidad.gateway.dto.UsuarioDTO;
import com.comunidad.gateway.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public UsuarioDTO register(@Valid @RequestBody RegisterRequestDTO request) {
        return authService.register(request);
    }

    @PostMapping("/login")
    public LoginResponseDTO login(@Valid @RequestBody LoginRequestDTO request) {
        return authService.login(request);
    }
}