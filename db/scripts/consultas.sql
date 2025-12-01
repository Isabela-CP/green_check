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
-- Busca solicitações com status 'válida' que possuem vistoria inicial,
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
-- - solicitacao.status: Status da solicitação (deve ser 'válida')
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
WHERE s.status = 'válida'
  AND m.cod_solicitacao IS NULL
GROUP BY s.bairro
HAVING COUNT(DISTINCT s.codigo) > 0
ORDER BY solicitacoes_abertas_sem_manutencao DESC;

-- ============================================================================
-- FIM DA CONSULTA 2
-- ============================================================================

