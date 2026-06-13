package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.NoticiaResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.service.NoticiasService;
import com.comunidad.gateway.util.AuthHeaderUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/noticias")
@RequiredArgsConstructor
public class NoticiasController {

    private final NoticiasService noticiasService;

    @GetMapping
    public PagedResponseDTO<List<NoticiaResponseDTO>> obtenerNoticias(
            HttpServletRequest request
    ) {
        String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
        return noticiasService.obtenerNoticias(authorizationHeader);
    }
}