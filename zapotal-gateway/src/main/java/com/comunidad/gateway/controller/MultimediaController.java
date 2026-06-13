package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.MultimediaResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.service.MultimediaService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/multimedia")
@RequiredArgsConstructor
public class MultimediaController {

    private final MultimediaService service;

    @GetMapping
    public PagedResponseDTO<List<MultimediaResponseDTO>> obtenerMultimedia() {
        return service.obtenerMultimedia();
    }
}