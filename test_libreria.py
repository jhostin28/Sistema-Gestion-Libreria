"""Ejecuta la suite completa de pruebas del Sistema de Librería."""
import unittest


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("tests")
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if resultado.wasSuccessful() else 1)
