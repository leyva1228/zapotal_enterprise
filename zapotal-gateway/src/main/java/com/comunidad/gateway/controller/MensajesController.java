package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.MensajeRequestDTO;
import com.comunidad.gateway.dto.MensajeResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.service.MensajesService;
import com.comunidad.gateway.util.AuthHeaderUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/mensajes")
@RequiredArgsConstructor
public class MensajesController {

    private final MensajesService mensajesService;

    @GetMapping
    public PagedResponseDTO<List<MensajeResponseDTO>> obtenerMensajes(HttpServletRequest request) {
        String auth = AuthHeaderUtil.getBearerToken(request);
        return mensajesService.obtenerMensajes(auth);
    }

    @PostMapping
    public MensajeResponseDTO crearMensaje(
            @Valid @RequestBody MensajeRequestDTO body,
            HttpServletRequest request
    ) {
        String auth = AuthHeaderUtil.getBearerToken(request);
        return mensajesService.crearMensaje(body, auth);
    }
}