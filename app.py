from flask import Flask, request, render_template, jsonify, abort, session, redirect, url_for
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime 
from config import Config
from whatsapp import WhatsApp
import requests
import re
import os
import bd
import hash

app = Flask(__name__)
#conexao do banco
conn = bd.Conexao()

#so serve quando vai usar gunicorn aqui no localhost não faz diferença nenhuma.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

#vamos iniciar uma sessão e trabalhar com ela para a parte administrativa.
Config.validacao()

app.secret_key=Config.SECRET_KEY

#Função para tratar mensagem de retorno ao usuário.
def tratativa_front(mensagem, status):
    return jsonify({"mensagem": mensagem, "status": status})

# Rotas Estaticas Site
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/produtos")
def produtos():
    #Exibindo os produtos para o usuário
    dep = {      
            "Mercearia": "Mercearia",
            "Produtos de Limpeza": "Produtos de Limpeza",
            "Higiene Pessoal": "Higiene Pessoal",
            "Biscoitos": "Biscoitos",
            "Chocolates": "Chocolates",
            "Bebidas": "Bebidas",
        }

    produtos = list(conn.select_tb("produtos").find({}).sort({"codProduto": 1}))

    return render_template("produtos.html", produtos=produtos, departamentos=dep)

@app.route("/carrinho")
def carrinho():
    return render_template("carrinho.html")

#Rotas Estaticas ADM
@app.route("/admin/login")
def login():
    return render_template("login.html")

@app.route("/admin/painel-produtos")
def painel():
    if "LOGADO" not in session:
        return redirect(url_for('login'))

    #Aqui será passada os dados do banco para criar a tabela
    produtos = list(conn.select_tb("produtos").find({}).sort({"codProduto": 1}))

    return render_template("painel_produtos.html", produtos=produtos)

@app.route("/admin/pedidos")
def pedidos():
    if "LOGADO" not in session:
        return redirect(url_for('login'))
    
    # buscando os dados e ordenando pelo mais recente ao mais antigo .sort("_id", -1)
    pedidos = list(conn.select_tb("pedidos").find({}, {"_id": 0}).sort("_id", -1)) 
    
    return render_template("painel_pedidos.html", pedidos=pedidos)

@app.route("/admin/WhatsApp")
def whatsapp():
    return render_template("whatsapp.html")

#Rota statica e Operacional - Reaproveitada para realizar edição dos itens
@app.route("/admin/novo-produto", methods=["GET", "POST"])
@app.route("/admin/novo-produto/<id>", methods=["GET", "POST"])
def novo_produto(id=None):
    if "LOGADO" not in session:
        return redirect(url_for('login'))
    #Por enquanto é só aqui que existe os departamentos porém depois eu vou passar ao banco de dados.
    dep = {      
        "Mercearia": "Mercearia",
        "Produtos de Limpeza": "Produtos de Limpeza",
        "Higiene Pessoal": "Higiene Pessoal",
        "Biscoitos": "Biscoitos",
        "Chocolates": "Chocolates",
        "Bebidas": "Bebidas",
    }

    produto = None

    #Verifica se recebeu um id na rota, caso não tenha id é um cadastrados
    if not id:
        return render_template("painel_novo_produto.html", departamento=dep)

    #Caso tenha id será convertido para ObjectId para conseguir interpretar no find no mongo
    try:
        oid = ObjectId(id)
    
    #Caso tenha erro no id (Pode ser possivelmente alguém tentado), será direcionado direto para pagina 404.
    except InvalidId:
        abort(404)

    #Tetando localizar o item pelo id
    produto = conn.select_tb("produtos").find_one({"_id": oid})

    #Verificando se o produto foi encontrado.
    if not produto:
        abort(404)

    #Se existe id e foi encontrado agora vamos direcionar ele a pagina /admin/novo-produto/produto
    return render_template("painel_novo_produto.html", produto=produto, departamento=dep)
    

