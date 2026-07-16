# Sistema de Gestión de Librería

Aplicación de escritorio en Python para administrar libros, clientes, ventas y alquileres. Utiliza **CustomTkinter** para la interfaz gráfica y **SQLite** para la persistencia de datos.

## Funcionalidades

- Inicio de sesión conectado a SQLite.
- Panel principal con indicadores.
- Libros: registrar, buscar, actualizar, eliminar y controlar stock.
- Clientes: registrar, buscar, actualizar y eliminar cuando no tienen movimientos asociados.
- Ventas: seleccionar cliente, agregar varios libros, calcular el total, descontar stock y consultar historial.
- Alquileres: registrar préstamos, definir fecha prevista, consultar historial y registrar devoluciones restaurando el stock.
- Reportes: total de libros, clientes, alquileres activos, ingresos por ventas y libros con stock bajo.
- Validaciones de campos obligatorios, valores negativos, ISBN y cédula duplicados, fechas y disponibilidad de inventario.
- Pruebas unitarias automáticas.

## Requisitos

- Python 3.10 o superior.
- Tkinter incluido en la instalación de Python.

Instalar la dependencia gráfica:

```bash
pip install -r requirements.txt
```

## Ejecución

Desde la carpeta del proyecto:

```bash
python main.py
```

Credenciales iniciales:

- Usuario: `admin`
- Contraseña: `1234`

## Pruebas automáticas

```bash
python -m unittest discover -s tests -v
```

## Estructura

```text
main.py
libreria.db
src/
  data/          conexión y creación de tablas
  logic/         reglas de negocio
  gui/           interfaz gráfica
  presentation/  versión original de consola
tests/           pruebas automáticas
```
