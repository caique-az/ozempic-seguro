"""
Módulo de componentes UI - Wrapper para compatibilidade.

Este módulo foi refatorado e dividido em submódulos em views/components/.
Mantido para compatibilidade com código existente.

Use preferencialmente:
    from .components import Header, ModernButton, etc.
ou:
    from .components.buttons import ModernButton
    from .components.dialogs import ToastNotification
"""

# Re-exportar todos os componentes do novo pacote
from .components import (
    FinalizarSessaoButton,
    # Gavetas
    GavetaButton,
    GavetaButtonGrid,
    # Common
    Header,
    ImageCache,
    MainButton,
    # Buttons
    ModernButton,
    # Dialogs
    ModernConfirmDialog,
    ResponsiveButtonGrid,
    # Layouts
    ResponsiveFrame,
    # Keyboard
    TecladoVirtual,
    ToastNotification,
    VoltarButton,
)

__all__ = [
    "FinalizarSessaoButton",
    "GavetaButton",
    "GavetaButtonGrid",
    "Header",
    "ImageCache",
    "MainButton",
    "ModernButton",
    "ModernConfirmDialog",
    "ResponsiveButtonGrid",
    "ResponsiveFrame",
    "TecladoVirtual",
    "ToastNotification",
    "VoltarButton",
]
