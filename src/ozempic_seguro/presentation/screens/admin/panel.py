from typing import Any

from ...navigation import Navigator, ScreenFactory
from ...widgets.buttons import ButtonGrid
from ..base import Screen
from ..diagnostics import DiagnosticsScreen
from ..operator import DrawerScreen
from ..timer_control import TimerControlScreen
from .audit import AuditScreen
from .history import HistoryScreen
from .register_user import RegisterUserScreen
from .users import UsersScreen


class AdminDrawersScreen(DrawerScreen):
    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Administrador - Gerenciar Gavetas")
        self.add_back_button()


class AdminPanelScreen(Screen):
    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Administrador")

        def go(factory: ScreenFactory) -> Any:
            return lambda: nav.show(factory)

        ButtonGrid(
            self,
            [
                ("👥 Gerenciar Usuários", go(lambda p: UsersScreen(p, nav)), "primary"),
                ("🗄️ Gerenciar Gavetas", go(lambda p: AdminDrawersScreen(p, nav)), "primary"),
                ("➕ Cadastro de Usuário", go(lambda p: RegisterUserScreen(p, nav)), "success"),
                ("📋 Registro de Auditoria", go(lambda p: AuditScreen(p, nav)), "secondary"),
                ("📊 Histórico", go(lambda p: HistoryScreen(p, nav)), "secondary"),
                ("⏱️ Controle de Timer", go(lambda p: TimerControlScreen(p, nav)), "secondary"),
                ("🔧 Diagnóstico", go(lambda p: DiagnosticsScreen(p, nav)), "warning"),
            ],
        )
        self.add_end_session_button()
