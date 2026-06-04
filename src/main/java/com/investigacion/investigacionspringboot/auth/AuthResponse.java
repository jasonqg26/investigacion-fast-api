package com.investigacion.investigacionspringboot.auth;

public record AuthResponse(
        Long id,
        String name,
        String email,
        String token,
        String message
) {
}
