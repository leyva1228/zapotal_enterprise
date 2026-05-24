package com.comunidad.comunidadapi.controller;

import com.comunidad.comunidadapi.dto.AutoridadDTO;
import com.comunidad.comunidadapi.service.AutoridadService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class AutoridadController {

    private final AutoridadService autoridadService;

    public AutoridadController(AutoridadService autoridadService) {
        this.autoridadService = autoridadService;
    }

    @GetMapping("/autoridades")
    public List<AutoridadDTO> listar() {
        return autoridadService.obtenerAutoridades();
    }
}