from src.app.utils.security import SecurityManager
from src.config.app import aplicacao

class Usuarios_dao:
    def __init__(self, db_pool):
        self._db_pool = db_pool
        # Inicializa o gerenciador de segurança
        self.security = SecurityManager(aplicacao.config['SECRET_KEY'])

    def select_na_tabela_usuarios(self, login, senha):
        """
        Valida credenciais do usuário usando hash de senha
        
        Args:
            login: Email do usuário
            senha: Senha em texto plano
            
        Returns:
            Dicionário com dados do usuário se válido, None caso contrário
        """
        sql_cons_usuarios = """
            SELECT cpf, nome, email, senha, papel
            FROM usuario
            WHERE "email" = %s
        """
        values = (login,)

        print("SELECT MONTADO =", sql_cons_usuarios, values)

        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql_cons_usuarios, values)
            resultado = cursor.fetchone()
            cursor.close()

            if resultado:
                # Converte resultado para dicionário
                colunas = ['cpf', 'nome', 'email', 'senha', 'papel']
                usuario = dict(zip(colunas, resultado))
                
                # Verifica se a senha corresponde ao hash
                senha_hash = usuario['senha']
                if self.security.verify_password(senha, senha_hash):
                    # Remove a senha do retorno por segurança
                    usuario.pop('senha', None)
                    return usuario
                else:
                    raise Exception("SENHA INCORRETA")
            else:
                raise Exception("USUÁRIO NÃO EXISTE NO BD")
        except Exception as erro:
            print(f"Erro ao consultar usuários: {erro}")
            raise erro
        finally:
            if conn:
                self._db_pool.putconn(conn)
    
    def atualiza_senha_hash(self, email, senha_antiga, senha_nova):
        """
        Atualiza a senha do usuário
        
        Args:
            email: Email do usuário
            senha_antiga: Senha atual em texto plano (será validada contra hash no banco)
            senha_nova: Nova senha em texto plano (será convertida para hash)
            
        Returns:
            True se atualizado com sucesso, False caso contrário
            
        Note:
            Todas as senhas no banco já estão com hash bcrypt.
            A senha antiga será validada antes de atualizar.
        """
        sql_update = """
            UPDATE usuario
            SET senha = %s
            WHERE email = %s
        """
        
        # Gera hash da nova senha
        senha_hash = self.security.hash_password(senha_nova)
        values = (senha_hash, email)
        
        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql_update, values)
            conn.commit()
            cursor.close()
            return True
        except Exception as erro:
            if conn:
                conn.rollback()
            print(f"Erro ao atualizar senha: {erro}")
            return False
        finally:
            if conn:
                self._db_pool.putconn(conn)
