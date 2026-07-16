import customtkinter as ctk
from tkinter import messagebox, ttk

from src.gui.styles import DANGER, SUCCESS, configure_treeview_style
from src.logic.cliente_logic import (
    actualizar_cliente,
    buscar_cliente,
    eliminar_cliente,
    registrar_cliente,
    ver_clientes,
)


class ClientesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#111827", corner_radius=0)
        configure_treeview_style()
        self.cliente_id = None
        self._crear_interfaz()
        self.cargar_clientes()

    def _crear_interfaz(self) -> None:
        ctk.CTkLabel(self, text="Gestión de clientes", font=("Segoe UI", 28, "bold"), anchor="w").pack(
            fill="x", padx=28, pady=(24, 10)
        )

        search = ctk.CTkFrame(self, fg_color="#1f2937", corner_radius=12)
        search.pack(fill="x", padx=28, pady=10)
        self.txt_buscar = ctk.CTkEntry(search, placeholder_text="Buscar por nombre, cédula o teléfono", height=38)
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=(15, 8), pady=13)
        ctk.CTkButton(search, text="Buscar", width=100, command=self.buscar).pack(side="left", padx=4)
        ctk.CTkButton(search, text="Mostrar todos", width=120, fg_color="#475569", command=self.cargar_clientes).pack(
            side="left", padx=(4, 15)
        )
        self.txt_buscar.bind("<Return>", lambda _e: self.buscar())

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(body, width=315, fg_color="#1f2937", corner_radius=14)
        form.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        form.grid_propagate(False)
        ctk.CTkLabel(form, text="Datos del cliente", font=("Segoe UI", 18, "bold")).pack(pady=(22, 15))

        self.campos = {}
        for clave, texto in [
            ("nombre", "Nombre completo"), ("cedula", "Cédula"), ("telefono", "Teléfono"),
            ("email", "Correo electrónico"), ("direccion", "Dirección"),
        ]:
            entry = ctk.CTkEntry(form, placeholder_text=texto, height=38)
            entry.pack(fill="x", padx=20, pady=7)
            self.campos[clave] = entry

        botones = ctk.CTkFrame(form, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(botones, text="Guardar", fg_color=SUCCESS, command=self.guardar).pack(fill="x", pady=4)
        ctk.CTkButton(botones, text="Actualizar", command=self.actualizar).pack(fill="x", pady=4)
        ctk.CTkButton(botones, text="Eliminar", fg_color=DANGER, command=self.eliminar).pack(fill="x", pady=4)
        ctk.CTkButton(botones, text="Limpiar", fg_color="#475569", command=self.limpiar_formulario).pack(fill="x", pady=4)

        table_frame = ctk.CTkFrame(body, fg_color="#1f2937", corner_radius=14)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columnas = ("id", "nombre", "cedula", "telefono", "email", "direccion", "fecha")
        self.tabla = ttk.Treeview(table_frame, columns=columnas, show="headings", style="Library.Treeview")
        headers = {"id": "ID", "nombre": "Nombre", "cedula": "Cédula", "telefono": "Teléfono", "email": "Correo", "direccion": "Dirección", "fecha": "Registro"}
        widths = {"id": 50, "nombre": 185, "cedula": 115, "telefono": 110, "email": 180, "direccion": 180, "fecha": 135}
        for col in columnas:
            self.tabla.heading(col, text=headers[col])
            self.tabla.column(col, width=widths[col], anchor="w" if col in ("nombre", "email", "direccion") else "center")

        sy = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        sx = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=(14, 0))
        sy.grid(row=0, column=1, sticky="ns", pady=(14, 0), padx=(0, 10))
        sx.grid(row=1, column=0, sticky="ew", padx=(12, 0), pady=(0, 12))
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_cliente)

    def _datos_formulario(self):
        datos = [self.campos[k].get().strip() for k in ("nombre", "cedula", "telefono", "email", "direccion")]
        if not datos[0]:
            raise ValueError("El nombre completo es obligatorio.")
        if datos[3] and "@" not in datos[3]:
            raise ValueError("El correo electrónico no tiene un formato válido.")
        return datos

    def guardar(self) -> None:
        try:
            registrar_cliente(*self._datos_formulario())
            messagebox.showinfo("Registro correcto", "El cliente fue registrado correctamente.")
            self.limpiar_formulario()
            self.cargar_clientes()
        except Exception as exc:
            messagebox.showerror("No fue posible registrar", str(exc))

    def actualizar(self) -> None:
        if self.cliente_id is None:
            messagebox.showwarning("Seleccione un cliente", "Seleccione el cliente que desea actualizar.")
            return
        try:
            actualizar_cliente(self.cliente_id, *self._datos_formulario())
            messagebox.showinfo("Actualización correcta", "El cliente fue actualizado correctamente.")
            self.limpiar_formulario()
            self.cargar_clientes()
        except Exception as exc:
            messagebox.showerror("No fue posible actualizar", str(exc))

    def eliminar(self) -> None:
        if self.cliente_id is None:
            messagebox.showwarning("Seleccione un cliente", "Seleccione el cliente que desea eliminar.")
            return
        if not messagebox.askyesno("Confirmar eliminación", "¿Desea eliminar el cliente seleccionado?"):
            return
        try:
            eliminar_cliente(self.cliente_id)
            messagebox.showinfo("Cliente eliminado", "El cliente fue eliminado correctamente.")
            self.limpiar_formulario()
            self.cargar_clientes()
        except Exception as exc:
            messagebox.showerror("No fue posible eliminar", str(exc))

    def buscar(self) -> None:
        termino = self.txt_buscar.get().strip()
        self._llenar_tabla(buscar_cliente(termino) if termino else ver_clientes())

    def cargar_clientes(self) -> None:
        self.txt_buscar.delete(0, "end")
        self._llenar_tabla(ver_clientes())

    def _llenar_tabla(self, clientes) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for c in clientes:
            self.tabla.insert("", "end", values=(
                c["id"], c["nombre_completo"], c["cedula"] or "", c["telefono"] or "",
                c["email"] or "", c["direccion"] or "", c["fecha_registro"] or "",
            ))

    def seleccionar_cliente(self, _event=None) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.cliente_id = int(valores[0])
        for clave, valor in zip(self.campos, valores[1:6]):
            self.campos[clave].delete(0, "end")
            self.campos[clave].insert(0, valor)

    def limpiar_formulario(self) -> None:
        self.cliente_id = None
        for entry in self.campos.values():
            entry.delete(0, "end")
        for item in self.tabla.selection():
            self.tabla.selection_remove(item)
