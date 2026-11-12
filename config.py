import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/ecommerce") 
    INSTANCIA_GREENAPI = os.environ.get("INSTANCIA_GREENAPI")
    TOKEN_GREENAPI = os.environ.get("TOKEN_GREENAPI")
    
    @classmethod
    def validacao(cls):
        if not cls.SECRET_KEY:
            raise RuntimeError("SECRET_KEY não definida!")