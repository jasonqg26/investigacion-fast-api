# config.py
# Configuración central de la aplicación.
# Equivalente a application.properties en Spring Boot.

FILE_STORAGE_BASE_URL        = "http://localhost:3000"
FILE_STORAGE_UPLOAD_URL_PATH = "/files/upload-url"   # genera URL pre-firmada de subida
FILE_STORAGE_UPLOAD_PATH     = "/files/upload"        # recibe el archivo (con token)
FILE_STORAGE_DOWNLOAD_PATH   = "/files/{fileId}"      # retorna URL de descarga
