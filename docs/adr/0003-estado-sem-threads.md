# ADR 0003: Estado de sessão sem threads, com relógio injetado

- **Status**: aceita
- **Data**: 2026-10-13

## Contexto

A expiração da sessão usava um `threading.Timer`, que rodava em outra thread e alterava o estado da sessão. Havia três problemas:

- o Tkinter não é thread-safe, e a interface não reagia à expiração: a sessão era limpa, mas a tela continuava aberta;
- a atividade do usuário nunca era registrada, então o "timeout por inatividade" contava a partir do login;
- testar regras de tempo exigia esperar ou fazer *patch* de `datetime` em vários módulos.

## Decisão

- `Session`, `LoginThrottle` e `SystemLock` guardam apenas instantes e recebem um `Clock` (port do domínio).
- Nenhum componente cria threads. A janela verifica a expiração a cada 15 segundos com `after()` do Tkinter, e qualquer toque na tela registra atividade.
- Os testes usam um `FakeClock` e avançam o tempo explicitamente.

## Consequências

- A expiração por inatividade funciona de ponta a ponta: o evento é auditado e a tela volta ao início.
- As regras de bloqueio e expiração são testadas de forma determinística e rápida.
- A expiração é detectada com até 15 segundos de atraso, o que é aceitável para um timeout de minutos.
- O estado continua em memória: reiniciar a aplicação libera bloqueios de login e reativa o timer. Persistir esse estado seria uma decisão futura, se necessário.
