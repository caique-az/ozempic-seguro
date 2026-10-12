"""
Sistema de temas para a interface do Ozempic Seguro.

Separa as constantes de cores em classes de tema para facilitar
customização e suporte a múltiplos temas no futuro.
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class BaseTheme:
    """Classe base para temas - define a interface de cores"""

    # Cores principais
    PRIMARY_BG: str
    SECONDARY_BG: str
    WHITE: str

    # Cores de status - Sucesso
    SUCCESS: str
    SUCCESS_BG: str
    SUCCESS_TEXT: str

    # Cores de status - Aviso
    WARNING: str
    WARNING_BG: str
    WARNING_TEXT: str

    # Cores de status - Erro
    ERROR: str
    ERROR_BG: str
    ERROR_TEXT: str

    # Cores de status - Info
    INFO: str

    # Cores de texto
    TEXT_PRIMARY: str
    TEXT_SECONDARY: str
    TEXT_LIGHT: str

    # Cores de borda
    BORDER: str
    BORDER_LIGHT: str

    # Cores de login
    LOGIN_FRAME: str

    # Cores de transição
    TRANSITION_OVERLAY: str


@dataclass(frozen=True)
class LightTheme(BaseTheme):
    """Tema claro (padrão)"""

    # Cores principais
    PRIMARY_BG: str = "#3B6A7D"
    SECONDARY_BG: str = "#2C5364"
    WHITE: str = "#FFFFFF"

    # Cores de status - Sucesso
    SUCCESS: str = "#28A745"
    SUCCESS_BG: str = "#E8F5E9"
    SUCCESS_TEXT: str = "#2E7D32"

    # Cores de status - Aviso
    WARNING: str = "#FFC107"
    WARNING_BG: str = "#FFF3CD"
    WARNING_TEXT: str = "#856404"

    # Cores de status - Erro
    ERROR: str = "#DC3545"
    ERROR_BG: str = "#FFEBEE"
    ERROR_TEXT: str = "#C62828"

    # Cores de status - Info
    INFO: str = "#2E86C1"

    # Cores de texto
    TEXT_PRIMARY: str = "#333333"
    TEXT_SECONDARY: str = "#666666"
    TEXT_LIGHT: str = "#999999"

    # Cores de borda
    BORDER: str = "#E0E0E0"
    BORDER_LIGHT: str = "#CCCCCC"

    # Cores de login
    LOGIN_FRAME: str = "#346172"

    # Cores de transição
    TRANSITION_OVERLAY: str = "#3B6A7D"


@dataclass(frozen=True)
class DarkTheme(BaseTheme):
    """Tema escuro (futuro)"""

    # Cores principais
    PRIMARY_BG: str = "#1E1E1E"
    SECONDARY_BG: str = "#2D2D2D"
    WHITE: str = "#FFFFFF"

    # Cores de status - Sucesso
    SUCCESS: str = "#4CAF50"
    SUCCESS_BG: str = "#1B3D1B"
    SUCCESS_TEXT: str = "#81C784"

    # Cores de status - Aviso
    WARNING: str = "#FFB300"
    WARNING_BG: str = "#3D3000"
    WARNING_TEXT: str = "#FFD54F"

    # Cores de status - Erro
    ERROR: str = "#F44336"
    ERROR_BG: str = "#3D1B1B"
    ERROR_TEXT: str = "#E57373"

    # Cores de status - Info
    INFO: str = "#42A5F5"

    # Cores de texto
    TEXT_PRIMARY: str = "#E0E0E0"
    TEXT_SECONDARY: str = "#BDBDBD"
    TEXT_LIGHT: str = "#757575"

    # Cores de borda
    BORDER: str = "#424242"
    BORDER_LIGHT: str = "#616161"

    # Cores de login
    LOGIN_FRAME: str = "#37474F"

    # Cores de transição
    TRANSITION_OVERLAY: str = "#1E1E1E"


class ThemeManager:
    """Gerenciador de temas singleton"""

    _current_theme: ClassVar[BaseTheme] = LightTheme()

    @classmethod
    def get_theme(cls) -> BaseTheme:
        """Retorna o tema atual"""
        return cls._current_theme

    @classmethod
    def set_theme(cls, theme: BaseTheme) -> None:
        """Define o tema atual"""
        cls._current_theme = theme

    @classmethod
    def set_light_theme(cls) -> None:
        """Define tema claro"""
        cls._current_theme = LightTheme()

    @classmethod
    def set_dark_theme(cls) -> None:
        """Define tema escuro"""
        cls._current_theme = DarkTheme()

    @classmethod
    def is_dark_mode(cls) -> bool:
        """Verifica se está em modo escuro"""
        return isinstance(cls._current_theme, DarkTheme)


# Instância padrão para acesso rápido
def get_current_theme() -> BaseTheme:
    """Retorna o tema atual"""
    return ThemeManager.get_theme()


__all__ = [
    "BaseTheme",
    "DarkTheme",
    "LightTheme",
    "ThemeManager",
    "get_current_theme",
]
