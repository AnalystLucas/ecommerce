from werkzeug.security import generate_password_hash, check_password_hash

class Seguraca:

    @staticmethod
    def gerar_hash(gerar_hash: str = '') -> dict:
        senha = gerar_hash

        if not senha or not senha.strip():
            return {'mensagem': 'Campo vazio, por favor informar uma senha !', 'status': False}

        return {
            'mensagem': 'Hash gerado com sucesso',
            'status': True,
            'hash': generate_password_hash(senha),
        }
    
    @staticmethod
    def verificar_senha(senha_hash: str, senha: str) -> dict:
        # Verificando se recebeu os campos para validar
        # Normalmente o hash vai vir do banco e a senha digitado pelo usuário
        if not senha_hash or not senha:
            return {'mensagem': 'Hash e senha são obrigatórios', 'status': False}
        if check_password_hash(senha_hash, senha):
            return {'mensagem': 'Senha confere', 'status': True}
        #Caso não deu certo a senha retorna erro
        return {'mensagem': 'Senha incorreta', 'status': False}
       
# Testando a segurança
# gerador = Seguraca()

# senha = gerador.gerar_hash('mercadodaju')

# print(senha['hash'])

# print(gerador.verificar_senha(senha['hash'], "teste"))
# print(gerador.verificar_senha(senha['hash'], "senha"))