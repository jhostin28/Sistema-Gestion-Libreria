import customtkinter as ctk
from tkinter import messagebox, ttk

from src.gui.styles import DANGER, SUCCESS, configure_treeview_style
from src.logic.libro_logic import (
    actualizar_libro,
    buscar_libro,
    eliminar_libro,
    registrar_libro,
    ver_libros,
)


class LibrosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#111827", corner_radius=0)
        configure_treeview_style()
        self.libro_id = None
        self._crear_interfaz()
        self.cargar_libros()

    def _crear_interfaz(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 10))
        ctk.CTkLabel(header, text="Gestión de libros", font=("Segoe UI", 28, "bold")).pack(side="left")

        search = ctk.CTkFrame(self, fg_color="#1f2937", corner_radius=12)
        search.pack(fill="x", padx=28, pady=10)
        self.txt_buscar = ctk.CTkEntry(search, placeholder_text="Buscar por título, autor o ISBN", height=38)
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=(15, 8), pady=13)
        ctk.CTkButton(search, text="Buscar", width=100, command=self.buscar).pack(side="left", padx=4)
        ctk.CTkButton(search, text="Mostrar todos", width=120, fg_color="#475569", command=self.cargar_libros).pack(
            side="left", padx=(4, 15)
        )
        self.txt_buscar.bind("<Return>", lambda _e: self.buscar())

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(body, width=310, fg_color="#1f2937", corner_radius=14)
        form.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        form.grid_propagate(False)
        ctk.CTkLabel(form, text="Datos del libro", font=("Segoe UI", 18, "bold")).pack(pady=(20, 12))

        self.campos = {}
        etiquetas = [
            ("titulo", "Título"),
            ("autor", "Autor"),
            ("categoria", "Categoría"),
            ("isbn", "ISBN"),
            ("cantidad", "Cantidad disponible"),
            ("precio_venta", "Precio de venta"),
            ("precio_alquiler", "Precio de alquiler"),
        ]
        for clave, placeholder in etiquetas:
            entry = ctk.CTkEntry(form, placeholder_text=placeholder, height=36)
            entry.pack(fill="x", padx=20, pady=5)
            self.campos[clave] = entry

        botones = ctk.CTkFrame(form, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=18)
        ctk.CTkButton(botones, text="Guardar", fg_color=SUCCESS, command=self.guardar).pack(fill="x", pady=4)
        ctk.CTkButton(botones, text="Actualizar", command=self.actualizar).pack(fill="x", pady=4)
        ctk.CTkButton(botones, text="Eliminar", fg_color=DANGER, command=self.eliminar).pack(fill="x", pady=4)
        ctk.CTkButton(botones, text="Limpiar", fg_color="#475569", command=self.limpiar_formulario).pack(fill="x", pady=4)

        table_frame = ctk.CTkFrame(body, fg_color="#1f2937", corner_radius=14)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columnas = ("id", "titulo", "autor", "categoria", "isbn", "stock", "venta", "alquiler")
        self.tabla = ttk.Treeview(table_frame, columns=columnas, show="headings", style="Library.Treeview")
        encabezados = {
            "id": "ID", "titulo": "Título", "autor": "Autor", "categoria": "Categoría",
            "isbn": "ISBN", "stock": "Stock", "venta": "Venta RD$", "alquiler": "Alquiler RD$",
        }
        anchos = {"id": 55, "titulo": 180, "autor": 150, "categoria": 115, "isbn": 115, "stock": 70, "venta": 95, "alquiler": 100}
        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, width=anchos[col], anchor="center" if col not in ("titulo", "autor") else "w")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=(14, 0))
        scroll_y.grid(row=0, column=1, sticky="ns", pady=(14, 0), padx=(0, 10))
        scroll_x.grid(row=1, column=0, sticky="ew", padx=(12, 0), pady=(0, 12))
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_libro)
        self.tabla.bind("<Double-1>", self.seleccionar_libro)

    def _datos_formulario(self):
        titulo = self.campos["titulo"].get().strip()
        autor = self.campos["autor"].get().strip()
        categoria = self.campos["categoria"].get().strip()
        isbn = self.campos["isbn"].get().strip()
        if not titulo or not autor:
            raise ValueError("El título y el autor son obligatorios.")
        try:
            cantidad = int(self.campos["cantidad"].get().strip())
            precio_venta = float(self.campos["precio_venta"].get().strip())
            precio_alquiler = float(self.campos["precio_alquiler"].get().strip())
        except ValueError as exc:
            raise ValueError("Cantidad y precios deben contener valores numéricos.") from exc
        if cantidad < 0 or precio_venta < 0 or precio_alquiler < 0:
            raise ValueError("No se permiten cantidades ni precios negativos.")
        return titulo, autor, categoria, isbn, cantidad, precio_venta, precio_alquiler

    def guardar(self) -> None:
        try:
            registrar_libro(*self._datos_formulario())
            messagebox.showinfo("Registro correcto", "El libro fue registrado correctamente.")
            self.limpiar_formulario()
            self.cargar_libros()
        except Exception as exc:
            messagebox.showerror("No fue posible registrar", str(exc))

    def actualizar(self) -> None:
        if self.libro_id is None:
            messagebox.showwarning("Seleccione un libro", "Seleccione el libro que desea actualizar.")
            return
        try:
            actualizar_libro(self.libro_id, *self._datos_formulario())
            messagebox.showinfo("Actualización correcta", "El libro fue actualizado correctamente.")
            self.limpiar_formulario()
            self.cargar_libros()
        except Exception as exc:
            messagebox.showerror("No fue posible actualizar", str(exc))

    def eliminar(self) -> None:
        if self.libro_id is None:
            messagebox.showwarning("Seleccione un libro", "Seleccione el libro que desea eliminar.")
            return
        if not messagebox.askyesno("Confirmar eliminación", "El libro dejará de aparecer en el inventario. ¿Continuar?"):
            return
        try:
            eliminar_libro(self.libro_id)
            messagebox.showinfo("Libro eliminado", "El libro fue retirado del inventario.")
            self.limpiar_formulario()
            self.cargar_libros()
        except Exception as exc:
            messagebox.showerror("No fue posible eliminar", str(exc))

    def buscar(self) -> None:
        termino = self.txt_buscar.get().strip()
        self._llenar_tabla(buscar_libro(termino) if termino else ver_libros())

    def cargar_libros(self) -> None:
        self.txt_buscar.delete(0, "end")
        self._llenar_tabla(ver_libros())

    def _llenar_tabla(self, libros) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for libro in libros:
            self.tabla.insert("", "end", values=(
                libro["id"], libro["titulo"], libro["autor"], libro["categoria"] or "",
                libro["isbn"] or "", libro["cantidad_disponible"], f'{libro["precio_venta"]:.2f}',
                f'{libro["precio_alquiler"]:.2f}',
            ))

    def seleccionar_libro(self, _event=None) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.libro_id = int(valores[0])
        datos = [valores[1], valores[2], valores[3], valores[4], valores[5], valores[6], valores[7]]
        for clave, valor in zip(self.campos, datos):
            self.campos[clave].delete(0, "end")
            self.campos[clave].insert(0, valor)

    def limpiar_formulario(self) -> None:
        self.libro_id = None
        for entry in self.campos.values():
            entry.delete(0, "end")
        for item in self.tabla.selection():
            self.tabla.selection_remove(item)
