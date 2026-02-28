from cloudinary.api_client.execute_request import email
from fastapi import FastAPI, Depends, Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from urllib3 import Retry
#XXXXXXXXXXX MODULOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
from Seguridad.Seguridad import crear_token, Encriptar_password, comparar_password
from Seguridad.Dependencias import Desencriptar_token
from Modelos.Usuarios import Usuario, Usuario_Log
from Modelos.Subir_Archivos import Subir_Imagen_cloudinary
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import *
from bson import json_util
import json



import os # para mis variables deentorno


app = FastAPI()

uri = os.getenv("URL_MongoDB")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://boterazo.github.io",# para probar mi Frontend
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://portafolio-jhon-yqwe.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],#Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],#Permite headers personalizados como:
)


#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.on_event("startup") 
def Inicio_API():
    # Create a new client and connect to the server
    app.state.client = MongoClient(uri, server_api=ServerApi('1'))
    app.state.Base_Datos = app.state.client["Usuarios"]          # Base de datos
    app.state.UsuarioBD = app.state.Base_Datos["users"]          # Colección
    app.state.UsuarioBD.create_index("email", unique=True) # creo un indice para evitar crear usuarios duplicados y que se guie por el email
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.on_event("shutdown")
def cierro_API():
    app.state.client.close()
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.post("/login")
def login(form: Usuario_Log):
    print("email ",form.email)
    print("password ",form.password)
    
    UsuarioBD = app.state.UsuarioBD
    # validar usuario aquí...
    user = UsuarioBD.find_one({"email":form.email})
    if not user:
        return {"INF":"Email NO REGISTRADO"}

    user = json.loads(json_util.dumps(user))

    password = comparar_password(form.password,user["password"])
    if not password:
        return {"INF":"CONTRASEÑA INCORRECTA"}
    print("password: ",password)
    # creo token
    access_token = crear_token({"sub": form.email})
    return {"access_token": access_token, "token_type": "bearer"}
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.get("/perfil")
def perfil(usuario: str = Depends(Desencriptar_token)):
    print(type(usuario))
    return {"usuario": usuario}

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.post("/Registrar")
async def Registrar(user:Usuario):
    UsuarioBD = app.state.UsuarioBD

    password = Encriptar_password(user.password)
    user.password = password

    try:
        UsuarioBD.insert_one(user.dict())
        return {"INFO":"USUARIO REGISTRADO","NOMBRE":user.email}
    except DuplicateKeyError as e:
        print("error:",type(e))
        return {"INFO":"Email ya reguistrado en la base de datos"}
    except Exception as e:
        print("ERROR:", e)
        return {"ERROR DESCONOSIDO"}

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.delete("/perfil")
async def Borrar_Usuario(emai:dict = Depends(Desencriptar_token)):
    UsuarioBD = app.state.UsuarioBD

    emai = emai["sub"]
    print("USUARIO: ",emai)
    UsuarioBD.delete_one({"email": emai })
    return{"INFO":"USUARIO ELIMINADO"}

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.get("/Base_Datos")
async def Consultar_DB():
    UsuarioBD = app.state.UsuarioBD

    datos = list(UsuarioBD.find())
    diccionario = json.loads(json_util.dumps(datos))
    for user in diccionario:
        user.pop("_id",None) # borro el id para que no se vea a la hora dellamar a la base de datos completa
        user.pop("password", None) # borro las claves para que no se vean a la ora de consultar toda la base de datos
    return diccionario
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.post("/Subir_Img")
async def Subir_Img(file: UploadFile = File(...),
                    tipo_imagen:str = Form(...),
                    Token:dict = Depends(Desencriptar_token)):

    emai = Token["sub"]

    UsuarioBD = app.state.UsuarioBD
    username = UsuarioBD.find_one({'email': emai})["username"]


    img = await file.read()  # Contenido del archivo en bytes
    if not img:
        return {"error": "No se pudo leer la imagen"}

    print(username+"_"+tipo_imagen)
    URL = Subir_Imagen_cloudinary(img,username,tipo_imagen,emai)
    #print(URL)
    UsuarioBD.update_one(
        {"email": emai},
        {"$set": {"URL_Foto_perfil": URL}})

    return {"URL":URL}
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
@app.get("/Obtener_Img")
async def Obtener_Img(token = Depends(Desencriptar_token)):
    UsuarioBD = app.state.UsuarioBD
    email = token["sub"]
    try:
        URL = UsuarioBD.find_one({'email': email})["URL_Foto_perfil"]
        return URL
    except Exception as e:
            print("ERROR:", e)
            return {"No hay URL DE IMAGEN"}
    
# para correr el server se usa uvicorn main:app --reload


