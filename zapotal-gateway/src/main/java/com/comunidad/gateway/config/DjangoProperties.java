package com.comunidad.gateway.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "django.api")
public record DjangoProperties(
        String url
) {
}