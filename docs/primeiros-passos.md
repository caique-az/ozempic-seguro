# Primeiros passos

## Requisitos

- Python 3.13 com Tkinter (já incluído no instalador oficial do Windows e do macOS; no Linux, instale o pacote `python3-tk`)
- Git

## Instalação

```bash
git clone https://github.com/caique-az/ozempic-seguro.git
cd ozempic-seguro
python -m venv .venv
```

Ative o ambiente virtual:

=== "Windows"

    ```powershell
    .venv\Scripts\activate
    ```

=== "Linux / macOS"

    ```bash
    source .venv/bin/activate
    ```

Instale o projeto com as ferramentas de desenvolvimento:

```bash
pip install -e ".[dev]"
```

## Configuração

Copie o arquivo de exemplo e defina as senhas iniciais:

```bash
cp .env.example .env
```

O `.env` é lido na inicialização. Variáveis definidas no ambiente têm prioridade sobre ele.

| Variável | Descrição | Padrão |
|---|---|---|
| `OZEMPIC_ADMIN_USERNAME` | Usuário do administrador criado na primeira execução | `00` |
| `OZEMPIC_ADMIN_PASSWORD` | Senha desse administrador | senha de fallback, com aviso no log |
| `OZEMPIC_TECNICO_USERNAME` | Usuário do técnico criado na primeira execução | `01` |
| `OZEMPIC_TECNICO_PASSWORD` | Senha desse técnico | senha de fallback, com aviso no log |
| `OZEMPIC_SESSION_TIMEOUT` | Minutos sem uso até a sessão expirar | `10` |
| `OZEMPIC_MAX_LOGIN_ATTEMPTS` | Tentativas de login antes do bloqueio | `3` |
| `OZEMPIC_LOCKOUT_DURATION` | Minutos de bloqueio após exceder as tentativas | `5` |
| `OZEMPIC_DRAWER_LOCK_MINUTES` | Minutos de bloqueio do sistema após abrir uma gaveta | `5` |
| `OZEMPIC_BCRYPT_ROUNDS` | Custo do bcrypt (entre 10 e 16) | `12` |
| `OZEMPIC_DB_PATH` | Caminho do arquivo SQLite | `src/ozempic_seguro/data/ozempic_seguro.db` |
| `OZEMPIC_ENV` | `development` ativa logs detalhados no console | `production` |

!!! warning "Senhas iniciais"
    Os usuários padrão só são criados quando ainda não existem. Se nenhuma senha for configurada, o sistema usa uma senha de fallback documentada e registra um aviso no log. Defina as senhas no `.env` antes de usar o equipamento em produção.

Valores inválidos (por exemplo, texto em um campo numérico) impedem a inicialização com uma mensagem explicando qual variável corrigir.

## Executando

```bash
python -m ozempic_seguro
```

Também funcionam `python run.py` (direto do código-fonte) e o comando `ozempic-seguro`, instalado junto com o pacote.

Na tela inicial, toque em qualquer ponto, escolha **Iniciar Sessão** e entre com um dos usuários configurados.

## Manutenção do banco

O script `scripts/manage_db.py` usa a mesma configuração da aplicação:

```bash
python scripts/manage_db.py reset                 # apaga o banco e recria com os usuários padrão
python scripts/manage_db.py reset-admin-password  # reaplica OZEMPIC_ADMIN_PASSWORD ao administrador
```

O comando `reset` pede confirmação, porque apaga todos os dados, inclusive a auditoria.

## Logs

Os logs de diagnóstico ficam em `logs/app.log`, com rotação a cada 10 MB (5 arquivos). Eles não substituem a auditoria, que fica no banco de dados.
