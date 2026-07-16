from datetime import date, timedelta

import customtkinter as ctk
from tkinter import messagebox, ttk

from src.gui.styles import DANGER, SUCCESS, configure_treeview_style
from src.logic.alquiler_logic import (
    registrar_alquiler,
    registrar_devolucion,
    ver_alquileres,
    ver_detalle_alquiler,
)
from src.logic.cliente_logic import ver_clientes
from src.logic.libro_logic import ver_libros


class AlquileresFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#111827", corner_radius=0)
        configure_treeview_style()
        self.items = []
        self.clientes_map = {}
        self.libros_map = {}
        self._crear_interfaz()
        self.cargar_catalogos()
        self.cargar_alquileres()

    def _crear_interfaz(self) -> None:
        ctk.CTkLabel(self, text="Gestión de alquileres", font=("Segoe UI", 28, "bold"), anchor="w").pack(
            fill="x", padx=28, pady=(24, 10)
        )

        form = ctk.CTkFrame(self, fg_color="#1f2937", corner_radius=14)
        form.pack(fill="x", padx=28, pady=10)
        for col in range(8):
            form.grid_columnconfigure(col, weight=1 if col in (0, 2) else 0)

        for col, text in [(0, "Cliente"), (2, "Libro"), (4, "Cantidad"), (5, "Devolución prevista")]:
            ctk.CTkLabel(form, text=text, font=("Segoe UI", 12, "bold")).grid(
                row=0, column=col, sticky="w", padx=(18 if col == 0 else 5, 5), pady=(14, 3)
            )

        self.opt_cliente = ctk.CTkOptionMenu(form, values=["Sin clientes"], height=38)
        self.opt_cliente.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(18, 8), pady=(0, 15))
        self.opt_libro = ctk.CTkOptionMenu(form, values=["Sin libros"], height=38)
        self.opt_libro.grid(row=1, column=2, columnspan=2, sticky="ew", padx=8, pady=(0, 15))
        self.txt_cantidad = ctk.CTkEntry(form, width=75, height=38)
        self.txt_cantidad.grid(row=1, column=4, padx=8, pady=(0, 15))
        self.txt_cantidad.insert(0, "1")
        self.txt_fecha = ctk.CTkEntry(form, width=130, height=38)
        self.txt_fecha.grid(row=1, column=5, padx=8, pady=(0, 15))
        self.txt_fecha.insert(0, (date.today() + timedelta(days=14)).isoformat())
        ctk.CTkButton(form, text="Agregar", width=95, height=38, command=self.agregar_item).grid(row=1, column=6, padx=6, pady=(0, 15))
        ctk.CTkButton(form, text="Actualizar listas", width=125, height=38, fg_color="#475569", command=self.cargar_catalogos).grid(
            row=1, column=7, padx=(6, 18), pady=(0, 15)
        )

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        contenido.grid_columnconfigure(0, weight=1)
        contenido.grid_columnconfigure(1, weight=1)
        contenido.grid_rowconfigure(0, weight=1)

        detalle = ctk.CTkFrame(contenido, fg_color="#1f2937", corner_radius=14)
        detalle.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        detalle.grid_columnconfigure(0, weight=1)
        detalle.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(detalle, text="Libros a alquilar", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 8)
        )
        cols = ("id", "titulo", "cantidad", "precio")
        self.tabla_items = ttk.Treeview(detalle, columns=cols, show="headings", style="Library.Treeview", height=10)
        for col, title, width in [("id", "ID", 45), ("titulo", "Libro", 210), ("cantidad", "Cant.", 70), ("precio", "Precio", 90)]:
            self.tabla_items.heading(col, text=title)
            self.tabla_items.column(col, width=width, anchor="w" if col == "titulo" else "center")
        self.tabla_items.grid(row=1, column=0, sticky="nsew", padx=12)
        actions = ctk.CTkFrame(detalle, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=12, pady=12)
        ctk.CTkButton(actions, text="Registrar alquiler", width=145, fg_color=SUCCESS, command=self.registrar).pack(side="right", padx=4)
        ctk.CTkButton(actions, text="Limpiar", width=80, fg_color="#475569", command=self.limpiar_items).pack(side="right", padx=4)
        ctk.CTkButton(actions, text="Quitar", width=80, fg_color=DANGER, command=self.quitar_item).pack(side="right", padx=4)

        historial = ctk.CTkFrame(contenido, fg_color="#1f2937", corner_radius=14)
        historial.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        historial.grid_columnconfigure(0, weight=1)
        historial.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(historial, text="Historial de alquileres", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 8)
        )
        cols_h = ("id", "cliente", "prestamo", "prevista", "real", "estado")
        self.tabla_alquileres = ttk.Treeview(historial, columns=cols_h, show="headings", style="Library.Treeview", height=10)
        specs = [
            ("id", "ID", 45), ("cliente", "Cliente", 155), ("prestamo", "Préstamo", 130),
            ("prevista", "Prevista", 95), ("real", "Devuelto", 120), ("estado", "Estado", 75),
        ]
        for col, title, width in specs:
            self.tabla_alquileres.heading(col, text=title)
            self.tabla_alquileres.column(col, width=width, anchor="w" if col == "cliente" else "center")
        self.tabla_alquileres.grid(row=1, column=0, sticky="nsew", padx=12)
        actions_h = ctk.CTkFrame(historial, fg_color="transparent")
        actions_h.grid(row=2, column=0, sticky="e", padx=12, pady=12)
        ctk.CTkButton(actions_h, text="Ver detalle", width=105, command=self.ver_detalle).pack(side="left", padx=4)
        ctk.CTkButton(actions_h, text="Registrar devolución", width=150, fg_color=SUCCESS, command=self.devolver).pack(side="left", padx=4)
        self.tabla_alquileres.bind("<Double-1>", lambda _e: self.ver_detalle())

    def cargar_catalogos(self) -> None:
        clientes = ver_clientes()
        self.clientes_map = {f'{c["id"]} - {c["nombre_completo"]}': c["id"] for c in clientes}
        valores_clientes = list(self.clientes_map) or ["Sin clientes registrados"]
        self.opt_cliente.configure(values=valores_clientes)
        self.opt_cliente.set(valores_clientes[0])

        libros = [l for l in ver_libros() if l["cantidad_disponible"] > 0]
        self.libros_map = {
            f'{l["id"]} - {l["titulo"]} (stock: {l["cantidad_disponible"]})': dict(l) for l in libros
        }
        valores_libros = list(self.libros_map) or ["Sin libros disponibles"]
        self.opt_libro.configure(values=valores_libros)
        self.opt_libro.set(valores_libros[0])

    def agregar_item(self) -> None:
        libro = self.libros_map.get(self.opt_libro.get())
        if libro is None:
            messagebox.showwarning("Sin libro", "No hay un libro disponible seleccionado.")
            return
        try:
            cantidad = int(self.txt_cantidad.get().strip())
        except ValueError:
            messagebox.showerror("Cantidad inválida", "La cantidad debe ser un número entero.")
            return
        if cantidad <= 0:
            messagebox.showerror("Cantidad inválida", "La cantidad debe ser mayor que cero.")
            return
        existente = next((i for i in self.items if i["libro_id"] == libro["id"]), None)
        nueva_cantidad = cantidad + (existente["cantidad"] if existente else 0)
        if nueva_cantidad > libro["cantidad_disponible"]:
            messagebox.showerror("Stock insuficiente", f'Solo hay {libro["cantidad_disponible"]} unidades disponibles.')
            return
        if existente:
            existente["cantidad"] = nueva_cantidad
        else:
            self.items.append({
                "libro_id": libro["id"], "titulo": libro["titulo"], "cantidad": cantidad,
                "precio": float(libro["precio_alquiler"]),
            })
        self._refrescar_items()

    def _refrescar_items(self) -> None:
        self.tabla_items.delete(*self.tabla_items.get_children())
        for item in self.items:
            self.tabla_items.insert("", "end", values=(
                item["libro_id"], item["titulo"], item["cantidad"], f'{item["precio"]:.2f}'
            ))

    def quitar_item(self) -> None:
        seleccion = self.tabla_items.selection()
        if not seleccion:
            messagebox.showwarning("Seleccione un libro", "Seleccione un libro del detalle.")
            return
        libro_id = int(self.tabla_items.item(seleccion[0], "values")[0])
        self.items = [i for i in self.items if i["libro_id"] != libro_id]
        self._refrescar_items()

    def limpiar_items(self) -> None:
        self.items.clear()
        self._refrescar_items()

    def registrar(self) -> None:
        cliente_id = self.clientes_map.get(self.opt_cliente.get())
        if cliente_id is None:
            messagebox.showwarning("Sin cliente", "Registre o seleccione un cliente.")
            return
        if not self.items:
            messagebox.showwarning("Alquiler vacío", "Agregue al menos un libro.")
            return
        fecha = self.txt_fecha.get().strip()
        try:
            fecha_obj = date.fromisoformat(fecha)
        except ValueError:
            messagebox.showerror("Fecha inválida", "Use el formato AAAA-MM-DD.")
            return
        if fecha_obj < date.today():
            messagebox.showerror("Fecha inválida", "La fecha prevista no puede estar en el pasado.")
            return
        payload = [{"libro_id": i["libro_id"], "cantidad": i["cantidad"]} for i in self.items]
        try:
            if not registrar_alquiler(cliente_id, payload, fecha):
                messagebox.showerror("Alquiler no registrado", "No existe stock suficiente para completar el alquiler.")
                return
            messagebox.showinfo("Alquiler registrado", "El alquiler fue registrado y el inventario fue actualizado.")
            self.limpiar_items()
            self.cargar_catalogos()
            self.cargar_alquileres()
        except Exception as exc:
            messagebox.showerror("Error en el alquiler", str(exc))

    def cargar_alquileres(self) -> None:
        self.tabla_alquileres.delete(*self.tabla_alquileres.get_children())
        for a in ver_alquileres():
            self.tabla_alquileres.insert("", "end", values=(
                a["id"], a["nombre_completo"], a["fecha_prestamo"], a["fecha_devolucion_prevista"] or "",
                a["fecha_devolucion_real"] or "", a["estado"],
            ))

    def _alquiler_seleccionado(self):
        seleccion = self.tabla_alquileres.selection()
        if not seleccion:
            messagebox.showwarning("Seleccione un alquiler", "Seleccione un alquiler del historial.")
            return None
        return int(self.tabla_alquileres.item(seleccion[0], "values")[0])

    def devolver(self) -> None:
        alquiler_id = self._alquiler_seleccionado()
        if alquiler_id is None:
            return
        if not messagebox.askyesno("Confirmar devolución", "¿Registrar la devolución y restaurar el stock?"):
            return
        try:
            if not registrar_devolucion(alquiler_id):
                messagebox.showwarning("No disponible", "El alquiler no existe o ya fue devuelto.")
                return
            messagebox.showinfo("Devolución registrada", "La devolución fue registrada y el stock fue restaurado.")
            self.cargar_alquileres()
            self.cargar_catalogos()
        except Exception as exc:
            messagebox.showerror("Error en la devolución", str(exc))

    def ver_detalle(self) -> None:
        alquiler_id = self._alquiler_seleccionado()
        if alquiler_id is None:
            return
        detalles = ver_detalle_alquiler(alquiler_id)
        texto = "\n".join(
            f'• {d["titulo"]}: {d["cantidad"]} × RD$ {d["precio_unitario"]:,.2f}' for d in detalles
        ) or "No hay detalles registrados."
        messagebox.showinfo(f"Detalle del alquiler #{alquiler_id}", texto)
