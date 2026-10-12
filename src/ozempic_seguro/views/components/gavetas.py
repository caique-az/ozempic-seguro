"""
Drawer components: GavetaButton, GavetaButtonGrid
"""

from tkinter import messagebox

import customtkinter
from PIL import Image

from ...paths import ASSETS_DIR
from ...services.auth_service import get_auth_service
from ...services.gaveta_service import GavetaService
from ...services.timer_control_service import get_timer_control_service


# Global cache for drawer images
class _GavetaImageCache:
    _gaveta_aberta = None
    _gaveta_fechada = None

    @classmethod
    def get_gaveta_aberta(cls):
        if cls._gaveta_aberta is None:
            cls._gaveta_aberta = customtkinter.CTkImage(
                Image.open(ASSETS_DIR / "gaveta.png"), size=(120, 120)
            )
        return cls._gaveta_aberta

    @classmethod
    def get_gaveta_fechada(cls):
        if cls._gaveta_fechada is None:
            cls._gaveta_fechada = customtkinter.CTkImage(
                Image.open(ASSETS_DIR / "gaveta_black.png"),
                size=(120, 120),
            )
        return cls._gaveta_fechada


class GavetaButton:
    """Drawer button component for the grid"""

    def __init__(self, master, text, command=None, name=None, user_type=None):
        self.frame = customtkinter.CTkFrame(master, fg_color="transparent")
        self.frame.pack(expand=True, fill="both")

        self._gaveta_service = GavetaService.get_instance()
        self.timer_service = get_timer_control_service()
        self.auth_service = get_auth_service()
        self.user_type = user_type

        # Use image cache (much faster)
        self.gaveta_aberta = _GavetaImageCache.get_gaveta_aberta()
        self.gaveta_fechada = _GavetaImageCache.get_gaveta_fechada()

        self.btn_gaveta = customtkinter.CTkButton(
            self.frame,
            text="",
            width=120,
            height=120,
            image=self.gaveta_fechada,
            fg_color="transparent",
            hover_color="#3B6A7D",
            command=self.handle_state,
        )
        self.btn_gaveta.pack(pady=(0, 5))

        self.label = customtkinter.CTkLabel(
            self.frame, text=text, font=("Arial", 12), text_color="white"
        )
        self.label.pack()

        self.command_original = command
        self.gaveta_id = text
        self.update_image()

    def update_image(self):
        """Updates the button image based on current state"""
        is_open = self._gaveta_service.get_state(int(self.gaveta_id))
        self.btn_gaveta.configure(image=self.gaveta_aberta if is_open else self.gaveta_fechada)

    def handle_state(self):
        """Handles the drawer state based on user type"""
        current_state = self._gaveta_service.get_state(int(self.gaveta_id))

        current_user = self.auth_service.get_current_user()
        user_id = current_user.get("id") if current_user else None

        if self.user_type == "administrador":
            if not current_state:
                self._open_drawer_with_confirmation()
            else:
                success, message = self._gaveta_service.close_drawer(
                    int(self.gaveta_id), self.user_type, user_id
                )
                messagebox.showinfo("Sucesso" if success else "Aviso", message)
                if success:
                    self.update_image()

        elif self.user_type == "vendedor":
            if not current_state:
                self._open_drawer_with_confirmation()
            else:
                messagebox.showwarning("Aviso", "Você não tem permissão para fechar gavetas")

        elif self.user_type == "repositor":
            if current_state:
                success, message = self._gaveta_service.close_drawer(
                    int(self.gaveta_id), self.user_type, user_id
                )
                messagebox.showinfo("Sucesso" if success else "Aviso", message)
                if success:
                    self.update_image()
            else:
                messagebox.showwarning("Aviso", "Você não tem permissão para abrir gavetas")
        else:
            messagebox.showerror("Erro", "Tipo de usuário desconhecido")

    def _open_drawer_with_confirmation(self):
        """Shows confirmation window before opening the drawer"""
        if not self.timer_service.is_timer_enabled():
            current_user = self.auth_service.get_current_user()
            user_id = current_user.get("id") if current_user else None
            success, message = self._gaveta_service.open_drawer(
                int(self.gaveta_id), self.user_type, user_id
            )
            messagebox.showinfo("Sucesso" if success else "Aviso", message)
            if success:
                self.update_image()
            return

        dialog = customtkinter.CTkToplevel()
        dialog.title("Confirmar Abertura")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (125)
        dialog.geometry(f"+{x}+{y}")

        main_frame = customtkinter.CTkFrame(dialog, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        customtkinter.CTkLabel(
            main_frame, text="Confirmar Abertura", font=("Arial", 16, "bold"), text_color="black"
        ).pack(pady=(10, 5))

        if self.user_type == "vendedor":
            mensagem = (
                f"Deseja realmente abrir a gaveta {self.gaveta_id}?\n\n"
                "O sistema será bloqueado por 5 minutos após a abertura.\n"
                "Você terá acesso somente para visualizar os dados."
            )
        else:
            mensagem = (
                f"Deseja realmente abrir a gaveta {self.gaveta_id}?\n\n"
                "O sistema será bloqueado por 5 minutos após a abertura."
            )

        customtkinter.CTkLabel(
            main_frame,
            text=mensagem,
            font=("Arial", 12),
            text_color="black",
            wraplength=400,
            justify="center",
        ).pack(pady=10, padx=20)

        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        customtkinter.CTkButton(
            button_frame,
            text="Confirmar",
            font=("Arial", 12, "bold"),
            width=120,
            command=lambda: self._on_confirm_opening(dialog),
        ).pack(side="left", padx=10)

        customtkinter.CTkButton(
            button_frame,
            text="Cancelar",
            font=("Arial", 12),
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=120,
            command=dialog.destroy,
        ).pack(side="right", padx=10)

        dialog.transient(self.frame.winfo_toplevel())
        dialog.wait_window(dialog)

    def _on_confirm_opening(self, dialog):
        """Confirms the drawer opening"""
        dialog.destroy()
        current_user = self.auth_service.get_current_user()
        user_id = current_user.get("id") if current_user else None

        success, message = self._gaveta_service.open_drawer(
            int(self.gaveta_id), self.user_type, user_id
        )
        messagebox.showinfo("Sucesso" if success else "Aviso", message)
        if success:
            self.update_image()

    def show_history(self):
        """Shows the drawer change history with pagination"""
        self.items_per_page = 20
        self.current_page = 1

        self.history_window = customtkinter.CTkToplevel()
        self.history_window.title(f"Histórico - Gaveta {self.gaveta_id}")
        self.history_window.geometry("600x400")

        main_frame = customtkinter.CTkFrame(self.history_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        customtkinter.CTkLabel(
            main_frame, text=f"Histórico - Gaveta {self.gaveta_id}", font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))

        self.history_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent")
        self.history_frame.pack(fill="both", expand=True)

        controls_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(5, 0))

        self.btn_previous = customtkinter.CTkButton(
            controls_frame, text="Anterior", command=self._previous_page, state="disabled"
        )
        self.btn_previous.pack(side="left", padx=5)

        self.lbl_page = customtkinter.CTkLabel(controls_frame, text="Página 1", width=100)
        self.lbl_page.pack(side="left")

        self.btn_next = customtkinter.CTkButton(
            controls_frame, text="Próximo", command=self._next_page
        )
        self.btn_next.pack(side="left", padx=5)

        customtkinter.CTkButton(
            controls_frame, text="Fechar", command=self.history_window.destroy
        ).pack(side="right")

        self._load_history()

    def _load_history(self):
        """Loads history items for the current page using GavetaService"""
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        offset = (self.current_page - 1) * self.items_per_page
        history_raw = self._gaveta_service.get_history_paginated(
            int(self.gaveta_id), offset, self.items_per_page
        )
        total = self._gaveta_service.count_history(int(self.gaveta_id))
        total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)

        self.lbl_page.configure(text=f"Página {self.current_page} de {total_pages}")
        self.btn_previous.configure(state="disabled" if self.current_page == 1 else "normal")
        self.btn_next.configure(state="disabled" if self.current_page >= total_pages else "normal")

        if not history_raw:
            customtkinter.CTkLabel(
                self.history_frame,
                text="Nenhum registro de histórico para esta gaveta.",
                text_color="gray",
            ).pack(pady=10)
            return

        for h in history_raw:
            acao = h[2] if len(h) > 2 else ""
            acao_texto = {"aberta": "Abriu", "fechada": "Fechou"}.get(
                acao.lower(), acao.capitalize()
            )
            usuario = h[3] if len(h) > 3 else ""
            data_hora = h[0] if h else ""

            frame_item = customtkinter.CTkFrame(
                self.history_frame, fg_color="#f0f0f0", corner_radius=5
            )
            frame_item.pack(fill="x", pady=2, padx=2)

            customtkinter.CTkLabel(
                frame_item,
                text=f"{data_hora} - {acao_texto} por {usuario}",
                anchor="w",
                justify="left",
            ).pack(fill="x", padx=5, pady=5)

    def _next_page(self):
        self.current_page += 1
        self._load_history()

    def _previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_history()


