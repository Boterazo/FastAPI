from pydantic import BaseModel


class Usuario(BaseModel):
    username: str
    email: str
    password: str

class Usuario_Log(BaseModel):
    email:str
    password: str



