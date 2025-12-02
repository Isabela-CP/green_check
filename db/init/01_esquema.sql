
-- TABELA: usuario
CREATE TABLE usuario (
    cpf VARCHAR(11) PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone VARCHAR(11),
    email VARCHAR(255) NOT NULL CHECK (email LIKE '%@%'),
    senha VARCHAR(255) NOT NULL,
    papel VARCHAR(20) NOT NULL CHECK (papel IN ('municipe', 'responsavel tecnico')),

    -- CPF deve ter tamanho 11 (sem pontos e traço)
    CONSTRAINT ck_usuario_cpf CHECK (LENGTH(cpf) = 11),

    -- Senha deve ter mais de 8 caracteres
    CONSTRAINT ck_usuario_senha CHECK (LENGTH(senha) > 8),

    -- Telefone exatamente 11 caracteres
    CONSTRAINT ck_usuario_telefone CHECK (LENGTH(telefone) = 11),

    -- Email deve ter pelo menos 6 caracteres e conter @
    CONSTRAINT ck_usuario_email CHECK (
        LENGTH(email) >= 6
        AND email LIKE '%@%'
    )
);

-- RESPONSÁVEL TÉCNICO (subtipo de usuario)
CREATE TABLE responsavel_tecnico (
    cpf VARCHAR(11) PRIMARY KEY REFERENCES usuario(cpf),
    conselho_regional VARCHAR(20) NOT NULL,
    registro_profissional VARCHAR(20) NOT NULL,
    UNIQUE(conselho_regional, registro_profissional)
);

-- EMPRESA TERCEIRIZADA
CREATE TABLE empresa_terceirizada (
    cnpj VARCHAR(14) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    CONSTRAINT ck_empresa_terceirizada_cnpj CHECK (LENGTH(cnpj) = 14)
);

-- solicitacao
CREATE TABLE solicitacao (
    codigo SERIAL PRIMARY KEY,
    cpf_usuario CHAR(11) REFERENCES usuario(cpf),
    cpf_resp_tecnico CHAR(11) REFERENCES responsavel_tecnico(cpf),
    descricao TEXT,
    bairro VARCHAR(255),
    rua TEXT,
    numero SMALLINT,
    data DATE,
    hora TIME,
    status VARCHAR(8),
    CONSTRAINT check_status CHECK (status IN ('valida', 'invalida'))
);

-- FOTOS DA solicitacao
CREATE TABLE fotos_solicitacao (
    codigo INTEGER REFERENCES solicitacao(codigo),
    caminho_foto TEXT NOT NULL,
    PRIMARY KEY (codigo, caminho_foto)
);

-- ESPÉCIE (Tabela de espécies de árvores)
-- Armazena informações sobre as espécies de árvores cadastradas no sistema
CREATE TABLE especie (
    nome_cientifico TEXT PRIMARY KEY,  -- Nome científico da espécie (chave primária)
    nome_popular TEXT,                  -- Nome popular/comum da espécie
    nativa BOOLEAN                      -- Indica se a espécie é nativa (TRUE) ou exótica (FALSE)
);

-- TAG NFC
CREATE TABLE tag (
    codigo_nfc TEXT PRIMARY KEY
);

-- arvore
CREATE TABLE arvore (
    id SERIAL PRIMARY KEY,
    codigo_nfc TEXT REFERENCES tag(codigo_nfc),
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    contador INTEGER NOT NULL,
    nome_cientifico TEXT REFERENCES especie(nome_cientifico),
    ultima_vistoria DATE,
    status TEXT,
    CONSTRAINT ck_arvore_status CHECK (status IN ('saudavel', 'doente', 'em risco', 'corte programado', 'cortada')),
    tipo VARCHAR(10) CHECK (tipo IN ('publico', 'privado')),
    altura NUMERIC,
    dap NUMERIC,
    UNIQUE (latitude, longitude, contador),
    UNIQUE (codigo_nfc)
);


-- VISTORIA INICIAL
CREATE TABLE vistoria_inicial (
    data DATE,
    hora TIME,
    risco TEXT,
    status TEXT,
    cod_solicitacao INTEGER REFERENCES solicitacao(codigo),
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    contador INTEGER NOT NULL,
    PRIMARY KEY (cod_solicitacao),
    FOREIGN KEY (latitude, longitude, contador)
        REFERENCES arvore(latitude, longitude, contador),
    CONSTRAINT ck_vistoria_status CHECK (status IN ('inválida', 'ok')),
    CONSTRAINT ck_vistoria_risco CHECK (risco IN ('baixo', 'medio', 'alto', 'critico'))
);

-- manutencao

CREATE TABLE manutencao (
    tipo TEXT,
    cod_solicitacao INTEGER REFERENCES vistoria_inicial(cod_solicitacao),
    laudo TEXT,
    cnpj VARCHAR(20) REFERENCES empresa_terceirizada(cnpj),
    tipo_contrato TEXT,
    prazo TEXT,
    cpf_resp_tecnico CHAR(11) REFERENCES responsavel_tecnico(cpf),
    PRIMARY KEY (cod_solicitacao, tipo),
    CONSTRAINT ck_manutencao_tipo CHECK (tipo IN ('poda', 'remocao', 'tratamento'))
);

-- FOTOS DA manutencao
CREATE TABLE foto_manutencao (
    cod_solicitacao INTEGER,
    tipo TEXT,
    caminho_foto TEXT NOT NULL,
    PRIMARY KEY (cod_solicitacao, tipo, caminho_foto),
    FOREIGN KEY (cod_solicitacao, tipo)
        REFERENCES manutencao(cod_solicitacao, tipo)
);

-- COMPENSAÇÃO AMBIENTAL
CREATE TABLE compensacao_ambiental (
    tipo TEXT,
    cod_solicitacao INTEGER,
    num_mudas INTEGER,
    status TEXT,
    PRIMARY KEY (tipo, cod_solicitacao),
    FOREIGN KEY (cod_solicitacao, tipo)
        REFERENCES manutencao(cod_solicitacao, tipo),
    CONSTRAINT check_status_ambiental CHECK (status IN ('em aberto', 'finalizada'))
);