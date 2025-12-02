# chamando a classe UsuariosDAO
from src.app.BD.usuarios_dao import Usuarios_dao
from src.app.utils.security import SecurityManager
from src.config.database import connection_pool
from src.config.app import aplicacao
from flask import redirect, request, session, make_response


class UsuariosControllers:
    def __init__(self):
        """Inicializa o controller com gerenciador de segurança"""
        self.security = SecurityManager(aplicacao.config['SECRET_KEY'])
    
    def valida_acesso_usuario(self):
        def view():
            usuario_dao = Usuarios_dao(connection_pool)
            try:
                login = request.form.get("login")
                senha = request.form.get("senha")
                
                # Valida credenciais (agora com hash)
                usuario = usuario_dao.select_na_tabela_usuarios(login, senha)

                if usuario:
                    print("USUÁRIO EXISTE!! Está VALIDADO!!")
                    
                    # Gera token seguro
                    token = self.security.generate_token(usuario['email'])
                    
                    # Armazena dados na sessão
                    session["usuario_logado"] = usuario['email']
                    session["usuario_cpf"] = usuario['cpf']
                    session["usuario_nome"] = usuario['nome']
                    session["usuario_papel"] = usuario['papel']
                    
                    # Cria resposta e define cookie com token
                    response = make_response(redirect("/arvores"))
                    response.set_cookie(
                        'auth_token',
                        token,
                        max_age=86400,  # 24 horas em segundos
                        httponly=True,  # Proteção contra XSS
                        secure=False,   # True em produção com HTTPS
                        samesite='Lax'  # Proteção contra CSRF
                    )
                    
                    return response

            except Exception as erro:
                print(f"ERRO NA AUTENTICAÇÃO: {erro}")
                return redirect("/")

        return view
