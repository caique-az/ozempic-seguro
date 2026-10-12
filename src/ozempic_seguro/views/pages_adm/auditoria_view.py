from datetime import datetime, timedelta
from tkinter import ttk

import customtkinter

from ...core.logger import logger
from ...services.audit_view_service import AuditFilter, get_audit_view_service


class AuditoriaFrame(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, *args, **kwargs):
        self.back_callback = back_callback
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)
        self.audit_view_service = get_audit_view_service()

        # Criar overlay para esconder construção
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)

        # Filter variables
        self.filter_action = customtkinter.StringVar(value="Todas")
        self.filter_start_date = customtkinter.StringVar()
        self.filter_end_date = customtkinter.StringVar()

        # Set default date (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        self.filter_start_date.set(start_date.strftime("%Y-%m-%d"))
        self.filter_end_date.set(end_date.strftime("%Y-%m-%d"))

        self.create_header()
        self.create_filters()
        self.create_table()
        self.load_data()
        self.create_back_button()

        # Remover overlay após tudo estar pronto
        self.update_idletasks()
        self._overlay.destroy()

    def create_header(self):
        """Creates the page header"""
        # Frame para o cabeçalho
        self.header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=10)

        # Título
        self.title_label = customtkinter.CTkLabel(
            self.header_frame,
            text="Registro de Auditoria",
            font=("Arial", 24, "bold"),
            text_color="white",
        )
        self.title_label.pack(side="left")

        # Refresh button
        self.btn_atualizar = customtkinter.CTkButton(
            self.header_frame,
            text="Atualizar",
            command=self.load_data,
            width=120,
            height=35,
            fg_color="#28a745",
            hover_color="#218838",
        )
        self.btn_atualizar.pack(side="right", padx=10)

    def create_filters(self):
        """Creates filter controls"""
        # Frame para os filtros
        self.filters_frame = customtkinter.CTkFrame(self, fg_color="#2c4d5c")
        self.filters_frame.pack(fill="x", padx=20, pady=(0, 10), ipady=10)

        # Filtro por ação
        customtkinter.CTkLabel(
            self.filters_frame, text="Ação:", text_color="white", font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Ações disponíveis do serviço
        self.cmb_action = customtkinter.CTkComboBox(
            self.filters_frame,
            values=self.audit_view_service.get_available_actions(),
            variable=self.filter_action,
            width=150,
            state="readonly",
        )
        self.cmb_action.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Filtro por data de início
        customtkinter.CTkLabel(
            self.filters_frame, text="Data Início:", text_color="white", font=("Arial", 12, "bold")
        ).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.entry_start_date = customtkinter.CTkEntry(
            self.filters_frame, textvariable=self.filter_start_date, width=120
        )
        self.entry_start_date.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Filtro por data de fim
        customtkinter.CTkLabel(
            self.filters_frame, text="Data Fim:", text_color="white", font=("Arial", 12, "bold")
        ).grid(row=0, column=4, padx=10, pady=5, sticky="w")

        self.entry_end_date = customtkinter.CTkEntry(
            self.filters_frame, textvariable=self.filter_end_date, width=120
        )
        self.entry_end_date.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Botão de aplicar filtros
        self.btn_apply = customtkinter.CTkButton(
            self.filters_frame,
            text="Aplicar Filtros",
            command=self.apply_filters,
            width=120,
            height=30,
            fg_color="#17a2b8",
            hover_color="#138496",
        )
        self.btn_apply.grid(row=0, column=6, padx=10, pady=5, sticky="e")

    def create_table(self):
        """Creates table to display audit records"""
        # Frame para a tabela
        self.table_frame = customtkinter.CTkFrame(self, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 100))

        # Create Treeview with scrollbar
        self.tree_scroll = ttk.Scrollbar(self.table_frame)
        self.tree_scroll.pack(side="right", fill="y")

        # Set style for tree
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#ffffff",
            foreground="black",
            rowheight=25,
            fieldbackground="#ffffff",
            font=("Arial", 10),
        )

        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Create tree
        self.tree = ttk.Treeview(
            self.table_frame, yscrollcommand=self.tree_scroll.set, selectmode="extended", height=20
        )

        # Configure scrollbar
        self.tree_scroll.config(command=self.tree.yview)

        # Define columns
        self.tree["columns"] = ("data", "usuario", "acao", "tabela", "id_afetado", "detalhes")

        # Format columns
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("data", anchor="w", width=150)
        self.tree.column("usuario", anchor="w", width=120)
        self.tree.column("acao", anchor="w", width=100)
        self.tree.column("tabela", anchor="w", width=100)
        self.tree.column("id_afetado", anchor="center", width=80)
        self.tree.column("detalhes", anchor="w", width=300)

        # Headers
        self.tree.heading("data", text="Data/Hora", anchor="w")
        self.tree.heading("usuario", text="Usuário", anchor="w")
        self.tree.heading("acao", text="Ação", anchor="w")
        self.tree.heading("tabela", text="Tabela", anchor="w")
        self.tree.heading("id_afetado", text="ID Afetado", anchor="center")
        self.tree.heading("detalhes", text="Detalhes", anchor="w")

        # Add tree to frame
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Add double-click event to view details
        self.tree.bind("<Double-1>", self.show_details)

    def load_data(self, apply_filters=False):
        """Loads audit table data using AuditViewService"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Create filter using service
        audit_filter = AuditFilter(
            action=self.filter_action.get(),
            start_date=self.filter_start_date.get(),
            end_date=self.filter_end_date.get(),
        )

        try:
            # Get audit records using service
            result = self.audit_view_service.get_logs(filter=audit_filter)

            # Fill table with records
            for log_item in result.items:
                # Format details
                detalhes = ""
                if log_item.dados_novos:
                    try:
                        import json

                        dados = (
                            json.loads(log_item.dados_novos)
                            if isinstance(log_item.dados_novos, str)
                            else log_item.dados_novos
                        )
                        if isinstance(dados, dict):
                            detalhes = ", ".join([f"{k}: {v}" for k, v in dados.items()])
                    except Exception:
                        detalhes = str(log_item.dados_novos)[:50]

                # Insert into tree
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        log_item.timestamp_display,
                        log_item.usuario,
                        log_item.action_display,
                        log_item.tabela,
                        log_item.id_afetado or "",
                        detalhes,
                    ),
                    tags=("linha",),
                )

            # Configure tags for alternating colors
            self.tree.tag_configure("linha", background="white")
            self.tree.tag_configure("linha_alternada", background="#f0f0f0")

            # Alternate row colors
            for i, item in enumerate(self.tree.get_children()):
                tag = "linha_alternada" if i % 2 == 0 else "linha"
                self.tree.item(item, tags=(tag,))

        except Exception as e:
            logger.error(f"Error loading audit data: {e}")

    def format_summary_details(self, record):
        """Formats record details for summary display"""
        action = record.get("acao", "").lower()

        if action == "login":
            return "Login realizado com sucesso"
        if action == "logout":
            return "Logout realizado"
        if action == "criar":
            return "Novo usuário criado"
        if action == "atualizar":
            return "Dados do usuário atualizados"
        if action == "excluir":
            return "Usuário removido"

        return ""

    def apply_filters(self):
        """Applies selected filters"""
        self.load_data(apply_filters=True)

    def show_details(self, event):
        """Shows complete details of selected record"""
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")

        # Create details window
        details_window = customtkinter.CTkToplevel(self)
        details_window.title("Detalhes do Registro")
        details_window.geometry("600x400")
        details_window.grab_set()

        # Frame for details
        details_frame = customtkinter.CTkFrame(details_window, fg_color="white")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Display details
        customtkinter.CTkLabel(
            details_frame, text=f"Data/Hora: {values[0]}", font=("Arial", 12), anchor="w"
        ).pack(fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(
            details_frame, text=f"Usuário: {values[1]}", font=("Arial", 12), anchor="w"
        ).pack(fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(
            details_frame, text=f"Ação: {values[2]}", font=("Arial", 12), anchor="w"
        ).pack(fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(
            details_frame, text=f"Tabela: {values[3]}", font=("Arial", 12), anchor="w"
        ).pack(fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(
            details_frame, text=f"ID Afetado: {values[4]}", font=("Arial", 12), anchor="w"
        ).pack(fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(
            details_frame, text=f"Detalhes: {values[5]}", font=("Arial", 12), anchor="w"
        ).pack(fill="x", padx=10, pady=5)

        # Close button
        btn_close = customtkinter.CTkButton(
            details_window,
            text="Fechar",
            command=details_window.destroy,
            width=100,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268",
        )
        btn_close.pack(pady=10)

    def create_back_button(self):
        """Creates the back button"""
        from ..components import VoltarButton

        VoltarButton(self, self.back_callback)
