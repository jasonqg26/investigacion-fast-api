# routers/protected.py
# Endpoints protegidos — equivale a ProtectedController + FileController de Spring Boot.
# Todos requieren un token válido via "Authorization: Bearer <token>".
#
#   GET  /api/protected/hello          →  endpoint de prueba
#   POST /api/protected/files          →  sube un archivo al servicio Node.js
#   GET  /api/protected/files/{fileId} →  obtiene la URL de descarga del servicio Node.js

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

import config
from dependencies import get_current_user_id
from models import FileDownloadResponse

router = APIRouter(prefix="/api/protected", tags=["protected"])


@router.get("/hello")
def hello(_user_id: int = Depends(get_current_user_id)):
    """Endpoint de prueba. Requiere autenticación."""
    return {"message": "Hello World"}


@router.post("/files", status_code=302)
def request_upload(
    _user_id: int = Depends(get_current_user_id),
):
    """
    El cliente solicita subir un archivo.
    FastAPI pide al servicio Node.js una URL pre-firmada de subida
    y redirige al cliente con 302 hacia esa URL.
    El archivo viaja directo del cliente al servicio, sin pasar por FastAPI.
    """
    url = f"{config.FILE_STORAGE_BASE_URL}{config.FILE_STORAGE_UPLOAD_URL_PATH}"

    try:
        with httpx.Client() as client:
            response = client.post(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo obtener la URL de subida: {exc.response.text}",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo conectar con la API externa de archivos",
        )

    data = response.json()
    upload_url = data.get("uploadUrl")

    if not upload_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La API de archivos no devolvio una URL de subida valida",
        )

    # 302 redirect — el cliente sigue este redirect y sube el archivo directo al Node.js
    return RedirectResponse(url=upload_url, status_code=302)


@router.get("/files/{file_id}", response_model=FileDownloadResponse)
def get_download_url(
    file_id: str,
    _user_id: int = Depends(get_current_user_id),
):
    """
    Consulta la URL de descarga de un archivo en el servicio Node.js.
    Retorna el fileId y la downloadUrl.
    """
    url = f"{config.FILE_STORAGE_BASE_URL}{config.FILE_STORAGE_DOWNLOAD_PATH}".replace(
        "{fileId}", file_id
    )

    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"No se pudo consultar el archivo en la API externa: {exc.response.text}",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo conectar con la API externa de archivos",
        )

    data = response.json()
    download_url = data.get("downloadUrl") or data.get("url")

    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La API de archivos no devolvio una URL valida",
        )

    return FileDownloadResponse(fileId=file_id, downloadUrl=download_url)
