from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .Seguridad import verificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # tipo de autorizacion verifica si es Bearer y le quita ese string y se queda con el token


def Desencriptar_token(token: str = Depends(oauth2_scheme)):
    payload = verificar_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    return payload
