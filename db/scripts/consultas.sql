-- ============================================================================
-- CONSULTAS SQL COMPLEXAS - GREEN CHECK
-- ============================================================================
-- Este arquivo contém consultas SQL de complexidade média e alta para o
-- sistema de gestão de árvores urbanas.
-- 
-- Todas as consultas foram adaptadas para o esquema atual do banco de dados,
-- utilizando as tabelas e constraints definidas em 01_esquema.sql
-- ============================================================================

-- ============================================================================
-- CONSULTA 1: Identificar Árvores com Aumento de Risco
-- ============================================================================
-- 
-- Motivação:
-- Detectar árvores cujo risco evoluiu para níveis piores ao longo do tempo,
-- priorizando inspeções/manutenções preventivas.
--
-- Explicação:
-- Para cada vistoria, identifica a vistoria anterior da mesma árvore.
-- Compara o risco atual com o risco anterior.
-- Retorna apenas vistorias onde o risco mudou (por exemplo, de 'baixo' → 'medio').
--
-- Complexidade: Média-Alta
-- - Utiliza subconsulta correlacionada para buscar a vistoria anterior
-- - Comparação de datas e horas para ordenação temporal
-- - Filtros complexos para identificar mudanças de risco
--
-- Valores de risco permitidos (definidos por constraint CHECK):
-- - 'baixo'
-- - 'medio'
-- - 'alto'
-- - 'critico'
--
-- Tabelas utilizadas:
-- - vistoria_inicial (auto-join para comparar vistorias da mesma árvore)
--
-- Campos utilizados:
-- - cod_solicitacao: Identificador único da vistoria
-- - latitude, longitude, contador: Chave composta para identificar a árvore
-- - data, hora: Para ordenação temporal e comparação
-- - risco: Valor do risco (validado por constraint CHECK)
-- ============================================================================
SELECT *
FROM (
    SELECT
        v_atual.cod_solicitacao,
        v_atual.latitude,
        v_atual.longitude,
        v_atual.contador,
        v_atual.data AS data_vistoria,
        v_atual.risco AS risco_atual,
        (
            SELECT v_prev.risco
            FROM vistoria_inicial v_prev
            WHERE v_prev.latitude = v_atual.latitude
              AND v_prev.longitude = v_atual.longitude
              AND v_prev.contador = v_atual.contador
              AND (v_prev.data < v_atual.data
                   OR (v_prev.data = v_atual.data AND v_prev.hora < v_atual.hora))
            ORDER BY v_prev.data DESC, v_prev.hora DESC
            LIMIT 1
        ) AS risco_previo
    FROM vistoria_inicial v_atual
) AS t
WHERE risco_previo IS NOT NULL
  AND risco_atual IS NOT NULL
  AND risco_previo <> risco_atual
ORDER BY data_vistoria DESC;

-- ============================================================================
-- FIM DA CONSULTA 1
-- ============================================================================

-- ============================================================================
-- CONSULTA 2: Solicitações Válidas sem Manutenção por Bairro
-- ============================================================================
-- 
-- Motivação:
-- Identificar bairros com maior número de solicitações válidas que já foram
-- vistoriadas mas ainda não receberam manutenção, permitindo priorizar ações
-- e alocação de recursos.
--
-- Explicação:
-- Busca solicitações com status 'valida' que possuem vistoria inicial,
-- mas não possuem nenhuma manutenção associada. Agrupa os resultados por
-- bairro e conta quantas solicitações atendem a esses critérios em cada
-- bairro, ordenando por quantidade decrescente.
--
-- Complexidade: Média
-- - Utiliza LEFT JOIN para identificar ausência de manutenção
-- - Agregação com COUNT DISTINCT para evitar duplicatas
-- - Filtros combinados (WHERE + HAVING) para refinar resultados
--
-- Tabelas utilizadas:
-- - solicitacao: Tabela principal de solicitações
-- - vistoria_inicial: Vistorias realizadas para as solicitações
-- - manutencao: Manutenções realizadas (verificação de ausência)
--
-- Campos utilizados:
-- - solicitacao.codigo: Identificador único da solicitação
-- - solicitacao.bairro: Bairro onde a solicitação foi feita
-- - solicitacao.status: Status da solicitação (deve ser 'valida')
-- - vistoria_inicial.cod_solicitacao: Relaciona vistoria com solicitação
-- - manutencao.cod_solicitacao: Relaciona manutenção com vistoria/solicitação
--
-- Observação:
-- A consulta utiliza LEFT JOIN para permitir identificar solicitações sem
-- manutenção. A condição m.cod_solicitacao IS NULL garante que apenas
-- solicitações sem manutenção sejam retornadas.
-- ============================================================================
SELECT
  s.bairro,
  COUNT(DISTINCT s.codigo) AS solicitacoes_abertas_sem_manutencao