#Rotas Operacionais
@app.route("/validar/login", methods=['POST'])
def validar_login():
    dados = request.get_json(silent=True) or {}

    #transformando em uma dicionario 
    login_dados = {
        'usuario': dados.get("usuario"),
        'senha': dados.get("senha")
    }
    
    #selecionando a tabela usuarios -> lembrando que em Mongo é Collection
    usuarios = conn.select_tb("usuarios")

    if not isinstance(login_dados["usuario"], str) or not isinstance(login_dados["senha"], str):
        return jsonify({'mensagem': 'Erro! dados invalidos'}), 400
    else:

        #buscando o usuario na tabela
        db_usuarios = usuarios.find_one({"usuario": login_dados["usuario"]})

        if not db_usuarios:
            return jsonify({'mensagem': 'Verificar usuário e/ou  senha!'}), 401

        # Validando via hash salvo no banco e checando com a função.
        # Não existe mais texto puro no banco para senha
        
        resultado = hash.Seguraca.verificar_senha(db_usuarios['senha'], login_dados['senha'])
        # print(resultado)
        
        if not resultado['status']:
            return jsonify({'mensagem': 'Verificar usuário e/ou  senha!'}), 401

        session["LOGADO"] = True
        return jsonify({'mensagem': 'Autorizado'}), 201

        # validação fraca para teste
        # if db_usuarios and db_usuarios["senha"] == login_dados["senha"]:
        #     return jsonify({'mensagem': 'Autorizado'}), 200
        
        # return jsonify({'mensagem': 'Não Autorizado'}), 401

@app.route("/inserir/novo-produto", methods=['POST'])
def inserir_produto():
    # Aqui só recebe os dados menos input="file"
    req = request.form
    # Aqui só recebe arquivos do input="file"
    req_arq = request.files.get("img-produto")
    #transforma tudo em dicionario python
    dados = req.to_dict()

    #Validação dos campos, 1 por 1 e 
    for k in req:
        v = req.get(k, "").strip()
        if not v:
            return jsonify({"mensagem": "Verificar campos vazio(s)", "status": "erro"}), 400

    if not req_arq:
        return jsonify({"mensagem": "Imagem não selecionada!", "status": "erro"}), 400
    
    #atualizando o campo codigo do produto para int
    dados["codProduto"] = int(dados["codProduto"])

    #atualiza o preço para float antes de inserir no banco
    try:
        dados["preco"] = float(dados["preco"].replace(",", "."))
    except ValueError:
        return jsonify({"mensagem": "Campo preço não é aceito [Letras, simbolos] Preenchimento Correto: 10,50 ou 1001,99", "status": "erro"}), 400

    #Criando o caminho e verificando se a pasta existe e se não existir cria pra evitar erros
    upload_img = os.path.join(app.root_path, "static", "img_prod")
    os.makedirs(upload_img, exist_ok=True)

    #atualizar dados para inserir o caminho da imagem.

    #Aqui estamos pegando a extensão do arquivo que foi selecionado no input
    ext = os.path.splitext(req_arq.filename)[1].lower()

    # Garantindo que nenhum arquivo diferente de imagem seja armazenado.
    ext_permitda = {".png", ".jpg", ".jpeg"}
    if ext not in ext_permitda:
        return jsonify({"mensagem": "Imagem inserida invalida! inserir arquivo como [.png, .jpg, .jpeg]", "status": "erro"}), 400
    
    #Aqui estamos criando o nome que será salvo, associado ao item, então nome do item + extensão
    nome_img = f"{secure_filename(dados['item'])}{ext}"
    #dados agora tem o caminho da imagem para usar na pagina de produtos posteriormente.
    dados["imagem"] = nome_img

    caminho = os.path.join(upload_img, nome_img)
    req_arq.save(caminho)
    
    col = conn.select_tb("produtos")

    try:
        response = conn.insert_db(col, dados)
    
    except DuplicateKeyError:
        return jsonify({"mensagem": "Código do produto duplicado!", "status": "erro"}), 409
    except PyMongoError:
        return jsonify({"mensagem": "Erro ao acessar o banco!"}), 500
    
    if not response.acknowledged:
        return jsonify({"mensagem": "Produto não cadastrado!", "status": "erro"}), 500

    return jsonify({"mensagem": "Produto cadastrado com sucesso", "status": "sucesso"}), 201

