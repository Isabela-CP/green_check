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

    @aplicacao.route('/clientes')
    @login_required
    def clientes():
        return cliente_cont.lista_cliente()()

    @aplicacao.route('/inclusaoClientes')
    @login_required
    def inclusao_clientes():
        return cliente_cont.exibe_form_inclusao_cliente()()

    @aplicacao.route('/listaDadosClientes/<int:id>')
    @login_required
    def lista_dados_clientes(id):
        return cliente_cont.lista_dados_cliente()(id)
    
    @aplicacao.route('/consulta')
    @login_required
    def consulta():
        return cliente_cont.select_arvores_por_status()()

    @aplicacao.route('/removeCliente/<int:id>')
    @login_required
    def remove_cliente(id):
        return cliente_cont.exclui_cliente()(id)

    @aplicacao.route('/validaBDUsuarios', methods=['POST'])
    def valida_bd_usuarios():
        return usuario_cont.valida_acesso_usuario()()

    @aplicacao.route('/insertBDClientes', methods=['POST'])
    @login_required
    def insert_bd_clientes():
        return cliente_cont.insere_novo_cliente()()

    @aplicacao.route('/logout')
    def logout():
        session.pop("usuario_logado", None)
        return redirect("/")
