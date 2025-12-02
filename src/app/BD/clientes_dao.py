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
            # Retornar erro amigável para o usuário
            return "Não foi possível carregar a listagem de árvores. Por favor, tente novamente mais tarde. Se o problema persistir, entre em contato com o suporte.", []
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

            # Validar latitude
            try:
                lat_valor = float(latitude) if latitude else None
                if lat_valor is None:
                    return "Por favor, informe a latitude da árvore. A latitude é obrigatória para o cadastro."
                if lat_valor < -90 or lat_valor > 90:
                    return f"A latitude informada ({latitude}) está fora do intervalo permitido. Por favor, informe uma latitude entre -90 e 90 graus."
                
                # Validar que latitude tem no máximo 8 dígitos (contando todos os dígitos, não o ponto decimal nem o sinal negativo)
                # Remover ponto decimal, sinal negativo e espaços, mas manter todos os dígitos incluindo zeros
                lat_str = ''.join(c for c in str(latitude) if c.isdigit())
                if len(lat_str) > 8:
                    return f"A latitude informada ({latitude}) possui mais de 8 dígitos. Por favor, informe uma latitude com no máximo 8 dígitos (exemplo: -23.5505 ou 45.6789)."
                    
            except (ValueError, TypeError):
                return f"A latitude informada ('{latitude}') não é um número válido. Por favor, informe apenas números (exemplo: -23.5505 ou 45.6789)."

            # Validar longitude
            try:
                lng_valor = float(longitude) if longitude else None
                if lng_valor is None:
                    return "Por favor, informe a longitude da árvore. A longitude é obrigatória para o cadastro."
                if lng_valor < -180 or lng_valor > 180:
                    return f"A longitude informada ({longitude}) está fora do intervalo permitido. Por favor, informe uma longitude entre -180 e 180 graus."
                
                # Validar que longitude tem no máximo 8 dígitos (contando todos os dígitos, não o ponto decimal nem o sinal negativo)
                # Remover ponto decimal, sinal negativo e espaços, mas manter todos os dígitos incluindo zeros
                lng_str = ''.join(c for c in str(longitude) if c.isdigit())
                if len(lng_str) > 8:
                    return f"A longitude informada ({longitude}) possui mais de 8 dígitos. Por favor, informe uma longitude com no máximo 8 dígitos (exemplo: -46.6333 ou 120.4567)."
                    
            except (ValueError, TypeError):
                return f"A longitude informada ('{longitude}') não é um número válido. Por favor, informe apenas números (exemplo: -46.6333 ou 120.4567)."

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

            # 2) DEFINIÇÃO DO CONTADOR E VALIDAÇÃO

            # Caso não exista nenhuma árvore neste ponto
            if not registros:
                contador = 1

            else:
                # Separar árvores removidas (cortadas) das ativas
                # Status "cortada" é considerado removida, outros status são ativos
                arvores_removidas = [r for r in registros if r[1] == "cortada"]
                arvores_ativas = [r for r in registros if r[1] != "cortada"]

                # Se todas estão removidas (cortadas), pode inserir nova com contador incrementado
                if not arvores_ativas:
                    maior_contador = max([r[0] for r in registros]) if registros else 0
                    contador = maior_contador + 1
                else:
                    # Existe pelo menos uma árvore ativa na mesma localização
                    # O contador será 1, mas precisa verificar se já existe uma árvore com contador = 1
                    contador = 1
                    existe_contador_1 = any(r[0] == 1 for r in arvores_ativas)
                    
                    if existe_contador_1:
                        # Já existe uma árvore ativa com contador = 1 na mesma localização
                        # Tentar inserir causará erro de chave duplicada
                        # Retornar mensagem amigável ANTES de tentar inserir
                        return f"Já existe uma árvore cadastrada na localização informada (Latitude: {latitude}, Longitude: {longitude}). Por favor, verifique se as coordenadas estão corretas. Se você deseja cadastrar uma nova árvore, utilize coordenadas diferentes ou aguarde até que a árvore existente seja removida."

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
            erro_str = str(erro).lower()
            
            # Erro de constraint de latitude
            if "ck_arvore_latitude" in erro_str or ("latitude" in erro_str and "check" in erro_str and "constraint" in erro_str):
                # Verificar se é erro de dígitos ou de range
                if "length" in erro_str or "8" in erro_str:
                    return f"A latitude informada ({latitude}) possui mais de 8 dígitos. Por favor, informe uma latitude com no máximo 8 dígitos (exemplo: -23.5505 ou 45.6789)."
                return "A latitude informada está fora do intervalo permitido. Por favor, informe uma latitude entre -90 e 90 graus."
            
            # Erro de constraint de longitude
            if "ck_arvore_longitude" in erro_str or ("longitude" in erro_str and "check" in erro_str and "constraint" in erro_str):
                # Verificar se é erro de dígitos ou de range
                if "length" in erro_str or "8" in erro_str:
                    return f"A longitude informada ({longitude}) possui mais de 8 dígitos. Por favor, informe uma longitude com no máximo 8 dígitos (exemplo: -46.6333 ou 120.4567)."
                return "A longitude informada está fora do intervalo permitido. Por favor, informe uma longitude entre -180 e 180 graus."
            
            # Erro de constraint de contador
            if "ck_arvore_contador" in erro_str or "contador" in erro_str and ("check" in erro_str or "constraint" in erro_str):
                return "Ocorreu um erro ao processar o contador da árvore. Por favor, tente novamente."
            
            # Erro de chave duplicada (árvore já existe na mesma localização)
            if "duplicate key" in erro_str and ("latitude" in erro_str or "longitude" in erro_str or "contador" in erro_str or "arvore_latitude_longitude_contador_key" in erro_str):
                # Tentar extrair as coordenadas do erro ou usar as que foram validadas
                try:
                    return f"Já existe uma árvore cadastrada na localização informada (Latitude: {latitude}, Longitude: {longitude}). Por favor, verifique se as coordenadas estão corretas. Se você deseja cadastrar uma nova árvore, utilize coordenadas diferentes ou aguarde até que a árvore existente seja removida."
                except:
                    return "Já existe uma árvore cadastrada nesta localização exata. Por favor, verifique se as coordenadas (latitude e longitude) estão corretas ou se você deseja cadastrar uma nova árvore em uma localização diferente."
            
            # Erro de foreign key (espécie não existe)
            if "violates foreign key constraint" in erro_str and ("especie" in erro_str or "nome_cientifico" in erro_str):
                return "A espécie informada não está cadastrada no sistema. Por favor, cadastre a espécie primeiro na página 'Cadastro de Espécie' ou verifique se o nome científico está correto."
            
            # Erro de foreign key (tag não existe)
            if "violates foreign key constraint" in erro_str and "tag" in erro_str:
                return "O código da TAG informado não está cadastrado no sistema. Verifique o código da TAG ou cadastre uma nova TAG antes de associá-la à árvore."
            
            # Erro de constraint de status
            if "ck_arvore_status" in erro_str or ("status" in erro_str and "check" in erro_str):
                return "O status informado não é válido. Por favor, selecione um dos status disponíveis: Saudável, Doente, Em Risco, Corte Programado ou Cortada."
            
            # Erro de constraint de tipo
            if "tipo" in erro_str and "check" in erro_str:
                return "O tipo informado não é válido. Por favor, selecione 'Pública' ou 'Privada'."
            
            # Erro genérico com mensagem amigável
            return "Não foi possível cadastrar a árvore. Verifique se todos os campos obrigatórios foram preenchidos corretamente e tente novamente. Se o problema persistir, entre em contato com o suporte."

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
            # Retornar erro amigável para o usuário
            return "Não foi possível realizar a consulta de árvores. Por favor, tente novamente mais tarde. Se o problema persistir, entre em contato com o suporte.", []
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
            if not nome_cientifico or not nome_cientifico.strip():
                return "Por favor, informe o nome científico da espécie. Este campo é obrigatório para o cadastro."

            # Validar nativa (obrigatório)
            if nativa is None:
                return "Por favor, selecione se a espécie é nativa ou exótica. Esta informação é obrigatória para o cadastro."

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
            erro_str = str(erro).lower()
            
            # Erro de chave duplicada (espécie já existe)
            if "duplicate key" in erro_str or "violates unique constraint" in erro_str:
                return f"A espécie '{nome_cientifico}' já está cadastrada no sistema. Verifique se o nome científico está correto ou se esta espécie já foi cadastrada anteriormente."
            
            # Erro genérico com mensagem amigável
            return "Não foi possível cadastrar a espécie. Verifique se todos os campos foram preenchidos corretamente e tente novamente. Se o problema persistir, entre em contato com o suporte."

        finally:
            if conn:
                self._db_pool.putconn(conn)

    # BUSCAR ESPÉCIES (para autocomplete)
    def select_especies(self, termo_busca=None):
        sql = """
            SELECT
                nome_cientifico,
                nome_popular,
                nativa
            FROM especie
        """
        
        params = []
        
        # Se houver termo de busca, filtrar por nome científico ou nome popular
        if termo_busca:
            sql += " WHERE nome_cientifico ILIKE %s OR nome_popular ILIKE %s"
            termo_like = f"%{termo_busca}%"
            params = [termo_like, termo_like]
        
        sql += " ORDER BY nome_cientifico"

        print("SELECT ESPECIES =", sql, params)

        conn = None
        try:
            conn = self._db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params) if params else None)
            resultados = cursor.fetchall()

            # Converter para lista de dicionários
            colunas = [desc[0] for desc in cursor.description]
            especies = [dict(zip(colunas, row)) for row in resultados]

            cursor.close()
            return None, especies
        except Exception as erro:
            print(f"Erro no select_especies: {erro}")
            # Retornar erro amigável para o usuário
            return "Não foi possível buscar as espécies. Por favor, tente novamente mais tarde. Se o problema persistir, entre em contato com o suporte.", []
        finally:
            if conn:
                self._db_pool.putconn(conn)