class GavetaButtonGrid(customtkinter.CTkFrame):
    """Button grid component with drawer images"""

    def __init__(self, master, button_data):
        super().__init__(master, fg_color="transparent")
        self.pack(expand=True, fill="both", padx=30, pady=20)

        self.button_data = button_data
        self.current_page = 0
        self.rows = 2
        self.cols = 4
        self.buttons_per_page = self.rows * self.cols
        self.total_pages = max(
            1, (len(self.button_data) + self.buttons_per_page - 1) // self.buttons_per_page
        )

        self.grid_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(expand=True, fill="both")

        self.nav_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=(10, 0))

        for i in range(self.rows):
            self.grid_frame.rowconfigure(i, weight=1)
        for j in range(self.cols):
            self.grid_frame.columnconfigure(j, weight=1)

        self.create_navigation_controls()
        self.show_page(0)

    def create_navigation_controls(self):
        """Creates navigation controls between pages"""
        self.btn_frame = customtkinter.CTkFrame(self.nav_frame, fg_color="transparent")
        self.btn_frame.pack(side="left", anchor="w", padx=10)

        self.btn_previous = customtkinter.CTkButton(
            self.btn_frame,
            text="← Anterior",
            command=self.previous_page,
            width=120,
            state="disabled",
        )
        self.btn_previous.pack(side="left", padx=(0, 5))

        self.btn_next = customtkinter.CTkButton(
            self.btn_frame, text="Próxima →", command=self.next_page, width=120
        )
        self.btn_next.pack(side="left")

        if self.total_pages <= 1:
            self.nav_frame.pack_forget()

    def previous_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)

    def show_page(self, page_num):
        """Shows the specified page"""
        if page_num < 0 or page_num >= self.total_pages:
            return

        self.current_page = page_num

        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        start_idx = page_num * self.buttons_per_page
        end_idx = min(start_idx + self.buttons_per_page, len(self.button_data))

        for i in range(self.rows):
            for j in range(self.cols):
                item_idx = start_idx + (i * self.cols) + j
                if item_idx >= end_idx:
                    break

                cell_frame = customtkinter.CTkFrame(self.grid_frame, fg_color="transparent")
                cell_frame.grid(row=i, column=j, padx=10, pady=10, sticky="nsew")

                if item_idx < end_idx:
                    btn_data = self.button_data[item_idx]
                    GavetaButton(
                        master=cell_frame,
                        text=btn_data["text"],
                        command=btn_data["command"],
                        name=btn_data["name"],
                        user_type=btn_data["user_type"],
                    )

        self.update_navigation_controls()

    def update_navigation_controls(self):
        """Updates the navigation controls state"""
        if hasattr(self, "btn_previous") and hasattr(self, "btn_next"):
            self.btn_previous.configure(state="normal" if self.current_page > 0 else "disabled")
            self.btn_next.configure(
                state="normal" if self.current_page < self.total_pages - 1 else "disabled"
            )
