-- ============================================================================
-- SCRIPT DE ALIMENTAÇÃO INICIAL DA BASE DE DADOS
-- ============================================================================
-- Este script insere dados iniciais para todas as tabelas do sistema,
-- garantindo relacionamentos válidos entre as entidades.
-- Mínimo de 2 tuplas por tabela conforme requisitos do projeto.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. USUÁRIOS (Base para munícipe e responsável técnico)
-- ----------------------------------------------------------------------------
INSERT INTO usuario (cpf, nome, telefone, email, senha, papel)
VALUES 
    ('00000000000', 'Usuário Administrador', NULL, 'admin@sistema.com', '123456789', 'municipe'),
    ('11111111111', 'Maria Silva Santos', '11987654321', 'maria.silva@email.com', 'senha12345', 'municipe'),
    ('22222222222', 'João Pedro Oliveira', '11976543210', 'joao.oliveira@email.com', 'senha98765', 'municipe'),
    ('33333333333', 'Ana Paula Costa', '11965432109', 'ana.costa@email.com', 'senha54321', 'municipe'),
    ('44444444444', 'Carlos Eduardo Lima', '11912345678', 'carlos.lima@crea.com', 'senha11111', 'responsavel tecnico'),
    ('55555555555', 'Fernanda Rodrigues', '11923456789', 'fernanda.rodrigues@crea.com', 'senha22222', 'responsavel tecnico')
ON CONFLICT (cpf) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. MUNÍCIPES (Subtipo de usuario)
-- ----------------------------------------------------------------------------
INSERT INTO municipe (cpf)
VALUES 
    ('00000000000'),
    ('11111111111'),
    ('22222222222'),
    ('33333333333')
ON CONFLICT (cpf) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. RESPONSÁVEIS TÉCNICOS (Subtipo de usuario)
-- ----------------------------------------------------------------------------
INSERT INTO responsavel_tecnico (cpf, conselho_regional, registro_profissional)
VALUES 
    ('44444444444', 'CREA-SP', '123456'),
    ('55555555555', 'CREA-SP', '789012')
ON CONFLICT (conselho_regional, registro_profissional) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. EMPRESAS TERCEIRIZADAS
-- ----------------------------------------------------------------------------
INSERT INTO empresa_terceirizada (cnpj, nome)
VALUES 
    ('12345678000190', 'Jardim & Paisagismo Ltda'),
    ('98765432000110', 'Arborização Urbana S.A.'),
    ('11223344000150', 'Meio Ambiente Sustentável EIRELI')
ON CONFLICT (cnpj) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. NOMES CIENTÍFICOS (Espécies de árvores)
-- ----------------------------------------------------------------------------
INSERT INTO nome_cientifico (nome_cientifico, nome_popular, nativa)
VALUES 
    ('Handroanthus impetiginosus', 'Ipê-roxo', TRUE),
    ('Tipuana tipu', 'Tipuana', FALSE),
    ('Ficus benjamina', 'Ficus', FALSE),
    ('Schinus terebinthifolius', 'Aroeira', TRUE),
    ('Mangifera indica', 'Mangueira', FALSE),
    ('Syagrus romanzoffiana', 'Palmeira-jerivá', TRUE)
