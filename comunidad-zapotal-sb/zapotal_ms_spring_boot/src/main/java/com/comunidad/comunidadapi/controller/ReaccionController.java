package com.comunidad.comunidadapi.controller;

import com.comunidad.comunidadapi.dto.ReaccionConteoDTO;
import com.comunidad.comunidadapi.dto.ReaccionRequestDTO;
import com.comunidad.comunidadapi.dto.ReaccionResponseDTO;
import com.comunidad.comunidadapi.service.ReaccionService;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/reacciones")
@CrossOrigin("*")
public class ReaccionController {

    private final ReaccionService reaccionService;

    public ReaccionController(
            ReaccionService reaccionService
    ) {
        this.reaccionService = reaccionService;
    }

    @PostMapping
    public ReaccionResponseDTO crearReaccion(
            @RequestBody ReaccionRequestDTO reaccionDTO
    ) {

        return reaccionService.crearReaccion(
                reaccionDTO
        );
    }

    @GetMapping("/conteo/{noticiaId}")
    public ReaccionConteoDTO obtenerConteo(
            @PathVariable Long noticiaId
    ) {

        return reaccionService.obtenerConteo(
                noticiaId
        );
    }
}