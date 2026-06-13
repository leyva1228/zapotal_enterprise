package com.comunidad.gateway.service;

import com.comunidad.gateway.client.ComentariosClient;
import com.comunidad.gateway.dto.ComentarioRequestDTO;
import com.comunidad.gateway.dto.ComentarioResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ComentariosService {

    private final ComentariosClient comentariosClient;

    public PagedResponseDTO<List<ComentarioResponseDTO>> obtenerComentarios(
            String authorizationHeader,
            String queryString
    ) {
        return comentariosClient.obtenerComentarios(authorizationHeader, queryString);
    }

    public ComentarioResponseDTO crearComentario(
            ComentarioRequestDTO request,
            String authorizationHeader
    ) {
        return comentariosClient.crearComentario(request, authorizationHeader);
    }
}
