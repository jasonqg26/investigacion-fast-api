# dependencies.py
# Dependencia de autenticación — equivale a AuthInterceptor en Spring Boot.
# FastAPI la inyecta automáticamente en cualquier endpoint que la declare.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import database

# HTTPBearer extrae automáticamente el token del header "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    """
    Verifica que el token sea válido y retorna el user_id asociado.
    Lanza 401 si el token no existe en el almacén de sesiones.
    """
    token = credentials.credentials
    user_id = database.tokens.get(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes loguearte para usar este endpoint",
        )

    return user_id
