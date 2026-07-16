import os
import sqlite3
from pathlib import Path
from sqlite3 import Connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_FILE = Path(os.environ.get("LIBRERIA_DB_FILE", PROJECT_ROOT / "libreria.db"))


def get_connection() -> Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables() -> None:
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nombre TEXT,
        rol TEXT DEFAULT 'empleado'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS libro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        categoria TEXT,
        isbn TEXT,
        cantidad_disponible INTEGER NOT NULL DEFAULT 0,
        precio_venta REAL DEFAULT 0.0,
        precio_alquiler REAL DEFAULT 0.0,
        estado TEXT DEFAULT 'activo'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS cliente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        cedula TEXT,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        fecha_registro TEXT DEFAULT (datetime('now','localtime'))
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha TEXT DEFAULT (datetime('now','localtime')),
        monto_total REAL DEFAULT 0.0,
        FOREIGN KEY(cliente_id) REFERENCES cliente(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        libro_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY(venta_id) REFERENCES venta(id),
        FOREIGN KEY(libro_id) REFERENCES libro(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS alquiler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        fecha_prestamo TEXT DEFAULT (datetime('now','localtime')),
        fecha_devolucion_prevista TEXT,
        fecha_devolucion_real TEXT,
        estado TEXT DEFAULT 'activo',
        FOREIGN KEY(cliente_id) REFERENCES cliente(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS detalle_alquiler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alquiler_id INTEGER NOT NULL,
        libro_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        FOREIGN KEY(alquiler_id) REFERENCES alquiler(id),
        FOREIGN KEY(libro_id) REFERENCES libro(id)
    )
    """)

    # Evitan duplicados cuando el dato fue suministrado.
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_libro_isbn ON libro(isbn) WHERE isbn IS NOT NULL AND TRIM(isbn) <> ''")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_cliente_cedula ON cliente(cedula) WHERE cedula IS NOT NULL AND TRIM(cedula) <> ''")

    c.execute("SELECT COUNT(*) FROM usuario WHERE username = 'admin'")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO usuario (username, password, nombre, rol) VALUES (?, ?, ?, ?)",
            ("admin", "1234", "Administrador", "admin"),
        )

    conn.commit()
    conn.close()
