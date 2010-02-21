import unittest

class CompozePackageIndexTests(unittest.TestCase):

    def _getTargetClass(self):
        from compoze.fetcher import CompozePackageIndex
        return CompozePackageIndex

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        cpi = self._makeOne()
        self.assertEqual(cpi.debug_msgs, [])
        self.assertEqual(cpi.info_msgs, [])
        self.assertEqual(cpi.warn_msgs, [])

    def test_debug(self):
        cpi = self._makeOne()
        cpi.debug('foo')
        self.assertEqual(cpi.debug_msgs, [('foo', ())])

    def test_info(self):
        cpi = self._makeOne()
        cpi.info('foo')
        self.assertEqual(cpi.info_msgs, [('foo', ())])

    def test_warn(self):
        cpi = self._makeOne()
        cpi.warn('foo')
        self.assertEqual(cpi.warn_msgs, [('foo', ())])
