package com.comunidad.gateway.controller;

import com.comunidad.gateway.service.DjangoHealthService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class HealthController {

    private final DjangoHealthService djangoHealthService;

    @GetMapping("/api/health")
    public String health() {
        return "Zapotal Gateway funcionando correctamente";
    }

    @GetMapping("/api/django-test")
    public String djangoTest() {
        return djangoHealthService.probarConexion();
    }
}