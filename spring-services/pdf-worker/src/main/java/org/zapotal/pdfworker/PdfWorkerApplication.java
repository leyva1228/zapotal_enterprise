package org.zapotal.pdfworker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Microservicio asincrono para generar y enviar boletas de donacion en PDF.
 *
 * <p>Arquitectura:
 * <ul>
 *   <li>Recibe peticiones internas de Django (con API Key compartida) en
 *       {@code /api/v1/internal/render-boleta}.</li>
 *   <li>Genera el PDF en background con {@code @Async} (no bloquea el response).</li>
 *   <li>Envia el email con el PDF adjunto via SMTP/Resend.</li>
 *   <li>Devuelve inmediatamente al Django con un job_id para tracking.</li>
 * </ul>
 *
 * <p>Por que existe: en Django, el endpoint
 * {@code /donaciones/procesar-simulado/} espera a que se genere el PDF y
 * se envie el email antes de responder al usuario, lo que bloquea el
 * request HTTP 3-10 segundos. Delegando este trabajo a un microservicio
 * Spring Boot con workers async, Django responde en <100ms.
 */
@SpringBootApplication
@EnableAsync
@EnableScheduling
public class PdfWorkerApplication {

    public static void main(String[] args) {
        SpringApplication.run(PdfWorkerApplication.class, args);
    }
}
