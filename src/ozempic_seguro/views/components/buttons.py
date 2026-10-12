"""
Componentes de botões: ModernButton, VoltarButton, FinalizarSessaoButton
"""

from typing import Any, ClassVar

import customtkinter
from PIL import Image

from ...paths import ASSETS_DIR


class ModernButton(customtkinter.CTkButton):
    """Componente de botão moderno com feedback visual aprimorado"""

    # Estilos predefinidos
    STYLES: ClassVar[dict[str, dict[str, Any]]] = {
        "primary": {
            "fg_color": "#2E86C1",
            "hover_color": "#1F618D",
            "text_color": "white",
            "border_color": "#2E86C1",
        },
        "secondary": {
            "fg_color": "white",
            "hover_color": "#F8F9FA",
            "text_color": "black",
            "border_color": "#DEE2E6",
            "border_width": 2,
        },
        "success": {
            "fg_color": "#28A745",
            "hover_color": "#1E7E34",
            "text_color": "white",
            "border_color": "#28A745",
        },
        "danger": {
            "fg_color": "#DC3545",
            "hover_color": "#C82333",
            "text_color": "white",
            "border_color": "#DC3545",
        },
        "warning": {
            "fg_color": "#FFC107",
            "hover_color": "#E0A800",
            "text_color": "black",
            "border_color": "#FFC107",
        },
    }

    def __init__(self, master, text, command=None, style="primary", loading=False, **kwargs):
        # Aplicar estilo selecionado
        selected_style = self.STYLES.get(style, self.STYLES["primary"])

        # Configurações padrão
        defaults = {"font": ("Arial", 14, "bold"), "corner_radius": 8, "height": 45, "width": 200}

        # Mesclar configurações
        config = {**defaults, **selected_style, **kwargs}

        self.original_command = command
        self.is_loading = loading
        self.original_text = text

        super().__init__(master, text=text, command=self._handle_click, **config)

        if loading:
            self.set_loading(True)

    def _handle_click(self):
        if not self.is_loading and self.original_command:
            self.original_command()

    def set_loading(self, loading=True):
        """Ativa/desativa estado de loading"""
        self.is_loading = loading
        if loading:
            self.configure(text="⏳ Processando...", state="disabled")
        else:
            self.configure(text=self.original_text, state="normal")

    def pulse_animation(self, duration=0.3):
        """Animação de pulso para feedback visual"""
        original_color = self.cget("fg_color")
        self.configure(fg_color="#85C1E9")
        self.after(int(duration * 1000), lambda: self.configure(fg_color=original_color))


class VoltarButton:
    """Componente de botão de voltar"""

    def __init__(self, master, command):
        self.frame = customtkinter.CTkFrame(master, fg_color="transparent")
        self.frame.place(relx=0.5, rely=0.88, anchor="center")

        voltar_path = ASSETS_DIR / "botao_voltar.png"

        self.elipse_img = customtkinter.CTkImage(Image.open(voltar_path), size=(40, 40))

        self.btn_voltar = customtkinter.CTkButton(
            self.frame,
            text="",
            width=40,
            height=40,
            image=self.elipse_img,
            fg_color="transparent",
            hover_color="#3B6A7D",
            command=command,
        )
        self.btn_voltar.pack()


class FinalizarSessaoButton:
    """Componente de botão de finalizar sessão"""

    def __init__(self, master, command):
        self.frame = customtkinter.CTkFrame(master, fg_color="transparent")
        self.frame.place(relx=0.5, rely=0.88, anchor="center")

        elipse_path = ASSETS_DIR / "elipse.png"

        self.elipse_img = customtkinter.CTkImage(Image.open(elipse_path), size=(40, 40))

        self.btn_finalizar = customtkinter.CTkButton(
            self.frame,
            text="",
            width=40,
            height=40,
            image=self.elipse_img,
            fg_color="transparent",
            hover_color="#3B6A7D",
            command=command,
        )
        self.btn_finalizar.pack()

        self.label = customtkinter.CTkLabel(
            self.frame,
            text="Finalizar sessão",
            font=("Arial", 12),
            text_color="white",
            fg_color="transparent",
        )
        self.label.pack(pady=(5, 0))
