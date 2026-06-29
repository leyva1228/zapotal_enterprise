package org.zapotal.pdfworker.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;

import java.io.IOException;
import java.util.List;

/**
 * Seguridad del microservicio.
 *
 * <p>El PDF worker SOLO debe aceptar peticiones de:
 * <ol>
 *   <li>El backend Django (mismo VPC / red interna) - autenticado por
 *       header X-Internal-API-Key.</li>
 *   <li>El health check de Render (sin auth).</li>
 * </ol>
 *
 * <p>El frontend React NO llama a este servicio directamente: siempre
 * pasa por Django.
 */
@Configuration
public class SecurityConfig {

    @Value("${app.internal.api-key}")
    private String internalApiKey;

    @Bean
    public FilterRegistrationBean<ApiKeyFilter> apiKeyFilter() {
        FilterRegistrationBean<ApiKeyFilter> reg = new FilterRegistrationBean<>();
        reg.setFilter(new ApiKeyFilter(internalApiKey));
        reg.addUrlPatterns("/api/v1/internal/*");
        reg.setOrder(1);
        return reg;
    }

    @Bean
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();
        // Solo Django en produccion habla con nosotros. NO permitimos
        // que el frontend React llame directamente: el CORS es restrictivo
        // y no se usan credentials para que el navegador no envie cookies.
        config.setAllowedOrigins(List.of(
                "https://api.comunidadzapotal.org",
                "http://localhost:8000"   // dev
        ));
        config.setAllowedMethods(List.of("GET", "POST"));
        config.setAllowedHeaders(List.of("Content-Type", "X-Internal-API-Key"));
        config.setAllowCredentials(false);
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }

    /**
     * Filtro que valida X-Internal-API-Key en endpoints /api/v1/internal/*.
     * Si la key falta o no coincide, devuelve 401 sin pasar al controller.
     */
    public static class ApiKeyFilter implements jakarta.servlet.Filter {

        private final String expectedKey;

        public ApiKeyFilter(String expectedKey) {
            this.expectedKey = expectedKey;
        }

        @Override
        public void doFilter(
                jakarta.servlet.ServletRequest req,
                jakarta.servlet.ServletResponse res,
                FilterChain chain
        ) throws IOException, ServletException {
            HttpServletRequest http = (HttpServletRequest) req;
            HttpServletResponse httpRes = (HttpServletResponse) res;
            String provided = http.getHeader("X-Internal-API-Key");
            if (provided == null || !provided.equals(expectedKey)) {
                httpRes.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                httpRes.setContentType("application/json");
                httpRes.getWriter().write("{\"error\":\"unauthorized\"}");
                return;
            }
            chain.doFilter(req, res);
        }
    }
}
