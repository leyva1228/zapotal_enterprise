package com.comunidad.gateway.service;

import com.comunidad.gateway.client.MultimediaClient;
import com.comunidad.gateway.dto.MultimediaResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MultimediaService {

    private final MultimediaClient client;

    public PagedResponseDTO<List<MultimediaResponseDTO>> obtenerMultimedia() {
        return client.obtenerMultimedia();
    }
}