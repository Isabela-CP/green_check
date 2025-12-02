"""
Script de verificação de senhas no banco de dados
Verifica se todas as senhas estão com hash bcrypt (não em texto plano)
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.config.database import connection_pool

def verificar_senhas():
    """
    Verifica se todas as senhas no banco de dados estão com hash bcrypt
    """
    conn = None
    
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # Busca todos os usuários
        cursor.execute("SELECT cpf, email, senha FROM usuario")
        usuarios = cursor.fetchall()
        
        print(f"Verificando {len(usuarios)} usuários...")
        print()
        
        senhas_ok = 0
        senhas_problema = []
        
        for cpf, email, senha_atual in usuarios:
            # Verifica se a senha está em hash (bcrypt começa com $2b$ ou $2a$)
            if senha_atual.startswith('$2b$') or senha_atual.startswith('$2a$'):
                senhas_ok += 1
                print(f"✓ Usuário {email}: senha com hash válido")
            else:
                senhas_problema.append((email, senha_atual))
                print(f"✗ Usuário {email}: senha NÃO está com hash (possível texto plano)")
        
        cursor.close()
        
        print()
        print("=" * 60)
        print(f"Total de usuários verificados: {len(usuarios)}")
        print(f"Senhas com hash válido: {senhas_ok}")
        print(f"Senhas com problema: {len(senhas_problema)}")
        print("=" * 60)
        
        if senhas_problema:
            print("\n⚠️  ATENÇÃO: Encontradas senhas que não estão com hash!")
            print("Todas as senhas devem estar com hash bcrypt.")
            print("\nPara corrigir, use o script generate_password_hash.py para gerar")
            print("os hashes e atualize manualmente no banco de dados.")
            return False
        else:
            print("\n✅ Todas as senhas estão com hash válido!")
            return True
        
    except Exception as erro:
        print(f"Erro na verificação: {erro}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)

if __name__ == '__main__':
    print("=" * 60)
    print("VERIFICAÇÃO DE SENHAS NO BANCO DE DADOS")
    print("=" * 60)
    print()
    verificar_senhas()

