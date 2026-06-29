package org.zapotal.pdfworker.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.math.BigDecimal;

/**
 * Payload que Django envia al PDF worker para generar una boleta.
 *
 * <p>El campo {@code email_destinatario} es OBLIGATORIO (es a donde se
 * envia la boleta). Si Django ya tiene el email del donante en su modelo,
 * lo pasa aqui; el worker no consulta nada de vuelta a Django para
 * mantener el acoplamiento bajo.
 */
public record BoletaRequest(
        @JsonProperty("donacion_id") Long donacionId,
        @JsonProperty("numero_boleta") String numeroBoleta,
        @JsonProperty("monto") BigDecimal monto,
        @JsonProperty("moneda") String moneda,
        @JsonProperty("email_destinatario") String emailDestinatario,
        @JsonProperty("nombre_donante") String nombreDonante,
        @JsonProperty("documento_donante") String documentoDonante,
        @JsonProperty("destino") String destino,
        @JsonProperty("mensaje") String mensaje,
        @JsonProperty("ultimos_4") String ultimos4,
        @JsonProperty("tipo_tarjeta") String tipoTarjeta,
        @JsonProperty("anonima") Boolean anonima
) {
}
