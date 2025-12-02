# chamando a classe ClientesDAO
from src.app.BD.clientes_dao import Clientes_dao
from src.config.database import connection_pool
from flask import render_template, redirect, request, flash

class ClientesControllers:
    def lista_arvore(self):
        def view():
            cliente_dao = Clientes_dao(connection_pool)
            erro, resultados = cliente_dao.select_na_tabela_clientes()
            return render_template('listagemArvores.html', arvores=resultados)
        return view

    def exibe_form_inclusao_arvore(self):
        def view():
            return render_template('inclusaoArvores.html')
        return view

    def insere_nova_arvore(self):
        def view():
            cliente_dao = Clientes_dao(connection_pool)
            erro = cliente_dao.inclui_clientes(request.form)
            if erro:
                # Exibe mensagem de erro amigável sem redirecionar
                flash(erro, 'danger')
                # Retorna o template de inclusão novamente com os dados do formulário
                return render_template('inclusaoArvores.html')
            # Sucesso: redireciona para listagem com mensagem de sucesso
            flash('Árvore cadastrada com sucesso!', 'success')
            return redirect('/arvores')
        return view

    def select_arvores_por_status(self):
        def view():
            cliente_dao = Clientes_dao(connection_pool)
            status = request.args.get('status', 'todos')
            erro, resultados = cliente_dao.select_arvores_por_status(status)
            return render_template('consulta.html', arvores=resultados, status_selecionado=status)
        return view