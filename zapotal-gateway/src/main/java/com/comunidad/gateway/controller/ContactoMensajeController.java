package com.comunidad.gateway.controller;

import com.comunidad.gateway.dto.ContactoMensajeRequestDTO;
import com.comunidad.gateway.dto.ContactoMensajeResponseDTO;
import com.comunidad.gateway.service.ContactoMensajeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/contacto")
@RequiredArgsConstructor
public class ContactoMensajeController {

    private final ContactoMensajeService service;

    @PostMapping
    public ContactoMensajeResponseDTO crearMensajeContacto(
            @Valid @RequestBody ContactoMensajeRequestDTO request
    ) {
        return service.crearMensajeContacto(request);
    }
}