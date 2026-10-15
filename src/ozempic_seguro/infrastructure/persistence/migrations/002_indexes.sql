-- Migração 002: índices para as consultas de histórico e auditoria

CREATE INDEX IF NOT EXISTS idx_historico_gavetas_gaveta ON historico_gavetas (gaveta_id, data_hora);
CREATE INDEX IF NOT EXISTS idx_historico_gavetas_data ON historico_gavetas (data_hora);
CREATE INDEX IF NOT EXISTS idx_auditoria_data ON auditoria (data_hora);
CREATE INDEX IF NOT EXISTS idx_auditoria_acao ON auditoria (acao, data_hora);
