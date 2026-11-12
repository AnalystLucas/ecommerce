from pymongo import MongoClient
from config import Config

class Conexao:

    def __init__(self):
        self.client = None
        self.bd = None
        self.bd_tabela = None

    def mongodb(self):
        if self.client is None:
            self.client = MongoClient(Config.MONGO_URI)
        return self.client
    
    def select_db(self):
        self.bd = self.mongodb()["ecommerce"]
        return self.bd
    
    def select_tb(self, tabela): # Tabela = Collection no MongoDB
        self.bd_tabela = self.select_db()[tabela]
        return self.bd_tabela
    
    def insert_db(self, col, dados: dict):
        #Recebendo os dados para criar a inserção no banco.
        res = col.insert_one(dados)
        return res 

# Esse foi um teste para verificar se o banco funciona.
# conn = Conexao()
# tabela = "produtos"
# col = conn.select_tb(tabela)
# print(col)
# doc = conn.insert_db(col, {"teste": "teste", "item": "teste", "preco": 19.10})
# print(doc)
