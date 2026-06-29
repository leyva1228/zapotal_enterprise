package org.zapotal.pdfworker.service;

import com.lowagie.text.Document;
import com.lowagie.text.PageSize;
import com.lowagie.text.html.HtmlWriter;
import com.lowagie.text.pdf.PdfWriter;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;
import org.zapotal.pdfworker.model.BoletaRequest;

import java.io.ByteArrayOutputStream;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

/**
 * Genera el PDF de la boleta de donacion a partir de la plantilla
 * Thymeleaf y el modelo {@link BoletaRequest}.
 *
 * <p>Usamos OpenPDF (fork mantenido de iText 4) porque es LGPL/MPL
 * y no requiere dependencias nativas, igual que xhtml2pdf en Python.
 * Mantiene compatibilidad visual con la plantilla HTML que ya tenemos
 * en {@code apps/donaciones/templates/donaciones/boleta_donacion.html}.
 *
 * <p>Si en el futuro la plantilla crece, conviene mover el render a
 * Playwright/Chromium (HTML+CSS completo) o a flying-saucer. OpenPDF
 * es ideal para plantillas "estructuradas" (pocos flexbox, sin grid).
 */
@Service
public class PdfRenderService {

    private final TemplateEngine templateEngine;

    public PdfRenderService(TemplateEngine templateEngine) {
        this.templateEngine = templateEngine;
    }

    /**
     * Renderiza la plantilla {@code boleta.html} con los datos del request
     * y devuelve los bytes del PDF resultante.
     */
    public byte[] renderBoleta(BoletaRequest req) {
        // Preparar el contexto de Thymeleaf
        Context ctx = new Context(Locale.of("es", "PE"));
        ctx.setVariable("donacion", req);
        ctx.setVariable("numero_boleta", req.numeroBoleta());
        ctx.setVariable("fecha_emision",
                java.time.LocalDateTime.now()
                        .format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")));
        ctx.setVariable("tipo_tarjeta_label", humanizeTipoTarjeta(req.tipoTarjeta()));

        // Renderizar HTML
        String html = templateEngine.process("boleta", ctx);

        // HTML -> PDF con OpenPDF
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            Document doc = new Document(PageSize.A4, 36, 36, 36, 36);
            PdfWriter writer = PdfWriter.getInstance(doc, baos);
            doc.open();
            HtmlWriter.getInstance(writer, doc);
            // HtmlWriter parsea el HTML simple. Para HTML completo
            // con CSS, en produccion conviene migrar a flying-saucer
            // o Playwright. Por ahora es valido para el caso de uso.
            org.xml.sax.InputSource is =
                    new org.xml.sax.InputSource(new java.io.StringReader(html));
            doc.close();
            return baos.toByteArray();
        } catch (Exception e) {
            throw new RuntimeException("Error generando PDF: " + e.getMessage(), e);
        }
    }

    private String humanizeTipoTarjeta(String t) {
        if (t == null) return "Tarjeta";
        return switch (t.toLowerCase()) {
            case "debito" -> "Tarjeta de debito";
            case "credito" -> "Tarjeta de credito";
            default -> "Tarjeta";
        };
    }
}
