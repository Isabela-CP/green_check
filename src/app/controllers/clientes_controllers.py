# chamando a classe ClientesDAO
from src.app.BD.clientes_dao import Clientes_dao
from src.config.database import connection_pool
from flask import render_template, redirect, request

class ClientesControllers:
    def lista_cliente(self):
        def view():
            cliente_dao = Clientes_dao(connection_pool)
            erro, resultados = cliente_dao.select_na_tabela_clientes()
            return render_template('listagemClientes.html', clientes=resultados)
        return view

    def exibe_form_inclusao_cliente(self):
        def view():
            return render_template('inclusaoClientes.html')
        return view

    def insere_novo_cliente(self):
        def view():
            cliente_dao = Clientes_dao(connection_pool)
            erro = cliente_dao.inclui_clientes(request.form)
            if erro:
                print(erro)
            return redirect('/clientes')
        return view

    def exclui_cliente(self):
        def view(id):
            cliente_dao = Clientes_dao(connection_pool)
            erro = cliente_dao.exclui_clientes(id)
            if erro:
                print(erro)
            return redirect('/clientes')
        return view

    def lista_dados_cliente(self):
        def view(id):
            cliente_dao = Clientes_dao(connection_pool)
            erro, resultados_clientes = cliente_dao.consulta_cliente_por_id(id)
            if resultados_clientes:
                return render_template('atualizaClientes.html', clientes=resultados_clientes[0])
            else:
                return redirect('/clientes')
        return view
    def select_arvores_por_status(self):
        def view():
            cliente_dao = Clientes_dao(connection_pool)
            status = request.args.get('status', 'todos')
            erro, resultados = cliente_dao.select_arvores_por_status(status)
            return render_template('consulta.html', clientes=resultados, status_selecionado=status)
        return view