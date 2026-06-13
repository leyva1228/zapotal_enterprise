package com.comunidad.gateway.util;

import jakarta.servlet.http.HttpServletRequest;

public class AuthHeaderUtil {

    private AuthHeaderUtil() {
    }

    public static String getBearerToken(HttpServletRequest request) {
        String header = request.getHeader("Authorization");

        if (header == null || header.isBlank()) {
            return null;
        }

        if (!header.startsWith("Bearer ")) {
            return null;
        }

        return header;
    }
}