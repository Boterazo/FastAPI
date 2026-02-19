from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext # libreria para encriptar contraseñas

from dotenv import load_dotenv # para mis variables deentorno
load_dotenv() # para mis variables deentorno
import os # para mis variables deentorno


Encriptar = CryptContext(schemes=["bcrypt"],deprecated="auto") # algoritmo de encriptacion bcrypt


SECRET_KEY = os.getenv("SECRET_KEY","123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5


def crear_token(data: dict,tipo_usuario=""):
    username = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # creo una fecha y hora de expiracion del token
    username.update({"exp": expire}) 
    username.update({"tipo_usuario":tipo_usuario})
    return jwt.encode(username, SECRET_KEY, algorithm=ALGORITHM) # retorno el token


def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #desencripto el token
        print(payload)
        return payload
    except JWTError:
        return None

def Encriptar_password(password: str):
    password = Encriptar.hash(password)
    return password

def comparar_password(password,password_DB):
    password = Encriptar.verify(password,password_DB)

    return password # retorna un booleano
