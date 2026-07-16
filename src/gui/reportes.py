import customtkinter as ctk
from tkinter import ttk

from src.data.database_mgr import get_connection
from src.gui.styles import configure_treeview_style
from src.logic.venta_logic import reporte_ventas


class ReportesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#111827", corner_radius=0)
        configure_treeview_style()
        self._crear_interfaz()
        self.actualizar()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 10))
        ctk.CTkLabel(header, text="Reportes y estadísticas", font=("Segoe UI", 28, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Actualizar", width=105, fg_color="#475569", command=self.actualizar).pack(side="right")

        self.cards = ctk.CTkFrame(self, fg_color="transparent")
        self.cards.pack(fill="x", padx=20, pady=10)
        for i in range(4):
            self.cards.grid_columnconfigure(i, weight=1)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=(5, 24))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        stock_frame = ctk.CTkFrame(content, fg_color="#1f2937", corner_radius=14)
        stock_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        stock_frame.grid_columnconfigure(0, weight=1)
        stock_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(stock_frame, text="Libros con stock bajo (≤ 3)", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(14, 8)
        )
        cols = ("id", "titulo", "stock")
        self.tabla_stock = ttk.Treeview(stock_frame, columns=cols, show="headings", style="Library.Treeview")
        for col, title, width in [("id", "ID", 50), ("titulo", "Libro", 260), ("stock", "Stock", 80)]:
            self.tabla_stock.heading(col, text=title)
            self.tabla_stock.column(col, width=width, anchor="w" if col == "titulo" else "center")
        self.tabla_stock.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        alquiler_frame = ctk.CTkFrame(content, fg_color="#1f2937", corner_radius=14)
        alquiler_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        alquiler_frame.grid_columnconfigure(0, weight=1)
        alquiler_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(alquiler_frame, text="Alquileres activos", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(14, 8)
        )
        cols_a = ("id", "cliente", "fecha", "prevista")
        self.tabla_alquileres = ttk.Treeview(alquiler_frame, columns=cols_a, show="headings", style="Library.Treeview")
        for col, title, width in [
            ("id", "ID", 45), ("cliente", "Cliente", 175), ("fecha", "Préstamo", 135), ("prevista", "Prevista", 100),
        ]:
            self.tabla_alquileres.heading(col, text=title)
            self.tabla_alquileres.column(col, width=width, anchor="w" if col == "cliente" else "center")
        self.tabla_alquileres.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def actualizar(self) -> None:
        for widget in self.cards.winfo_children():
            widget.destroy()

        conn = get_connection()
        try:
            total_libros = conn.execute("SELECT COUNT(*) FROM libro WHERE estado='activo'").fetchone()[0]
            total_clientes = conn.execute("SELECT COUNT(*) FROM cliente").fetchone()[0]
            activos = conn.execute("SELECT COUNT(*) FROM alquiler WHERE estado='activo'").fetchone()[0]
            stock_bajo = conn.execute("SELECT id, titulo, cantidad_disponible FROM libro WHERE estado='activo' AND cantidad_disponible <= 3 ORDER BY cantidad_disponible, titulo").fetchall()
            alquileres = conn.execute("""
                SELECT a.id, c.nombre_completo, a.fecha_prestamo, a.fecha_devolucion_prevista
                FROM alquiler a JOIN cliente c ON c.id=a.cliente_id
                WHERE a.estado='activo' ORDER BY a.fecha_devolucion_prevista
            """).fetchall()
        finally:
            conn.close()

        ventas = reporte_ventas()
        ingresos = float(ventas["ingresos_totales"] or 0)
        datos = [
            ("Libros activos", total_libros),
            ("Clientes", total_clientes),
            ("Alquileres activos", activos),
            ("Ingresos por ventas", f"RD$ {ingresos:,.2f}"),
        ]
        for col, (titulo, valor) in enumerate(datos):
            card = ctk.CTkFrame(self.cards, fg_color="#1f2937", corner_radius=14, height=115)
            card.grid(row=0, column=col, sticky="nsew", padx=8)
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=str(valor), font=("Segoe UI", 24, "bold")).pack(pady=(22, 2))
            ctk.CTkLabel(card, text=titulo, text_color="#94a3b8", font=("Segoe UI", 12)).pack()

        self.tabla_stock.delete(*self.tabla_stock.get_children())
        for libro in stock_bajo:
            self.tabla_stock.insert("", "end", values=(libro["id"], libro["titulo"], libro["cantidad_disponible"]))

        self.tabla_alquileres.delete(*self.tabla_alquileres.get_children())
        for a in alquileres:
            self.tabla_alquileres.insert("", "end", values=(
                a["id"], a["nombre_completo"], a["fecha_prestamo"], a["fecha_devolucion_prevista"] or ""
            ))
