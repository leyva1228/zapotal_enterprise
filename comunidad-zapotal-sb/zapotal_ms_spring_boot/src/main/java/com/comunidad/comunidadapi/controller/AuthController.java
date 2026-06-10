package com.comunidad.comunidadapi.controller;

import com.comunidad.comunidadapi.dto.LoginRequestDTO;
import com.comunidad.comunidadapi.dto.LoginResponseDTO;
import com.comunidad.comunidadapi.dto.RegisterRequestDTO;
import com.comunidad.comunidadapi.service.AuthService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin("*")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    // LOGIN
    @PostMapping("/login")
    public ResponseEntity<LoginResponseDTO> login(
            @RequestBody LoginRequestDTO request
    ) {

        LoginResponseDTO response = authService.login(request);

        return ResponseEntity.ok(response);
    }

    // REGISTER
    @PostMapping("/register")
    public ResponseEntity<String> register(
            @RequestBody RegisterRequestDTO request
    ) {

        String response = authService.register(request);

        return ResponseEntity.ok(response);
    }
}