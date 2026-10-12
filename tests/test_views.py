"""
Testes para Views com componentes UI mockados.
"""

from unittest.mock import Mock, patch


class TestLoginView:
    """Testes para LoginView - testes básicos de estrutura"""

    def test_login_view_module_imports(self):
        """Testa que o módulo LoginView pode ser importado"""
        from ozempic_seguro.views.login_view import LoginFrame

        assert LoginFrame is not None

    def test_login_view_has_required_methods(self):
        """Testa que LoginView tem os métodos necessários"""
        from ozempic_seguro.views.login_view import LoginFrame

        assert hasattr(LoginFrame, "verify_login")
        assert hasattr(LoginFrame, "create_login_interface")


class TestComponentsView:
    """Testes para componentes de UI"""

    def test_components_module_imports(self):
        """Testa que os componentes podem ser importados"""
        from ozempic_seguro.views.components import (
            ModernButton,
            ResponsiveFrame,
            Header,
        )

        assert ModernButton is not None
        assert ResponsiveFrame is not None
        assert Header is not None

    def test_modern_button_has_styles(self):
        """Testa que ModernButton tem estilos definidos"""
        from ozempic_seguro.views.components import ModernButton

        assert hasattr(ModernButton, "STYLES")

    def test_components_all_exports(self):
        """Testa que __all__ está definido corretamente"""
        from ozempic_seguro.views import components

        assert hasattr(components, "__all__")
        assert "ModernButton" in components.__all__
        assert "ResponsiveFrame" in components.__all__


class TestNavigationController:
    """Testes para NavigationController"""

    @patch("ozempic_seguro.controllers.navigation_controller.customtkinter.CTkFrame")
    @patch("ozempic_seguro.controllers.navigation_controller.TelaToqueFrame")
    @patch("ozempic_seguro.controllers.navigation_controller.TelaLogoFrame")
    def test_navigation_controller_init(self, mock_logo, mock_toque, mock_ctk_frame):
        """Testa inicialização do NavigationController"""
        from ozempic_seguro.controllers.navigation_controller import NavigationController

        app = Mock()
        app.container = Mock()

        controller = NavigationController(app)

        assert controller.app == app
        assert controller.container == app.container
        assert controller.frames == {}
        assert controller.current_frame is None

    @patch("ozempic_seguro.controllers.navigation_controller.customtkinter.CTkFrame")
    def test_show_frame(self, mock_ctk_frame):
        """Testa exibição de frame"""
        from ozempic_seguro.controllers.navigation_controller import NavigationController

        app = Mock()
        app.container = Mock()

        controller = NavigationController(app)

        # Mock frame
        mock_frame = Mock()
        mock_frame.winfo_exists.return_value = True
        controller.frames["test"] = mock_frame

        controller.show_frame("test")

        assert controller.current_frame == mock_frame

    @patch("ozempic_seguro.controllers.navigation_controller.customtkinter.CTkFrame")
    def test_cleanup(self, mock_ctk_frame):
        """Testa cleanup do controller"""
        from ozempic_seguro.controllers.navigation_controller import NavigationController

        app = Mock()
        app.container = Mock()
        app.after_cancel = Mock()

        controller = NavigationController(app)
        controller.after_id = 123

        # Mock frames
        frame1 = Mock()
        frame1.winfo_exists.return_value = True
        frame2 = Mock()
        frame2.winfo_exists.return_value = True

        controller.frames = {"frame1": frame1, "frame2": frame2}

        controller.cleanup()

        assert controller.is_running is False
        app.after_cancel.assert_called_once_with(123)
        frame1.destroy.assert_called_once()
        frame2.destroy.assert_called_once()
        assert len(controller.frames) == 0


class TestAuditService:
    """Testes para AuditService"""

    def test_audit_service_module_imports(self):
        """Testa que o módulo AuditService pode ser importado"""
        from ozempic_seguro.services.audit_service import AuditService

        assert AuditService is not None

    def test_audit_service_has_required_methods(self):
        """Testa que AuditService tem os métodos necessários"""
        from ozempic_seguro.services.audit_service import AuditService

        assert hasattr(AuditService, "create_log")
        assert hasattr(AuditService, "get_logs")
