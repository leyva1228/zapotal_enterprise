package com.comunidad.gateway.service;

import com.comunidad.gateway.client.ReaccionesClient;
import com.comunidad.gateway.dto.PagedResponseDTO;
import com.comunidad.gateway.dto.ReaccionRequestDTO;
import com.comunidad.gateway.dto.ReaccionResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ReaccionesService {

    private final ReaccionesClient reaccionesClient;

    public PagedResponseDTO<List<ReaccionResponseDTO>> obtenerReacciones(String authorizationHeader) {
        return reaccionesClient.obtenerReacciones(authorizationHeader);
    }

    public ReaccionResponseDTO crearReaccion(
            ReaccionRequestDTO request,
            String authorizationHeader
    ) {
        return reaccionesClient.crearReaccion(request, authorizationHeader);
    }
}