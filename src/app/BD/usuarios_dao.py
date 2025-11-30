class Usuarios_dao:
    def __init__(self, db_pool):
        self._db_pool = db_pool

    def select_na_tabela_usuarios(self, login, senha):
        sql_cons_usuarios = """
            SELECT *
            FROM usuario
            WHERE "email" = %s
              AND "senha" = %s
        """
        values = (login, senha)

        print("SELECT MONTADO =", sql_cons_usuarios, values)

        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql_cons_usuarios, values)
            resultado = cursor.fetchall()
            cursor.close()

            if len(resultado) > 0:
                dados = len(resultado)
                return dados
            else:
                raise Exception("USUÁRIO NÃO EXISTE NO BD")
        except Exception as erro:
            print(f"Erro ao consultar usuários: {erro}")
            raise erro
        finally:
            if conn:
                self._db_pool.putconn(conn)
