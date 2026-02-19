
import os # para mis variables deentorno

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.uploader import upload



CLOUD_NAME = os.getenv("CLOUD_NAME")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


cloudinary.config(
  cloud_name = CLOUD_NAME,
  api_key = API_KEY,
  api_secret = API_SECRET,
  secure = True  # Esto asegura que se generen URLs HTTPS
)

def Subir_Imagen_cloudinary(archivo:bytes,username:str,img_tipo:str,emai:str):
  
  resultado =  upload(
                      archivo,
                      folder="Usuarios/"+emai,
                      public_id= username+'_'+img_tipo,
                      overwrite=True # indica que si ya existe un archivo con ese mismo public_id, Cloudinary lo reemplaza en lugar de crear uno nuevo.
                      )  # Opcional: "folder" para organizar

  #print("URL segura:", resultado['secure_url'])
  return resultado['secure_url']



