package org.zapotal.pdfworker.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.zapotal.pdfworker.model.BoletaRequest;

/**
 * Orquesta la generacion del PDF + envio del email en background.
 *
 * <p>Es el unico metodo que el controller invoca externamente.
 * El metodo es {@code @Async} para que el controller responda rapido
 * (job_id encolado) mientras el PDF se genera y el email se envia
 * en otro thread.
 */
@Service
public class BoletaOrchestrator {

    private static final Logger log = LoggerFactory.getLogger(BoletaOrchestrator.class);

    private final PdfRenderService pdfRender;
    private final EmailService emailService;

    public BoletaOrchestrator(PdfRenderService pdfRender, EmailService emailService) {
        this.pdfRender = pdfRender;
        this.emailService = emailService;
    }

    @Async
    public void procesarYEnvia(BoletaRequest req) {
        log.info("Procesando boleta {} para donacion {}",
                req.numeroBoleta(), req.donacionId());
        try {
            byte[] pdf = pdfRender.renderBoleta(req);
            emailService.enviarBoleta(req, pdf);
            log.info("Boleta {} procesada y enviada correctamente", req.numeroBoleta());
        } catch (Exception e) {
            log.error("Error procesando boleta {}: {}",
                    req.numeroBoleta(), e.getMessage(), e);
        }
    }
}
