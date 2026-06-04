package com.investigacion.investigacionspringboot.auth;

import com.investigacion.investigacionspringboot.user.User;
import com.investigacion.investigacionspringboot.user.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthSessionService authSessionService;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            AuthSessionService authSessionService
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.authSessionService = authSessionService;
    }

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new AuthException("El correo ya esta registrado");
        }

        User user = new User(
                request.name(),
                request.email(),
                passwordEncoder.encode(request.password())
        );

        User savedUser = userRepository.save(user);
        return toResponse(savedUser, null, "Usuario registrado correctamente");
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.email())
                .orElseThrow(() -> new AuthException("Credenciales incorrectas"));

        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
            throw new AuthException("Credenciales incorrectas");
        }

        String token = authSessionService.createToken(user);
        return toResponse(user, token, "Login correcto");
    }

    private AuthResponse toResponse(User user, String token, String message) {
        return new AuthResponse(
                user.getId(),
                user.getName(),
                user.getEmail(),
                token,
                message
        );
    }
}
