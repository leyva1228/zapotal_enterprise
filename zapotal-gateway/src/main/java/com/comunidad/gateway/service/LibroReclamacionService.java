package com.comunidad.gateway.service;

import com.comunidad.gateway.client.LibroReclamacionClient;
import com.comunidad.gateway.dto.LibroReclamacionRequestDTO;
import com.comunidad.gateway.dto.LibroReclamacionResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class LibroReclamacionService {

    private final LibroReclamacionClient client;

    public LibroReclamacionResponseDTO crearReclamo(
            LibroReclamacionRequestDTO request
    ) {
        return client.crearReclamo(request);
    }
}