# tests/conftest.py
# Configuración global de pytest.
#
# Problema: passlib 1.7.4 intenta leer bcrypt.__about__.__version__ para
# detectar el backend, pero bcrypt 4.x eliminó ese atributo y pasllib lanza
# ValueError. El parche fuerza a passlib a usar el backend "bcrypt" directamente
# sin pasar por la detección de versión que falla.

import bcrypt as _bcrypt_lib
from passlib.handlers import bcrypt as _passlib_bcrypt


def _patched_load_backend(name, dryrun=False):
    """Reemplaza el loader de passlib para evitar la detección de __about__."""
    if name == "bcrypt":
        try:
            # Fuerza que passlib acepte bcrypt 4.x saltando la comprobación de versión
            _passlib_bcrypt.bcrypt.__about__ = type(
                "__about__", (), {"__version__": _bcrypt_lib.__version__}
            )()
        except Exception:
            pass
    return True


# Aplica el parche solo si passlib aún no detectó el backend correctamente
try:
    from passlib.context import CryptContext as _CryptContext
    _ctx = _CryptContext(schemes=["bcrypt"], deprecated="auto")
    _ctx.hash("test")  # dispara la carga del backend
except ValueError:
    # bcrypt 4.x: inyectamos el atributo __about__ que passlib busca
    _bcrypt_lib.__about__ = type(  # type: ignore[attr-defined]
        "__about__", (), {"__version__": _bcrypt_lib.__version__}
    )()
