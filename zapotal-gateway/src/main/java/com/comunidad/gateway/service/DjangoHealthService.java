package com.comunidad.gateway.service;

import com.comunidad.gateway.client.DjangoHealthClient;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class DjangoHealthService {

    private final DjangoHealthClient client;

    public String probarConexion() {
        return client.probarConexion();
    }
}