package com.comunidad.gateway.service;

import com.comunidad.gateway.client.MensajesClient;
import com.comunidad.gateway.dto.MensajeRequestDTO;
import com.comunidad.gateway.dto.MensajeResponseDTO;
import com.comunidad.gateway.dto.PagedResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MensajesService {

    private final MensajesClient mensajesClient;

    public PagedResponseDTO<List<MensajeResponseDTO>> obtenerMensajes(String auth) {
        return mensajesClient.obtenerMensajes(auth);
    }

    public MensajeResponseDTO crearMensaje(MensajeRequestDTO request, String auth) {
        return mensajesClient.crearMensaje(request, auth);
    }
}