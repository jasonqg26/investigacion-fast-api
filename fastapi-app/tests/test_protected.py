# tests/test_protected.py
# Pruebas para los endpoints protegidos:
#   GET  /api/protected/hello
#   POST /api/protected/files
#   GET  /api/protected/files/{fileId}

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
import database

# allow_redirects=False para capturar el 302 sin que el cliente lo siga
client = TestClient(app, raise_server_exceptions=True)


@pytest.fixture(autouse=True)
def limpiar_base_de_datos():
    """Limpia la BD en memoria y reinicia el contador antes de cada prueba."""
    database.users.clear()
    database.tokens.clear()
    database._next_id = 1
    yield
    database.users.clear()
    database.tokens.clear()


@pytest.fixture
def token_valido():
    """Registra un usuario, hace login y devuelve el token de sesión."""
    client.post("/api/auth/register", json={
        "name": "Tester",
        "email": "tester@example.com",
        "password": "clave123",
    })
    response = client.post("/api/auth/login", json={
        "email": "tester@example.com",
        "password": "clave123",
    })
    return response.json()["token"]


@pytest.fixture
def auth_headers(token_valido):
    """Cabeceras con Bearer token listas para usar en cada request."""
    return {"Authorization": f"Bearer {token_valido}"}


# ---------------------------------------------------------------------------
# GET /api/protected/hello
# ---------------------------------------------------------------------------

class TestHello:

    def test_hello_con_token_valido(self, auth_headers):
        """Token válido devuelve 200 con mensaje Hello World."""
        response = client.get("/api/protected/hello", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_hello_sin_token(self):
        """Sin cabecera Authorization devuelve 401 (FastAPI HTTPBearer)."""
        response = client.get("/api/protected/hello")
        assert response.status_code == 401

    def test_hello_token_invalido(self):
        """Token que no existe en la BD devuelve 401."""
        response = client.get(
            "/api/protected/hello",
            headers={"Authorization": "Bearer token-inventado"},
        )
        assert response.status_code == 401
        assert "loguearte" in response.json()["detail"].lower()

    def test_hello_token_malformado(self):
        """Cabecera sin esquema Bearer devuelve 401 (FastAPI HTTPBearer)."""
        response = client.get(
            "/api/protected/hello",
            headers={"Authorization": "token-sin-esquema"},
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/protected/files
# ---------------------------------------------------------------------------

class TestSolicitarUpload:

    def test_upload_redirige_a_url_presignada(self, auth_headers):
        """Con token válido y servicio externo OK, devuelve 302 con Location."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"uploadUrl": "http://storage.local/upload/abc"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = mock_response
            response = client.post(
                "/api/protected/files",
                headers=auth_headers,
                follow_redirects=False,
            )

        assert response.status_code == 302
        assert response.headers["location"] == "http://storage.local/upload/abc"

    def test_upload_sin_token(self):
        """Sin autenticación devuelve 401 (FastAPI HTTPBearer)."""
        response = client.post("/api/protected/files", follow_redirects=False)
        assert response.status_code == 401

    def test_upload_servicio_externo_falla(self, auth_headers):
        """Si el servicio de archivos responde con error, devuelve 400."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_response
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = mock_response
            response = client.post(
                "/api/protected/files",
                headers=auth_headers,
                follow_redirects=False,
            )

        assert response.status_code == 400

    def test_upload_servicio_externo_no_disponible(self, auth_headers):
        """Si no se puede conectar al servicio externo, devuelve 502."""
        import httpx

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.side_effect = (
                httpx.RequestError("conexión fallida", request=MagicMock())
            )
            response = client.post(
                "/api/protected/files",
                headers=auth_headers,
                follow_redirects=False,
            )

        assert response.status_code == 502

    def test_upload_respuesta_sin_upload_url(self, auth_headers):
        """Si el servicio no devuelve uploadUrl, retorna 400."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # sin uploadUrl
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = mock_response
            response = client.post(
                "/api/protected/files",
                headers=auth_headers,
                follow_redirects=False,
            )

        assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/protected/files/{fileId}
# ---------------------------------------------------------------------------

class TestObtenerDownload:

    def test_obtener_url_descarga_exitoso(self, auth_headers):
        """Con token válido y servicio OK, devuelve fileId y downloadUrl."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"downloadUrl": "http://storage.local/files/xyz"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_response
            response = client.get(
                "/api/protected/files/xyz",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["fileId"] == "xyz"
        assert data["downloadUrl"] == "http://storage.local/files/xyz"

    def test_obtener_url_descarga_campo_url(self, auth_headers):
        """Acepta también el campo 'url' como fallback a 'downloadUrl'."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"url": "http://storage.local/files/abc"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_response
            response = client.get(
                "/api/protected/files/abc",
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert response.json()["downloadUrl"] == "http://storage.local/files/abc"

    def test_obtener_url_sin_token(self):
        """Sin autenticación devuelve 401 (FastAPI HTTPBearer)."""
        response = client.get("/api/protected/files/xyz")
        assert response.status_code == 401

    def test_obtener_url_archivo_no_encontrado(self, auth_headers):
        """Si el servicio devuelve 404, el endpoint lo propaga."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "not found", request=MagicMock(), response=mock_response
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_response
            response = client.get(
                "/api/protected/files/no-existe",
                headers=auth_headers,
            )

        assert response.status_code == 404

    def test_obtener_url_servicio_no_disponible(self, auth_headers):
        """Si no se puede conectar al servicio, devuelve 502."""
        import httpx

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.side_effect = (
                httpx.RequestError("timeout", request=MagicMock())
            )
            response = client.get(
                "/api/protected/files/xyz",
                headers=auth_headers,
            )

        assert response.status_code == 502

    def test_obtener_url_respuesta_sin_url(self, auth_headers):
        """Si el servicio no devuelve ninguna URL, retorna 400."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_response
            response = client.get(
                "/api/protected/files/xyz",
                headers=auth_headers,
            )

        assert response.status_code == 400
