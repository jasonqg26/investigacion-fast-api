# tests/test_auth.py
# Pruebas para los endpoints de autenticación:
#   POST /api/auth/register
#   POST /api/auth/login

import pytest
from fastapi.testclient import TestClient

from main import app
import database

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_base_de_datos():
    """Limpia la BD en memoria antes de cada prueba para garantizar aislamiento."""
    database.users.clear()
    database.tokens.clear()
    # Reinicia el contador de IDs para que los tests sean predecibles
    database._next_id = 1
    yield
    database.users.clear()
    database.tokens.clear()


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

class TestRegistro:

    def test_registro_exitoso(self):
        """Registrar un usuario nuevo devuelve 201 y los datos correctos."""
        response = client.post("/api/auth/register", json={
            "name": "Juan Perez",
            "email": "juan@example.com",
            "password": "segura123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Juan Perez"
        assert data["email"] == "juan@example.com"
        assert data["token"] is None
        assert "registrado" in data["message"].lower()

    def test_registro_email_duplicado(self):
        """Registrar con un email ya existente devuelve 400."""
        payload = {"name": "Ana", "email": "ana@example.com", "password": "clave123"}
        client.post("/api/auth/register", json=payload)
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 400
        assert "correo" in response.json()["detail"].lower()

    def test_registro_email_invalido(self):
        """Email con formato inválido devuelve 422."""
        response = client.post("/api/auth/register", json={
            "name": "Pedro",
            "email": "no-es-un-email",
            "password": "clave123",
        })
        assert response.status_code == 422

    def test_registro_password_corta(self):
        """Contraseña de menos de 6 caracteres devuelve 422."""
        response = client.post("/api/auth/register", json={
            "name": "Maria",
            "email": "maria@example.com",
            "password": "123",
        })
        assert response.status_code == 422
        assert "contraseña" in response.json()["message"].lower()

    def test_registro_nombre_vacio(self):
        """Nombre en blanco devuelve 422."""
        response = client.post("/api/auth/register", json={
            "name": "   ",
            "email": "user@example.com",
            "password": "clave123",
        })
        assert response.status_code == 422
        assert "nombre" in response.json()["message"].lower()

    def test_registro_campos_faltantes(self):
        """Cuerpo vacío devuelve 422."""
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422

    def test_registro_guarda_en_base_de_datos(self):
        """Después de registrar, el usuario queda guardado en memoria."""
        client.post("/api/auth/register", json={
            "name": "Luis",
            "email": "luis@example.com",
            "password": "clave123",
        })
        assert len(database.users) == 1
        usuario = list(database.users.values())[0]
        assert usuario["email"] == "luis@example.com"

    def test_registro_password_no_se_guarda_en_texto_plano(self):
        """La contraseña almacenada debe ser un hash bcrypt, no texto plano."""
        client.post("/api/auth/register", json={
            "name": "Sofia",
            "email": "sofia@example.com",
            "password": "mipassword",
        })
        usuario = list(database.users.values())[0]
        assert usuario["password"] != "mipassword"
        assert usuario["password"].startswith("$2b$")


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

class TestLogin:

    def _registrar_usuario(self, email="test@example.com", password="clave123"):
        """Helper para crear un usuario antes de probar login."""
        client.post("/api/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": password,
        })

    def test_login_exitoso(self):
        """Credenciales correctas devuelven 200 y un token."""
        self._registrar_usuario()
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "clave123",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["token"] is not None
        assert len(data["token"]) > 0
        assert "login correcto" in data["message"].lower()

    def test_login_guarda_token_en_bd(self):
        """El token generado queda registrado en la BD en memoria."""
        self._registrar_usuario()
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "clave123",
        })
        token = response.json()["token"]
        assert token in database.tokens

    def test_login_password_incorrecta(self):
        """Contraseña errónea devuelve 400 con mensaje genérico."""
        self._registrar_usuario()
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "equivocada",
        })
        assert response.status_code == 400
        assert "credenciales" in response.json()["detail"].lower()

    def test_login_email_no_registrado(self):
        """Email inexistente devuelve 400 (no enumera usuarios)."""
        response = client.post("/api/auth/login", json={
            "email": "noexiste@example.com",
            "password": "clave123",
        })
        assert response.status_code == 400
        assert "credenciales" in response.json()["detail"].lower()

    def test_login_retorna_datos_del_usuario(self):
        """La respuesta incluye id, name y email del usuario autenticado."""
        self._registrar_usuario(email="carlos@example.com")
        response = client.post("/api/auth/login", json={
            "email": "carlos@example.com",
            "password": "clave123",
        })
        data = response.json()
        assert data["email"] == "carlos@example.com"
        assert data["name"] == "Test User"
        assert isinstance(data["id"], int)

    def test_login_email_invalido(self):
        """Email con formato inválido en login devuelve 422."""
        response = client.post("/api/auth/login", json={
            "email": "esto-no-es-email",
            "password": "clave123",
        })
        assert response.status_code == 422
