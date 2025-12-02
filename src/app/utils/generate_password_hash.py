"""
Script para gerar hash de senhas usando bcrypt
Use este script para gerar hashes que podem ser inseridos diretamente no banco de dados
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import bcrypt

def generate_hash(password: str) -> str:
    """
    Gera hash bcrypt da senha
    
    Args:
        password: Senha em texto plano
        
    Returns:
        String com o hash da senha
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def main():
    """Função principal para gerar hashes interativamente"""
    print("=" * 60)
    print("GERADOR DE HASH DE SENHAS - Green Check")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        # Modo não-interativo: recebe senha como argumento
        senha = sys.argv[1]
        hash_senha = generate_hash(senha)
        print(f"Senha: {senha}")
        print(f"Hash:  {hash_senha}")
        print()
        print("SQL para usar no INSERT:")
        print(f"'{hash_senha}'")
    else:
        # Modo interativo
        print("Digite as senhas que deseja converter para hash.")
        print("Pressione Ctrl+C para sair.")
        print()
        
        while True:
            try:
                senha = input("Digite a senha (ou 'sair' para terminar): ").strip()
                
                if senha.lower() in ['sair', 'exit', 'quit']:
                    break
                
                if not senha:
                    print("Senha não pode estar vazia!")
                    continue
                
                hash_senha = generate_hash(senha)
                
                print()
                print("-" * 60)
                print(f"Senha original: {senha}")
                print(f"Hash gerado:   {hash_senha}")
                print()
                print("SQL para usar no INSERT:")
                print(f"'{hash_senha}'")
                print("-" * 60)
                print()
                
            except KeyboardInterrupt:
                print("\n\nEncerrando...")
                break
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == '__main__':
    main()

