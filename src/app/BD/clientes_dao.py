class Clientes_dao:
    def __init__(self, db_pool):
        self._db_pool = db_pool

    # LISTAR TODAS AS ÁRVORES (para /clientes)
    def select_na_tabela_clientes(self):
        sql = """
            SELECT
                "id",
                "latitude",
                "longitude",
                "status",
                "tipo",
                "altura",
                "dap",
                "ultima_vistoria",
                "nome_cientifico"
            FROM arvore
            ORDER BY "id"
        """

        print("SELECT ARVORE =", sql)

        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql)
            resultados = cursor.fetchall()

            # Converter para lista de dicionários
            colunas = [desc[0] for desc in cursor.description]
            arvore = [dict(zip(colunas, row)) for row in resultados]

            cursor.close()
            return None, arvore
        except Exception as erro:
            print(f"Erro no select_na_tabela_clientes (arvores): {erro}")
            return erro, []
        finally:
            if conn:
                self._db_pool.putconn(conn)

    # INSERIR NOVA ÁRVORE
    def inclui_clientes(self, dados):
        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()

            latitude = dados.get("latitude")
            longitude = dados.get("longitude")
            codigo_tag = dados.get("codigo_tag")  # pode vir None

            # 1) BUSCAR REGISTROS EXISTENTES
            cursor.execute(
                """
                SELECT contador, status 
                FROM tag
                JOIN arvore USING(latitude, longitude, contador)
                WHERE latitude = %s AND longitude = %s
                ORDER BY contador ASC
            """,
                (latitude, longitude),
            )

            registros = cursor.fetchall()

            # 2) DEFINIÇÃO DO CONTADOR

            # Caso não exista nenhuma árvore neste ponto
            if not registros:
                contador = 1

            else:
                # Verifica se TODAS estão REMOVIDA
                todas_removidas = all(r[1] == "REMOVIDA" for r in registros)

                if todas_removidas:
                    # usa o último contador + 1
                    maior_contador = registros[-1][0]
                    contador = maior_contador + 1
                else:
                    # existe árvore ativa → contador volta para 1
                    contador = 1

            # 3) INSERIR ÁRVORE
            sql_arvore = """
                INSERT INTO arvore
                    (latitude, longitude, contador, nome_cientifico, ultima_vistoria, status, tipo, altura, dap)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                sql_arvore,
                (
                    latitude,
                    longitude,
                    contador,
                    dados.get("nome_cientifico"),
                    dados.get("data_ultima_vistoria") or None,
                    dados.get("status"),
                    dados.get("tipo"),
                    dados.get("altura_m") or None,
                    dados.get("dap_cm") or None,
                ),
            )

            # 4) INSERIR TAG (SE TIVER)
            if dados.get("tem_tag") and codigo_tag:
                sql_tag = """
                    INSERT INTO tag (codigo_nfc, latitude, longitude, contador)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_tag, (codigo_tag, latitude, longitude, contador))

            # FINALIZA
            conn.commit()
            cursor.close()
            return None

        except Exception as erro:
            if conn:
                conn.rollback()
            print(f"Erro ao inserir árvore: {erro}")
            return erro

        finally:
            if conn:
                self._db_pool.putconn(conn)

    # EXCLUIR ÁRVORE
    def exclui_clientes(self, id_arvore):
        sql = """
            DELETE FROM arvore
            WHERE "id" = %s
        """
        values = (id_arvore,)

        print("DELETE ARVORE =", sql, values)

        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            return None
        except Exception as erro:
            if conn:
                conn.rollback()
            print(f"Erro ao excluir árvore: {erro}")
            return erro
        finally:
            if conn:
                self._db_pool.putconn(conn)

    # CONSULTAR ÁRVORE POR ID
    def consulta_cliente_por_id(self, id_arvore):
        sql = """
            SELECT
                "id",
                "latitude",
                "longitude",
                "status",
                "tipo",
                "altura",
                "dap",
                "ultima_vistoria",
                "nome_cientifico"
            FROM arvore
            WHERE "id" = %s
        """
        values = (id_arvore,)

        print("SELECT ARVORE POR ID =", sql, values)

        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql, values)
            resultado = cursor.fetchone()

            if resultado:
                colunas = [desc[0] for desc in cursor.description]
                arvore = dict(zip(colunas, resultado))
                cursor.close()
                return None, [arvore]
            else:
                cursor.close()
                return None, []
        except Exception as erro:
            print(f"Erro em consulta_cliente_por_id (arvore): {erro}")
            return erro, []
        finally:
            if conn:
                self._db_pool.putconn(conn)

    def select_arvores_por_status(self, status):
        sql = """
            SELECT
                "id",
                "latitude",
                "longitude",
                "status",
                "tipo",
                "altura",
                "dap",
                "ultima_vistoria",
                "nome_cientifico"
            FROM arvore
        """

        params = []

        # Se vier um status específico (e não "todos"), filtra
        if status and status != "todos":
            sql += ' WHERE "status" = %s'
            params.append(status)

        sql += ' ORDER BY "id"'

        print("SELECT ARVORES POR STATUS =", sql, params)

        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params) if params else None)
            resultados = cursor.fetchall()

            colunas = [desc[0] for desc in cursor.description]
            arvores = [dict(zip(colunas, row)) for row in resultados]

            cursor.close()
            return None, arvores
        except Exception as erro:
            print(f"Erro em consulta_cliente_por_status (arvores): {erro}")
            return erro, []
        finally:
            if conn:
                self._db_pool.putconn(conn)
