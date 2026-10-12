"""
DatabaseManager - Compatibility wrapper (DEPRECATED).

.. deprecated:: 1.3.2
    This module is kept only for backward compatibility.
    For new development, use directly:
    - DatabaseConnection for connection
    - UserRepository for user operations
    - AuditRepository for audit operations
    - GavetaRepository for drawer operations
"""

import warnings


def _warn(method: str, alt: str) -> None:
    """Emit deprecation warning"""
    warnings.warn(
        f"DatabaseManager.{method}() is deprecated. Use {alt} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


class DatabaseManager:
    """
    Compatibility wrapper for legacy code (DEPRECATED).

    All methods delegate to specific repositories.
    Will be removed in future versions.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize via DatabaseConnection"""
        from .connection import DatabaseConnection

        self._db = DatabaseConnection.get_instance()
        self.conn = self._db.conn
        self.cursor = self._db.cursor

        # Lazy-loaded repositories
        self._user_repo = None
        self._audit_repo = None
        self._gaveta_repo = None

    @property
    def _users(self):
        if self._user_repo is None:
            from .user_repository import UserRepository

            self._user_repo = UserRepository()
        return self._user_repo

    @property
    def _audit(self):
        if self._audit_repo is None:
            from .audit_repository import AuditRepository

            self._audit_repo = AuditRepository()
        return self._audit_repo

    @property
    def _gavetas(self):
        if self._gaveta_repo is None:
            from .gaveta_repository import GavetaRepository

            self._gaveta_repo = GavetaRepository()
        return self._gaveta_repo

    # =========================================================================
    # User methods - delegate to UserRepository
    # =========================================================================

    def criar_usuario(self, username, senha, nome_completo, tipo):
        """DEPRECATED: Use UserRepository.create_user()"""
        _warn("criar_usuario", "UserRepository.create_user()")
        return bool(self._users.create_user(username, senha, nome_completo, tipo))

    def autenticar_usuario(self, username, senha):
        """DEPRECATED: Use UserRepository.authenticate_user()"""
        _warn("autenticar_usuario", "UserRepository.authenticate_user()")
        return self._users.authenticate_user(username, senha)

    def get_usuarios(self):
        """DEPRECATED: Use UserRepository.get_users()"""
        _warn("get_usuarios", "UserRepository.get_users()")
        return self._users.get_users()

    def excluir_usuario(self, usuario_id):
        """DEPRECATED: Use UserRepository.delete_user()"""
        _warn("excluir_usuario", "UserRepository.delete_user()")
        return self._users.delete_user(usuario_id)

    def eh_unico_administrador(self, usuario_id):
        """DEPRECATED: Use UserRepository.is_unique_admin()"""
        _warn("eh_unico_administrador", "UserRepository.is_unique_admin()")
        return self._users.is_unique_admin(usuario_id)

    def atualizar_senha(self, usuario_id, nova_senha):
        """DEPRECATED: Use UserRepository.update_password()"""
        _warn("atualizar_senha", "UserRepository.update_password()")
        return self._users.update_password(usuario_id, nova_senha)

    # =========================================================================
    # Drawer methods - delegate to GavetaRepository
    # =========================================================================

    def get_estado_gaveta(self, numero_gaveta):
        """DEPRECATED: Use GavetaRepository.get_state()"""
        _warn("get_estado_gaveta", "GavetaRepository.get_state()")
        return self._gavetas.get_state(numero_gaveta)

    def set_estado_gaveta(self, numero_gaveta, estado, usuario_tipo, usuario_id=None):
        """DEPRECATED: Use GavetaRepository.set_state()"""
        _warn("set_estado_gaveta", "GavetaRepository.set_state()")
        return self._gavetas.set_state(numero_gaveta, estado, usuario_tipo, usuario_id)

    def get_historico_gaveta(self, numero_gaveta, limite=10):
        """DEPRECATED: Use GavetaRepository.get_history()"""
        _warn("get_historico_gaveta", "GavetaRepository.get_history()")
        return self._gavetas.get_history(numero_gaveta, limite)

    def get_historico_paginado(self, numero_gaveta, offset=0, limit=20):
        """DEPRECATED: Use GavetaRepository.get_history_paginated()"""
        _warn("get_historico_paginado", "GavetaRepository.get_history_paginated()")
        return self._gavetas.get_history_paginated(numero_gaveta, offset, limit)

    def get_total_historico(self, numero_gaveta):
        """DEPRECATED: Use GavetaRepository.count_history()"""
        _warn("get_total_historico", "GavetaRepository.count_history()")
        return self._gavetas.count_history(numero_gaveta)

    def get_todo_historico(self):
        """DEPRECATED: Use GavetaRepository.get_all_history()"""
        _warn("get_todo_historico", "GavetaRepository.get_all_history()")
        return self._gavetas.get_all_history()

    def get_todo_historico_paginado(self, offset=0, limit=20):
        """DEPRECATED: Use GavetaRepository.get_all_history_paginated()"""
        _warn("get_todo_historico_paginado", "GavetaRepository.get_all_history_paginated()")
        return self._gavetas.get_all_history_paginated(offset, limit)

    def get_total_todo_historico(self):
        """DEPRECATED: Use GavetaRepository.count_all_history()"""
        _warn("get_total_todo_historico", "GavetaRepository.count_all_history()")
        return self._gavetas.count_all_history()

    # =========================================================================
    # Audit methods - delegate to AuditRepository
    # =========================================================================

    def registrar_auditoria(
        self,
        usuario_id,
        acao,
        tabela_afetada,
        id_afetado=None,
        dados_anteriores=None,
        dados_novos=None,
        endereco_ip=None,
    ):
        """DEPRECATED: Use AuditRepository.create_log()"""
        _warn("registrar_auditoria", "AuditRepository.create_log()")
        return self._audit.create_log(
            user_id=usuario_id,
            action=acao,
            affected_table=tabela_afetada,
            id_afetado=id_afetado,
            previous_data=dados_anteriores,
            new_data=dados_novos,
            ip_address=endereco_ip,
        )

    def buscar_logs_auditoria(
        self,
        offset=0,
        limit=50,
        filtro_usuario=None,
        filtro_acao=None,
        filtro_tabela=None,
        data_inicio=None,
        data_fim=None,
    ):
        """DEPRECATED: Use AuditRepository.get_logs()"""
        _warn("buscar_logs_auditoria", "AuditRepository.get_logs()")
        return self._audit.get_logs(
            offset=offset,
            limit=limit,
            user_filter=filtro_usuario,
            action_filter=filtro_acao,
            table_filter=filtro_tabela,
            start_date=data_inicio,
            end_date=data_fim,
        )

    def contar_logs_auditoria(
        self,
        filtro_usuario=None,
        filtro_acao=None,
        filtro_tabela=None,
        data_inicio=None,
        data_fim=None,
    ):
        """DEPRECATED: Use AuditRepository.count_logs()"""
        _warn("contar_logs_auditoria", "AuditRepository.count_logs()")
        return self._audit.count_logs(
            user_filter=filtro_usuario,
            action_filter=filtro_acao,
            table_filter=filtro_tabela,
            start_date=data_inicio,
            end_date=data_fim,
        )

    # =========================================================================
    # Utility methods
    # =========================================================================

    def close(self):
        """Close database connection"""
        if hasattr(self, "_db") and self._db:
            self._db.close()

    # =========================================================================
    # English aliases for standardization
    # =========================================================================

    # User methods
    create_user = criar_usuario
    authenticate_user = autenticar_usuario
    update_password = atualizar_senha
    delete_user = excluir_usuario
    get_users = get_usuarios
    is_unique_admin = eh_unico_administrador

    # Drawer methods
    get_drawer_state = get_estado_gaveta
    set_drawer_state = set_estado_gaveta
    get_drawer_history = get_historico_gaveta
    get_drawer_history_paginated = get_historico_paginado
    get_total_drawer_history = get_total_historico
    get_all_history = get_todo_historico
    get_all_history_paginated = get_todo_historico_paginado
    get_total_all_history = get_total_todo_historico

    # Audit methods
    create_audit_log = registrar_auditoria
    search_audit_logs = buscar_logs_auditoria
    count_audit_logs = contar_logs_auditoria