ON CONFLICT (nome_cientifico) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. ÁRVORES
-- ----------------------------------------------------------------------------
INSERT INTO arvore (latitude, longitude, contador, nome_cientifico, ultima_vistoria, status, tipo, altura, dap)
VALUES 
    -- Árvore 1: Ipê-roxo saudável com tag (público)
    (-23.550520, -46.633308, 1, 'Handroanthus impetiginosus', '2024-01-15', 'Saudável', 'público', 8.5, 45.0),
    
    -- Árvore 2: Tipuana doente (público)
    (-23.551520, -46.634308, 1, 'Tipuana tipu', '2024-02-20', 'Doente', 'público', 12.0, 60.0),
    
    -- Árvore 3: Ficus em risco (público)
    (-23.552520, -46.635308, 1, 'Ficus benjamina', '2024-03-10', 'Em Risco', 'público', 6.0, 35.0),
    
    -- Árvore 4: Aroeira saudável (público)
    (-23.553520, -46.636308, 1, 'Schinus terebinthifolius', '2024-01-25', 'Saudável', 'público', 5.5, 30.0),
    
    -- Árvore 5: Mangueira cortada (contador 1) - privado
    (-23.554520, -46.637308, 1, 'Mangifera indica', '2023-12-10', 'Cortada', 'privado', 10.0, 50.0),
    
    -- Árvore 6: Nova árvore no mesmo local da mangueira (contador 2) - público
    (-23.554520, -46.637308, 2, 'Syagrus romanzoffiana', '2024-04-01', 'Saudável', 'público', 3.0, 15.0),
    
    -- Árvore 7: Palmeira-jerivá saudável (público)
    (-23.555520, -46.638308, 1, 'Syagrus romanzoffiana', '2024-02-28', 'Saudável', 'público', 4.5, 20.0),
    
    -- Árvore 8: Ipê-roxo doente (privado)
    (-23.556520, -46.639308, 1, 'Handroanthus impetiginosus', '2024-03-15', 'Doente', 'privado', 7.0, 40.0)
ON CONFLICT (latitude, longitude, contador) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 7. TAGS NFC (Associadas às árvores)
-- ----------------------------------------------------------------------------
INSERT INTO tag (codigo_nfc, latitude, longitude, contador)
VALUES 
    ('NFC001', -23.550520, -46.633308, 1),
    ('NFC002', -23.551520, -46.634308, 1),
    ('NFC003', -23.552520, -46.635308, 1),
    ('NFC004', -23.553520, -46.636308, 1)
ON CONFLICT (codigo_nfc) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 8. SOLICITAÇÕES (Feitas por munícipe, atribuídas a responsável técnico)
-- ----------------------------------------------------------------------------
INSERT INTO solicitacao (cpf_usuario, cpf_resp_tecnico, descricao, bairro, rua, numero, data, hora, status)
VALUES 
    -- Solicitação 1: Árvore doente reportada
    ('11111111111', '44444444444', 'Árvore apresentando folhas amareladas e galhos secos', 'Centro', 'Rua das Flores', '123', '2024-02-15', '10:30:00', 'válida'),
    
    -- Solicitação 2: Árvore em risco
    ('22222222222', '44444444444', 'Árvore com inclinação perigosa próximo à calçada', 'Jardim América', 'Av. Paulista', '456', '2024-03-05', '14:20:00', 'válida'),
    
    -- Solicitação 3: Solicitação inválida
    ('33333333333', '55555555555', 'Árvore muito alta', 'Vila Madalena', 'Rua Harmonia', '789', '2024-01-20', '09:15:00', 'inválida'),
    
    -- Solicitação 4: Nova solicitação
    ('11111111111', '55555555555', 'Árvore com raízes expostas causando danos na calçada', 'Pinheiros', 'Rua dos Pinheiros', '321', '2024-03-20', '16:45:00', 'válida')
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- 9. FOTOS DAS SOLICITAÇÕES
-- ----------------------------------------------------------------------------
INSERT INTO fotos_solicitacao (codigo, caminho_foto)
VALUES 
    (1, '/fotos/solicitacao_001_foto1.jpg'),
    (1, '/fotos/solicitacao_001_foto2.jpg'),
    (2, '/fotos/solicitacao_002_foto1.jpg'),
    (3, '/fotos/solicitacao_003_foto1.jpg'),
    (4, '/fotos/solicitacao_004_foto1.jpg'),
    (4, '/fotos/solicitacao_004_foto2.jpg')
