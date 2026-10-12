import tkinter

import customtkinter

from ...core.logger import logger
from ...services.user_management_service import get_user_management_service
from ..components import Header, ModernButton, ModernConfirmDialog, ToastNotification, VoltarButton


class GerenciamentoUsuariosFrame(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, logged_in_user=None, *args, **kwargs):
        self.back_callback = back_callback
        self.logged_in_user = logged_in_user
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)
        self.management_service = get_user_management_service()
        self.selected_user = None
        self.selected_user_data = None

        # Create overlay to hide construction
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)

        # State control variables
        self.confirming_deletion = False
        self.message_visible = False

        self.create_header()
        self.create_users_table()
        self.create_right_panel()
        self.create_back_button()

        # Remove overlay after everything is ready
        self.update_idletasks()
        self._overlay.destroy()

    def create_header(self):
        # Header
        self.header = Header(self, "Gerenciamento de Usuários")

        # Main frame for content
        self.main_content = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=40, pady=(20, 100))

        # Frame for table and empty area
        self.content_frame = customtkinter.CTkFrame(self.main_content, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Configure grid to divide space
        self.content_frame.columnconfigure(0, weight=1)  # Table column
        self.content_frame.columnconfigure(1, weight=1)  # Right panel column
        self.content_frame.rowconfigure(0, weight=1)  # Single row

    def create_users_table(self):
        # Frame for table
        self.table_frame = customtkinter.CTkFrame(
            self.content_frame,
            fg_color="white",
            corner_radius=15,
        )
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        # Configure table grid
        self.table_frame.columnconfigure(0, weight=1)
        self.table_frame.rowconfigure(1, weight=1)  # Row for scrollable content

        # Headers da tabela
        self.create_table_headers()

        # Frame for scrollable content
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.table_frame, fg_color="white")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scrollable_frame.columnconfigure(0, weight=1)

        # Load initial data
        self.load_data()

    def create_table_headers(self):
        # Frame for headers
        header_frame = customtkinter.CTkFrame(
            self.table_frame,
            fg_color="#e0e0e0",
            corner_radius=8,
            border_width=1,
            border_color="#cccccc",
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Configure headers grid
        for i in range(3):  # 3 columns
            header_frame.columnconfigure(i, weight=1)

        # Headers atualizados
        headers = ["Usuário", "Nome Completo", "Tipo"]

        for col, text in enumerate(headers):
            lbl = customtkinter.CTkLabel(
                header_frame,
                text=text,
                font=("Arial", 13, "bold"),
                text_color="#333333",
                anchor="w",
            )
            lbl.grid(row=0, column=col, padx=15, pady=8, sticky="ew")

    def load_data(self):
        # Clear existing frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            # Get users using management service
            usuarios = self.management_service.get_all_users()

            # Add items
            for idx, user in enumerate(usuarios):
                # Frame for a table row
                row_frame = customtkinter.CTkFrame(
                    self.scrollable_frame,
                    fg_color="#f0f0f0" if idx % 2 == 0 else "#f8f8f8",
                    corner_radius=8,
                    height=50,
                    border_width=1,
                    border_color="#e0e0e0",
                )
                row_frame.grid(row=idx, column=0, sticky="nsew", pady=2, padx=5)
                row_frame.grid_propagate(False)

                # Store user data for click use (using UserData)
                row_frame.user_data = (
                    user.id,
                    user.username,
                    user.full_name,
                    user.user_type,
                    user.active,
                    user.created_at,
                )

                # Frame for row content filling all space
                content_frame = customtkinter.CTkFrame(row_frame, fg_color="transparent")
                content_frame.pack(fill="both", expand=True, padx=10, pady=8)

                # Configure content grid
                for i in range(3):
                    content_frame.columnconfigure(i, weight=1)

                # Data to display (using UserData properties)
                dados = [user.username, user.full_name, user.user_type_display]

                # Add data as labels inside frame
                for col, text in enumerate(dados):
                    # Frame for each cell filling available space
                    cell_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
                    cell_frame.grid(row=0, column=col, sticky="nsew", padx=5)
                    cell_frame.columnconfigure(0, weight=1)

                    # Set font style
                    font_style = ("Arial", 12, "bold") if col == 0 else ("Arial", 12)

                    lbl = customtkinter.CTkLabel(
                        cell_frame,
                        text=str(text),
                        font=font_style,
                        text_color="#333333",
                        anchor="w",
                    )
                    lbl.pack(side="left", fill="x", expand=True, anchor="w")

                    # Configure cell to fill all horizontal space
                    cell_frame.grid_propagate(False)

                # Function to handle click events
                def make_click_handler(data):
                    return lambda e: self.display_user_details(*data)

                # Create click handler
                click_handler = make_click_handler(row_frame.user_data)

                # Add click event only once on main frame
                row_frame.bind("<Button-1>", click_handler)

                # Function to propagate click to child elements
                def propagate_click(widget, handler):
                    widget.bind("<Button-1>", handler)
                    for child in widget.winfo_children():
                        if isinstance(child, customtkinter.CTkFrame | customtkinter.CTkLabel):
                            propagate_click(child, handler)

                # Apply click propagation for internal elements
                propagate_click(content_frame, click_handler)

                # Remove cursor effects only
                for widget in [row_frame, content_frame, *content_frame.winfo_children()]:
                    try:
                        if hasattr(widget, "configure"):
                            widget.configure(cursor="")
                    except Exception:
                        continue

        except Exception as e:
            logger.error(f"Error loading users: {e}")

    def create_right_panel(self):
        # Frame for right panel
        self.right_panel = customtkinter.CTkFrame(
            self.content_frame,
            fg_color="white",
            corner_radius=15,
        )
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        # Configure right panel grid
        self.right_panel.columnconfigure(0, weight=1)

        # Initial instruction label
        self.lbl_instruction = customtkinter.CTkLabel(
            self.right_panel,
            text="Selecione um usuário para visualizar e editar",
            font=("Arial", 14, "bold"),
            text_color="#666666",
            wraplength=300,
        )
        self.lbl_instruction.grid(row=0, column=0, pady=50, padx=20, sticky="n")

        # Frame for user details (initially hidden)
        self.details_frame = customtkinter.CTkFrame(self.right_panel, fg_color="white")

        # Frame for action buttons
        self.buttons_frame = customtkinter.CTkFrame(self.right_panel, fg_color="white")

        # Frame for messages (initially empty)
        self.message_frame = customtkinter.CTkFrame(self.right_panel, fg_color="white")

    def display_user_details(self, user_id, username, full_name, user_type, active, created_at):
        self.selected_user = user_id
        self.selected_user_type = user_type

        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # Configure details frame
        self.details_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Title
        lbl_titulo = customtkinter.CTkLabel(
            self.details_frame,
            text="Detalhes do Usuário",
            font=("Arial", 16, "bold"),
            text_color="#333333",
        )
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")

        # Format creation date
        try:
            if created_at and isinstance(created_at, str):
                formatted_date = created_at.split(" ")[0] if " " in created_at else created_at
            else:
                formatted_date = "N/A"
        except (ValueError, AttributeError, IndexError):
            formatted_date = "N/A"

        # User information
        fields = [
            ("Usuário:", username),
            ("Nome Completo:", full_name),
            ("Tipo:", user_type.capitalize()),
            ("Status:", "Ativo" if active else "Inativo"),
            ("Data de Criação:", formatted_date),
        ]

        for idx, (label, value) in enumerate(fields):
            frame = customtkinter.CTkFrame(self.details_frame, fg_color="transparent")
            frame.grid(row=idx + 1, column=0, columnspan=2, padx=10, pady=2, sticky="nsew")

            lbl = customtkinter.CTkLabel(frame, text=label, font=("Arial", 12, "bold"), anchor="w")
            lbl.pack(side="left")

            lbl_value = customtkinter.CTkLabel(
                frame, text=value, font=("Arial", 12), text_color="#333333"
            )
            lbl_value.pack(side="left")

        # Configure buttons frame
        self.buttons_frame.grid(
            row=2, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="nsew"
        )

        # Clear existing buttons
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        # Configure grid for buttons (2 columns)
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)

        # Check if technician user
        is_technician = user_type.lower() == "tecnico"

        # Change Password button - disabled for technicians
        btn_alterar_senha = ModernButton(
            self.buttons_frame,
            text="🔑 Alterar Senha",
            command=(
                self.open_change_password_window
                if not is_technician
                else self.show_technician_warning
            ),
            style="success" if not is_technician else "secondary",
            height=50,
        )
        btn_alterar_senha.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        # Delete User button - disabled for technicians
        btn_excluir = ModernButton(
            self.buttons_frame,
            text="🗑️ Excluir Usuário",
            command=self.confirm_deletion if not is_technician else self.show_technician_warning,
            style="danger" if not is_technician else "secondary",
            height=50,
        )
        btn_excluir.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")

        # If technician, show warning
        if is_technician:
            warning_frame = customtkinter.CTkFrame(
                self.details_frame, fg_color="#FFF3CD", corner_radius=8
            )
            warning_frame.grid(
                row=len(fields) + 2, column=0, columnspan=2, padx=10, pady=20, sticky="ew"
            )

            lbl_warning = customtkinter.CTkLabel(
                warning_frame,
                text="⚠️ Usuários técnicos não podem ser modificados ou excluídos",
                font=("Arial", 11, "bold"),
                text_color="#856404",
                wraplength=300,
            )
            lbl_warning.pack(padx=10, pady=10)

        # Hide instruction
        self.lbl_instruction.grid_forget()

    def open_change_password_window(self):
        if not self.selected_user:
            return

        # Create dialog window
        self.dialog = customtkinter.CTkToplevel(self)
        self.dialog.title("Alterar Senha")
        self.dialog.geometry("700x400")  # Largura: 700px, Altura: 400px
        self.dialog.grab_set()  # Make window modal

        # Center the window
        window_width = 700
        window_height = 400
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Frame principal
        main_frame = customtkinter.CTkFrame(self.dialog, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Frame for password fields (left side)
        fields_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        fields_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Title
        lbl_title = customtkinter.CTkLabel(
            fields_frame, text="Alterar Senha", font=("Arial", 16, "bold")
        )
        lbl_title.pack(pady=(0, 20))

        # New Password field
        lbl_new_password = customtkinter.CTkLabel(fields_frame, text="Nova Senha:", anchor="w")
        lbl_new_password.pack(fill="x", pady=(0, 5))

        self.entry_new_password = customtkinter.CTkEntry(fields_frame, show="•", width=300)
        self.entry_new_password.pack(fill="x", pady=(0, 10))
        self.entry_new_password.bind(
            "<Button-1>", lambda e: self.set_active_field(self.entry_new_password)
        )

        # Confirm Password field
        lbl_confirm_password = customtkinter.CTkLabel(
            fields_frame, text="Confirmar Senha:", anchor="w"
        )
        lbl_confirm_password.pack(fill="x", pady=(10, 5))

        self.entry_confirm_password = customtkinter.CTkEntry(fields_frame, show="•", width=300)
        self.entry_confirm_password.pack(fill="x", pady=(0, 10))
        self.entry_confirm_password.bind(
            "<Button-1>", lambda e: self.set_active_field(self.entry_confirm_password)
        )

        # Label for error/success messages
        self.lbl_message = customtkinter.CTkLabel(
            fields_frame, text="", text_color="red", wraplength=300, justify="left"
        )
        self.lbl_message.pack(fill="x", pady=(10, 0))

        # Frame for buttons
        buttons_frame_dialog = customtkinter.CTkFrame(fields_frame, fg_color="transparent")
        buttons_frame_dialog.pack(fill="x", pady=(20, 0))

        # Botão Salvar
        btn_save = ModernButton(
            buttons_frame_dialog,
            text="💾 Salvar",
            command=self.save_new_password,
            style="success",
            height=40,
        )
        btn_save.pack(side="left", padx=5, pady=10, fill="x", expand=True)

        # Botão Cancelar
        btn_cancel = ModernButton(
            buttons_frame_dialog,
            text="❌ Cancelar",
            command=self.dialog.destroy,
            style="secondary",
            height=40,
        )
        btn_cancel.pack(side="left", padx=5, pady=10, fill="x", expand=True)

        # Frame for keyboard (right side)
        keyboard_frame = customtkinter.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        keyboard_frame.pack(side="right", fill="y", padx=(10, 0))

        # Title do teclado
        customtkinter.CTkLabel(
            keyboard_frame, text="Teclado Numérico", font=("Arial", 14, "bold"), text_color="black"
        ).pack(pady=(10, 5))

        # Numeric keyboard
        buttons = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", "⌫"]]

        for _, button_row in enumerate(buttons):
            row_frame = customtkinter.CTkFrame(keyboard_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            # Configurar 3 colunas iguais
            for col in range(3):
                row_frame.columnconfigure(col, weight=1, uniform="button")

            for j, text in enumerate(button_row):
                if text:
                    btn = ModernButton(
                        row_frame,
                        text=text,
                        command=lambda t=text: self.key_pressed(t),
                        style="primary",
                        height=50,
                        font=("Arial", 16),
                    )
                    btn.grid(row=0, column=j, padx=3, pady=3, sticky="nsew")

        # Set initial active field
        self.active_field = self.entry_new_password
        self.entry_new_password.focus_set()

    def set_active_field(self, field):
        """Sets which field is active to receive keyboard input"""
        self.active_field = field

    def key_pressed(self, value):
        """Handles numeric keyboard key presses"""
        if value == "⌫":  # Backspace
            current_text = self.active_field.get()
            self.active_field.delete(0, tkinter.END)
            self.active_field.insert(0, current_text[:-1])
        else:
            self.active_field.insert(tkinter.END, value)

    def save_new_password(self):
        """Saves new password using UserManagementService"""
        new_password = self.entry_new_password.get()
        confirm_password = self.entry_confirm_password.get()

        # Use service to change password (validation included)
        result = self.management_service.change_password(
            self.selected_user, new_password, confirm_password
        )

        if result.success:
            self.lbl_message.configure(text=f"✅ {result.message}", text_color="#28a745")
        else:
            self.lbl_message.configure(text=f"❌ {result.message}", text_color="#dc3545")

    def confirm_deletion(self):
        """Confirms and executes user deletion"""
        if not self.selected_user:
            return

        # Get user data for confirmation
        user = self.management_service.get_user_by_id(self.selected_user)
        if not user:
            ToastNotification.show(self, "Usuário não encontrado", "error")
            return

        # Modern confirmation before deleting
        if not ModernConfirmDialog.ask(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário '{user.full_name}' (ID: {user.username})?\n\nEsta ação não pode ser desfeita.",
            icon="warning",
            confirm_text="Excluir",
            cancel_text="Cancelar",
        ):
            return

        # Get logged user ID to prevent self-deletion
        current_user_id = self.logged_in_user.get("id") if self.logged_in_user else None

        # Use service to delete
        result = self.management_service.delete_user(self.selected_user, current_user_id)

        if result.success:
            self.load_data()
            self.clear_details_panel()
            ToastNotification.show(self, result.message, "success")
        else:
            ToastNotification.show(self, result.message, "error")

    def show_technician_warning(self):
        """Shows warning that technician users cannot be modified"""
        from tkinter import messagebox

        messagebox.showwarning(
            "Ação Não Permitida",
            "Usuários do tipo técnico não podem ser modificados ou excluídos.\n\n"
            "Esta é uma medida de segurança do sistema.",
        )

    def clear_details_panel(self):
        # Hide details and buttons frames
        self.details_frame.grid_forget()
        self.buttons_frame.grid_forget()

        # Show instruction again
        self.lbl_instruction.grid(row=0, column=0, pady=50, padx=20, sticky="n")

        # Clear selected user
        self.selected_user = None
        self.selected_user_type = None

    def show_error_message(self, message):
        """
        Displays an error message in a custom dialog window.

        Args:
            message (str): Error message to display
        """
        # Create a custom dialog window
        error_window = customtkinter.CTkToplevel(self)
        error_window.title("Aviso")
        error_window.geometry("500x200")
        error_window.grab_set()  # Make window modal

        # Center window on screen
        window_width = 500
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        error_window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        # Frame principal
        main_frame = customtkinter.CTkFrame(error_window, fg_color="#f8d7da", corner_radius=10)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Warning icon
        warning_icon = customtkinter.CTkLabel(main_frame, text="⚠️", font=("Arial", 24))
        warning_icon.pack(pady=(20, 10))

        # Error message
        lbl_msg = customtkinter.CTkLabel(
            main_frame,
            text=message,
            text_color="#721c24",
            font=("Arial", 12),
            wraplength=400,
            justify="center",
        )
        lbl_msg.pack(padx=20, pady=10)

        # Botão OK
        btn_ok = ModernButton(
            main_frame,
            text="OK",
            command=error_window.destroy,
            style="danger",
            width=100,
            height=35,
        )
        btn_ok.pack(pady=(10, 20))

        # Configure what happens when window is closed
        error_window.protocol("WM_DELETE_WINDOW", error_window.destroy)

        # Wait until window is closed
        self.wait_window(error_window)

    def show_success_message(self, message):
        """
        Displays a success message in a custom dialog window.

        Args:
            message (str): Success message to display
        """
        # Create a custom dialog window
        success_window = customtkinter.CTkToplevel(self)
        success_window.title("Sucesso")
        success_window.geometry("500x200")
        success_window.grab_set()  # Make window modal

        # Center window on screen
        window_width = 500
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        success_window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        # Frame principal
        main_frame = customtkinter.CTkFrame(success_window, fg_color="#dff0d8", corner_radius=10)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Success icon
        success_icon = customtkinter.CTkLabel(main_frame, text="✔️", font=("Arial", 24))
        success_icon.pack(pady=(20, 10))

        # Success message
        lbl_msg = customtkinter.CTkLabel(
            main_frame,
            text=message,
            text_color="#3c763d",
            font=("Arial", 12),
            wraplength=400,
            justify="center",
        )
        lbl_msg.pack(padx=20, pady=10)

        # Botão OK
        btn_ok = ModernButton(
            main_frame,
            text="OK",
            command=success_window.destroy,
            style="success",
            width=100,
            height=35,
        )
        btn_ok.pack(pady=(10, 20))

        # Configure what happens when window is closed
        success_window.protocol("WM_DELETE_WINDOW", success_window.destroy)

        # Wait until window is closed
        self.wait_window(success_window)

    def create_back_button(self):
        # Back button (added last to stay on top)
        self.back_btn = VoltarButton(self, command=self.back_callback)
