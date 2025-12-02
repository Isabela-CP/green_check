# chamando a classe usuarios_controller
from src.app.controllers.usuarios_controllers import UsuariosControllers
from src.app.controllers.clientes_controllers import ClientesControllers
from src.app.controllers.auth import login_required
from flask import render_template, session, redirect, request


usuario_cont = UsuariosControllers()
cliente_cont = ClientesControllers()

def rotas(aplicacao):
    # Evitar problema com o CORS
    @aplicacao.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Origin'] = "http://localhost"
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    @aplicacao.route('/')
    def index():
        print('Acessou a pagina de ACESSO a aplicacao...')
        return render_template('login.html')

    @aplicacao.route('/arvores')
    @login_required
    def arvores():
        return cliente_cont.lista_arvore()()

    @aplicacao.route('/inclusaoArvores')
    @login_required
    def inclusao_arvores():
        return cliente_cont.exibe_form_inclusao_arvore()()
    
    @aplicacao.route('/consulta')
    @login_required
    def consulta():
        return cliente_cont.select_arvores_por_status()()

    @aplicacao.route('/validaBDUsuarios', methods=['POST'])
    def valida_bd_usuarios():
        return usuario_cont.valida_acesso_usuario()()

    @aplicacao.route('/insertBDArvores', methods=['POST'])
    @login_required
    def insert_bd_arvores():
        return cliente_cont.insere_nova_arvore()()

    @aplicacao.route('/logout')
    def logout():
        """Faz logout do usuário, limpando sessão e cookie"""
        session.clear()
        response = redirect("/")
        # Remove o cookie de autenticação
        response.set_cookie('auth_token', '', expires=0)
        return response
