import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import src.data.database_mgr as database_mgr
from src.data.database_mgr import create_tables, get_connection
from src.logic.alquiler_logic import registrar_alquiler, registrar_devolucion
from src.logic.auth_logic import login
from src.logic.cliente_logic import actualizar_cliente, eliminar_cliente, registrar_cliente
from src.logic.libro_logic import (
    actualizar_libro,
    buscar_libro,
    eliminar_libro,
    registrar_libro,
    ver_libros,
)
from src.logic.venta_logic import registrar_venta, reporte_ventas


class TestSistemaLibreria(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_mgr.DB_FILE = Path(self.temp_dir.name) / "test_libreria.db"
        create_tables()

    def tearDown(self):
        self.temp_dir.cleanup()

    def crear_libro(self, isbn="978000000001"):
        return registrar_libro("Python práctico", "Ana Pérez", "Programación", isbn, 10, 900, 120)

    def crear_cliente(self, cedula="001-0000001-1"):
        return registrar_cliente("Cliente Prueba", cedula, "809-000-0000", "cliente@correo.com", "Santo Domingo")

    def test_01_login_correcto(self):
        self.assertIsNotNone(login("admin", "1234"))

    def test_02_login_incorrecto(self):
        self.assertIsNone(login("admin", "incorrecta"))

    def test_03_registro_busqueda_y_actualizacion_libro(self):
        libro_id = self.crear_libro()
        resultado = buscar_libro("Python")
        self.assertEqual(len(resultado), 1)
        actualizar_libro(libro_id, "Python avanzado", "Ana Pérez", "Programación", "978000000001", 8, 1000, 150)
        self.assertEqual(ver_libros()[0]["titulo"], "Python avanzado")

    def test_04_rechaza_isbn_duplicado(self):
        self.crear_libro()
        with self.assertRaises(ValueError):
            self.crear_libro()

    def test_05_rechaza_stock_negativo(self):
        with self.assertRaises(ValueError):
            registrar_libro("Libro", "Autor", "Categoría", "978000000002", -1, 100, 20)

    def test_06_registro_actualizacion_y_eliminacion_cliente(self):
        cliente_id = self.crear_cliente()
        actualizar_cliente(cliente_id, "Cliente Actualizado", "001-0000001-1", "809-111-1111", "nuevo@correo.com", "Santiago")
        conn = get_connection()
        cliente = conn.execute("SELECT * FROM cliente WHERE id=?", (cliente_id,)).fetchone()
        conn.close()
        self.assertEqual(cliente["nombre_completo"], "Cliente Actualizado")
        self.assertTrue(eliminar_cliente(cliente_id))

    def test_07_venta_descuenta_stock_y_calcula_total(self):
        cliente_id = self.crear_cliente()
        libro_id = self.crear_libro()
        venta_id = registrar_venta(cliente_id, [{"libro_id": libro_id, "cantidad": 2}])
        self.assertTrue(venta_id)
        conn = get_connection()
        stock = conn.execute("SELECT cantidad_disponible FROM libro WHERE id=?", (libro_id,)).fetchone()[0]
        conn.close()
        self.assertEqual(stock, 8)
        self.assertEqual(reporte_ventas()["ingresos_totales"], 1800)

    def test_08_venta_sin_stock_no_se_registra(self):
        cliente_id = self.crear_cliente()
        libro_id = self.crear_libro()
        self.assertFalse(registrar_venta(cliente_id, [{"libro_id": libro_id, "cantidad": 99}]))
        self.assertEqual(reporte_ventas()["total_ventas"], 0)

    def test_09_alquiler_y_devolucion_restauran_stock(self):
        cliente_id = self.crear_cliente()
        libro_id = self.crear_libro()
        fecha = (date.today() + timedelta(days=7)).isoformat()
        alquiler_id = registrar_alquiler(cliente_id, [{"libro_id": libro_id, "cantidad": 3}], fecha)
        self.assertTrue(alquiler_id)
        conn = get_connection()
        stock_alquilado = conn.execute("SELECT cantidad_disponible FROM libro WHERE id=?", (libro_id,)).fetchone()[0]
        conn.close()
        self.assertEqual(stock_alquilado, 7)
        self.assertTrue(registrar_devolucion(alquiler_id))
        conn = get_connection()
        stock_devuelto = conn.execute("SELECT cantidad_disponible FROM libro WHERE id=?", (libro_id,)).fetchone()[0]
        estado = conn.execute("SELECT estado FROM alquiler WHERE id=?", (alquiler_id,)).fetchone()[0]
        conn.close()
        self.assertEqual(stock_devuelto, 10)
        self.assertEqual(estado, "devuelto")

    def test_10_eliminacion_logica_de_libro(self):
        libro_id = self.crear_libro()
        self.assertTrue(eliminar_libro(libro_id))
        self.assertEqual(len(ver_libros()), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
