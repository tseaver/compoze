import unittest

class Test_is_archive(unittest.TestCase):

    def _callFUT(self, filename):
        from compoze.pooler import is_archive
        return is_archive(filename)

    def test_empty(self):
        self.assertFalse(self._callFUT(''))

    def test_bogus(self):
        self.assertFalse(self._callFUT('nonesuch.txt'))

    def test_tgz(self):
        self.assertFalse(self._callFUT('foo_tgz'))
        self.assertTrue(self._callFUT('foo.tgz'))

    def test_tar_gz(self):
        self.assertFalse(self._callFUT('foo_tar.gz'))
        self.assertTrue(self._callFUT('foo.tar.gz'))

    def test_tbz(self):
        self.assertFalse(self._callFUT('foo_tbz'))
        self.assertTrue(self._callFUT('foo.tbz'))

    def test_tar_bz2(self):
        self.assertFalse(self._callFUT('foo_tar.bz2'))
        self.assertTrue(self._callFUT('foo.tar.bz2'))

    def test_zip(self):
        self.assertFalse(self._callFUT('foo_zip'))
        self.assertTrue(self._callFUT('foo.zip'))

class PoolerTests(unittest.TestCase):

    _tmpdirs = None

    def tearDown(self):
        if self._tmpdirs is not None:
            import shutil
            for x in self._tmpdirs:
                shutil.rmtree(x)

    def _getTargetClass(self):
        from compoze.pooler import Pooler
        return Pooler

    def _makeValues(self, **kw):
        from optparse import Values
        return Values(kw.copy())

    def _makeOptions(self, path='.', default_verbose=False, *args, **kw):
        default = kw.copy()
        default.setdefault('verbose', default_verbose)
        values = self._makeValues(**default)
        values.path = path
        return values

    def _makeOne(self, *args, **kw):
        logger = kw.pop('logger', None)
        options = self._makeOptions()
        options.path = '.'
        if logger is not None:
            return self._getTargetClass()(options, logger=logger, *args)
        return self._getTargetClass()(options, *args)

    def _makeTempDir(self):
        import tempfile
        if self._tmpdirs is None:
            self._tmpdirs = []
        result = tempfile.mkdtemp()
        self._tmpdirs.append(result)
        return result

    def _makeFile(self, dir, name, text='TEXT'):
        import os
        filename = os.path.join(dir, name)
        f = open(filename, 'w')
        f.write(text)
        f.flush()
        f.close()
        return filename

    def _makeLink(self, source, target, name):
        import os
        s_file = os.path.join(source, name)
        t_file = os.path.join(target, name)
        os.symlink(s_file, t_file)

    def test_ctor_defaults(self):
        import os
        here = os.path.abspath('.')
        values = self._makeValues()
        pooler = self._getTargetClass()(values)
        self.assertEqual(pooler.pool_dir, None)
        self.assertEqual(pooler.release_dir, here)
        self.assertFalse(pooler.options.verbose)

    def test_ctor_uses_global_options_as_default(self):
        g_options = self._makeOptions(path='/tmp/foo',
                                      verbose=True,
                                     )
        pooler = self._getTargetClass()(g_options, '/tmp/bar')
        self.assertEqual(pooler.pool_dir, '/tmp/bar')
        self.assertEqual(pooler.release_dir, '/tmp/foo')
        self.assertTrue(pooler.options.verbose)

    def test_blather_not_verbose(self):
        def _dont_go_here(*args):
            assert 0, args
        pooler = self._makeOne('--quiet', self._makeTempDir(),
                                logger=_dont_go_here)
        pooler.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        logged = []
        pooler = self._makeOne('--verbose', self._makeTempDir(),
                                logger=logged.append)
        pooler.blather('foo')
        self.assertEqual(logged, ['foo'])

    def test_listArchves_empty_releasedir(self):
        release_dir = self._makeTempDir()
        pool_dir = self._makeTempDir()
        pooler = self._makeOne('--quiet',
                                '--path=%s' % release_dir,
                                pool_dir,
                               )
        self.assertEqual(pooler.listArchives(), ([], []))

    def test_listArchves_non_empty_releasedir(self):
        release_dir = self._makeTempDir()
        self._makeFile(release_dir, 'foo.tar.gz')
        pool_dir = self._makeTempDir()
        pooler = self._makeOne('--quiet',
                                '--path=%s' % release_dir,
                                pool_dir,
                               )
        self.assertEqual(pooler.listArchives(),
                        (['foo.tar.gz'], ['foo.tar.gz']))

    def test_listArchves_already_in_pool(self):
        release_dir = self._makeTempDir()
        pool_dir = self._makeTempDir()
        self._makeFile(pool_dir, 'foo.tar.gz')
        self._makeLink(pool_dir, release_dir, 'foo.tar.gz')
        pooler = self._makeOne('--quiet',
                                '--path=%s' % release_dir,
                                pool_dir,
                               )
        self.assertEqual(pooler.listArchives(),
                        (['foo.tar.gz'], []))

    def test_move_to_pool_no_pool_dir_raises(self):
        pooler = self._makeOne()
        self.assertRaises(ValueError, pooler.move_to_pool)

    def test_move_to_pool_no_archives_in_release_dir_raises(self):
        release_dir = self._makeTempDir()
        pool_dir = self._makeTempDir()
        pooler = self._makeOne('--quiet',
                                '--path=%s' % release_dir,
                                pool_dir,
                               )
        self.assertRaises(ValueError, pooler.move_to_pool)

    def test_move_to_pool_invalid_pool_dir_raises(self):
        release_dir = self._makeTempDir()
        self._makeFile(release_dir, 'foo.tar.gz')
        pool_dir = self._makeTempDir()
        pooler = self._makeOne('--quiet',
                                '--path=%s' % release_dir,
                                self._makeFile(pool_dir, 'foolish'),
                               )
        self.assertRaises(ValueError, pooler.move_to_pool)

    def test_move_to_pool_creates_pool_dir(self):
        import os
        release_dir = self._makeTempDir()
        source = self._makeFile(release_dir, 'foo.tar.gz')
        pool_dir = self._makeTempDir()
        newdir = os.path.join(pool_dir, 'newdir')
        pooler = self._makeOne('--quiet',
                                '--path=%s' % release_dir,
                                newdir,
                               )
        pooler.move_to_pool()

        self.assertTrue(os.path.isdir(newdir))
        self.assertTrue(os.path.isfile(os.path.join(newdir, 'foo.tar.gz')))
        self.assertTrue(os.path.islink(source))

    def test_move_to_pool_existing_in_pool_dir(self):
        import os
        release_dir = self._makeTempDir()
        source = self._makeFile(release_dir, 'foo.tar.gz', 'SOURCE')
        pool_dir = self._makeTempDir()
        target = self._makeFile(pool_dir, 'foo.tar.gz', 'TARGET')
        pooler = self._makeOne('--quiet',
                                '--path=%s' % release_dir,
                                pool_dir,
                               )
        pooler.move_to_pool()

        self.assertTrue(os.path.isfile(target))
        self.assertEqual(open(target).read(), 'TARGET') # not replaced
        self.assertTrue(os.path.islink(source))
