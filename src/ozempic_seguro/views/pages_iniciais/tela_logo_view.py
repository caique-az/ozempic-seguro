import customtkinter
from PIL import Image

from ...paths import ASSETS_DIR

# Cache de imagem para evitar recarregamento
_logo_img_cache = None


def _get_logo_image():
    global _logo_img_cache
    if _logo_img_cache is None:
        img_path = ASSETS_DIR / "logo.jpg"
        _logo_img_cache = customtkinter.CTkImage(Image.open(img_path), size=(300, 300))
    return _logo_img_cache


class TelaLogoFrame(customtkinter.CTkFrame):
    def __init__(self, master, on_click_callback, *args, **kwargs):
        super().__init__(master, fg_color="white", *args, **kwargs)

        self.on_click = on_click_callback

        self.label = customtkinter.CTkLabel(
            self, text="TOQUE NA TELA PARA COMEÇAR", font=("Arial", 32, "bold"), text_color="black"
        )
        self.label.pack(pady=40)

        # Usar imagem do cache
        self.img = _get_logo_image()
        self.img_label = customtkinter.CTkLabel(self, image=self.img, text="")
        self.img_label.pack(pady=20)

        # Bind para clique
        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)
        self.img_label.bind("<Button-1>", self._on_click)

    def _on_click(self, event=None):
        if self.on_click:
            self.on_click()
