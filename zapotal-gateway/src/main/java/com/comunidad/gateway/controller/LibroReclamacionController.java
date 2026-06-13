package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.LibroReclamacionRequestDTO;
import com.comunidad.gateway.dto.LibroReclamacionResponseDTO;
import com.comunidad.gateway.service.LibroReclamacionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/libro-reclamaciones")
@RequiredArgsConstructor
public class LibroReclamacionController {

    private final LibroReclamacionService service;

    @PostMapping
    public LibroReclamacionResponseDTO crearReclamo(
            @Valid @RequestBody LibroReclamacionRequestDTO request
    ) {
        return service.crearReclamo(request);
    }
}