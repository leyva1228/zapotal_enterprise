package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.AutoridadResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.service.AutoridadesService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/autoridades")
@RequiredArgsConstructor
public class AutoridadesController {

    private final AutoridadesService autoridadesService;

    @GetMapping
    public PagedResponseDTO<List<AutoridadResponseDTO>> obtenerAutoridades() {

        return autoridadesService.obtenerAutoridades();
    }
}