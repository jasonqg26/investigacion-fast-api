# database.py
# "Base de datos" en memoria — equivale a H2 in-memory de Spring Boot.
# Los datos se pierden al reiniciar, igual que en el proyecto original.
#
# Estructura:
#   users: dict[int, dict]  →  { id: { id, name, email, password_hash } }
#   tokens: dict[str, int]  →  { token: user_id }

from threading import Lock

_lock = Lock()

# Almacén de usuarios: id → datos del usuario
users: dict[int, dict] = {}

# Almacén de sesiones activas: token → user_id
tokens: dict[str, int] = {}

# Contador autoincremental para IDs (equivale a GenerationType.IDENTITY)
_next_id: int = 1


def next_id() -> int:
    """Retorna el siguiente ID disponible de forma segura entre hilos."""
    global _next_id
    with _lock:
        current = _next_id
        _next_id += 1
        return current
