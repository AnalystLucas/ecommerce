import bd
from pymongo import ReturnDocument
from whatsapp import WhatsApp
from requests import exceptions
import time
import re

mongo = bd.Conexao()

def verificar_novos_pedidos():
    total = 0
    
    while True:
        pedido = mongo.select_tb("pedidos").find_one_and_update(
            {"status": "Pendente WhatsApps"},
            {"$set": {"status": "WhatsApp Enviando"}},
            sort=[("_id", 1)],
            return_document=ReturnDocument.AFTER,
        )
        
        if pedido is None:
            break
        
        nlimpo = re.sub(r"\D", "", pedido.get("contato") or "")
        itens = "\n".join(pedido['descricao'])
        
        montar_mensagem = (
            f"Olá, {pedido['nome']}!\n"
            f"Recebemos o seu pedido:\n\n"
            f"{itens}\n\n"
            f"Mercado da ju Agradece!"
        )
        
        try:
            res = WhatsApp.enviar_mensagem(nlimpo, montar_mensagem)
            dados = res.json()
        except exceptions.RequestException as e:
            print(f"Falha no pedido {pedido['nome']}: {e}")
            
            mongo.select_tb("pedidos").update_one({"_id": pedido['_id']}, {"$set": {"status": "Pendente WhatsApps"}})
            break

        mongo.select_tb("pedidos").update_one({"_id": pedido['_id']},{"$set": {"status": "WhatsApp Enviado"}})
        print(f"Pedido de {pedido['nome']} enviado!")
        
        total +=1
    if total == 0:
        print("Nenhum pedido novo...")


verificar_novos_pedidos()