"""Image loading with a process-wide cache (Tk images are expensive to create)."""

from functools import cache

import customtkinter
from PIL import Image

from ..paths import ASSETS_DIR


@cache
def image(name: str, size: int) -> customtkinter.CTkImage:
    with Image.open(ASSETS_DIR / name) as source:
        picture = source.copy()
    return customtkinter.CTkImage(picture, size=(size, size))


def preload() -> None:
    """Load the images used on the first screens before the window is shown.

    Tk images belong to the root window that created them, so the cache is reset
    for every new root.
    """
    image.cache_clear()
    for name, size in [
        ("logo.jpg", 60),
        ("logo.jpg", 300),
        ("dedo.png", 300),
        ("gaveta.png", 120),
        ("gaveta_black.png", 120),
    ]:
        image(name, size)
