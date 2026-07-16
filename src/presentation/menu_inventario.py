from src.logic.libro_logic import (
    registrar_libro, ver_libros, buscar_libro,
    obtener_libro_por_id, actualizar_libro, eliminar_libro
)


def mostrar_libros(libros):
    if not libros:
        print("\n  (Sin resultados)")
        return
    print(f"\n{'ID':<5} {'Título':<30} {'Autor':<20} {'Categoría':<15} {'Stock':<7} {'P.Venta':>10} {'P.Alquiler':>11}")
    print("-" * 105)
    for l in libros:
        print(f"{l['id']:<5} {l['titulo']:<30} {l['autor']:<20} {(l['categoria'] or '-'):<15} "
              f"{l['cantidad_disponible']:<7} {l['precio_venta']:>10.2f} {l['precio_alquiler']:>11.2f}")


def menu_inventario(usuario):
    while True:
        print("\n" + "=" * 45)
        print("         MÓDULO DE INVENTARIO")
        print("=" * 45)
        print("  1. Ver todos los libros")
        print("  2. Buscar libro")
        print("  3. Registrar nuevo libro")
        if usuario["rol"] == "admin":
            print("  4. Actualizar libro")
            print("  5. Eliminar libro")
        print("  0. Volver al menú principal")
        print("-" * 45)
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            libros = ver_libros()
            mostrar_libros(libros)

        elif opcion == "2":
            termino = input("  Buscar por título, autor o ISBN: ").strip()
            libros = buscar_libro(termino)
            mostrar_libros(libros)

        elif opcion == "3":
            print("\n--- REGISTRAR LIBRO ---")
            titulo = input("  Título: ").strip()
            autor = input("  Autor: ").strip()
            categoria = input("  Categoría: ").strip()
            isbn = input("  ISBN: ").strip()
            try:
                cantidad = int(input("  Cantidad disponible: ").strip())
                precio_venta = float(input("  Precio de venta (RD$): ").strip())
                precio_alquiler = float(input("  Precio de alquiler (RD$): ").strip())
            except ValueError:
                print("\n✘ Valores numéricos inválidos.")
                continue
            if titulo and autor:
                registrar_libro(titulo, autor, categoria, isbn, cantidad, precio_venta, precio_alquiler)
            else:
                print("\n✘ Título y autor son obligatorios.")

        elif opcion == "4" and usuario["rol"] == "admin":
            try:
                libro_id = int(input("  ID del libro a actualizar: ").strip())
            except ValueError:
                print("\n✘ ID inválido.")
                continue
            libro = obtener_libro_por_id(libro_id)
            if not libro:
                print("\n✘ Libro no encontrado.")
                continue
            print(f"  Editando: {libro['titulo']} (Enter para mantener valor actual)")
            titulo = input(f"  Título [{libro['titulo']}]: ").strip() or libro['titulo']
            autor = input(f"  Autor [{libro['autor']}]: ").strip() or libro['autor']
            categoria = input(f"  Categoría [{libro['categoria']}]: ").strip() or libro['categoria']
            isbn = input(f"  ISBN [{libro['isbn']}]: ").strip() or libro['isbn']
            try:
                cant_str = input(f"  Cantidad [{libro['cantidad_disponible']}]: ").strip()
                cantidad = int(cant_str) if cant_str else libro['cantidad_disponible']
                pv_str = input(f"  Precio venta [{libro['precio_venta']}]: ").strip()
                precio_venta = float(pv_str) if pv_str else libro['precio_venta']
                pa_str = input(f"  Precio alquiler [{libro['precio_alquiler']}]: ").strip()
                precio_alquiler = float(pa_str) if pa_str else libro['precio_alquiler']
            except ValueError:
                print("\n✘ Valores numéricos inválidos.")
                continue
            actualizar_libro(libro_id, titulo, autor, categoria, isbn, cantidad, precio_venta, precio_alquiler)

        elif opcion == "5" and usuario["rol"] == "admin":
            try:
                libro_id = int(input("  ID del libro a eliminar: ").strip())
            except ValueError:
                print("\n✘ ID inválido.")
                continue
            libro = obtener_libro_por_id(libro_id)
            if not libro:
                print("\n✘ Libro no encontrado.")
                continue
            confirmar = input(f"  ¿Eliminar '{libro['titulo']}'? (s/n): ").strip().lower()
            if confirmar == "s":
                eliminar_libro(libro_id)

        elif opcion == "0":
            break
        else:
            print("\n✘ Opción no válida.")
