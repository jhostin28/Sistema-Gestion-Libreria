from src.logic.alquiler_logic import (
    registrar_alquiler, ver_alquileres,
    registrar_devolucion, ver_detalle_alquiler
)
from src.logic.libro_logic import ver_libros, obtener_libro_por_id
from src.logic.cliente_logic import obtener_cliente_por_id, buscar_cliente


def menu_alquileres():
    while True:
        print("\n" + "=" * 45)
        print("         MÓDULO DE ALQUILERES")
        print("=" * 45)
        print("  1. Registrar nuevo alquiler")
        print("  2. Ver alquileres activos")
        print("  3. Registrar devolución")
        print("  4. Ver historial completo")
        print("  0. Volver al menú principal")
        print("-" * 45)
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            _registrar_alquiler()

        elif opcion == "2":
            alquileres = ver_alquileres()
            _mostrar_alquileres([a for a in alquileres if a['estado'] == 'activo'])

        elif opcion == "3":
            try:
                alquiler_id = int(input("  ID del alquiler a devolver: ").strip())
            except ValueError:
                print("\n✘ ID inválido.")
                continue
            detalles = ver_detalle_alquiler(alquiler_id)
            if detalles:
                print(f"\n--- DETALLE ALQUILER #{alquiler_id} ---")
                for d in detalles:
                    print(f"  {d['titulo']} x{d['cantidad']} - RD$ {d['precio_unitario']:,.2f}/u")
            confirmar = input("\n  ¿Confirmar devolución? (s/n): ").strip().lower()
            if confirmar == "s":
                registrar_devolucion(alquiler_id)

        elif opcion == "4":
            alquileres = ver_alquileres()
            _mostrar_alquileres(alquileres)

        elif opcion == "0":
            break
        else:
            print("\n✘ Opción no válida.")


def _mostrar_alquileres(alquileres):
    if not alquileres:
        print("\n  (Sin alquileres)")
        return
    print(f"\n{'ID':<5} {'Cliente':<22} {'Préstamo':<20} {'Dev.Prevista':<14} {'Estado':<10}")
    print("-" * 76)
    for a in alquileres:
        print(f"  {a['id']:<5} {a['nombre_completo']:<22} {a['fecha_prestamo']:<20} "
              f"{(a['fecha_devolucion_prevista'] or '-'):<14} {a['estado']:<10}")


def _registrar_alquiler():
    print("\n--- REGISTRAR ALQUILER ---")

    # Seleccionar cliente (requerido)
    termino = input("  Buscar cliente por nombre o ID: ").strip()
    try:
        cliente_id = int(termino)
        cliente = obtener_cliente_por_id(cliente_id)
        if not cliente:
            print("\n✘ Cliente no encontrado.")
            return
        print(f"  Cliente: {cliente['nombre_completo']}")
    except ValueError:
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

    # Fecha devolución
    fecha_dev = input("  Fecha devolución prevista (YYYY-MM-DD): ").strip()
    if not fecha_dev:
        print("\n✘ La fecha de devolución es obligatoria.")
        return

    # Mostrar libros
    libros = ver_libros()
    if not libros:
        print("\n✘ No hay libros disponibles.")
        return
    print(f"\n{'ID':<5} {'Título':<30} {'Stock':<7} {'P.Alquiler':>12}")
    print("-" * 59)
    for l in libros:
        print(f"  {l['id']:<5} {l['titulo']:<30} {l['cantidad_disponible']:<7} RD$ {l['precio_alquiler']:>8,.2f}")

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

    registrar_alquiler(cliente_id, items, fecha_dev)
