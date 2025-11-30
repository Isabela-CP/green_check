import psycopg2
from psycopg2 import pool
import os
import time

# Configuração de conexão com PostgreSQL
# Usa variáveis de ambiente ou valores padrão
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),  # 'db' é o nome do serviço no docker-compose
    'port': int(os.getenv('DB_PORT', '5432')),  # Porta interna do container
    'user': os.getenv('DB_USER', 'arvore_user'),
    'password': os.getenv('DB_PASSWORD', 'arvore_pass'),
    'database': os.getenv('DB_NAME', 'arvore_urbana')
}

# Criar pool de conexões com retry
connection_pool = None
max_retries = 30
retry_delay = 2

for attempt in range(max_retries):
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        
        if connection_pool:
            print('Conexão com PostgreSQL realizada com SUCESSO!')
            break
        else:
            print('Erro ao criar pool de conexões')
    except (Exception, psycopg2.Error) as error:
        if attempt < max_retries - 1:
            print(f'Tentativa {attempt + 1}/{max_retries}: Aguardando PostgreSQL... ({error})')
            time.sleep(retry_delay)
        else:
            print(f'Erro na conexão com PostgreSQL após {max_retries} tentativas: {error}')
            raise

def get_connection():
    """Retorna uma conexão do pool"""
    return connection_pool.getconn()

def return_connection(connection):
    """Retorna uma conexão para o pool"""
    connection_pool.putconn(connection)

