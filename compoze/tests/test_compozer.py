import unittest
import os
import tempfile

here = os.path.abspath(os.path.dirname(__file__))


class CompozerTests(unittest.TestCase):

    def _getTargetClass(self):
        from compoze.compozer import Compozer
        return Compozer

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_empty_argv_raises(self):
        self.assertRaises(ValueError, self._makeOne, argv=[])

