
-- TABELA: usuario
CREATE TABLE usuario (
    cpf VARCHAR(14) PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT NOT NULL,
    senha TEXT NOT NULL,
    papel TEXT NOT NULL,

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
    ),

    -- Papel limitado a valores permitidos
    CONSTRAINT ck_usuario_papel CHECK (
        papel IN ('municipe', 'responsavel tecnico')
    )
);

-- MUNÍCIPE (subtipo de usuario)
CREATE TABLE municipe (
    cpf VARCHAR(14) PRIMARY KEY REFERENCES usuario(cpf)
);

-- RESPONSÁVEL TÉCNICO (subtipo de usuario)
CREATE TABLE responsavel_tecnico (
    cpf VARCHAR(14) PRIMARY KEY REFERENCES usuario(cpf),
    conselho_regional TEXT NOT NULL,
    registro_profissional TEXT NOT NULL,
    UNIQUE(conselho_regional, registro_profissional)
);

-- EMPRESA TERCEIRIZADA
CREATE TABLE empresa_terceirizada (
    cnpj VARCHAR(20) PRIMARY KEY,
    nome TEXT NOT NULL
);

-- solicitacao
CREATE TABLE solicitacao (
    codigo SERIAL PRIMARY KEY,
    cpf_usuario CHAR(11) REFERENCES usuario(cpf),
    cpf_resp_tecnico CHAR(11) REFERENCES responsavel_tecnico(cpf),
    descricao TEXT,
    bairro TEXT,
    rua TEXT,
    numero TEXT,
    data DATE,
    hora TIME,
    status VARCHAR(8),
    CONSTRAINT check_status CHECK (status IN ('válida', 'inválida'))
);

-- FOTOS DA solicitacao
CREATE TABLE fotos_solicitacao (
    codigo INTEGER REFERENCES solicitacao(codigo),
    caminho_foto TEXT NOT NULL,
    PRIMARY KEY (codigo, caminho_foto)
);

-- nome_cientifico
CREATE TABLE nome_cientifico (
    nome_cientifico TEXT PRIMARY KEY,
    nome_popular TEXT,
    nativa BOOLEAN
);

-- arvore
CREATE TABLE arvore (
    id SERIAL PRIMARY KEY,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    contador INTEGER NOT NULL,
    nome_cientifico TEXT REFERENCES nome_cientifico(nome_cientifico),
    ultima_vistoria DATE,
    status TEXT,
    tipo TEXT,
    altura NUMERIC,
    dap NUMERIC,
    UNIQUE (latitude, longitude, contador),
    CONSTRAINT ck_arvore_tipo CHECK (tipo IN ('público', 'privado'))
);


-- TAG NFC
CREATE TABLE tag (
    codigo_nfc TEXT PRIMARY KEY,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    contador INTEGER NOT NULL,
    FOREIGN KEY (latitude, longitude, contador)
        REFERENCES arvore(latitude, longitude, contador),
    UNIQUE(latitude, longitude, contador)
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
    CONSTRAINT ck_vistoria_status CHECK (status IN ('inválida', 'ok'))
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
    PRIMARY KEY (cod_solicitacao, tipo)
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