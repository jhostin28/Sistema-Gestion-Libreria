from datetime import date

from src.data.database_mgr import get_connection


def registrar_alquiler(cliente_id, items, fecha_devolucion_prevista):
    if not items:
        raise ValueError("El alquiler debe incluir al menos un libro.")
    try:
        fecha = date.fromisoformat(fecha_devolucion_prevista)
    except ValueError as exc:
        raise ValueError("La fecha prevista debe usar el formato AAAA-MM-DD.") from exc
    if fecha < date.today():
        raise ValueError("La fecha prevista no puede estar en el pasado.")

    conn = get_connection()
    try:
        c = conn.cursor()
        if c.execute("SELECT id FROM cliente WHERE id=?", (int(cliente_id),)).fetchone() is None:
            raise ValueError("El cliente seleccionado no existe.")

        detalles = []
        for item in items:
            libro_id = int(item["libro_id"])
            cantidad = int(item["cantidad"])
            if cantidad <= 0:
                raise ValueError("Las cantidades deben ser mayores que cero.")
            libro = c.execute(
                "SELECT cantidad_disponible, precio_alquiler FROM libro WHERE id=? AND estado='activo'",
                (libro_id,),
            ).fetchone()
            if not libro or libro["cantidad_disponible"] < cantidad:
                return False
            detalles.append((libro_id, cantidad, float(libro["precio_alquiler"])))

        c.execute(
            "INSERT INTO alquiler (cliente_id, fecha_devolucion_prevista) VALUES (?, ?)",
            (int(cliente_id), fecha_devolucion_prevista),
        )
        alquiler_id = c.lastrowid
        for libro_id, cantidad, precio in detalles:
            c.execute("""
                INSERT INTO detalle_alquiler (alquiler_id, libro_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            """, (alquiler_id, libro_id, cantidad, precio))
            c.execute(
                "UPDATE libro SET cantidad_disponible=cantidad_disponible-? WHERE id=?",
                (cantidad, libro_id),
            )
        conn.commit()
        return alquiler_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ver_alquileres():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT a.id, c.nombre_completo, a.fecha_prestamo,
                   a.fecha_devolucion_prevista, a.fecha_devolucion_real, a.estado
            FROM alquiler a JOIN cliente c ON a.cliente_id=c.id
            ORDER BY a.id DESC
        """).fetchall()
    finally:
        conn.close()


def registrar_devolucion(alquiler_id):
    conn = get_connection()
    try:
        c = conn.cursor()
        alquiler = c.execute(
            "SELECT id FROM alquiler WHERE id=? AND estado='activo'", (int(alquiler_id),)
        ).fetchone()
        if alquiler is None:
            return False
        detalles = c.execute(
            "SELECT libro_id, cantidad FROM detalle_alquiler WHERE alquiler_id=?", (int(alquiler_id),)
        ).fetchall()
        for detalle in detalles:
            c.execute(
                "UPDATE libro SET cantidad_disponible=cantidad_disponible+? WHERE id=?",
                (detalle["cantidad"], detalle["libro_id"]),
            )
        c.execute("""
            UPDATE alquiler
            SET estado='devuelto', fecha_devolucion_real=datetime('now','localtime')
            WHERE id=?
        """, (int(alquiler_id),))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ver_detalle_alquiler(alquiler_id):
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT l.titulo, da.cantidad, da.precio_unitario
            FROM detalle_alquiler da JOIN libro l ON da.libro_id=l.id
            WHERE da.alquiler_id=?
        """, (int(alquiler_id),)).fetchall()
    finally:
        conn.close()
