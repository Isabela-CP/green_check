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