ON CONFLICT (codigo, caminho_foto) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 10. VISTORIAS INICIAIS (Relacionam solicitação com árvore)
-- ----------------------------------------------------------------------------
INSERT INTO vistoria_inicial (cod_solicitacao, data, hora, risco, status, latitude, longitude, contador)
VALUES 
    -- Vistoria 1: Solicitação 1 -> Árvore 2 (Tipuana doente)
    (1, '2024-02-18', '09:00:00', 'Médio', 'ok', -23.551520, -46.634308, 1),
    
    -- Vistoria 2: Solicitação 2 -> Árvore 3 (Ficus em risco)
    (2, '2024-03-08', '10:30:00', 'Alto', 'ok', -23.552520, -46.635308, 1),
    
    -- Vistoria 3: Solicitação 4 -> Árvore 8 (Ipê-roxo doente) - vistoria inválida
    (4, '2024-03-22', '14:00:00', 'Baixo', 'invalida', -23.556520, -46.639308, 1)
ON CONFLICT (cod_solicitacao) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 11. MANUTENÇÕES (Relacionam vistoria com empresa e responsável técnico)
-- ----------------------------------------------------------------------------
INSERT INTO manutencao (cod_solicitacao, tipo, laudo, cnpj, tipo_contrato, prazo, cpf_resp_tecnico)
VALUES 
    -- Manutenção 1: Podas na árvore doente
    (1, 'Poda', 'Realizada poda de galhos secos e tratamento fitossanitário', '12345678000190', 'Serviço', '30 dias', '44444444444'),
    
    -- Manutenção 2: Remoção de árvore em risco
    (2, 'Remoção', 'Árvore removida devido ao risco de queda. Compensação ambiental necessária', '98765432000110', 'Serviço', '15 dias', '44444444444'),
    
    -- Manutenção 3: Tratamento de raízes
    (4, 'Tratamento', 'Aplicação de tratamento nas raízes expostas e nivelamento da calçada', '12345678000190', 'Serviço', '45 dias', '55555555555'),
    
    -- Manutenção 4: Compensação ambiental (relacionada com manutenção 2)
    (2, 'Compensação', 'Plantio de 3 mudas nativas como compensação pela remoção', '11223344000150', 'Serviço', '60 dias', '44444444444')
ON CONFLICT (cod_solicitacao, tipo) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 12. FOTOS DAS MANUTENÇÕES
-- ----------------------------------------------------------------------------
INSERT INTO foto_manutencao (cod_solicitacao, tipo, caminho_foto)
VALUES 
    (1, 'Poda', '/fotos/manutencao_001_poda_antes.jpg'),
    (1, 'Poda', '/fotos/manutencao_001_poda_depois.jpg'),
    (2, 'Remoção', '/fotos/manutencao_002_remocao.jpg'),
    (4, 'Tratamento', '/fotos/manutencao_004_tratamento.jpg'),
    (2, 'Compensação', '/fotos/manutencao_002_compensacao_plantio.jpg')
ON CONFLICT (cod_solicitacao, tipo, caminho_foto) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 13. COMPENSAÇÕES AMBIENTAIS (Relacionadas com manutenções)
-- ----------------------------------------------------------------------------
INSERT INTO compensacao_ambiental (tipo, cod_solicitacao, num_mudas, status)
VALUES 
    -- Compensação da remoção (manutenção tipo 'Compensação')
    ('Compensação', 2, 3, 'finalizada'),
    
    -- Compensação futura (manutenção tipo 'Remoção')
    ('Remoção', 2, 0, 'em aberto')
ON CONFLICT (tipo, cod_solicitacao) DO NOTHING;

-- ============================================================================
-- FIM DO SCRIPT DE ALIMENTAÇÃO
-- ============================================================================
-- Total de tuplas inseridas:
-- - usuario: 6 tuplas
-- - municipe: 4 tuplas
-- - responsavel_tecnico: 2 tuplas
-- - empresa_terceirizada: 3 tuplas
-- - nome_cientifico: 6 tuplas
-- - arvore: 8 tuplas
-- - tag: 4 tuplas
-- - solicitacao: 4 tuplas
-- - fotos_solicitacao: 6 tuplas
-- - vistoria_inicial: 3 tuplas
-- - manutencao: 4 tuplas
-- - foto_manutencao: 5 tuplas
-- - compensacao_ambiental: 2 tuplas
-- ============================================================================
