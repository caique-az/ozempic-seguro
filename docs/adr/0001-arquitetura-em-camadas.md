# ADR 0001: Arquitetura em camadas com composition root

- **Status**: aceita
- **Data**: 2026-10-13

## Contexto

A versão 1.x seguia um MVC com services e repositories, mas na prática:

- as regras de permissão das gavetas ficavam no widget da gaveta; chamar o service diretamente permitia que qualquer perfil abrisse ou fechasse gavetas;
- as dependências eram obtidas por um *service locator* (`ServiceFactory`) e por vários singletons (`DatabaseConnection`, `SessionManager`, `GavetaService`), o que obrigava os testes a reiniciar estado global a cada execução;
- a regra de senha existia em três lugares com limites diferentes;
- havia módulos sem uso (cache, logger estruturado, gerenciador de temas) e um wrapper obsoleto (`DatabaseManager`).

## Decisão

Organizar o código em quatro camadas com dependências apontando para dentro:

- `domain`: regras puras e interfaces (`Protocol`) para tudo que é externo;
- `application`: casos de uso que recebem as dependências pelo construtor;
- `infrastructure`: implementações das interfaces (SQLite, bcrypt, relógio, configuração);
- `presentation`: telas que chamam os casos de uso e exibem o resultado.

Um único módulo, `bootstrap.py`, cria as implementações e monta os casos de uso. Não há singletons nem *service locator*.

## Consequências

- Permissões e políticas são verificadas nos casos de uso, independentemente da interface que os chama.
- Os casos de uso são testados com implementações em memória, sem banco e sem bcrypt, em menos de um segundo.
- Trocar o SQLite ou integrar o hardware das gavetas exige apenas uma nova implementação de *port* e uma linha no `bootstrap.py`.
- Há mais arquivos e alguma cerimônia (*ports*, DTOs) do que no MVC anterior. Para um sistema que controla acesso a medicamentos, a clareza sobre onde cada regra vive compensa o custo.
- As camadas internas passam no mypy em modo strict; a interface tem uma concessão por herdar de widgets sem tipagem.