FROM solicitacao s
LEFT JOIN vistoria_inicial v ON v.cod_solicitacao = s.codigo
LEFT JOIN manutencao m ON m.cod_solicitacao = v.cod_solicitacao
WHERE s.status = 'valida'
  AND m.cod_solicitacao IS NULL
GROUP BY s.bairro
HAVING COUNT(DISTINCT s.codigo) > 0
ORDER BY solicitacoes_abertas_sem_manutencao DESC;

-- ============================================================================
-- FIM DA CONSULTA 2
-- ============================================================================

-- ============================================================================
-- CONSULTA 3: Identificação de Empresas com Qualificação Completa para Risco Ecológico (Divisão Relacional)
-- ============================================================================
-- 
-- Motivação:
-- Identificar empresas terceirizadas que realizaram remoção/corte em TODAS
-- as espécies nativas que já tiveram risco 'alto' em alguma vistoria. Isso
-- permite identificar empresas com experiência completa em lidar com espécies
-- nativas de alto risco, importante para preservação ambiental.
--
-- Explicação:
-- Esta é uma consulta de DIVISÃO RELACIONAL, que identifica empresas que
-- atenderam a TODAS as espécies nativas que já tiveram risco alto.
-- 
-- A consulta funciona em duas partes:
-- 1. Divisor (subconsulta): Conta quantas espécies nativas diferentes já
--    tiveram risco 'alto' em alguma vistoria.
-- 2. Dividendo (consulta principal): Para cada empresa, conta quantas
--    espécies nativas diferentes ela cortou/removeu.
-- 3. HAVING: Compara se o número de espécies atendidas pela empresa é igual
--    ao número total de espécies nativas que tiveram risco alto.
--
-- Complexidade: Alta (Divisão Relacional)
-- - Utiliza divisão relacional (HAVING com subconsulta)
-- - Múltiplos JOINs para relacionar empresa → manutenção → vistoria → árvore → espécie
-- - Verificação de espécies nativas através de JOIN com tabela especie
-- - Agregação com COUNT DISTINCT para contar espécies únicas
--
-- Tabelas utilizadas:
-- - empresa_terceirizada: Empresas que realizam manutenções
-- - manutencao: Manutenções realizadas (filtro por tipo 'remocao')
-- - vistoria_inicial: Vistorias que identificaram risco alto
-- - arvore: Árvores que foram vistoriadas/manutenidas
-- - especie: Informação sobre espécies (campo nativa)
--
-- Campos utilizados:
-- - empresa_terceirizada.cnpj: Identificador da empresa
-- - manutencao.tipo: Tipo de manutenção (deve ser 'remocao')
-- - manutencao.cod_solicitacao: Relaciona manutenção com vistoria
-- - vistoria_inicial.cod_solicitacao: Relaciona vistoria com solicitação
-- - vistoria_inicial.risco: Nível de risco (deve ser 'alto')
-- - vistoria_inicial.latitude, longitude, contador: Identificam a árvore
-- - arvore.nome_cientifico: Nome científico da espécie
-- - especie.nativa: Indica se a espécie é nativa (TRUE) ou exótica (FALSE)
--
-- Valores de tipo de manutenção permitidos (definidos por constraint CHECK):
-- - 'poda'
-- - 'remocao'
-- - 'tratamento'
--
-- Observações importantes:
-- 1. A consulta usa 'remocao' como equivalente a 'corte', pois 'corte' não
--    existe no banco de dados atual.
-- 2. É necessário fazer JOIN com a tabela especie para verificar se uma
--    espécie é nativa, pois arvore.tipo indica apenas se é 'publico' ou
--    'privado', não se a espécie é nativa.
-- 3. A consulta retornará apenas empresas que atenderam TODAS as espécies
--    nativas que tiveram risco alto (divisão relacional completa).
-- ============================================================================
SELECT 
    e.cnpj,
    COUNT(DISTINCT a.nome_cientifico) AS especies_criticas_atendidas
