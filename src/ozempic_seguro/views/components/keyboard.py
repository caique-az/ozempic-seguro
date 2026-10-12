"""
Virtual keyboard component: TecladoVirtual
"""

import customtkinter


class TecladoVirtual(customtkinter.CTkFrame):
    """Virtual keyboard for data entry"""

    LAYOUT = (
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ç"],
        ["z", "x", "c", "v", "b", "n", "m"],
        ["MAIÚSCULAS", "LIMPAR", "ESPAÇO"],
    )

    def __init__(self, master, current_entry=None, save_command=None, **kwargs):
        super().__init__(master, fg_color="#f0f0f0", corner_radius=10, **kwargs)
        self.current_entry = current_entry
        self.save_command = save_command
        self.uppercase_enabled = False
        self.btn_uppercase = None
        self.create_keyboard()

    def create_keyboard(self):
        """Creates the keyboard layout"""
        for i, row in enumerate(self.LAYOUT):
            self.grid_rowconfigure(i, weight=1)

            if i == len(self.LAYOUT) - 2:  # Second to last row
                self._create_row_with_actions(i, row)
            elif i == len(self.LAYOUT) - 1:  # Last row
                self._create_function_row(i)
            else:
                self._create_normal_row(i, row)

    def _create_normal_row(self, row, keys):
        """Creates a normal row of keys"""
        for j in range(10):
            self.grid_columnconfigure(j, weight=1)

        for j, key in enumerate(keys):
            displayed_key = key.upper() if self.uppercase_enabled and key.isalpha() else key

            btn = customtkinter.CTkButton(
                self,
                text=displayed_key,
                height=40,
                font=("Arial", 12, "bold"),
                fg_color="#ffffff",
                text_color="#000000",
                hover_color="#e0e0e0",
                corner_radius=5,
                command=lambda t=key: self.key_pressed(t),
            )
            btn.grid(row=row, column=j, padx=2, pady=2, sticky="nsew")

    def _create_row_with_actions(self, row, keys):
        """Creates the second to last row with action buttons"""
        for j in range(10):
            self.grid_columnconfigure(j, weight=1)

        # Letras
        for j, key in enumerate(keys):
            btn = customtkinter.CTkButton(
                self,
                text=key.upper() if self.uppercase_enabled else key,
                height=40,
                font=("Arial", 12, "bold"),
                fg_color="#ffffff",
                text_color="#000000",
                hover_color="#e0e0e0",
                corner_radius=5,
                command=lambda t=key: self.key_pressed(t),
            )
            btn.grid(row=row, column=j, padx=2, pady=2, sticky="nsew")

        # SAVE button
        btn_salvar = customtkinter.CTkButton(
            self,
            text="SALVAR",
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#2ecc71",
            text_color="white",
            hover_color="#27ae60",
            corner_radius=5,
            command=lambda: self.key_pressed("SALVAR"),
        )
        btn_salvar.grid(row=row, column=7, columnspan=2, padx=2, pady=2, sticky="nsew")

        # Delete button
        btn_apagar = customtkinter.CTkButton(
            self,
            text="⌫",
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#e74c3c",
            text_color="white",
            hover_color="#c0392b",
            corner_radius=5,
            command=lambda: self.key_pressed("⌫"),
        )
        btn_apagar.grid(row=row, column=9, padx=2, pady=2, sticky="nsew")

    def _create_function_row(self, row):
        """Creates the last row with function buttons"""
        for j in range(10):
            self.grid_columnconfigure(j, weight=1)

        # MAIÚSCULAS
        self.btn_uppercase = customtkinter.CTkButton(
            self,
            text="MAIÚSCULAS",
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#3498db" if self.uppercase_enabled else "#ffffff",
            text_color="#ffffff" if self.uppercase_enabled else "#000000",
            hover_color="#2980b9" if self.uppercase_enabled else "#e0e0e0",
            corner_radius=5,
            command=lambda: self.key_pressed("MAIÚSCULAS"),
        )
        self.btn_uppercase.grid(row=row, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")

        # LIMPAR
        customtkinter.CTkButton(
            self,
            text="LIMPAR",
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#ffffff",
            text_color="#000000",
            hover_color="#e0e0e0",
            corner_radius=5,
            command=lambda: self.key_pressed("LIMPAR"),
        ).grid(row=row, column=2, columnspan=2, padx=2, pady=2, sticky="nsew")

        # ESPAÇO
        customtkinter.CTkButton(
            self,
            text="______",
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#ffffff",
            text_color="#000000",
            hover_color="#e0e0e0",
            corner_radius=5,
            command=lambda: self.key_pressed(" "),
        ).grid(row=row, column=4, columnspan=6, padx=2, pady=2, sticky="nsew")

    def key_pressed(self, key):
        """Processes the pressed key"""
        if not self.current_entry:
            return

        if key == "⌫":
            current_text = self.current_entry.get()
            self.current_entry.delete(0, "end")
            self.current_entry.insert(0, current_text[:-1])
        elif key == "LIMPAR":
            self.current_entry.delete(0, "end")
        elif key == "SALVAR" and self.save_command:
            self.save_command()
        elif key == "MAIÚSCULAS":
            self.uppercase_enabled = not self.uppercase_enabled

            if self.btn_uppercase:
                self.btn_uppercase.configure(
                    fg_color="#3498db" if self.uppercase_enabled else "#ffffff",
                    text_color="#ffffff" if self.uppercase_enabled else "#000000",
                    hover_color="#2980b9" if self.uppercase_enabled else "#e0e0e0",
                )

            # Rebuild the keyboard
            for widget in self.winfo_children():
                widget.destroy()
            self.create_keyboard()
        else:
            inserted_key = key.upper() if self.uppercase_enabled and key.isalpha() else key
            self.current_entry.insert("end", inserted_key)

    def set_entry(self, entry):
        """Sets the active input field"""
        self.current_entry = entry
