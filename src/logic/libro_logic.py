import sqlite3

from src.data.database_mgr import get_connection


def _validar_datos(titulo, autor, cantidad, precio_venta, precio_alquiler) -> None:
    if not str(titulo).strip() or not str(autor).strip():
        raise ValueError("El título y el autor son obligatorios.")
    if int(cantidad) < 0:
        raise ValueError("La cantidad disponible no puede ser negativa.")
    if float(precio_venta) < 0 or float(precio_alquiler) < 0:
        raise ValueError("Los precios no pueden ser negativos.")


def registrar_libro(titulo, autor, categoria, isbn, cantidad, precio_venta, precio_alquiler):
    _validar_datos(titulo, autor, cantidad, precio_venta, precio_alquiler)
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO libro (titulo, autor, categoria, isbn, cantidad_disponible, precio_venta, precio_alquiler)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            titulo.strip(), autor.strip(), categoria.strip(), isbn.strip(), int(cantidad),
            float(precio_venta), float(precio_alquiler),
        ))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if "isbn" in str(exc).lower():
            raise ValueError("Ya existe un libro registrado con ese ISBN.") from exc
        raise
    finally:
        conn.close()


def ver_libros():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM libro WHERE estado = 'activo' ORDER BY id").fetchall()
    finally:
        conn.close()


def buscar_libro(termino):
    conn = get_connection()
    try:
        patron = f"%{termino}%"
        return conn.execute("""
            SELECT * FROM libro
            WHERE estado = 'activo' AND (titulo LIKE ? OR autor LIKE ? OR isbn LIKE ?)
            ORDER BY id
        """, (patron, patron, patron)).fetchall()
    finally:
        conn.close()


def obtener_libro_por_id(libro_id):
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM libro WHERE id = ? AND estado = 'activo'", (libro_id,)).fetchone()
    finally:
        conn.close()


def actualizar_libro(libro_id, titulo, autor, categoria, isbn, cantidad, precio_venta, precio_alquiler):
    _validar_datos(titulo, autor, cantidad, precio_venta, precio_alquiler)
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            UPDATE libro
            SET titulo=?, autor=?, categoria=?, isbn=?, cantidad_disponible=?,
                precio_venta=?, precio_alquiler=?
            WHERE id=? AND estado='activo'
        """, (
            titulo.strip(), autor.strip(), categoria.strip(), isbn.strip(), int(cantidad),
            float(precio_venta), float(precio_alquiler), int(libro_id),
        ))
        if c.rowcount == 0:
            raise ValueError("El libro seleccionado no existe o está inactivo.")
        conn.commit()
        return True
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if "isbn" in str(exc).lower():
            raise ValueError("Ya existe otro libro registrado con ese ISBN.") from exc
        raise
    finally:
        conn.close()


def eliminar_libro(libro_id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("UPDATE libro SET estado = 'inactivo' WHERE id = ? AND estado='activo'", (int(libro_id),))
        if c.rowcount == 0:
            raise ValueError("El libro seleccionado no existe o ya fue eliminado.")
        conn.commit()
        return True
    finally:
        conn.close()


def actualizar_stock(libro_id, cantidad_delta, conn=None):
    cerrar = conn is None
    if cerrar:
        conn = get_connection()
    try:
        c = conn.cursor()
        c.execute(
            "UPDATE libro SET cantidad_disponible = cantidad_disponible + ? WHERE id = ?",
            (int(cantidad_delta), int(libro_id)),
        )
        if cerrar:
            conn.commit()
    finally:
        if cerrar:
            conn.close()
