import unittest
import os

here = os.path.abspath(os.path.dirname(__file__))

class FetcherTests(unittest.TestCase):

    def _getTargetClass(self):
        from compoze.fetcher import Fetcher
        return Fetcher

    def _makeOne(self, *args, **kw):
        from optparse import Values
        default = kw.copy()
        default.setdefault('verbose', False)
        values = Values(default)
        values.path = '.'
        return self._getTargetClass()(values, *args)

    def test_ctor_empty_argv_raises(self):
        self.assertRaises(ValueError, self._makeOne, argv=[])

    def test_ctor_no_download_invalid_path_raises(self):
        self.assertRaises(ValueError, self._makeOne,
                          '--fetch-site-packages',
                          '--path=%s' % __file__,
                         )

    def test_ctor_default_index_url_cheeseshop(self):
        tested = self._makeOne('--fetch-site-packages')
        self.assertEqual(tested.options.index_urls,
                         ['http://pypi.python.org/simple'])
