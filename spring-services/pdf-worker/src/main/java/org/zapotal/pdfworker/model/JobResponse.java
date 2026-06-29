package org.zapotal.pdfworker.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;

/**
 * Respuesta que el PDF worker envia a Django despues de aceptar un job.
 *
 * <p>Django guarda el {@code job_id} en la donacion y el frontend lo usa
 * para hacer polling (o el worker notifica via webhook cuando termina).
 */
public record JobResponse(
        @JsonProperty("job_id") String jobId,
        @JsonProperty("status") String status,         // "queued" | "rendering" | "sent" | "failed"
        @JsonProperty("created_at") Instant createdAt
) {
}
