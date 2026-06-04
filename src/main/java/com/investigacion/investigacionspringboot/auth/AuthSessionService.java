package com.investigacion.investigacionspringboot.auth;

import com.investigacion.investigacionspringboot.user.User;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class AuthSessionService {

    private final Map<String, Long> activeTokens = new ConcurrentHashMap<>();

    public String createToken(User user) {
        String token = UUID.randomUUID().toString();
        activeTokens.put(token, user.getId());
        return token;
    }

    public Optional<Long> findUserIdByToken(String token) {
        if (token == null || token.isBlank()) {
            return Optional.empty();
        }

        return Optional.ofNullable(activeTokens.get(token));
    }
}
