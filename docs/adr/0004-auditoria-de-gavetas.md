# ADR 0004: Registrar aberturas e fechamentos de gavetas na auditoria

- **Status**: aceita
- **Data**: 2026-10-13

## Contexto

Aberturas e fechamentos de gavetas eram gravados apenas em `historico_gavetas`. A auditoria, que é a tela usada para investigar o que aconteceu, registrava logins e alterações de usuários, mas não o evento mais sensível do sistema: o acesso aos medicamentos.

Além disso, ligar e desligar o timer de bloqueio, que afeta diretamente esse controle, não deixava rastro.

## Decisão

Os casos de uso registram na auditoria:

- `ABRIR_GAVETA` e `FECHAR_GAVETA`, com o número da gaveta como alvo;
- `TIMER_ATIVADO`, `TIMER_DESATIVADO` e `BLOQUEIO_REMOVIDO`;
- `LOGOUT` e `SESSION_EXPIRED`, que existiam no código mas nunca eram gravados.

O histórico de gavetas continua existindo, porque atende a uma consulta diferente (o que aconteceu com uma gaveta específica).

## Consequências

- Uma única tela responde "quem fez o quê, e quando" para todas as ações sensíveis.
- A informação de abertura fica duplicada entre `historico_gavetas` e `auditoria`. A duplicação é intencional: cada tabela atende a uma consulta e pode evoluir separadamente.
- O filtro da auditoria passa a listar os eventos a partir do próprio enum `AuditAction`; antes, as opções "LOGIN" e "ATUALIZAR" não correspondiam a nenhum código gravado e nunca retornavam resultados.
