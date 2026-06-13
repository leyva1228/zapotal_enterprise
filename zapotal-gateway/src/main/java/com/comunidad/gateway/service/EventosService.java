package com.comunidad.gateway.service;

import com.comunidad.gateway.client.EventosClient;
import com.comunidad.gateway.dto.EventoResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class EventosService {

    private final EventosClient eventosClient;

    public PagedResponseDTO<List<EventoResponseDTO>> obtenerEventos(String authorizationHeader) {
        return eventosClient.obtenerEventos(authorizationHeader);
    }
}