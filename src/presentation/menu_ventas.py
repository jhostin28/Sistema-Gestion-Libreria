from src.logic.venta_logic import registrar_venta, ver_ventas, ver_detalle_venta, reporte_ventas
from src.logic.libro_logic import ver_libros, obtener_libro_por_id
from src.logic.cliente_logic import ver_clientes, obtener_cliente_por_id


def menu_ventas():
    while True:
        print("\n" + "=" * 45)
        print("         MÓDULO DE VENTAS")
        print("=" * 45)
        print("  1. Registrar nueva venta")
        print("  2. Ver historial de ventas")
        print("  3. Ver detalle de una venta")
        print("  4. Reporte de ventas")
        print("  0. Volver al menú principal")
        print("-" * 45)
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            _registrar_venta()

        elif opcion == "2":
            ventas = ver_ventas()
            if not ventas:
                print("\n  (Sin ventas registradas)")
            else:
                print(f"\n{'ID':<5} {'Cliente':<25} {'Fecha':<22} {'Total':>12}")
                print("-" * 70)
                for v in ventas:
                    cliente = v['nombre_completo'] or 'Sin cliente'
                    print(f"{v['id']:<5} {cliente:<25} {v['fecha']:<22} RD$ {v['monto_total']:>10,.2f}")

        elif opcion == "3":
            try:
                venta_id = int(input("  ID de la venta: ").strip())
            except ValueError:
                print("\n✘ ID inválido.")
                continue
            detalles = ver_detalle_venta(venta_id)
            if not detalles:
                print("\n✘ Venta no encontrada.")
            else:
                print(f"\n--- DETALLE VENTA #{venta_id} ---")
                print(f"{'Título':<30} {'Cant':>5} {'P.Unit':>10} {'Subtotal':>12}")
                print("-" * 62)
                total = 0
                for d in detalles:
                    print(f"{d['titulo']:<30} {d['cantidad']:>5} {d['precio_unitario']:>10.2f} {d['subtotal']:>12.2f}")
                    total += d['subtotal']
                print("-" * 62)
                print(f"{'TOTAL':>47} RD$ {total:>10,.2f}")

        elif opcion == "4":
            rep = reporte_ventas()
            print("\n--- REPORTE GENERAL DE VENTAS ---")
            print(f"  Total de ventas:     {rep['total_ventas']}")
            print(f"  Ingresos totales:    RD$ {(rep['ingresos_totales'] or 0):,.2f}")
            print(f"  Venta mayor:         RD$ {(rep['venta_mayor'] or 0):,.2f}")
            print(f"  Venta menor:         RD$ {(rep['venta_menor'] or 0):,.2f}")

        elif opcion == "0":
            break
        else:
            print("\n✘ Opción no válida.")


def _registrar_venta():
    print("\n--- REGISTRAR VENTA ---")

    # Seleccionar cliente (opcional)
    usar_cliente = input("  ¿Asociar a un cliente? (s/n): ").strip().lower()
    cliente_id = None
    if usar_cliente == "s":
        termino = input("  Buscar cliente por nombre o ID: ").strip()
        try:
            cliente_id = int(termino)
            cliente = obtener_cliente_por_id(cliente_id)
            if not cliente:
                print("\n✘ Cliente no encontrado.")
                return
            print(f"  Cliente: {cliente['nombre_completo']}")
        except ValueError:
            from src.logic.cliente_logic import buscar_cliente
            clientes = buscar_cliente(termino)
            if not clientes:
                print("\n✘ No se encontraron clientes.")
                return
            print(f"\n{'ID':<5} {'Nombre':<25}")
            for c in clientes:
                print(f"  {c['id']:<5} {c['nombre_completo']}")
            try:
                cliente_id = int(input("  Seleccione ID del cliente: ").strip())
            except ValueError:
                print("\n✘ ID inválido.")
                return

    # Mostrar libros disponibles
    libros = ver_libros()
    if not libros:
        print("\n✘ No hay libros disponibles.")
        return
    print(f"\n{'ID':<5} {'Título':<30} {'Stock':<7} {'Precio':>10}")
    print("-" * 57)
    for l in libros:
        print(f"  {l['id']:<5} {l['titulo']:<30} {l['cantidad_disponible']:<7} RD$ {l['precio_venta']:>8,.2f}")

    # Agregar items
    items = []
    while True:
        try:
            libro_id = int(input("\n  ID del libro (0 para terminar): ").strip())
        except ValueError:
            print("  ✘ ID inválido.")
            continue
        if libro_id == 0:
            break
        libro = obtener_libro_por_id(libro_id)
        if not libro:
            print("  ✘ Libro no encontrado.")
            continue
        try:
            cantidad = int(input(f"  Cantidad (disponible: {libro['cantidad_disponible']}): ").strip())
        except ValueError:
            print("  ✘ Cantidad inválida.")
            continue
        if cantidad <= 0 or cantidad > libro['cantidad_disponible']:
            print("  ✘ Cantidad no válida.")
            continue
        items.append({"libro_id": libro_id, "cantidad": cantidad})
        print(f"  ✔ Agregado: {libro['titulo']} x{cantidad}")

    if not items:
        print("\n✘ No se agregaron libros.")
        return

    registrar_venta(cliente_id, items)
