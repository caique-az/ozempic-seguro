"""
Componentes de diálogos e notificações: ModernConfirmDialog, ToastNotification
"""

from typing import ClassVar

import customtkinter

from .buttons import ModernButton


class ModernConfirmDialog:
    """Componente de confirmação visual moderna"""

    ICON_SYMBOLS: ClassVar[dict[str, str]] = {
        "question": "❓",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
        "success": "✅",
    }

    def __init__(
        self,
        parent,
        title,
        message,
        icon="question",
        confirm_text="Confirmar",
        cancel_text="Cancelar",
    ):
        self.result = None
        self.parent = parent

        # Criar janela modal
        self.dialog = customtkinter.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._center_window()
        self._create_content(title, message, icon, confirm_text, cancel_text)
        self.dialog.wait_window()

    def _center_window(self):
        """Centraliza a janela na tela"""
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 250) // 2
        self.dialog.geometry(f"400x250+{x}+{y}")

    def _create_content(self, title, message, icon, confirm_text, cancel_text):
        """Cria o conteúdo da janela"""
        main_frame = customtkinter.CTkFrame(self.dialog, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Ícone
        icon_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        icon_frame.pack(pady=(10, 20))

        customtkinter.CTkLabel(
            icon_frame,
            text=self.ICON_SYMBOLS.get(icon, "❓"),
            font=("Arial", 32),
            text_color="#2E86C1",
        ).pack()

        # Mensagem
        customtkinter.CTkLabel(
            main_frame, text=message, font=("Arial", 14), text_color="black", wraplength=350
        ).pack(pady=(0, 30))

        # Botões
        btn_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack()

        ModernButton(
            btn_frame, text=cancel_text, command=self._cancel, style="secondary", width=120
        ).pack(side="left", padx=(0, 10))

        ModernButton(
            btn_frame, text=confirm_text, command=self._confirm, style="primary", width=120
        ).pack(side="left")

    def _confirm(self):
        self.result = True
        self.dialog.destroy()

    def _cancel(self):
        self.result = False
        self.dialog.destroy()

    @staticmethod
    def ask(parent, title, message, **kwargs):
        """Mostra diálogo e retorna True/False"""
        dialog = ModernConfirmDialog(parent, title, message, **kwargs)
        return dialog.result


class ToastNotification:
    """Componente de notificação toast com animação"""

    COLORS: ClassVar[dict[str, str]] = {
        "info": "#2E86C1",
        "success": "#28A745",
        "warning": "#FFC107",
        "error": "#DC3545",
    }

    ICONS: ClassVar[dict[str, str]] = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}

    def __init__(self, parent, message, type="info", duration=3000):
        self.parent = parent
        self.duration = duration
        self._destroyed = False

        color = self.COLORS.get(type, "#2E86C1")
        icon = self.ICONS.get(type, "ℹ️")

        # Usar cantos retos para evitar artefatos de transparência
        self.frame = customtkinter.CTkLabel(
            parent,
            text=f"  {icon}  {message}  ",
            font=("Arial", 13, "bold"),
            text_color="white",
            fg_color=color,
            corner_radius=0,
            padx=20,
            pady=12,
        )
        # Começa fora da tela (à direita)
        self.frame.place(relx=1.3, rely=0.02, anchor="ne")

        # Iniciar animação de entrada (slide in)
        self._slide_in()

    def _slide_in(self, current_x=1.3):
        """Animação de entrada - desliza da direita"""
        if self._destroyed:
            return

        target_x = 0.98
        step = 0.04  # Velocidade da animação

        if current_x > target_x:
            current_x -= step
            if current_x < target_x:
                current_x = target_x

            try:
                self.frame.place(relx=current_x, rely=0.02, anchor="ne")
                self.parent.after(15, lambda: self._slide_in(current_x))
            except Exception:
                pass  # Widget pode ter sido destruído
        else:
            # Animação de entrada completa, agendar saída
            self.parent.after(self.duration, self._slide_out)

    def _slide_out(self, current_x=0.98):
        """Animação de saída - desliza para a direita"""
        if self._destroyed:
            return

        target_x = 1.3
        step = 0.04

        if current_x < target_x:
            current_x += step

            try:
                if hasattr(self, "frame") and self.frame.winfo_exists():
                    self.frame.place(relx=current_x, rely=0.02, anchor="ne")
                    self.parent.after(15, lambda: self._slide_out(current_x))
                else:
                    return
            except Exception:
                return  # Widget pode ter sido destruído
        else:
            # Animação completa, destruir
            self.destroy()

    def destroy(self):
        """Destrói o toast"""
        self._destroyed = True
        try:
            if hasattr(self, "frame") and self.frame.winfo_exists():
                self.frame.destroy()
        except Exception:
            pass  # Widget já destruído

    @staticmethod
    def show(parent, message, type="info", duration=3000):
        """Método estático para mostrar notificação"""
        return ToastNotification(parent, message, type, duration)
