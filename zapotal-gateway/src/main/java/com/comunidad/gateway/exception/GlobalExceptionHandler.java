package com.comunidad.gateway.exception;

import com.comunidad.gateway.dto.ErrorResponseDTO;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.time.LocalDateTime;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(WebClientResponseException.class)
    public ResponseEntity<ErrorResponseDTO> handleWebClientException(
            WebClientResponseException ex,
            HttpServletRequest request
    ) {
        return ResponseEntity.status(ex.getStatusCode()).body(
                new ErrorResponseDTO(
                        LocalDateTime.now().toString(),
                        ex.getStatusCode().value(),
                        ex.getStatusText(),
                        ex.getResponseBodyAsString(),
                        request.getRequestURI()
                )
        );
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponseDTO> handleValidation(
            MethodArgumentNotValidException ex,
            HttpServletRequest request
    ) {
        String message = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .findFirst()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .orElse("Datos inválidos");

        return ResponseEntity.badRequest().body(
                new ErrorResponseDTO(
                        LocalDateTime.now().toString(),
                        400,
                        "Bad Request",
                        message,
                        request.getRequestURI()
                )
        );
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponseDTO> handleGeneralException(
            Exception ex,
            HttpServletRequest request
    ) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                new ErrorResponseDTO(
                        LocalDateTime.now().toString(),
                        500,
                        "Internal Server Error",
                        "Error interno del gateway",
                        request.getRequestURI()
                )
        );
    }
}