@app.route("/alterar/produto/<id>", methods=['UPDATE'])
def alterar_produto(id):
    dados = request.form
    arquivo = request.files.get("img-produto")    

    dados = dados.to_dict()

    # Transformando o id em ObjectId
    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"mensagem": "ID do produto inválido", "status": "erro"}), 400

    # Verificando se existe arquivo para realizar atualizar junto com os dados.
    if arquivo and arquivo.filename != '': 
        #Aqui estamos pegando a extensão do arquivo que foi selecionado no input
        ext = os.path.splitext(arquivo.filename)[1].lower()
        
        # Garantindo que nenhum arquivo diferente de imagem seja armazenado.
        ext_permitda = {".png", ".jpg", ".jpeg"}
        if ext not in ext_permitda:
            return jsonify({"mensagem": "Imagem inserida invalida! inserir arquivo como [.png, .jpg, .jpeg]", "status": "erro"}), 400

        nome_img = f"{secure_filename(dados['item'])}{ext}"

        # Atualizando dados para enviar ao banco caso tenha alteração de imagem.
        dados['imagem'] = nome_img
        # Criando o caminho
        upload_img = os.path.join(app.root_path, "static", "img_prod")
        caminho = os.path.join(upload_img, nome_img)

        #Consulta no banco para pegar o nome da imagem anterior
        col_produtos = conn.select_tb("produtos").find_one({"_id": oid})

        #verificando se a imagem nova tem o mesmo nome da anterior
        if col_produtos['imagem'] != nome_img:
            #se for diferente vai gerar o caminho até a imagem antiga
            del_img = os.path.join(upload_img, col_produtos['imagem'])
            #verificando se o arquivo existe para remover 
            if os.path.exists(del_img):
                os.remove(del_img)
        
        #Caso o arquivo não tenha o nome diferente ele vem direto para o save e o arquivo é sobreescrito.
        #Casi o arquivo anterior tenha nome diferente ele já foi deletado e será criado o novo arquivo com novo nome.
        arquivo.save(caminho)

    #alterando o codigo para numero.
    dados['codProduto'] = int(dados['codProduto'])

    try:
        dados["preco"] = float(dados["preco"].replace(",", "-").replace(".", ",").replace("-", "."))
    except ValueError:
        return jsonify({"mensagem": "Campo preço não é aceito [Letras, simbolos] Preenchimento Correto: 10,50 ou 1001,99", "status": "erro"}), 400
    
    col_update = conn.select_tb("produtos").update_one({"_id": oid}, {"$set": dados})

    if col_update.matched_count == 0:
        return jsonify({"mensagem": "Produto não encontrando", "status": "erro"}), 404
    
    if col_update.modified_count == 0:
        return jsonify({"mensagem": "Nenhuma alteração realizadas, as informações são iguais!", "status": "erro"})
    
    
    return jsonify({"mensagem": "Produto atualizado!", "status": "sucesso"}), 201

@app.route("/deletar/produto/<id>", methods=['DELETE'])
def deletar_produto(id):

    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"mensagem": "ID do produto inválido", "status": "erro"}), 400

    #Buscando o caminho do arquivo para deltar na pasta evitando assim que o disco cresca em volume de imagem sem produto.
    col_deletar = conn.select_tb("produtos").find_one({"_id": oid})

    del_img = col_deletar['imagem']
    
    #criando o caminho para remover o arquivo. 
    caminho = os.path.join(app.root_path, "static", "img_prod")
    caminho_img = os.path.join(caminho, del_img)

    #se existe a imagem deleta
    if os.path.exists(caminho_img):
        os.remove(caminho_img)

    col_deletar = conn.select_tb("produtos").delete_one({"_id": oid})

    if col_deletar.deleted_count == 0:
        return jsonify({"mensagem": "Produto não encontrado", "status": "erro"}), 404

    return jsonify(ok=True), 200
        
@app.route("/inserir/pedido", methods=['POST'])
def inserir_pedidos():
    req = request.get_json()
    produtos = conn.select_tb("produtos")
    
    total = 0;
    frete = 25;
    itens = []
    
    for k in req:
        try:
            v = req.get(k, "").strip()
        except:
            pass
        
        if not v:
            return jsonify({"mensagem": "Verificar campos vazio(s)", "status": "erro"}), 400

    for item in req['itens']:
        
        resultado = produtos.find_one({"_id": ObjectId(item['id'])})

        if not resultado:
            return jsonify({"mensagem": "Produto" + resultado['item'] +" não encontrado!, Remova para continuar"}), 404

        itens.append(resultado['item'])

        total += float(resultado["preco"]) * float(item["qtd"])

    if total > 250:        
        frete = 0

    total += frete

    # Formatando para criar o pedido e enviar ao banco.
    lista_pedido = {
        "nome": req['nome'].lower(),
        "endereco": req['endereco'].lower(),
        "descricao": itens,
        "data": datetime.now(),
        "valor_compra": total,
        "tipo_pagamento": req['tipo_pag'],
        "contato": req['celular'],
        "status": "Pendente WhatsApps",
    }

    col = conn.select_tb("pedidos")

    pedido = conn.insert_db(col, lista_pedido)

    if not pedido.acknowledged: 
        return jsonify({"mensagem": "Pedido não enviado!", "status": "erro"}), 500

    return jsonify({"mensagem": "Pedido finalizado!", "status": "sucesso"}), 201

