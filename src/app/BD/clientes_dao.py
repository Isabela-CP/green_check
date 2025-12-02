class Clientes_dao:
    def __init__(self, db_pool):
        self._db_pool = db_pool

    # LISTAR TODAS AS ÁRVORES (para /arvores)
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

            # 1) BUSCAR REGISTROS EXISTENTES na mesma localização
            cursor.execute(
                """
                SELECT contador, status 
                FROM arvore
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

            # 3) INSERIR TAG (SE TIVER) - Deve ser inserida ANTES da árvore
            if dados.get("tem_tag") and codigo_tag:
                sql_tag = """
                    INSERT INTO tag (codigo_nfc)
                    VALUES (%s)
                    ON CONFLICT (codigo_nfc) DO NOTHING
                """
                cursor.execute(sql_tag, (codigo_tag,))

            # 4) INSERIR ÁRVORE
            sql_arvore = """
                INSERT INTO arvore
                    (codigo_nfc, latitude, longitude, contador, nome_cientifico, ultima_vistoria, status, tipo, altura, dap)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                sql_arvore,
                (
                    codigo_tag if dados.get("tem_tag") and codigo_tag else None,
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

            # FINALIZA
            conn.commit()
            cursor.close()
            return None

        except Exception as erro:
            if conn:
                conn.rollback()
            print(f"Erro ao inserir árvore: {erro}")
            
            # Tratar erros específicos e retornar mensagens amigáveis
            erro_str = str(erro)
            
            # Erro de chave duplicada (árvore já existe na mesma localização)
            if "duplicate key value violates unique constraint" in erro_str and "arvore_latitude_longitude_contador_key" in erro_str:
                return "Já existe uma árvore cadastrada nesta localização (latitude e longitude). Por favor, verifique as coordenadas ou aguarde a remoção da árvore existente."
            
            # Erro de foreign key (tag não existe)
            if "violates foreign key constraint" in erro_str and "tag" in erro_str:
                return "O código da TAG informado não existe no sistema. Por favor, verifique o código ou cadastre a TAG primeiro."
            
            # Erro genérico
            return f"Erro ao cadastrar árvore: {erro_str}"

        finally:
            if conn:
                self._db_pool.putconn(conn)

    # EXCLUIR ÁRVORE - DESABILITADO
    # A remoção de árvores foi desabilitada devido a conflitos de foreign key.
    # Árvores não podem ser removidas quando possuem vistorias associadas,
    # pois isso violaria a integridade referencial do banco de dados.
    # 
    # Se for necessário remover uma árvore, primeiro é preciso:
    # 1. Remover todas as vistorias associadas
    # 2. Remover todas as manutenções associadas
    # 3. Remover todas as solicitações associadas
    # 4. Então remover a árvore
    #
    # def exclui_clientes(self, id_arvore):
    #     sql = """
    #         DELETE FROM arvore
    #         WHERE "id" = %s
    #     """
    #     values = (id_arvore,)
    #
    #     print("DELETE ARVORE =", sql, values)
    #
    #     conn = None
    #     try:
    #         conn = self._db_pool.getconn()
    #         cursor = conn.cursor()
    #         cursor.execute(sql, values)
    #         conn.commit()
    #         cursor.close()
    #         return None
    #     except Exception as erro:
    #         if conn:
    #             conn.rollback()
    #         print(f"Erro ao excluir árvore: {erro}")
    #         return erro
    #     finally:
    #         if conn:
    #             self._db_pool.putconn(conn)

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

    # INSERIR NOVA ESPÉCIE
    def inclui_especie(self, dados):
        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()

            nome_cientifico = dados.get("nome_cientifico")
            nome_popular = dados.get("nome_popular") or None
            nativa_str = dados.get("nativa")
            
            # Converter string para boolean
            nativa = nativa_str.lower() == "true" if nativa_str else None

            # Validar nome científico (obrigatório)
            if not nome_cientifico:
                return "Nome científico é obrigatório."

            # Validar nativa (obrigatório)
            if nativa is None:
                return "É necessário informar se a espécie é nativa ou exótica."

            # Inserir espécie
            sql_especie = """
                INSERT INTO especie (nome_cientifico, nome_popular, nativa)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                sql_especie,
                (nome_cientifico, nome_popular, nativa)
            )

            # Finalizar
            conn.commit()
            cursor.close()
            return None

        except Exception as erro:
            if conn:
                conn.rollback()
            print(f"Erro ao inserir espécie: {erro}")
            
            # Tratar erros específicos e retornar mensagens amigáveis
            erro_str = str(erro)
            
            # Erro de chave duplicada (espécie já existe)
            if "duplicate key value violates unique constraint" in erro_str or "violates unique constraint" in erro_str:
                return f"A espécie com nome científico '{nome_cientifico}' já está cadastrada no sistema."
            
            # Erro genérico
            return f"Erro ao cadastrar espécie: {erro_str}"

        finally:
            if conn:
                self._db_pool.putconn(conn)
