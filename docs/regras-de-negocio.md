# Regras de negócio

Esta página descreve o que o sistema garante. Cada regra está implementada nas camadas de domínio ou de aplicação e coberta por testes; a interface apenas reflete o resultado.

## Perfis e permissões

| Permissão | Administrador | Vendedor | Repositor | Técnico |
|---|:-:|:-:|:-:|:-:|
| Abrir gaveta | ✅ | ✅ | | |
| Fechar gaveta | ✅ | | ✅ | |
| Ver histórico de uma gaveta | ✅ | ✅ | ✅ | |
| Ver histórico de todas as gavetas | ✅ | | | |
| Consultar auditoria | ✅ | | | |
| Gerenciar usuários | ✅ | | | |
| Ligar e desligar o timer | ✅ | | | ✅ |
| Remover um bloqueio ativo | ✅ | | | |
| Diagnóstico | ✅ | | | ✅ |

A matriz fica em `domain/permissions.py`, e cada caso de uso a verifica antes de agir. Uma ação negada mostra uma mensagem ao usuário (por exemplo, "Você não tem permissão para fechar gavetas") e não altera nada.

## Credenciais

O equipamento usa um teclado numérico, então as credenciais seguem estas regras:

- **Usuário**: só números, até 8 dígitos, único no sistema.
- **Senha**: só números, de 4 a 8 dígitos.
- **Nome**: obrigatório, até 26 caracteres.

As regras valem no cadastro e na troca de senha. Os usuários padrão criados na primeira execução usam as senhas definidas na configuração.

Senhas são armazenadas apenas como hash bcrypt.

## Login e bloqueio por tentativas

- Usuários desativados não conseguem entrar.
- Cada senha incorreta conta **uma** tentativa. Ao atingir o limite (padrão: 3), o usuário fica bloqueado por um tempo (padrão: 5 minutos).
- Durante o bloqueio, nem a senha correta é aceita, e a tela mostra uma contagem regressiva.
- Um login bem-sucedido zera as tentativas daquele usuário.
- O controle de tentativas fica em memória: reiniciar a aplicação libera os bloqueios.

## Sessão

- A sessão expira após um período sem uso (padrão: 10 minutos). Qualquer toque na tela conta como atividade.
- Quando expira, a tela volta para o início e o evento é registrado na auditoria.
- Ao finalizar a sessão, seja pelo botão "Finalizar sessão" ou por expiração, o timer de gavetas é reativado caso tenha sido desligado.

## Gavetas

- O sistema controla 15 gavetas, numeradas de 1001 a 1015.
- Só é possível abrir uma gaveta fechada e fechar uma gaveta aberta.
- Toda abertura e todo fechamento ficam no histórico da gaveta, com usuário e horário, e também na auditoria.

### Bloqueio após abertura (timer)

Quando um **vendedor ou administrador** abre uma gaveta e o timer está ligado:

1. A interface pede confirmação, informando quanto tempo o sistema ficará bloqueado.
2. Após a abertura, novas aberturas ficam bloqueadas por alguns minutos (padrão: 5).
3. Durante o bloqueio, fechar gavetas continua permitido.

Controle do timer:

- Técnicos e administradores podem desligar o timer, por exemplo durante uma manutenção. Com o timer desligado, as aberturas não bloqueiam o sistema e um bloqueio em andamento fica suspenso.
- Administradores podem remover um bloqueio em andamento.
- O timer volta a ser ligado automaticamente quando a sessão termina.
- O estado do timer fica em memória: ao reiniciar a aplicação, ele volta ligado e sem bloqueio.

## Usuários

- Apenas administradores cadastram usuários, trocam senhas e excluem usuários.
- A troca de senha exige confirmação igual à nova senha.
- **Técnicos são protegidos**: não podem ter a senha trocada nem ser excluídos pelo painel.
- Ninguém pode excluir a própria conta.
- O sistema sempre mantém pelo menos um administrador ativo.
- **Excluir significa desativar**: o usuário deixa de acessar o sistema, mas o registro permanece, porque a auditoria e o histórico das gavetas fazem referência a ele. O nome de usuário continua reservado. Veja a [ADR 0002](adr/0002-desativar-usuarios.md).

## Auditoria

Cada evento é gravado com data e hora, usuário (quando houver), alvo e estação de trabalho.

| Evento | Código gravado | Quando acontece |
|---|---|---|
| Login | `LOGIN_SUCCESS` | Login bem-sucedido |
| Login com falha | `LOGIN_FAILED` | Usuário inexistente, desativado ou senha incorreta |
| Login bloqueado | `LOGIN_BLOCKED` | Tentativa durante o bloqueio por tentativas |
| Logout | `LOGOUT` | Sessão finalizada pelo usuário ou ao fechar o app |
| Sessão expirada | `SESSION_EXPIRED` | Sessão encerrada por inatividade |
| Usuário criado | `CRIAR` | Cadastro de usuário |
| Usuário excluído | `EXCLUIR` | Desativação de usuário |
| Senha alterada | `ATUALIZAR_SENHA` | Troca de senha pelo administrador |
| Gaveta aberta | `ABRIR_GAVETA` | Abertura de gaveta |
| Gaveta fechada | `FECHAR_GAVETA` | Fechamento de gaveta |
| Timer ativado | `TIMER_ATIVADO` | Timer ligado manualmente ou ao fim da sessão |
| Timer desativado | `TIMER_DESATIVADO` | Timer desligado |
| Bloqueio removido | `BLOQUEIO_REMOVIDO` | Administrador remove um bloqueio ativo |

A tela de auditoria filtra por evento e por período (padrão: últimos 7 dias). Registros de versões anteriores com códigos que não existem mais continuam visíveis, com o código original.
