import sys
import unittest


class LoadTest(unittest.TestCase):
    def test_package(self):
        try:
            import mashmaestro

            modulename = mashmaestro.__name__
            if modulename not in sys.modules:
                self.fail("Failed to import")
            else:
                self.assertTrue(True)
        except Exception:
            self.fail("failed to import package")
