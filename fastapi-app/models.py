# models.py
# Schemas de Pydantic — equivalen a los records/DTOs de Spring Boot.
# Pydantic valida automáticamente los datos de entrada.

from pydantic import BaseModel, EmailStr, field_validator


# --- Auth ---

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre es obligatorio")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    id: int
    name: str
    email: str
    token: str | None = None
    message: str


# --- Files ---

class FileUploadResponse(BaseModel):
    fileId: str


class FileDownloadResponse(BaseModel):
    fileId: str
    downloadUrl: str
