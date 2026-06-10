package com.comunidad.comunidadapi.controller;

import com.comunidad.comunidadapi.dto.EventoDTO;
import com.comunidad.comunidadapi.service.EventoService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class EventoController {

    private final EventoService eventoService;

    public EventoController(EventoService eventoService) {

        this.eventoService = eventoService;
    }

    @GetMapping("/api/eventos")
    public List<EventoDTO> obtenerEventos() {

        return eventoService.obtenerEventos();
    }
}