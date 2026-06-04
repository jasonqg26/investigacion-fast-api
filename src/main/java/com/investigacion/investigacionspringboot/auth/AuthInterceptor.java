package com.investigacion.investigacionspringboot.auth;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class AuthInterceptor implements HandlerInterceptor {

    private static final String BEARER_PREFIX = "Bearer ";

    private final AuthSessionService authSessionService;

    public AuthInterceptor(AuthSessionService authSessionService) {
        this.authSessionService = authSessionService;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        String authorizationHeader = request.getHeader("Authorization");
        String token = getToken(authorizationHeader);

        return authSessionService.findUserIdByToken(token)
                .map(userId -> {
                    request.setAttribute("userId", userId);
                    return true;
                })
                .orElseGet(() -> {
                    response.setStatus(HttpStatus.UNAUTHORIZED.value());
                    response.setContentType("application/json");

                    try {
                        response.getWriter().write("{\"message\":\"Debes loguearte para usar este endpoint\"}");
                    } catch (Exception ignored) {
                        return false;
                    }

                    return false;
                });
    }

    private String getToken(String authorizationHeader) {
        if (authorizationHeader == null || !authorizationHeader.startsWith(BEARER_PREFIX)) {
            return null;
        }

        return authorizationHeader.substring(BEARER_PREFIX.length());
    }
}
