package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.dto.ReaccionRequestDTO;
import com.comunidad.gateway.dto.ReaccionResponseDTO;
import com.comunidad.gateway.service.ReaccionesService;
import com.comunidad.gateway.util.AuthHeaderUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/reacciones")
@RequiredArgsConstructor
public class ReaccionesController {

    private final ReaccionesService reaccionesService;

    @GetMapping
    public PagedResponseDTO<List<ReaccionResponseDTO>> obtenerReacciones(
            HttpServletRequest request
    ) {
        String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
        return reaccionesService.obtenerReacciones(authorizationHeader);
    }

    @PostMapping
    public ReaccionResponseDTO crearReaccion(
            @Valid @RequestBody ReaccionRequestDTO reaccionRequest,
            HttpServletRequest request
    ) {
        String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
        return reaccionesService.crearReaccion(reaccionRequest, authorizationHeader);
    }
}