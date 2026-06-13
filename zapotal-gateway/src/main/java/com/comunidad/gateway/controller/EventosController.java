package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.EventoResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.service.EventosService;
import com.comunidad.gateway.util.AuthHeaderUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/eventos")
@RequiredArgsConstructor
public class EventosController {

    private final EventosService eventosService;

    @GetMapping
    public PagedResponseDTO<List<EventoResponseDTO>> obtenerEventos(HttpServletRequest request) {
        String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
        return eventosService.obtenerEventos(authorizationHeader);
    }
}