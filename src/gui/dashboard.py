import customtkinter as ctk
from tkinter import messagebox

from src.data.database_mgr import get_connection
from src.gui.alquileres import AlquileresFrame
from src.gui.clientes import ClientesFrame
from src.gui.libros import LibrosFrame
from src.gui.reportes import ReportesFrame
from src.gui.ventas import VentasFrame


class Dashboard(ctk.CTk):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario or {"nombre": "Administrador", "rol": "admin"}
        self.title("Sistema de Gestión de Librería")
        self.geometry("1380x790")
        self.minsize(1120, 680)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menu = ctk.CTkFrame(self, width=245, corner_radius=0, fg_color="#0f172a")
        self.menu.grid(row=0, column=0, sticky="nsw")
        self.menu.grid_propagate(False)

        ctk.CTkLabel(
            self.menu,
            text="📚  LIBRERÍA",
            font=("Segoe UI", 23, "bold"),
        ).pack(pady=(35, 8), padx=18)
        ctk.CTkLabel(
            self.menu,
            text=self.usuario.get("nombre") or self.usuario.get("username", "Usuario"),
            text_color="#94a3b8",
            font=("Segoe UI", 12),
        ).pack(pady=(0, 28))

        self._crear_boton("🏠  Inicio", self.mostrar_inicio)
        self._crear_boton("📚  Libros", self.abrir_libros)
        self._crear_boton("👥  Clientes", self.abrir_clientes)
        self._crear_boton("💰  Ventas", self.abrir_ventas)
        self._crear_boton("📖  Alquileres", self.abrir_alquileres)
        self._crear_boton("📊  Reportes", self.abrir_reportes)

        ctk.CTkButton(
            self.menu,
            text="Cerrar sesión",
            height=42,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=self.cerrar_sesion,
        ).pack(side="bottom", fill="x", padx=20, pady=26)

        self.panel = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        self.panel.grid(row=0, column=1, sticky="nsew")
        self.mostrar_inicio()

    def _crear_boton(self, texto, comando) -> None:
        ctk.CTkButton(
            self.menu,
            text=texto,
            height=44,
            anchor="w",
            font=("Segoe UI", 14),
            fg_color="transparent",
            hover_color="#1e293b",
            command=comando,
        ).pack(fill="x", padx=16, pady=4)

    def limpiar_panel(self) -> None:
        for widget in self.panel.winfo_children():
            widget.destroy()

    def mostrar_inicio(self) -> None:
        self.limpiar_panel()
        contenedor = ctk.CTkFrame(self.panel, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=34, pady=30)

        ctk.CTkLabel(
            contenedor,
            text="Panel principal",
            font=("Segoe UI", 31, "bold"),
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            contenedor,
            text="Resumen general del sistema",
            text_color="#94a3b8",
            font=("Segoe UI", 14),
            anchor="w",
        ).pack(fill="x", pady=(3, 25))

        resumen = self._obtener_resumen()
        cards = ctk.CTkFrame(contenedor, fg_color="transparent")
        cards.pack(fill="x")
        for i in range(4):
            cards.grid_columnconfigure(i, weight=1)

        datos = [
            ("📚", "Libros activos", resumen["libros"]),
            ("👥", "Clientes", resumen["clientes"]),
            ("💰", "Ventas", resumen["ventas"]),
            ("📖", "Alquileres activos", resumen["alquileres"]),
        ]
        for col, (icono, titulo, valor) in enumerate(datos):
            card = ctk.CTkFrame(cards, height=150, fg_color="#1f2937", corner_radius=15)
            card.grid(row=0, column=col, sticky="nsew", padx=8)
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=icono, font=("Segoe UI Emoji", 30)).pack(pady=(22, 4))
            ctk.CTkLabel(card, text=str(valor), font=("Segoe UI", 26, "bold")).pack()
            ctk.CTkLabel(card, text=titulo, text_color="#94a3b8", font=("Segoe UI", 12)).pack()

        accesos = ctk.CTkFrame(contenedor, fg_color="#1f2937", corner_radius=15)
        accesos.pack(fill="both", expand=True, pady=(28, 0))
        ctk.CTkLabel(
            accesos,
            text="Accesos rápidos",
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        ).pack(fill="x", padx=25, pady=(22, 15))

        grid = ctk.CTkFrame(accesos, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1)
        accesos_data = [
            ("Registrar libro", self.abrir_libros),
            ("Registrar cliente", self.abrir_clientes),
            ("Nueva venta", self.abrir_ventas),
            ("Nuevo alquiler", self.abrir_alquileres),
        ]
        for col, (texto, comando) in enumerate(accesos_data):
            ctk.CTkButton(grid, text=texto, height=48, command=comando).grid(
                row=0, column=col, sticky="ew", padx=7, pady=8
            )

    def _obtener_resumen(self) -> dict:
        conn = get_connection()
        try:
            return {
                "libros": conn.execute("SELECT COUNT(*) FROM libro WHERE estado='activo'").fetchone()[0],
                "clientes": conn.execute("SELECT COUNT(*) FROM cliente").fetchone()[0],
                "ventas": conn.execute("SELECT COUNT(*) FROM venta").fetchone()[0],
                "alquileres": conn.execute("SELECT COUNT(*) FROM alquiler WHERE estado='activo'").fetchone()[0],
            }
        finally:
            conn.close()

    def abrir_libros(self) -> None:
        self.limpiar_panel()
        LibrosFrame(self.panel).pack(fill="both", expand=True)

    def abrir_clientes(self) -> None:
        self.limpiar_panel()
        ClientesFrame(self.panel).pack(fill="both", expand=True)

    def abrir_ventas(self) -> None:
        self.limpiar_panel()
        VentasFrame(self.panel).pack(fill="both", expand=True)

    def abrir_alquileres(self) -> None:
        self.limpiar_panel()
        AlquileresFrame(self.panel).pack(fill="both", expand=True)

    def abrir_reportes(self) -> None:
        self.limpiar_panel()
        ReportesFrame(self.panel).pack(fill="both", expand=True)

    def cerrar_sesion(self) -> None:
        if messagebox.askyesno("Cerrar sesión", "¿Desea cerrar la aplicación?"):
            self.destroy()
