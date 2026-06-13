package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.NotificacionResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.service.NotificacionesService;
import com.comunidad.gateway.util.AuthHeaderUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/notificaciones")
@RequiredArgsConstructor
public class NotificacionesController {

    private final NotificacionesService service;

    @GetMapping
    public PagedResponseDTO<List<NotificacionResponseDTO>> obtenerNotificaciones(
            HttpServletRequest request
    ) {
        String auth = AuthHeaderUtil.getBearerToken(request);
        return service.obtenerNotificaciones(auth);
    }
}