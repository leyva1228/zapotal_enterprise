package com.comunidad.gateway;

import com.comunidad.gateway.config.DjangoProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties(DjangoProperties.class)
public class ZapotalGatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(ZapotalGatewayApplication.class, args);
    }

}