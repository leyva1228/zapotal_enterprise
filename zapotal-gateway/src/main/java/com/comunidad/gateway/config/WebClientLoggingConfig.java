package com.comunidad.gateway.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.ExchangeFilterFunction;
import reactor.core.publisher.Mono;

@Configuration
@Slf4j
public class WebClientLoggingConfig {

    @Bean
    public ExchangeFilterFunction logRequest() {
        return ExchangeFilterFunction.ofRequestProcessor(request -> {

            log.info(
                    "SPRING -> DJANGO {} {}",
                    request.method(),
                    request.url()
            );

            return Mono.just(request);
        });
    }

    @Bean
    public ExchangeFilterFunction logResponse() {
        return ExchangeFilterFunction.ofResponseProcessor(response -> {

            log.info(
                    "DJANGO -> SPRING STATUS {}",
                    response.statusCode()
            );

            return Mono.just(response);
        });
    }
}