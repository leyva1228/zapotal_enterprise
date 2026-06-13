package com.comunidad.gateway.service;

import com.comunidad.gateway.client.NotificacionesClient;
import com.comunidad.gateway.dto.NotificacionResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class NotificacionesService {

    private final NotificacionesClient client;

    public PagedResponseDTO<List<NotificacionResponseDTO>> obtenerNotificaciones(String auth) {
        return client.obtenerNotificaciones(auth);
    }
}