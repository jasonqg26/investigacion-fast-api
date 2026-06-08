# routers/auth.py
# Endpoints de autenticación — equivale a AuthController + AuthService de Spring Boot.
#
#   POST /api/auth/register  →  registra un usuario nuevo
#   POST /api/auth/login     →  autentica y retorna un token de sesión

import uuid

from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext

import database
from models import AuthResponse, LoginRequest, RegisterRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Contexto de hashing — equivale a BCryptPasswordEncoder de Spring Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
def register(request: RegisterRequest):
    # Verificar que el email no esté registrado
    email_exists = any(u["email"] == request.email for u in database.users.values())
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )

    user_id = database.next_id()
    database.users[user_id] = {
        "id": user_id,
        "name": request.name,
        "email": request.email,
        "password": pwd_context.hash(request.password),
    }

    return AuthResponse(
        id=user_id,
        name=request.name,
        email=request.email,
        token=None,
        message="Usuario registrado correctamente",
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    # Buscar usuario por email
    user = next(
        (u for u in database.users.values() if u["email"] == request.email),
        None,
    )

    # Mismo mensaje para email inexistente o contraseña incorrecta (evita enumeración)
    if user is None or not pwd_context.verify(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales incorrectas",
        )

    # Generar token de sesión en memoria
    token = str(uuid.uuid4())
    database.tokens[token] = user["id"]

    return AuthResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        token=token,
        message="Login correcto",
    )
