package org.zapotal.pdfworker.controller;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.zapotal.pdfworker.model.BoletaRequest;
import org.zapotal.pdfworker.model.JobResponse;
import org.zapotal.pdfworker.service.BoletaOrchestrator;
import org.zapotal.pdfworker.service.EmailService;

import java.time.Instant;

/**
 * Endpoints HTTP del PDF worker.
 *
 * <p>El frontend React NO consume estos endpoints directamente.
 * Siempre pasan por el backend Django que actua de proxy + autenticador.
 */
@RestController
@RequestMapping("/api/v1")
public class BoletaController {

    private final BoletaOrchestrator orchestrator;
    private final EmailService emailService;

    public BoletaController(BoletaOrchestrator orchestrator, EmailService emailService) {
        this.orchestrator = orchestrator;
        this.emailService = emailService;
    }

    /**
     * Endpoint principal: encola un job para generar PDF + enviar email.
     * El filtro {@code ApiKeyFilter} ya valido X-Internal-API-Key.
     *
     * <p>Responde 202 Accepted en <100ms con un job_id. El PDF se genera
     * en background y el email sale en otro thread del pool.
     */
    @PostMapping("/internal/render-boleta")
    public ResponseEntity<JobResponse> renderBoleta(@Valid @RequestBody BoletaRequest req) {
        String jobId = emailService.nuevoJobId();
        // Delega al orchestrator (que es @Async). El metodo retorna
        // instantaneamente; el worker procesa en otro thread.
        orchestrator.procesaYEnvia(req);
        return ResponseEntity.status(HttpStatus.ACCEPTED)
                .body(new JobResponse(jobId, "queued", Instant.now()));
    }

    /**
     * Health check (no requiere API key porque esta en una ruta diferente).
     */
    @GetMapping("/internal/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("OK");
    }
}
