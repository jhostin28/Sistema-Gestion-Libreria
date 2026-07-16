import customtkinter as ctk
from tkinter import messagebox, ttk

from src.gui.styles import DANGER, SUCCESS, configure_treeview_style
from src.logic.cliente_logic import ver_clientes
from src.logic.libro_logic import ver_libros
from src.logic.venta_logic import registrar_venta, ver_detalle_venta, ver_ventas


class VentasFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#111827", corner_radius=0)
        configure_treeview_style()
        self.items = []
        self.clientes_map = {}
        self.libros_map = {}
        self._crear_interfaz()
        self.cargar_catalogos()
        self.cargar_ventas()

    def _crear_interfaz(self) -> None:
        ctk.CTkLabel(self, text="Registro de ventas", font=("Segoe UI", 28, "bold"), anchor="w").pack(
            fill="x", padx=28, pady=(24, 10)
        )

        form = ctk.CTkFrame(self, fg_color="#1f2937", corner_radius=14)
        form.pack(fill="x", padx=28, pady=10)
        for col in range(7):
            form.grid_columnconfigure(col, weight=1 if col in (0, 2) else 0)

        ctk.CTkLabel(form, text="Cliente", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", padx=(18, 5), pady=(14, 3))
        ctk.CTkLabel(form, text="Libro", font=("Segoe UI", 12, "bold")).grid(row=0, column=2, sticky="w", padx=5, pady=(14, 3))
        ctk.CTkLabel(form, text="Cantidad", font=("Segoe UI", 12, "bold")).grid(row=0, column=4, sticky="w", padx=5, pady=(14, 3))

        self.opt_cliente = ctk.CTkOptionMenu(form, values=["Sin clientes"], height=38)
        self.opt_cliente.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(18, 8), pady=(0, 15))
        self.opt_libro = ctk.CTkOptionMenu(form, values=["Sin libros"], height=38)
        self.opt_libro.grid(row=1, column=2, columnspan=2, sticky="ew", padx=8, pady=(0, 15))
        self.txt_cantidad = ctk.CTkEntry(form, width=85, height=38, placeholder_text="1")
        self.txt_cantidad.grid(row=1, column=4, sticky="ew", padx=8, pady=(0, 15))
        self.txt_cantidad.insert(0, "1")
        ctk.CTkButton(form, text="Agregar", width=100, height=38, command=self.agregar_item).grid(row=1, column=5, padx=6, pady=(0, 15))
        ctk.CTkButton(form, text="Actualizar listas", width=125, height=38, fg_color="#475569", command=self.cargar_catalogos).grid(
            row=1, column=6, padx=(6, 18), pady=(0, 15)
        )

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        contenido.grid_columnconfigure(0, weight=1)
        contenido.grid_columnconfigure(1, weight=1)
        contenido.grid_rowconfigure(0, weight=1)

        carrito_frame = ctk.CTkFrame(contenido, fg_color="#1f2937", corner_radius=14)
        carrito_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        carrito_frame.grid_columnconfigure(0, weight=1)
        carrito_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(carrito_frame, text="Detalle de la venta", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 8)
        )

        cols = ("id", "titulo", "cantidad", "precio", "subtotal")
        self.tabla_items = ttk.Treeview(carrito_frame, columns=cols, show="headings", style="Library.Treeview", height=10)
        for col, title, width in [
            ("id", "ID", 45), ("titulo", "Libro", 190), ("cantidad", "Cant.", 65),
            ("precio", "Precio", 85), ("subtotal", "Subtotal", 95),
        ]:
            self.tabla_items.heading(col, text=title)
            self.tabla_items.column(col, width=width, anchor="w" if col == "titulo" else "center")
        self.tabla_items.grid(row=1, column=0, sticky="nsew", padx=12)

        acciones = ctk.CTkFrame(carrito_frame, fg_color="transparent")
        acciones.grid(row=2, column=0, sticky="ew", padx=12, pady=12)
        self.lbl_total = ctk.CTkLabel(acciones, text="Total: RD$ 0.00", font=("Segoe UI", 18, "bold"))
        self.lbl_total.pack(side="left")
        ctk.CTkButton(acciones, text="Quitar", width=80, fg_color=DANGER, command=self.quitar_item).pack(side="right", padx=4)
        ctk.CTkButton(acciones, text="Limpiar", width=80, fg_color="#475569", command=self.limpiar_items).pack(side="right", padx=4)
        ctk.CTkButton(acciones, text="Registrar venta", width=135, fg_color=SUCCESS, command=self.registrar).pack(side="right", padx=4)

        historial = ctk.CTkFrame(contenido, fg_color="#1f2937", corner_radius=14)
        historial.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        historial.grid_columnconfigure(0, weight=1)
        historial.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(historial, text="Historial de ventas", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 8)
        )
        cols_h = ("id", "cliente", "fecha", "total")
        self.tabla_ventas = ttk.Treeview(historial, columns=cols_h, show="headings", style="Library.Treeview", height=10)
        for col, title, width in [
            ("id", "ID", 45), ("cliente", "Cliente", 180), ("fecha", "Fecha", 145), ("total", "Total", 95),
        ]:
            self.tabla_ventas.heading(col, text=title)
            self.tabla_ventas.column(col, width=width, anchor="w" if col == "cliente" else "center")
        self.tabla_ventas.grid(row=1, column=0, sticky="nsew", padx=12)
        ctk.CTkButton(historial, text="Ver detalle", width=120, command=self.ver_detalle).grid(
            row=2, column=0, sticky="e", padx=12, pady=12
        )
        self.tabla_ventas.bind("<Double-1>", lambda _e: self.ver_detalle())

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
                "precio": float(libro["precio_venta"]),
            })
        self._refrescar_items()

    def _refrescar_items(self) -> None:
        self.tabla_items.delete(*self.tabla_items.get_children())
        total = 0.0
        for item in self.items:
            subtotal = item["cantidad"] * item["precio"]
            total += subtotal
            self.tabla_items.insert("", "end", values=(
                item["libro_id"], item["titulo"], item["cantidad"], f'{item["precio"]:.2f}', f'{subtotal:.2f}'
            ))
        self.lbl_total.configure(text=f"Total: RD$ {total:,.2f}")

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
            messagebox.showwarning("Venta vacía", "Agregue al menos un libro a la venta.")
            return
        payload = [{"libro_id": i["libro_id"], "cantidad": i["cantidad"]} for i in self.items]
        try:
            if not registrar_venta(cliente_id, payload):
                messagebox.showerror("Venta no registrada", "No existe stock suficiente para completar la venta.")
                return
            messagebox.showinfo("Venta registrada", "La venta fue registrada y el inventario fue actualizado.")
            self.limpiar_items()
            self.cargar_catalogos()
            self.cargar_ventas()
        except Exception as exc:
            messagebox.showerror("Error en la venta", str(exc))

    def cargar_ventas(self) -> None:
        self.tabla_ventas.delete(*self.tabla_ventas.get_children())
        for venta in ver_ventas():
            self.tabla_ventas.insert("", "end", values=(
                venta["id"], venta["nombre_completo"] or "Cliente eliminado", venta["fecha"], f'{venta["monto_total"]:.2f}'
            ))

    def ver_detalle(self) -> None:
        seleccion = self.tabla_ventas.selection()
        if not seleccion:
            messagebox.showwarning("Seleccione una venta", "Seleccione una venta del historial.")
            return
        venta_id = int(self.tabla_ventas.item(seleccion[0], "values")[0])
        detalles = ver_detalle_venta(venta_id)
        if not detalles:
            messagebox.showinfo("Detalle de venta", "La venta no tiene detalles registrados.")
            return
        texto = "\n".join(
            f'• {d["titulo"]}: {d["cantidad"]} × RD$ {d["precio_unitario"]:,.2f} = RD$ {d["subtotal"]:,.2f}'
            for d in detalles
        )
        messagebox.showinfo(f"Detalle de la venta #{venta_id}", texto)
