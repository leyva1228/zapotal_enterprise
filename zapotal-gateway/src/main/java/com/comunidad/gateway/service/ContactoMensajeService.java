package com.comunidad.gateway.service;

import com.comunidad.gateway.client.ContactoMensajeClient;
import com.comunidad.gateway.dto.ContactoMensajeRequestDTO;
import com.comunidad.gateway.dto.ContactoMensajeResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ContactoMensajeService {

    private final ContactoMensajeClient client;

    public ContactoMensajeResponseDTO crearMensajeContacto(ContactoMensajeRequestDTO request) {
        return client.crearMensajeContacto(request);
    }
}