import customtkinter as ctk
from tkinter import messagebox

from src.gui.dashboard import Dashboard
from src.logic.auth_logic import login


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Librería")
        self.geometry("920x560")
        self.resizable(False, False)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f172a")
        left.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            left,
            text="📚",
            font=("Segoe UI Emoji", 72),
        ).pack(pady=(120, 10))
        ctk.CTkLabel(
            left,
            text="BIBLIOTECA",
            font=("Segoe UI", 32, "bold"),
        ).pack()
        ctk.CTkLabel(
            left,
            text="Sistema de gestión de libros, clientes,\nventas y alquileres",
            font=("Segoe UI", 15),
            text_color="#94a3b8",
            justify="center",
        ).pack(pady=18)

        right = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        right.grid(row=0, column=1, sticky="nsew")

        form = ctk.CTkFrame(right, width=340, fg_color="#1f2937", corner_radius=18)
        form.pack(expand=True, padx=55, pady=65, fill="both")

        ctk.CTkLabel(
            form,
            text="Iniciar sesión",
            font=("Segoe UI", 27, "bold"),
        ).pack(pady=(45, 8))
        ctk.CTkLabel(
            form,
            text="Ingrese sus credenciales para continuar",
            text_color="#94a3b8",
            font=("Segoe UI", 12),
        ).pack(pady=(0, 28))

        self.usuario = ctk.CTkEntry(
            form,
            width=285,
            height=44,
            placeholder_text="Usuario",
        )
        self.usuario.pack(pady=8)

        self.password = ctk.CTkEntry(
            form,
            width=285,
            height=44,
            placeholder_text="Contraseña",
            show="•",
        )
        self.password.pack(pady=8)

        ctk.CTkButton(
            form,
            text="Iniciar sesión",
            width=285,
            height=44,
            font=("Segoe UI", 14, "bold"),
            command=self.validar_login,
        ).pack(pady=(24, 12))

        ctk.CTkLabel(
            form,
            text="Usuario inicial: admin  |  Contraseña: 1234",
            text_color="#64748b",
            font=("Segoe UI", 10),
        ).pack()

        self.usuario.bind("<Return>", lambda _event: self.validar_login())
        self.password.bind("<Return>", lambda _event: self.validar_login())
        self.after(150, self.usuario.focus_set)

    def validar_login(self) -> None:
        username = self.usuario.get().strip()
        password = self.password.get().strip()

        if not username or not password:
            messagebox.showwarning("Campos incompletos", "Complete el usuario y la contraseña.")
            return

        usuario = login(username, password)
        if usuario is None:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            self.password.delete(0, "end")
            self.password.focus_set()
            return

        datos_usuario = dict(usuario)
        self.destroy()
        dashboard = Dashboard(datos_usuario)
        dashboard.mainloop()
