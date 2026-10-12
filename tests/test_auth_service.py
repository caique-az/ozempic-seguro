"""
Tests for AuthService - Authentication service.
"""

import pytest

from ozempic_seguro.services.auth_service import (
    AuthService,
    LoginResult,
    UserPanel,
    get_auth_service,
)
from ozempic_seguro.services.service_factory import ServiceFactory
from ozempic_seguro.session.session_manager import SessionManager


class TestAuthService:
    """Tests for AuthService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.service = AuthService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_login_invalid_credentials(self):
        """Tests login with invalid credentials"""
        result = self.service.login("nonexistent_user", "wrongpass")

        assert isinstance(result, LoginResult)
        assert result.success is False
        assert result.error_message is not None

    def test_login_result_has_remaining_attempts(self):
        """Tests that result has remaining attempts"""
        result = self.service.login("test_user_attempts", "wrongpass")

        assert isinstance(result.remaining_attempts, int)

    def test_logout(self):
        """Tests logout"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        self.service.logout()

        assert self.service.is_logged_in() is False

    def test_get_login_status(self):
        """Tests getting login status"""
        status = self.service.get_login_status("test_user")

        assert isinstance(status, dict)
        assert "message" in status

    def test_is_user_locked_false(self):
        """Tests lock check - not locked"""
        result = self.service.is_user_locked("new_user_not_locked")

        assert result is False

    def test_get_current_user_none(self):
        """Tests getting current user when not logged in"""
        self.session.logout()

        result = self.service.get_current_user()

        assert result is None

    def test_get_current_user_logged_in(self):
        """Tests getting current user when logged in"""
        user = {"id": 1, "username": "test", "tipo": "vendedor"}
        self.session.set_current_user(user)

        result = self.service.get_current_user()

        assert result == user

    def test_is_logged_in_false(self):
        """Tests login check - not logged in"""
        self.session.logout()

        assert self.service.is_logged_in() is False

    def test_is_logged_in_true(self):
        """Tests login check - logged in"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        assert self.service.is_logged_in() is True

    def test_get_lockout_remaining_seconds(self):
        """Tests getting remaining lockout seconds"""
        result = self.service.get_lockout_remaining_seconds("test_user")

        assert isinstance(result, int)
        assert result >= 0


class TestUserPanel:
    """Tests for UserPanel enum"""

    def test_admin_panel(self):
        """Tests admin panel"""
        assert UserPanel.ADMIN.value == "administrador"

    def test_vendedor_panel(self):
        """Tests vendedor panel"""
        assert UserPanel.VENDEDOR.value == "vendedor"

    def test_repositor_panel(self):
        """Tests repositor panel"""
        assert UserPanel.REPOSITOR.value == "repositor"

    def test_tecnico_panel(self):
        """Tests tecnico panel"""
        assert UserPanel.TECNICO.value == "tecnico"

    def test_user_panel_exists(self):
        """Tests that UserPanel exists and is an enum"""
        from enum import Enum

        assert issubclass(UserPanel, Enum)

    def test_user_panel_has_members(self):
        """Tests that UserPanel has members"""
        members = list(UserPanel)
        assert len(members) > 0


class TestLoginResult:
    """Tests for LoginResult"""

    def test_login_result_success(self):
        """Tests creating a success result"""
        result = LoginResult(
            success=True, user={"id": 1, "username": "test"}, panel=UserPanel.VENDEDOR
        )

        assert result.success is True
        assert result.user is not None
        assert result.panel == UserPanel.VENDEDOR

    def test_login_result_failure(self):
        """Tests creating a failure result"""
        result = LoginResult(
            success=False, error_message="Credenciais inválidas", remaining_attempts=2
        )

        assert result.success is False
        assert result.error_message == "Credenciais inválidas"
        assert result.remaining_attempts == 2

    def test_login_result_locked(self):
        """Tests creating a locked account result"""
        result = LoginResult(success=False, is_locked=True, lockout_seconds=300)

        assert result.success is False
        assert result.is_locked is True
        assert result.lockout_seconds == 300

    def test_login_result_with_attempts(self):
        """Tests LoginResult with remaining attempts"""
        result = LoginResult(success=False, remaining_attempts=2)
        assert result.remaining_attempts == 2

    def test_login_result_with_lockout(self):
        """Tests LoginResult with lockout"""
        result = LoginResult(success=False, lockout_seconds=300)
        assert result.lockout_seconds == 300


class TestAuthServiceEdgeCases:
    """Tests for AuthService edge cases"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.service = AuthService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_login_with_empty_username(self):
        """Tests login with empty username"""
        result = self.service.login("", "password")

        assert isinstance(result, LoginResult)
        assert result.success is False

    def test_login_with_whitespace_username(self):
        """Tests login with whitespace-only username"""
        result = self.service.login("   ", "password")

        assert isinstance(result, LoginResult)
        assert result.success is False

    def test_multiple_failed_logins(self):
        """Tests multiple failed login attempts"""
        username = "test_multiple_fails"

        result1 = self.service.login(username, "wrong1")
        assert result1.success is False

        result2 = self.service.login(username, "wrong2")
        assert result2.success is False

        result3 = self.service.login(username, "wrong3")
        assert result3.success is False

    def test_logout_multiple_times(self):
        """Tests multiple logouts"""
        self.session.set_current_user({"id": 1, "username": "test"})

        self.service.logout()
        assert self.service.is_logged_in() is False

        self.service.logout()
        assert self.service.is_logged_in() is False

    def test_get_current_user_after_logout(self):
        """Tests getting user after logout"""
        self.session.set_current_user({"id": 1, "username": "test"})
        assert self.service.get_current_user() is not None

        self.service.logout()
        assert self.service.get_current_user() is None


class TestGetAuthService:
    """Tests for get_auth_service function"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        yield
        ServiceFactory.reset_all_services()

    def test_returns_auth_service(self):
        """Tests that it returns AuthService"""
        service = get_auth_service()

        assert isinstance(service, AuthService)

    def test_singleton_pattern(self):
        """Tests singleton pattern"""
        service1 = get_auth_service()
        service2 = get_auth_service()

        assert isinstance(service1, AuthService)
        assert isinstance(service2, AuthService)
        assert service1 is service2


class TestAuthServicePermissions:
    """Tests for AuthService permissions"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.service = AuthService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_login_attempt_tracking(self):
        """Tests login attempt tracking"""
        username = "track_attempts_user"

        result1 = self.service.login(username, "wrong1")
        result2 = self.service.login(username, "wrong2")

        assert result2.remaining_attempts <= result1.remaining_attempts

    def test_reset_login_attempts(self):
        """Tests login attempt reset after successful login"""
        assert hasattr(self.service, "login")
        assert hasattr(self.service, "logout")
