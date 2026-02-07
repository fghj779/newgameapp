import importlib
import unittest


class TestScaffold(unittest.TestCase):
    def test_packages_import(self):
        modules = [
            "orbital_colony",
            "orbital_colony.core_physics",
            "orbital_colony.economy_engine",
            "orbital_colony.npc_ai",
            "orbital_colony.rendering_layer",
            "orbital_colony.shared",
        ]
        for name in modules:
            with self.subTest(module=name):
                importlib.import_module(name)


if __name__ == "__main__":
    unittest.main()
