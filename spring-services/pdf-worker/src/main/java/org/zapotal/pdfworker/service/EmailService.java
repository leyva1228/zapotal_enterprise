package org.zapotal.pdfworker.service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.zapotal.pdfworker.model.BoletaRequest;

import java.util.UUID;

/**
 * Envia emails de boleta en background.
 *
 * <p>{@code @Async} garantiza que el response HTTP al endpoint de Django
 * no espere al SMTP. El thread pool esta configurado en
 * {@code AsyncConfig} con un tamanio fijo.
 *
 * <p>Si el envio falla, se loguea con nivel WARN. En produccion convendria
 * reencolar con un dead-letter queue (SQS / RabbitMQ / Redis Streams)
 * para que el operador pueda revisar.
 */
@Service
public class EmailService {

    private static final Logger log = LoggerFactory.getLogger(EmailService.class);

    private final JavaMailSender mailSender;
    private final String fromAddress;

    public EmailService(
            JavaMailSender mailSender,
            @Value("${app.email.from}") String fromAddress
    ) {
        this.mailSender = mailSender;
        this.fromAddress = fromAddress;
    }

    @Async
    public void enviarBoleta(BoletaRequest req, byte[] pdfBytes) {
        try {
            MimeMessage msg = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(msg, true, "UTF-8");
            helper.setFrom(fromAddress);
            helper.setTo(req.emailDestinatario());
            helper.setSubject(
                    String.format("Comunidad Zapotal - Boleta de donacion %s",
                            req.numeroBoleta())
            );
            helper.setText(
                    String.format(
                            "Hola %s,\n\nGracias por tu donacion a la Comunidad Zapotal "
                                    + "de S/ %s. Adjuntamos tu boleta en formato PDF.\n\n"
                                    + "Comunidad Campesina Nino Dios de Zapotal",
                            req.nombreDonante() != null ? req.nombreDonante() : "Donante",
                            req.monto()
                    ),
                    false
            );
            helper.addAttachment(
                    String.format("boleta-%s.pdf", req.numeroBoleta()),
                    new org.springframework.core.io.ByteArrayResource(pdfBytes)
            );
            mailSender.send(msg);
            log.info("Email boleta {} enviado a {}", req.numeroBoleta(), req.emailDestinatario());
        } catch (MessagingException | RuntimeException e) {
            // En produccion: reencolar a dead-letter queue.
            log.warn("Error enviando email boleta {}: {}", req.numeroBoleta(), e.getMessage());
        }
    }

    /** Genera un job_id unico para tracking */
    public String nuevoJobId() {
        return "job_" + UUID.randomUUID().toString().replace("-", "").substring(0, 16);
    }
}
