package com.comunidad.gateway.service;

import com.comunidad.gateway.client.AutoridadesClient;
import com.comunidad.gateway.dto.AutoridadResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AutoridadesService {

    private final AutoridadesClient autoridadesClient;

    public PagedResponseDTO<List<AutoridadResponseDTO>> obtenerAutoridades() {
        return autoridadesClient.obtenerAutoridades();
    }
}