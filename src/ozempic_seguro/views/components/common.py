"""
Componentes comuns: Header, ImageCache, MainButton
"""

import customtkinter
from PIL import Image

from ...paths import ASSETS_DIR


class ImageCache:
    """Cache de imagens para evitar recarregamento"""

    _logo_img = None
    _digital_img = None

    @staticmethod
    def get_logo():
        if ImageCache._logo_img is None:
            logo_path = ASSETS_DIR / "logo.jpg"
            imagem = Image.open(logo_path)
            ImageCache._logo_img = customtkinter.CTkImage(imagem, size=(60, 60))
        return ImageCache._logo_img

    @staticmethod
    def get_digital():
        if ImageCache._digital_img is None:
            digital_path = ASSETS_DIR / "digital.png"
            imagem = Image.open(digital_path)
            ImageCache._digital_img = customtkinter.CTkImage(imagem, size=(70, 70))
        return ImageCache._digital_img


class Header(customtkinter.CTkFrame):
    """Componente de cabeçalho reutilizável"""

    def __init__(self, master, title, *args, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=0, height=80, *args, **kwargs)
        self.pack(fill="x", side="top")

        customtkinter.CTkLabel(
            self, text=title, font=("Arial", 24, "bold"), text_color="black"
        ).pack(side="left", padx=20, pady=20)

        logo_img = ImageCache.get_logo()
        customtkinter.CTkLabel(self, image=logo_img, text="", bg_color="white").pack(
            side="right", padx=20
        )


class MainButton(customtkinter.CTkButton):
    """Componente de botão principal reutilizável"""

    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            font=("Arial", 16, "bold"),
            width=220,
            height=60,
            fg_color="white",
            text_color="black",
            hover_color="#e0e0e0",
            command=command,
            **kwargs,
        )
