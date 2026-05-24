package com.comunidad.comunidadapi.controller;

import com.comunidad.comunidadapi.dto.NoticiaDTO;
import com.comunidad.comunidadapi.service.NoticiaService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class NoticiaController {

    private final NoticiaService noticiaService;

    public NoticiaController(NoticiaService noticiaService) {
        this.noticiaService = noticiaService;
    }

    @GetMapping("/api/noticias")
    public List<NoticiaDTO> obtenerNoticias() {
        return noticiaService.obtenerNoticias();
    }
}