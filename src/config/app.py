import os
from flask import Flask
from flask_cors import CORS

# Obter o diretório base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Criando a aplicação Flask
aplicacao = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'src/app/views/templates'),
    static_folder=os.path.join(BASE_DIR, 'src/app/views'),
    static_url_path='/estatico'
)

# Configuração do CORS
CORS(aplicacao)

# Configuração para processar dados de formulários
aplicacao.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# Importar rotas - precisa ser feito depois de criar a aplicação
from src.app.rotas import rotas
rotas(aplicacao)

