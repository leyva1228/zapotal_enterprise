package com.comunidad.gateway.service;

import com.comunidad.gateway.client.NoticiasClient;
import com.comunidad.gateway.dto.NoticiaResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class NoticiasService {

    private final NoticiasClient noticiasClient;

    public PagedResponseDTO<List<NoticiaResponseDTO>> obtenerNoticias(String authorizationHeader) {
        return noticiasClient.obtenerNoticias(authorizationHeader);
    }
}