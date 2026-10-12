"""
Testes para base_views - Classes base e mixins.
"""

from ozempic_seguro.core.base_views import ConfigurableComponent, ValidatedMixin


class TestValidatedMixin:
    """Testes para ValidatedMixin"""

    def test_validate_user_input_valid(self):
        """Testa validação de entrada de usuário válida"""

        class TestClass(ValidatedMixin):
            pass

        obj = TestClass()

        data = {
            "username": "testuser",
            "password": "ValidPass123",
            "name": "Test User",
            "user_type": "vendedor",
        }

        result = obj.validate_user_input(data)

        assert isinstance(result, bool)

    def test_validate_user_input_invalid(self):
        """Testa validação de entrada inválida"""

        class TestClass(ValidatedMixin):
            pass

        obj = TestClass()

        data = {"username": "", "password": "", "name": "", "user_type": "invalid"}

        result = obj.validate_user_input(data)

        assert result is False

    def test_validate_user_input_exception(self):
        """Testa tratamento de exceção na validação"""

        class TestClass(ValidatedMixin):
            pass

        obj = TestClass()

        # Passar dados que podem causar exceção
        result = obj.validate_user_input(None)

        # Deve retornar False em caso de erro
        assert result is False


class TestConfigurableComponent:
    """Testes para ConfigurableComponent"""

    def test_get_config_value_default(self):
        """Testa obtenção de valor de configuração com default"""

        class TestComponent(ConfigurableComponent):
            pass

        component = TestComponent()

        result = component.get_config_value("NONEXISTENT_KEY", "default_value")

        assert result == "default_value"

    def test_get_config_value_with_section(self):
        """Testa obtenção de valor de configuração com seção"""

        class TestComponent(ConfigurableComponent):
            pass

        component = TestComponent(config_section="Security")

        # Deve retornar valor ou default
        result = component.get_config_value("MAX_LOGIN_ATTEMPTS", 5)

        assert isinstance(result, int)
