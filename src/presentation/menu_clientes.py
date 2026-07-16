from src.logic.cliente_logic import (
    registrar_cliente, ver_clientes, buscar_cliente,
    obtener_cliente_por_id, actualizar_cliente
)


def mostrar_clientes(clientes):
    if not clientes:
        print("\n  (Sin clientes registrados)")
        return
    print(f"\n{'ID':<5} {'Nombre':<25} {'Cédula':<15} {'Teléfono':<15} {'Email':<25}")
    print("-" * 90)
    for c in clientes:
        print(f"{c['id']:<5} {c['nombre_completo']:<25} {(c['cedula'] or '-'):<15} "
              f"{(c['telefono'] or '-'):<15} {(c['email'] or '-'):<25}")


def menu_clientes():
    while True:
        print("\n" + "=" * 45)
        print("         MÓDULO DE CLIENTES")
        print("=" * 45)
        print("  1. Ver todos los clientes")
        print("  2. Buscar cliente")
        print("  3. Registrar nuevo cliente")
        print("  4. Actualizar cliente")
        print("  0. Volver al menú principal")
        print("-" * 45)
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            clientes = ver_clientes()
            mostrar_clientes(clientes)

        elif opcion == "2":
            termino = input("  Buscar por nombre, cédula o teléfono: ").strip()
            clientes = buscar_cliente(termino)
            mostrar_clientes(clientes)

        elif opcion == "3":
            print("\n--- REGISTRAR CLIENTE ---")
            nombre = input("  Nombre completo: ").strip()
            cedula = input("  Cédula: ").strip()
            telefono = input("  Teléfono: ").strip()
            email = input("  Email: ").strip()
            direccion = input("  Dirección: ").strip()
            if nombre:
                registrar_cliente(nombre, cedula, telefono, email, direccion)
            else:
                print("\n✘ El nombre es obligatorio.")

        elif opcion == "4":
            try:
                cliente_id = int(input("  ID del cliente a actualizar: ").strip())
            except ValueError:
                print("\n✘ ID inválido.")
                continue
            cliente = obtener_cliente_por_id(cliente_id)
            if not cliente:
                print("\n✘ Cliente no encontrado.")
                continue
            print(f"  Editando: {cliente['nombre_completo']} (Enter para mantener valor actual)")
            nombre = input(f"  Nombre [{cliente['nombre_completo']}]: ").strip() or cliente['nombre_completo']
            cedula = input(f"  Cédula [{cliente['cedula']}]: ").strip() or cliente['cedula']
            telefono = input(f"  Teléfono [{cliente['telefono']}]: ").strip() or cliente['telefono']
            email = input(f"  Email [{cliente['email']}]: ").strip() or cliente['email']
            direccion = input(f"  Dirección [{cliente['direccion']}]: ").strip() or cliente['direccion']
            actualizar_cliente(cliente_id, nombre, cedula, telefono, email, direccion)

        elif opcion == "0":
            break
        else:
            print("\n✘ Opción no válida.")
