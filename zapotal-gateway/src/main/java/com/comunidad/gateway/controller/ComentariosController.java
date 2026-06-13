package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.ComentarioRequestDTO;
import com.comunidad.gateway.dto.ComentarioResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.service.ComentariosService;
import com.comunidad.gateway.util.AuthHeaderUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/comentarios")
@RequiredArgsConstructor
public class ComentariosController {

    private final ComentariosService comentariosService;

    @GetMapping
    public PagedResponseDTO<List<ComentarioResponseDTO>> obtenerComentarios(
            HttpServletRequest request
    ) {
        String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
        return comentariosService.obtenerComentarios(
                authorizationHeader,
                request.getQueryString()
        );
    }

    @PostMapping
    public ComentarioResponseDTO crearComentario(
            @Valid @RequestBody ComentarioRequestDTO comentarioRequest,
            HttpServletRequest request
    ) {
        String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
        return comentariosService.crearComentario(comentarioRequest, authorizationHeader);
    }
}