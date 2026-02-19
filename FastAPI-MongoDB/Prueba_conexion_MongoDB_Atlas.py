
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

from dotenv import load_dotenv # para mis variables deentorno
load_dotenv() # para mis variables deentorno
import os # para mis variables deentorno


uri = os.getenv("URL_MongoDB")


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

UsuariosDB = client["Usuarios"]          # Base de datos
coleccion = UsuariosDB["users"]          # Colección

try:
    
    print("Colecciones:", UsuariosDB.list_collection_names())

    usuarios = UsuariosDB.get_collection('users')
    # Ver todos los documentos
    print("Documentos en la colección:")
    for doc in usuarios.find():
        print(doc)

    # consultar un usuario por el nombre "en caso de encontrar una llave en otra llave espesifica hacer esto ej: jhon.email"
    consulta = {'email': 'jhonsebastianboterolemos@gmail.com'}
    user = coleccion.find_one(consulta)
    print(type(user))
    user = json.dumps(user,indent=4,default=str)
    print("-----Usuario encontrado: \n",user)

    # insertar datos a una colleccion
    try:
        dato = coleccion.create_index("email", unique=True) # creo un indice para evitar crear usuarios duplicados y que se guie por el email
        coleccion.insert_one({
            "username":"Blusan",
            "email":"blusan@hotmail.com",
            "disabled":False,
            "password":"$2a$12$9q9mjNbCqsDp9A1sL/t2Lu0N8RI7rXkpJ0cxLIo3aCQ1tHBTuxEB2", #1234
            })
    except:
        print("Email ya reguistrado en la base de datos")

    # Buscar documentos
    for user in coleccion.find({"disabled": True}):
        print("disabled true --->",user["username"])

    # traer todo en la coleccion
    for doc in coleccion.find():
        print("Correos: ",doc['email']) # solo los emails

    client.close()

except Exception as e:
    raise Exception("No se puede encontrar el documento debido al siguiente error: ", e)