FROM empresa_terceirizada e
JOIN manutencao m ON m.cnpj = e.cnpj
JOIN vistoria_inicial v ON v.cod_solicitacao = m.cod_solicitacao
JOIN arvore a 
    ON v.latitude = a.latitude 
    AND v.longitude = a.longitude 
    AND v.contador = a.contador
JOIN especie esp ON esp.nome_cientifico = a.nome_cientifico
WHERE m.tipo = 'remocao'  -- A empresa tem que ter feito remoção (equivalente a corte)
  AND esp.nativa = TRUE    -- Apenas espécies nativas
GROUP BY e.cnpj
HAVING COUNT(DISTINCT a.nome_cientifico) = (
    -- O DIVISOR COMPLEXO: 
    -- Quantas espécies NATIVAS já tiveram risco ALTO na história?
    SELECT COUNT(DISTINCT a_alvo.nome_cientifico)
    FROM arvore a_alvo
    JOIN especie esp_alvo ON esp_alvo.nome_cientifico = a_alvo.nome_cientifico
    JOIN vistoria_inicial v_alvo 
        ON v_alvo.latitude = a_alvo.latitude 
        AND v_alvo.longitude = a_alvo.longitude 
        AND v_alvo.contador = a_alvo.contador
    WHERE esp_alvo.nativa = TRUE   -- Condição 1: Espécie nativa
      AND v_alvo.risco = 'alto'     -- Condição 2: Histórico de risco alto
);

-- ============================================================================
-- FIM DA CONSULTA 3
-- ============================================================================

-- ============================================================================
-- CONSULTA 4: Tipos de Manutenção mais Frequentes por Nível de Risco
-- ============================================================================
-- 
-- Motivação:
-- Analisar quais tipos de manutenção são mais aplicados para cada nível de
-- risco identificado na vistoria inicial, permitindo entender padrões de
-- intervenção e planejar recursos adequados para cada tipo de situação.
--
-- Explicação:
-- Agrupa as manutenções por nível de risco e tipo de manutenção, calculando:
-- 1. Quantidade de manutenções de cada tipo por risco
-- 2. Total de manutenções para cada nível de risco
-- 3. Percentual que cada tipo representa em relação ao total do risco
--
-- Complexidade: Média
-- - Utiliza CTE (Common Table Expression) para otimizar cálculo de totais
-- - Agregação com COUNT para quantificar manutenções
-- - Cálculo de percentuais com ROUND para precisão de 2 casas decimais
-- - INNER JOIN garante que apenas vistorias com manutenção sejam consideradas
--
-- Tabelas utilizadas:
-- - vistoria_inicial: Vistorias que identificaram níveis de risco
-- - manutencao: Manutenções realizadas após as vistorias
--
-- Campos utilizados:
-- - vistoria_inicial.risco: Nível de risco (validado por constraint CHECK)
-- - vistoria_inicial.cod_solicitacao: Identificador único da vistoria
-- - manutencao.tipo: Tipo de manutenção (validado por constraint CHECK)
-- - manutencao.cod_solicitacao: Relaciona manutenção com vistoria
--
-- Valores de risco permitidos (definidos por constraint CHECK):
-- - 'baixo'
-- - 'medio'
-- - 'alto'
-- - 'critico'
--
-- Valores de tipo de manutenção permitidos (definidos por constraint CHECK):
-- - 'poda'
-- - 'remocao'
-- - 'tratamento'
--
-- Observações importantes:
-- 1. A consulta usa INNER JOIN, então apenas vistorias que possuem manutenção
--    são incluídas nos resultados.
-- 2. O CTE otimiza a consulta evitando calcular o total de manutenções por
--    risco múltiplas vezes.
-- 3. A ordenação é por risco (alfabética) e quantidade (decrescente), mostrando
--    os tipos mais frequentes primeiro para cada risco.
-- ============================================================================
WITH totais_por_risco AS (
    SELECT 
        v.risco,
        COUNT(*) AS total
    FROM vistoria_inicial v
    INNER JOIN manutencao m ON m.cod_solicitacao = v.cod_solicitacao
    GROUP BY v.risco
)
SELECT 
    v.risco,
    m.tipo AS tipo_manutencao,
    COUNT(*) AS quantidade,
    t.total AS total_manutencoes_risco,
    ROUND((COUNT(*) * 100.0) / t.total, 2) AS percentual
