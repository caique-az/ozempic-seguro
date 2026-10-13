# Arquitetura - Ozempic Seguro

## Visão Geral

Sistema desktop para controle de medicamentos termolábeis usando Python + CustomTkinter.

```
┌─────────────────────────────────────────────────────────────┐
│                        Views (UI)                           │
│  CustomTkinter frames, teclado virtual, componentes        │
├─────────────────────────────────────────────────────────────┤
│                    View Services                            │
│  UserManagementService, UserRegistrationService, etc.      │
├─────────────────────────────────────────────────────────────┤
│                   Domain Services                           │
│  UserService, AuditService, GavetaService, AuthService     │
├─────────────────────────────────────────────────────────────┤
│                    Repositories                             │
│  UserRepository, AuditRepository, GavetaRepository         │
├─────────────────────────────────────────────────────────────┤
│                  Database Connection                        │
│  SQLite + bcrypt + migrations                              │
└─────────────────────────────────────────────────────────────┘
```

## Estrutura de Diretórios

```
src/ozempic_seguro/
├── config.py              # Configurações centralizadas
├── main.py                # Entry point
├── controllers/           # NavigationController
├── core/                  # Utilitários (cache, logger, validators, exceptions)
├── repositories/          # Camada de persistência
│   ├── connection.py      # Singleton de conexão SQLite
│   ├── user_repository.py
│   ├── audit_repository.py
│   └── gaveta_repository.py
├── services/              # Lógica de negócio
│   ├── service_factory.py # DI container
│   ├── user_service.py    # CRUD + autenticação
│   ├── audit_service.py   # Logs de auditoria
│   └── gaveta_service.py  # Controle de gavetas
├── session/               # Gerenciamento de sessão
│   ├── session_manager.py # Singleton de sessão
│   ├── login_attempts.py  # Controle de força bruta
│   └── timer_manager.py   # Timer de bloqueio
└── views/                 # Interface gráfica
    ├── components/        # Componentes reutilizáveis
    ├── pages_adm/         # Telas administrativas
    └── pages_iniciais/    # Telas de usuário
```

## Padrões Utilizados

### 1. Repository Pattern
Separa lógica de persistência da lógica de negócio.

```python
# Repositório cuida apenas de SQL
class UserRepository:
    def create_user(self, username, senha, nome, tipo) -> int
    def authenticate_user(self, username, password) -> Optional[Dict]
    def delete_user(self, user_id) -> bool

# Service cuida de regras de negócio
class UserService:
    def create_user(self, ...) -> Tuple[bool, str]  # Valida, cria, audita
```

### 2. Service Factory (DI Container)
Gerencia instâncias singleton de serviços.

```python
from services.service_factory import ServiceFactory

user_service = ServiceFactory.get_user_service()
audit_service = ServiceFactory.get_audit_service()

# Para testes
ServiceFactory.set_mock_user_service(mock)
```

### 3. View Services (Application Services)
Encapsulam lógica de UI complexa, delegando para Domain Services.

```python
# View Service - usado pelas views
class UserManagementService:
    def get_all_users(self) -> List[UserData]  # Retorna DTOs
    def change_password(self, ...) -> OperationResult

# Domain Service - lógica de negócio pura
class UserService:
    def update_password(self, ...) -> Tuple[bool, str]
```

### 4. Singleton Pattern
Usado em: `DatabaseConnection`, `SessionManager`, `GavetaService`

```python
class SessionManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### 5. DTOs (Data Transfer Objects)
Cada service expõe DTOs para comunicação com views:

| Service | DTOs |
|---------|------|
| `GavetaService` | `DrawerState`, `DrawerHistoryItem`, `PaginatedResult` |
| `AuthService` | `LoginResult`, `UserPanel` (enum) |
| `UserManagementService` | `UserData`, `OperationResult` |
| `UserRegistrationService` | `RegistrationResult` |
| `TimerControlService` | `TimerStatus` |
| `AuditViewService` | `AuditLogItem`, `AuditFilter`, `PaginatedAuditResult` |

```python
from services.gaveta_service import GavetaService, DrawerState, PaginatedResult
from services.auth_service import AuthService, LoginResult
```

## Segurança

### Autenticação
- **bcrypt** (12 rounds) para hash de senhas
- Senhas numéricas de 4-8 dígitos (teclado virtual)
- Bloqueio após 3 tentativas falhas (5 min)

### Sessão
- Timeout de 10 min por inatividade
- Timer de bloqueio após abertura de gaveta (5 min)

### Auditoria
- Todas as ações são logadas com timestamp, IP, user_id
- Logs estruturados em JSON

## Fluxo de Dados

### Login
```
View → UserService.authenticate() → UserRepository.authenticate_user()
                ↓
        SessionManager.set_current_user()
                ↓
        AuditRepository.create_log()
```

### Abertura de Gaveta
```
View → GavetaService.open_drawer() → GavetaRepository.set_state()
                ↓
        SessionManager.block_for_minutes(5)
                ↓
        AuditRepository.create_log()
```

## Exceções Customizadas

Hierarquia em `core/exceptions.py`:

```
OzempicError
├── AuthenticationError
│   ├── InvalidCredentialsError
│   ├── SessionExpiredError
│   └── AccountLockedError
├── UserError
│   ├── UserNotFoundError
│   ├── UserAlreadyExistsError
│   └── LastAdminError
├── ValidationError
│   ├── InvalidUsernameError
│   └── WeakPasswordError
├── DatabaseError
│   ├── ConnectionError
│   └── MigrationError
└── DrawerError
    ├── DrawerNotFoundError
    └── DrawerStateError
```

## Testes

```bash
pytest                           # Todos os testes
pytest --cov=src/ozempic_seguro  # Com cobertura
pytest -m unit                   # Apenas unitários
pytest -m integration            # Apenas integração
```

### Estrutura
- `tests/test_*.py` - Testes unitários e integração
- Fixtures em `conftest.py`
- Mocks via `ServiceFactory.set_mock_*()`

## Configuração

Todas as configurações em `config.py`:

| Classe | Responsabilidade |
|--------|-----------------|
| `SecurityConfig` | bcrypt rounds, timeouts, limites |
| `DatabaseConfig` | SQLite path, pragmas |
| `UIConfig` | Cores, dimensões, fontes |
| `LoggingConfig` | Níveis, rotação |
| `AppConfig` | Versão, diretórios |

## Decisões de Design

### Por que senhas de 4-8 dígitos?
Sistema usa teclado virtual numérico para entrada rápida em ambiente de farmácia.
A segurança é garantida por:
- Bloqueio após 3 tentativas
- Timeout de sessão
- Ambiente 100% offline

### Por que SQLite?
- Aplicação desktop single-user
- Sem necessidade de servidor
- Portabilidade (arquivo único)
- Performance adequada para o caso de uso

### Por que CustomTkinter?
- Interface moderna sem dependências pesadas
- Cross-platform (Windows foco principal)
- Widgets nativos com tema dark/light
