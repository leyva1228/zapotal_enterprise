package com.comunidad.gateway.client;

import com.comunidad.gateway.dto.ContactoMensajeRequestDTO;
import com.comunidad.gateway.dto.ContactoMensajeResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@RequiredArgsConstructor
public class ContactoMensajeClient {

    private final WebClient djangoWebClient;

    public ContactoMensajeResponseDTO crearMensajeContacto(ContactoMensajeRequestDTO request) {
        return djangoWebClient.post()
                .uri("/api/v1/contacto-mensajes/")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ContactoMensajeResponseDTO.class)
                .block();
    }
}