# ADR 0002: Desativar usuários em vez de apagá-los

- **Status**: aceita
- **Data**: 2026-10-13

## Contexto

A exclusão de usuários fazia `DELETE FROM usuarios`. As tabelas `auditoria` e `historico_gavetas` referenciam `usuarios` por chave estrangeira, e as chaves estrangeiras estão ativas. Como todo login gera um registro de auditoria, **qualquer usuário que já tivesse entrado no sistema não podia ser excluído**: a operação falhava com erro de integridade.

Mesmo sem a restrição, apagar o usuário deixaria a trilha de auditoria apontando para um registro inexistente, o que contraria o objetivo do sistema.

## Decisão

"Excluir" um usuário passa a significar desativá-lo (`ativo = 0`):

- usuários desativados não conseguem entrar;
- o registro continua existindo, então auditoria e histórico mantêm o nome de quem fez cada ação;
- a lista de usuários mostra o status "Inativo", e as ações ficam indisponíveis.

## Consequências

- A exclusão funciona para qualquer usuário, inclusive os que têm histórico.
- O nome de usuário de um usuário desativado continua reservado e não pode ser reutilizado.
- A regra de manter um administrador ativo passa a contar apenas usuários ativos.
- Uma futura opção de reativação é simples: basta voltar `ativo` para 1.
