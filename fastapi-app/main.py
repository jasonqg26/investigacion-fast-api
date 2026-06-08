# main.py
# Punto de entrada de la aplicación FastAPI.
# Equivale a SpringBootApplication.java
#
# Para correr:
#   uvicorn main:app --reload --port 8081
#
# Documentación automática disponible en:
#   http://localhost:8081/docs   (Swagger UI)
#   http://localhost:8081/redoc  (ReDoc)

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routers import auth, protected

app = FastAPI(
    title="API Gateway",
    description="Autenticación y proxy hacia el servicio de archivos.",
    version="1.0.0",
)

# Registrar routers
app.include_router(auth.router)
app.include_router(protected.router)


# Manejador de errores de validación — devuelve el primer mensaje de error en el
# mismo formato que usa Spring Boot ({ "message": "..." })
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    first_error = exc.errors()[0]["msg"].replace("Value error, ", "")
    return JSONResponse(
        status_code=422,
        content={"message": first_error},
    )
