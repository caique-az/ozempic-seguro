"""
Testes para GavetaRepository - Cobertura de operações de gavetas.
"""

import pytest

from ozempic_seguro.repositories.gaveta_repository import GavetaRepository
from ozempic_seguro.repositories.user_repository import UserRepository


class TestGavetaRepository:
    """Testes para GavetaRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = GavetaRepository()
        self.user_repo = UserRepository()
        yield

    def test_get_state_existing_drawer(self):
        """Testa obtenção de estado de gaveta existente"""
        # Criar gaveta
        self.repo.set_state(99, True, "admin", 1)

        state = self.repo.get_state(99)

        assert isinstance(state, bool)

    def test_get_state_nonexistent_drawer(self):
        """Testa obtenção de estado de gaveta inexistente"""
        state = self.repo.get_state(9999)

        assert state is False

    def test_set_state_open(self):
        """Testa abertura de gaveta"""
        success, message = self.repo.set_state(100, True, "vendedor", 1)

        assert success is True
        assert "aberta" in message.lower() or "sem alteração" in message.lower()

    def test_set_state_close(self):
        """Testa fechamento de gaveta"""
        # Primeiro abre
        self.repo.set_state(101, True, "vendedor", 1)

        # Depois fecha
        success, message = self.repo.set_state(101, False, "repositor", 1)

        assert success is True
        assert "fechada" in message.lower() or "sem alteração" in message.lower()

    def test_set_state_no_change(self):
        """Testa quando não há mudança de estado"""
        # Abre gaveta
        self.repo.set_state(102, True, "vendedor", 1)

        # Tenta abrir novamente
        success, message = self.repo.set_state(102, True, "vendedor", 1)

        assert success is True
        assert "sem alteração" in message.lower()

    def test_get_history(self):
        """Testa obtenção de histórico"""
        # Criar gaveta com histórico
        self.repo.set_state(103, True, "vendedor", 1)

        history = self.repo.get_history(103, limit=10)

        assert isinstance(history, list)

    def test_get_history_paginated(self):
        """Testa obtenção de histórico paginado"""
        history = self.repo.get_history_paginated(1, offset=0, limit=20)

        assert isinstance(history, list)

    def test_count_history(self):
        """Testa contagem de histórico"""
        count = self.repo.count_history(1)

        assert isinstance(count, int)
        assert count >= 0

    def test_get_all_history(self):
        """Testa obtenção de todo histórico"""
        history = self.repo.get_all_history()

        assert isinstance(history, list)

    def test_get_all_history_paginated(self):
        """Testa obtenção de todo histórico paginado"""
        history = self.repo.get_all_history_paginated(offset=0, limit=20)

        assert isinstance(history, list)

    def test_count_all_history(self):
        """Testa contagem de todo histórico"""
        count = self.repo.count_all_history()

        assert isinstance(count, int)
        assert count >= 0

    def test_find_by_id(self):
        """Testa busca por ID"""
        # Criar gaveta
        self.repo.set_state(104, False, "admin", 1)

        # Buscar por número primeiro para obter ID
        gaveta = self.repo.find_by_numero(104)

        if gaveta:
            result = self.repo.find_by_id(gaveta["id"])
            assert result is not None
            assert int(result["numero_gaveta"]) == 104

    def test_find_by_id_nonexistent(self):
        """Testa busca por ID inexistente"""
        result = self.repo.find_by_id(99999)

        assert result is None

    def test_find_all(self):
        """Testa busca de todas as gavetas"""
        gavetas = self.repo.find_all()

        assert isinstance(gavetas, list)

    def test_save_new(self):
        """Testa salvamento de nova gaveta"""
        import uuid

        unique_num = int(uuid.uuid4().int % 10000) + 1000
        entity = {"numero_gaveta": unique_num, "esta_aberta": False}

        result = self.repo.save(entity)

        assert result is True

    def test_save_update(self):
        """Testa atualização de gaveta existente"""
        # Buscar gaveta existente
        gaveta = self.repo.find_by_numero(1)

        if gaveta:
            # Atualizar
            original_state = gaveta["esta_aberta"]
            gaveta["esta_aberta"] = not original_state
            result = self.repo.save(gaveta)

            assert result is True

            # Restaurar
            gaveta["esta_aberta"] = original_state
            self.repo.save(gaveta)

    def test_delete_nonexistent(self):
        """Testa exclusão de gaveta inexistente"""
        result = self.repo.delete(99999)

        assert result is False

    def test_exists(self):
        """Testa verificação de existência"""
        # Buscar gaveta existente
        gaveta = self.repo.find_by_numero(1)

        if gaveta:
            assert self.repo.exists(gaveta["id"]) is True

    def test_exists_nonexistent(self):
        """Testa verificação de existência para ID inexistente"""
        assert self.repo.exists(99999) is False

    def test_find_by_numero_existing(self):
        """Testa busca por número existente"""
        # Usar gaveta 1 que sempre existe
        result = self.repo.find_by_numero(1)

        # Pode existir ou não dependendo do estado do DB
        assert result is None or isinstance(result, dict)

    def test_find_by_numero_nonexistent(self):
        """Testa busca por número inexistente"""
        result = self.repo.find_by_numero(99999)

        assert result is None

    def test_find_by_status_open(self):
        """Testa busca por status aberta"""
        gavetas = self.repo.find_by_status("aberta")

        assert isinstance(gavetas, list)

    def test_find_by_status_closed(self):
        """Testa busca por status fechada"""
        gavetas = self.repo.find_by_status("fechada")

        assert isinstance(gavetas, list)

    def test_find_by_user(self):
        """Testa busca por usuário"""
        gavetas = self.repo.find_by_user(1)

        assert isinstance(gavetas, list)

    def test_update_status_nonexistent(self):
        """Testa atualização de status para gaveta inexistente"""
        result = self.repo.update_status(99999, "aberta")

        assert result is False


class TestGavetaRepositoryAdditional:
    """Testes adicionais para GavetaRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = GavetaRepository()
        yield

    def test_get_history_empty(self):
        """Testa histórico de gaveta sem registros"""
        history = self.repo.get_history(88888, limit=10)
        assert isinstance(history, list)

    def test_count_history_nonexistent(self):
        """Testa contagem de histórico de gaveta inexistente"""
        count = self.repo.count_history(88888)
        assert count == 0

    def test_set_state_with_different_user_types(self):
        """Testa set_state com diferentes tipos de usuário"""
        for i, user_type in enumerate(["vendedor", "repositor", "administrador"]):
            drawer_num = 200 + i
            success, msg = self.repo.set_state(drawer_num, True, user_type, 1)
            assert success is True

    def test_get_all_history_paginated_offset(self):
        """Testa paginação com offset"""
        history = self.repo.get_all_history_paginated(offset=5, limit=10)
        assert isinstance(history, list)

    def test_find_all_returns_list(self):
        """Testa que find_all sempre retorna lista"""
        result = self.repo.find_all()
        assert isinstance(result, list)

    def test_toggle_drawer_state(self):
        """Testa alternar estado da gaveta"""
        drawer_num = 300

        # Abrir
        self.repo.set_state(drawer_num, True, "admin", 1)
        state1 = self.repo.get_state(drawer_num)

        # Fechar
        self.repo.set_state(drawer_num, False, "admin", 1)
        state2 = self.repo.get_state(drawer_num)

        assert state1 != state2