FROM vistoria_inicial v
INNER JOIN manutencao m ON m.cod_solicitacao = v.cod_solicitacao
INNER JOIN totais_por_risco t ON t.risco = v.risco
GROUP BY v.risco, m.tipo, t.total
ORDER BY v.risco, quantidade DESC;

-- ============================================================================
-- FIM DA CONSULTA 4
-- ============================================================================

-- ============================================================================
-- CONSULTA 5: Identificação de Manutenções Ineficazes
-- ============================================================================
-- 
-- Motivação:
-- Identificar casos onde uma manutenção foi realizada (ex: uma poda), mas em
-- menos de 60 dias a mesma árvore gerou uma nova vistoria apontando risco
-- 'alto' ou 'medio'. Isso indica que o serviço pode ter sido mal feito pela
-- empresa terceirizada ou que o diagnóstico inicial estava errado.
--
-- Explicação:
-- A consulta identifica manutenções que não foram efetivas, comparando:
-- 1. A data da manutenção (vistoria original)
-- 2. Novas vistorias na mesma árvore dentro de 60 dias
-- 3. Se a nova vistoria aponta risco preocupante ('alto' ou 'medio')
--
-- Complexidade: Média-Alta
-- - Utiliza auto-join em vistoria_inicial para comparar vistorias da mesma árvore
-- - Filtro temporal (60 dias) usando aritmética de datas
-- - Múltiplos JOINs para relacionar manutenção → vistoria → árvore → empresa
-- - Cálculo de dias entre manutenção e nova vistoria
--
-- Tabelas utilizadas:
-- - manutencao: Manutenções realizadas
-- - vistoria_inicial: Vistorias originais e novas (auto-join)
-- - empresa_terceirizada: Empresas responsáveis pelas manutenções
-- - arvore: Árvores que foram manutenidas e revistoriadas
--
-- Campos utilizados:
-- - manutencao.cod_solicitacao: Relaciona manutenção com vistoria original
-- - manutencao.tipo: Tipo de serviço executado
-- - manutencao.cnpj: Identifica a empresa responsável
-- - vistoria_inicial.data: Data da vistoria (original e nova)
-- - vistoria_inicial.risco: Nível de risco da nova vistoria
-- - vistoria_inicial.latitude, longitude, contador: Identificam a árvore
-- - arvore.nome_cientifico: Nome científico da espécie
-- - empresa_terceirizada.cnpj: CNPJ da empresa
--
-- Valores de risco permitidos (definidos por constraint CHECK):
-- - 'baixo'
-- - 'medio'
-- - 'alto'
-- - 'critico'
--
-- Observações importantes:
-- 1. A consulta considera apenas riscos 'alto' ou 'medio' como preocupantes.
--    Riscos 'baixo' ou 'critico' não são considerados reincidência.
-- 2. O filtro temporal de 60 dias é calculado usando aritmética de datas
--    do PostgreSQL (v_origem.data + 60).
-- 3. A condição v_nova.data > v_origem.data garante que apenas vistorias
--    posteriores à manutenção sejam consideradas.
-- 4. A ordenação por dias_apos_servico ASC mostra os casos mais críticos
--    primeiro (menos tempo entre manutenção e problema).
-- ============================================================================
SELECT 
    e.cnpj AS empresa_responsavel,
    m.tipo AS servico_executado,
    a.nome_cientifico,
    v_origem.data AS data_servico,
    v_nova.data AS data_novo_problema,
    v_nova.risco AS risco_reincidente,
    (v_nova.data - v_origem.data) AS dias_apos_servico
FROM manutencao m
JOIN vistoria_inicial v_origem ON m.cod_solicitacao = v_origem.cod_solicitacao
JOIN empresa_terceirizada e ON m.cnpj = e.cnpj
JOIN arvore a 
    ON v_origem.latitude = a.latitude 
    AND v_origem.longitude = a.longitude 
    AND v_origem.contador = a.contador
JOIN vistoria_inicial v_nova 
    ON v_nova.latitude = a.latitude 
    AND v_nova.longitude = a.longitude 
    AND v_nova.contador = a.contador
WHERE 
    v_nova.data > v_origem.data 
    AND v_nova.data <= (v_origem.data + 60)
    AND v_nova.risco IN ('alto', 'medio')
ORDER BY dias_apos_servico ASC;

-- ============================================================================
-- FIM DA CONSULTA 5
-- ============================================================================

