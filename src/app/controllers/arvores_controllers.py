# chamando a classe ArvoresDAO
from src.app.BD.arvores_dao import Arvores_dao
from src.config.database import connection_pool
from flask import render_template, redirect, request, flash, jsonify

class ArvoresControllers:
    def lista_arvore(self):
        def view():
            arvore_dao = Arvores_dao(connection_pool)
            erro, resultados = arvore_dao.select_na_tabela_clientes()
            if erro:
                flash(str(erro), 'danger')
            return render_template('listagemArvores.html', arvores=resultados if not erro else [])
        return view

    def exibe_form_inclusao_arvore(self):
        def view():
            return render_template('inclusaoArvores.html')
        return view

    def insere_nova_arvore(self):
        def view():
            arvore_dao = Arvores_dao(connection_pool)
            erro = arvore_dao.inclui_clientes(request.form)
            if erro:
                # Exibe mensagem de erro amigável sem redirecionar
                flash(erro, 'danger')
                # Retorna o template de inclusão novamente com os dados do formulário preservados
                dados_form = {
                    'latitude': request.form.get('latitude', ''),
                    'longitude': request.form.get('longitude', ''),
                    'status': request.form.get('status', 'saudavel'),
                    'tipo': request.form.get('tipo', 'publico'),
                    'altura_m': request.form.get('altura_m', ''),
                    'dap_cm': request.form.get('dap_cm', ''),
                    'nome_cientifico': request.form.get('nome_cientifico', ''),
                    'tem_tag': request.form.get('tem_tag') == 'on',
                    'codigo_tag': request.form.get('codigo_tag', '')
                }
                return render_template('inclusaoArvores.html', dados_form=dados_form)
            # Sucesso: redireciona para listagem com mensagem de sucesso
            flash('Árvore cadastrada com sucesso!', 'success')
            return redirect('/arvores')
        return view

    def select_arvores_por_status(self):
        def view():
            arvore_dao = Arvores_dao(connection_pool)
            status = request.args.get('status', 'todos')
            erro, resultados = arvore_dao.select_arvores_por_status(status)
            if erro:
                flash(str(erro), 'danger')
            return render_template('consulta.html', arvores=resultados if not erro else [], status_selecionado=status)
        return view

    def exibe_form_inclusao_especie(self):
        def view():
            return render_template('inclusaoEspecies.html')
        return view

    def insere_nova_especie(self):
        def view():
            arvore_dao = Arvores_dao(connection_pool)
            erro = arvore_dao.inclui_especie(request.form)
            if erro:
                # Exibe mensagem de erro amigável sem redirecionar
                flash(erro, 'danger')
                # Retorna o template de inclusão novamente com os dados do formulário preservados
                dados_form = {
                    'nome_cientifico': request.form.get('nome_cientifico', ''),
                    'nome_popular': request.form.get('nome_popular', ''),
                    'nativa': request.form.get('nativa', '')
                }
                return render_template('inclusaoEspecies.html', dados_form=dados_form)
            # Sucesso: redireciona para listagem com mensagem de sucesso
            flash('Espécie cadastrada com sucesso!', 'success')
            return redirect('/inclusaoEspecies')
        return view

    def busca_especies(self):
        def view():
            arvore_dao = Arvores_dao(connection_pool)
            termo_busca = request.args.get('q', '').strip()
            erro, especies = arvore_dao.select_especies(termo_busca if termo_busca else None)
            if erro:
                # Retornar erro amigável em JSON
                return jsonify({'erro': str(erro)}), 500
            return jsonify(especies)
        return view