from src.data.database_mgr import get_connection


def registrar_venta(cliente_id, items):
    if not items:
        raise ValueError("La venta debe incluir al menos un libro.")
    conn = get_connection()
    try:
        c = conn.cursor()
        cliente = c.execute("SELECT id FROM cliente WHERE id=?", (int(cliente_id),)).fetchone()
        if cliente is None:
            raise ValueError("El cliente seleccionado no existe.")

        detalles = []
        monto_total = 0.0
        for item in items:
            libro_id = int(item["libro_id"])
            cantidad = int(item["cantidad"])
            if cantidad <= 0:
                raise ValueError("Las cantidades deben ser mayores que cero.")
            libro = c.execute(
                "SELECT cantidad_disponible, precio_venta, titulo FROM libro WHERE id=? AND estado='activo'",
                (libro_id,),
            ).fetchone()
            if not libro or libro["cantidad_disponible"] < cantidad:
                return False
            precio = float(libro["precio_venta"])
            subtotal = precio * cantidad
            monto_total += subtotal
            detalles.append((libro_id, cantidad, precio, subtotal))

        c.execute("INSERT INTO venta (cliente_id, monto_total) VALUES (?, ?)", (int(cliente_id), monto_total))
        venta_id = c.lastrowid
        for libro_id, cantidad, precio, subtotal in detalles:
            c.execute("""
                INSERT INTO detalle_venta (venta_id, libro_id, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (venta_id, libro_id, cantidad, precio, subtotal))
            c.execute(
                "UPDATE libro SET cantidad_disponible=cantidad_disponible-? WHERE id=?",
                (cantidad, libro_id),
            )
        conn.commit()
        return venta_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ver_ventas():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT v.id, c.nombre_completo, v.fecha, v.monto_total
            FROM venta v LEFT JOIN cliente c ON v.cliente_id=c.id
            ORDER BY v.id DESC
        """).fetchall()
    finally:
        conn.close()


def ver_detalle_venta(venta_id):
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT dv.id, l.titulo, dv.cantidad, dv.precio_unitario, dv.subtotal
            FROM detalle_venta dv JOIN libro l ON dv.libro_id=l.id
            WHERE dv.venta_id=?
        """, (int(venta_id),)).fetchall()
    finally:
        conn.close()


def reporte_ventas():
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT COUNT(*) AS total_ventas, COALESCE(SUM(monto_total),0) AS ingresos_totales,
                   COALESCE(MAX(monto_total),0) AS venta_mayor,
                   COALESCE(MIN(monto_total),0) AS venta_menor
            FROM venta
        """).fetchone()
    finally:
        conn.close()
