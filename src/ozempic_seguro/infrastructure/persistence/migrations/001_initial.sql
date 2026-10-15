-- Migração 001: Criação inicial das tabelas

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    nome_completo TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('administrador','vendedor','repositor','tecnico')),
    ativo BOOLEAN DEFAULT 1,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gavetas (
    id INTEGER PRIMARY KEY,
    numero_gaveta TEXT NOT NULL UNIQUE,
    esta_aberta BOOLEAN DEFAULT 0,
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS historico_gavetas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gaveta_id INTEGER,
    usuario_id INTEGER,
    acao TEXT NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gaveta_id) REFERENCES gavetas (id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);

CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    acao TEXT NOT NULL,
    tabela_afetada TEXT NOT NULL,
    id_afetado INTEGER,
    dados_anteriores TEXT,
    dados_novos TEXT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    endereco_ip TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
