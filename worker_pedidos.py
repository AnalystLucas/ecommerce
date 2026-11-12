import bd
from pymongo import ReturnDocument
import time

mongo = bd.Conexao()

def verificar_novos_pedidos():
    total = 0
    
    while True:
        pedido = mongo.select_tb("pedidos").find_one_and_update(
            {"status": "Pendente WhatsApps"},
            {"$set": {"status": "WhatsApp Enviado"}},
            sort=[("_id", 1)],
            return_document=ReturnDocument.AFTER,
        )
        if pedido is None:
            break
        print(f"Chegou pedido novo! #{pedido['_id']} | {pedido}")
        total +=1
    if total == 0:
        print("Nenhum pedido novo...")


verificar_novos_pedidos()