@app.route("/API/verificar/conexao")
def verificar_conexao():
    try:
        res = WhatsApp.verificar_conexao()
    except requests.exceptions.Timeout:
        return tratativa_front("API demorou para responder !", "erro"), 504
    except requests.exceptions.ConnectionError:
        return tratativa_front("Não foi possivel se conectar a API", "erro"), 502
    except requests.exceptions.HTTPError:
        return tratativa_front("erro na API", "erro"), 502
        
    if res == "notAuthorized":
        return jsonify({"mensagem": "WhatsApp deslogado!", "status": "erro"}), 409
    
    if res != "authorized":
        return jsonify({"mensagem": "Entrar em contato com administrador do sistema", "status": "erro"}), 503
    
    return jsonify({"mensagem": "WhatsApp Logado!", "status": "sucesso"}), 200

@app.route("/API/conectar/qr")
def gerar_qr():
    try:
        res = WhatsApp.qrcode()
    except requests.exceptions.Timeout:
            return tratativa_front("API demorou para responder !", "erro"), 504
    except requests.exceptions.ConnectionError:
        return tratativa_front("Não foi possivel se conectar a API", "erro"), 502
    except requests.exceptions.HTTPError:
        return tratativa_front("erro na API", "erro"), 502
    
    if res["type"] == "qrCode": 
        return jsonify({"mensagem": res["message"], "status": "sucesso"})
    
    return jsonify({"mensagem": "Qrcode só pode ser gerado quando esta deslogado!", "status": "erro"})

@app.route("/API/reconectar")
def reconectar():
    try:
        res = WhatsApp.reconectar()
    except requests.exceptions.Timeout:
        return tratativa_front("API demorou para responder !", "erro"), 504
    except requests.exceptions.ConnectionError:
        return tratativa_front("Não foi possivel se conectar a API", "erro"), 502
    except requests.exceptions.HTTPError:
        return tratativa_front("erro na API", "erro"), 502
    
    if res["isReboot"] == True:
        return jsonify({"mensagem": "WhatsApp Reconectado!", "status": "sucesso"}), 200
    
    return jsonify({"mensagem": "Não foi possivel reconectar!", "status": "erro"}), 200

@app.route("/API/desconectar")
def desconectar():
    res = WhatsApp.desconectar()
    
    if res["isLogout"] == True:
        return jsonify({"mensagem": "WhatsApp Desconectado!", "status": "sucesso"}), 200
    
    return jsonify({"mensagem": "Não foi possivel Desconectar!", "status": "erro"}), 200

# Rotas Operacionais Sites
@app.route("/filtro/departamentos", methods=['POST'])
def filtro_departamento():
    buscadb = {}
    req = request.get_json()
    dep = {      
            "Mercearia": "Mercearia",
            "Produtos de Limpeza": "Produtos de Limpeza",
            "Higiene Pessoal": "Higiene Pessoal",
            "Biscoitos": "Biscoitos",
            "Chocolates": "Chocolates",
            "Bebidas": "Bebidas",
        }
    departamento = (req.get("filtro") or "").strip()
    busca = (req.get("busca") or "").strip()
    
    if departamento:
        buscadb["departamento"] = departamento
    
    if busca:
        buscadb["item"] = {"$regex": re.escape(busca), "$options": "i"}

    departamento = req['filtro']

    try:
        filtro_dep = list(conn.select_tb("produtos").find(buscadb).sort({"codProduto": 1}))
    except PyMongoError:
        return jsonify({"mensagem": "Não foi possivel acessar o banco!", "status": "erro"}), 500
    
    return render_template("produtos.html", produtos=filtro_dep, departamentos=dep), 200


#Rota que não ajuda não quebrar o front.
@app.errorhandler(Exception)
def erro_geral(e):
    app.logger.exception("Erro não trtado")
    return jsonify({"mensagem": "Erro interno do sistema.", "status": "erro"}), 500
    
#Rota personalizada de pagina não encontrada.
@app.errorhandler(404)
def pg_nao_encontrada(error):
    return render_template("pagina_404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)