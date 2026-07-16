import sqlite3

from src.data.database_mgr import get_connection


def _validar(nombre, email) -> None:
    if not str(nombre).strip():
        raise ValueError("El nombre completo es obligatorio.")
    if email and "@" not in str(email):
        raise ValueError("El correo electrónico no tiene un formato válido.")


def registrar_cliente(nombre, cedula, telefono, email, direccion):
    _validar(nombre, email)
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO cliente (nombre_completo, cedula, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre.strip(), cedula.strip(), telefono.strip(), email.strip(), direccion.strip()))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if "cedula" in str(exc).lower():
            raise ValueError("Ya existe un cliente registrado con esa cédula.") from exc
        raise
    finally:
        conn.close()


def ver_clientes():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM cliente ORDER BY id").fetchall()
    finally:
        conn.close()


def buscar_cliente(termino):
    conn = get_connection()
    try:
        patron = f"%{termino}%"
        return conn.execute("""
            SELECT * FROM cliente
            WHERE nombre_completo LIKE ? OR cedula LIKE ? OR telefono LIKE ?
            ORDER BY id
        """, (patron, patron, patron)).fetchall()
    finally:
        conn.close()


def obtener_cliente_por_id(cliente_id):
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM cliente WHERE id = ?", (int(cliente_id),)).fetchone()
    finally:
        conn.close()


def actualizar_cliente(cliente_id, nombre, cedula, telefono, email, direccion):
    _validar(nombre, email)
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            UPDATE cliente
            SET nombre_completo=?, cedula=?, telefono=?, email=?, direccion=?
            WHERE id=?
        """, (nombre.strip(), cedula.strip(), telefono.strip(), email.strip(), direccion.strip(), int(cliente_id)))
        if c.rowcount == 0:
            raise ValueError("El cliente seleccionado no existe.")
        conn.commit()
        return True
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if "cedula" in str(exc).lower():
            raise ValueError("Ya existe otro cliente registrado con esa cédula.") from exc
        raise
    finally:
        conn.close()


def eliminar_cliente(cliente_id):
    conn = get_connection()
    try:
        cliente_id = int(cliente_id)
        tiene_ventas = conn.execute("SELECT 1 FROM venta WHERE cliente_id=? LIMIT 1", (cliente_id,)).fetchone()
        tiene_alquileres = conn.execute("SELECT 1 FROM alquiler WHERE cliente_id=? LIMIT 1", (cliente_id,)).fetchone()
        if tiene_ventas or tiene_alquileres:
            raise ValueError("No se puede eliminar un cliente con ventas o alquileres registrados.")
        c = conn.cursor()
        c.execute("DELETE FROM cliente WHERE id=?", (cliente_id,))
        if c.rowcount == 0:
            raise ValueError("El cliente seleccionado no existe.")
        conn.commit()
        return True
    finally:
        conn.close()
