# Changelog

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e as versões seguem o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.0] - não lançada

Reescrita da arquitetura em camadas (veja a [ADR 0001](adr/0001-arquitetura-em-camadas.md)).

### Alterado

- Código organizado em `domain`, `application`, `infrastructure` e `presentation`, com dependências injetadas por `bootstrap.build_services()` no lugar do `ServiceFactory` e dos singletons.
- Permissões verificadas nos casos de uso, e não mais apenas na tela.
- Regra de senha unificada: só números, de 4 a 8 dígitos, no cadastro e na troca de senha.
- Excluir um usuário passa a desativá-lo ([ADR 0002](adr/0002-desativar-usuarios.md)).
- Configuração lida de fato das variáveis `OZEMPIC_*` e do arquivo `.env`, com validação na inicialização.
- Gavetas numeradas de 1001 a 1015.
- Tela de controle do timer disponível também para administradores, com opção de remover um bloqueio ativo.
- A aplicação pode ser iniciada com `python -m ozempic_seguro`.
- Ruff como formatador e linter, mypy em modo strict e cobertura mínima de 95% nas camadas de lógica.
- Documentação publicada com MkDocs Material.

### Adicionado

- Auditoria de aberturas e fechamentos de gavetas e de mudanças no timer ([ADR 0004](adr/0004-auditoria-de-gavetas.md)).
- Botão de histórico em cada gaveta.
- Migração `002` com índices para histórico e auditoria.
- Variáveis `OZEMPIC_DB_PATH` e `OZEMPIC_DRAWER_LOCK_MINUTES`.

### Corrigido

- Cada senha incorreta contava como duas tentativas, bloqueando a conta na segunda tentativa em vez da terceira.
- Usuários que já tinham feito login não podiam ser excluídos (erro de chave estrangeira).
- Logout e expiração de sessão nunca eram registrados na auditoria.
- A atividade do usuário não era registrada, então a sessão expirava contando a partir do login; ao expirar, a tela continuava aberta.
- Os filtros "LOGIN" e "ATUALIZAR" da auditoria nunca retornavam resultados, e a estação de origem não era exibida.
- O histórico de uma gaveta era inacessível pela interface e, quando exibido, trocava as colunas de ação e data.
- A tela do timer descrevia um bloqueio por inatividade, mas controla o bloqueio após a abertura de gavetas.
- A conexão com o banco ficava aberta quando uma migração falhava.
- As imagens da interface não eram versionadas no repositório.
- Os scripts de manutenção do banco estavam quebrados e duplicavam o schema; foram substituídos por `scripts/manage_db.py`.
- 39 testes quebrados pela tradução dos identificadores, 15 testes que nunca rodavam por classes duplicadas e dois scripts que alteravam o banco real durante os testes.

### Removido

- Módulos sem uso: cache em memória, logger estruturado, gerenciador de temas, wrapper `DatabaseManager`, telas inalcançáveis.

## [1.3.4] - 2026-01-03

- Refatoração de linting e tipagem; `BaseUserFrame`.

## [1.3.3] - 2025-12-18

- Ampliação dos testes automatizados.

## [1.3.2] - 2025-12-11

- Repositórios separados e `DatabaseConnection`.

## [1.3.1] - 2025-12-09

- Componentes de interface modulares e logging estruturado.

## [1.3.0] - 2025-09-16

- Testes automatizados com pytest.

## [1.2.0] - 2025-08-30

- Migração para bcrypt e proteção contra força bruta.

## [1.1.0] - 2025-06-25

- Camada de services e injeção de dependências.

## [1.0.0] - 2024-05-30

- Versão inicial.
