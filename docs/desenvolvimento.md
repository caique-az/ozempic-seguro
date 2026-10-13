# Desenvolvimento

## Comandos

```bash
pip install -e ".[dev]"     # projeto + ferramentas de desenvolvimento

pytest                      # testes com cobertura (mínimo de 95%)
pytest tests/application    # uma camada
pytest tests/application/test_auth.py::TestLogin::test_locks_after_max_attempts   # um teste
pytest --no-cov -m "not ui" # sem cobertura e sem os testes que abrem janelas

ruff format .               # formata
ruff check .                # lint
mypy                        # tipos (modo strict)
pre-commit install          # roda ruff e mypy a cada commit

mkdocs serve                # documentação em http://127.0.0.1:8000 (requer .[docs])
```

## Testes

Os testes espelham as camadas:

| Pasta | O que cobre | Como |
|---|---|---|
| `tests/domain/` | Regras puras | Sem dependências |
| `tests/application/` | Casos de uso | *Fakes* em memória para os ports e um relógio controlável (`conftest.py`) |
| `tests/infrastructure/` | SQLite, migrações, configuração, bcrypt | Banco real em diretório temporário |
| `tests/test_bootstrap.py` | Todas as camadas juntas | Implementações reais, de ponta a ponta |
| `tests/presentation/` | Conversões da interface e *smoke test* das telas | O *smoke test* abre a janela de verdade e é pulado onde não há display |

Algumas convenções:

- Regras de tempo (bloqueio, expiração) são testadas avançando o `FakeClock`, nunca com `sleep`.
- Cada bug corrigido ganha um teste de regressão, com um comentário explicando o problema original.
- Warnings fazem o teste falhar (`filterwarnings = error`), o que pega, por exemplo, conexões não fechadas.

### Cobertura

A cobertura (com branches) mede domínio, aplicação e infraestrutura, com mínimo de 95%. A interface fica fora do cálculo porque o *smoke test* só roda onde existe display: no CI, ele roda no Windows e é pulado no Linux.

## Qualidade de código

- **Ruff** formata e faz o lint (inclui ordenação de imports, regras de pytest, pathlib e proibição de `print`).
- **mypy** roda em modo strict no pacote inteiro. A única concessão é na interface, que herda de widgets do CustomTkinter sem tipagem.
- O **CI** (`.github/workflows/ci.yml`) roda lint e tipos no Ubuntu e os testes no Ubuntu e no Windows.
- A **documentação** é publicada no GitHub Pages por `.github/workflows/docs.yml` a cada push na `main`.

## Convenções

- Código, identificadores e comentários em inglês; textos da interface e mensagens de erro para o usuário em português.
- Nomes de tabelas e colunas do banco em português (herdados do schema original), traduzidos nos repositórios.
- Novas regras de negócio entram no domínio ou na aplicação, nunca nas telas.
- Commits seguem o [Conventional Commits](https://www.conventionalcommits.org/pt-br/), por exemplo `feat(application): ...` ou `fix(infrastructure): ...`.

## Adicionando uma funcionalidade

Um roteiro típico, de dentro para fora:

1. **Domínio**: modele a regra e, se precisar de algo externo, declare um *port* em `ports.py`.
2. **Aplicação**: crie o caso de uso, verifique permissões com `require(...)` e registre a auditoria.
3. **Infraestrutura**: implemente o *port*; se mudar o schema, adicione uma migração.
4. **Bootstrap**: conecte a implementação em `build_services`.
5. **Apresentação**: crie ou ajuste a tela, chamando o caso de uso dentro de `self.attempt(...)`.
6. **Testes** em cada camada e, se for uma decisão relevante, uma nova ADR.
