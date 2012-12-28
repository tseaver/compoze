import unittest

class _ArchiveTests:

    _tmpdirs = ()

    def tearDown(self):
        import shutil
        for x in self._tmpdirs:
            shutil.rmtree(x, ignore_errors=True)

    def _makeOne(self):
        return self._getTargetClass()(self._makeArchive())

    def _makeTempdir(self):
        import tempfile
        if self._tmpdirs == ():
            self._tmpdirs = []
        result = tempfile.mkdtemp()
        self._tmpdirs.append(result)
        return result

    def _fixtureFiles(self):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        fixturedir = os.path.join(here, 'fixtures', 'archive')
        return [{'name':'archive/1.txt',
                 'path':os.path.join(fixturedir, '1.txt')},
                {'name':'archive/folder/2.txt',
                 'path':os.path.join(fixturedir, 'folder', '2.txt')},
               ]

    def test_names(self):
        archive = self._makeOne()
        names = archive.names()
        expected = [ x['name'] for x in self._fixtureFiles() ]
        self.assertEqual(names, expected)

    def test_lines(self):
        archive = self._makeOne()
        name = self._fixtureFiles()[0]['name']
        lines = archive.lines(name)
        self.assertEqual(lines[:2],
                         [b'This is the first line of text file 1.',
                          b'This is the second line of text file 1.'])

    def test_extract(self):
        import os
        archive = self._makeOne()
        name = self._fixtureFiles()[1]['name']
        target = self._makeTempdir()
        lines = archive.extract(name, target)
        path = os.path.join(target, name)
        expected = ('This is the first line of text file 2.\n'
                    'This is the second line of text file 2.\n')
        with open(path) as f:
            self.assertEqual(f.read(), expected)

    def test_extractall(self):
        import os
        archive = self._makeOne()
        target = self._makeTempdir()
        archive.extractall(target)
        name = self._fixtureFiles()[0]['name']
        path = os.path.join(target, name)
        expected = ('This is the first line of text file 1.\n'
                    'This is the second line of text file 1.\n')
        with open(path) as f:
            self.assertEqual(f.read(), expected)
        name = self._fixtureFiles()[1]['name']
        path = os.path.join(target, name)
        expected = ('This is the first line of text file 2.\n'
                    'This is the second line of text file 2.\n')
        with open(path) as f:
            self.assertEqual(f.read(), expected)

    def test_close_disables_other_methods(self):
        archive = self._makeOne()
        archive.close()
        self.assertRaises(IOError, archive.names)
        name = self._fixtureFiles()[1]['name']
        self.assertRaises(IOError, archive.lines, name)
        self.assertRaises(IOError, archive.extract, name, self._makeTempdir())

class ZipArchiveTests(_ArchiveTests, unittest.TestCase):

    def _getTargetClass(self):
        from compoze.indexer import ZipArchive
        return ZipArchive

    def _getPrefixes(self, path):
        prefixes = []
        elements = path.split('/')
        start = elements.index('archive')
        for i in range(start + 1, len(elements)):
            prefixes.append('/'.join(elements[start:i]) + '/')
        return prefixes

    def _makeArchive(self):
        import os
        import zipfile
        tmpdir = self._makeTempdir()
        filename = os.path.join(tmpdir, 'archive.zip')
        archive = zipfile.ZipFile(filename, 'w')
        for data in self._fixtureFiles():
            for prefix in self._getPrefixes(data['path']):
                if prefix not in archive.namelist():
                    archive.writestr(prefix, '')
            archive.write(data['path'], data['name'])
        archive.close()
        return filename

    def test_names(self):
        # Override to deal with having directories stored.
        archive = self._makeOne()
        names = archive.names()
        expected = []
        for x in self._fixtureFiles():
            for prefix in self._getPrefixes(x['name']):
                if prefix not in expected:
                    expected.append(prefix)
            expected.append(x['name'])
        self.assertEqual(names, sorted(expected))

    def test_extract_dirs(self):
        import os
        archive = self._makeOne()
        target = self._makeTempdir()
        name = self._fixtureFiles()[1]['name']
        for prefix in self._getPrefixes(name):
            archive.extract(prefix, target)
            self.assertTrue(os.path.isdir(os.path.join(target, prefix)))

class TarGzArchiveTests(_ArchiveTests, unittest.TestCase):

    def _getTargetClass(self):
        from compoze.indexer import TarArchive
        return TarArchive

    def _makeArchive(self):
        import os
        import tarfile
        tmpdir = self._makeTempdir()
        filename = os.path.join(tmpdir, 'archive.tgz')
        archive = tarfile.open(filename, 'w:gz')
        try:
            for data in self._fixtureFiles():
                archive.add(data['path'], data['name'])
        finally:
            archive.close()
        return filename

class TarBz2ArchiveTests(_ArchiveTests, unittest.TestCase):

    def _getTargetClass(self):
        from compoze.indexer import TarArchive
        return TarArchive

    def _makeArchive(self):
        import os
        import tarfile
        tmpdir = self._makeTempdir()
        filename = os.path.join(tmpdir, 'archive.tar.bz2')
        archive = tarfile.open(filename, 'w:bz2')
        try:
            for data in self._fixtureFiles():
                archive.add(data['path'], data['name'])
        finally:
            archive.close()
        return filename

class Test__getArchiver(unittest.TestCase):

    def _getFilename(self, base):
        import os
        return os.path.join(os.path.dirname(__file__),
                            'fixtures', 'archive', base)

    def test_tar_gz(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import TarArchive
        fname = self._getFilename('folder.tar.gz')
        self.assertTrue(isinstance(_getArchiver(fname), TarArchive))

    def test_tgz(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import TarArchive
        fname = self._getFilename('folder.tgz')
        self.assertTrue(isinstance(_getArchiver(fname), TarArchive))

    def test_bz2(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import TarArchive
        fname = self._getFilename('folder.bz2')
        self.assertTrue(isinstance(_getArchiver(fname), TarArchive))

    def test_zip(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import ZipArchive
        fname = self._getFilename('folder.zip')
        self.assertTrue(isinstance(_getArchiver(fname), ZipArchive))

    def test_egg(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import ZipArchive
        fname = self._getFilename('folder.egg')
        self.assertTrue(isinstance(_getArchiver(fname), ZipArchive))


class IndexerTests(unittest.TestCase):

    _tmpdir = None

    def tearDown(self):
        if self._tmpdir is not None:
            import shutil
            shutil.rmtree(self._tmpdir)

    def _getTargetClass(self):
        from compoze.indexer import Indexer
        return Indexer

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
        if logger is not None:
            return self._getTargetClass()(options, logger=logger, *args)
        return self._getTargetClass()(options, *args)

    def _makeTempdir(self):
        import tempfile
        result = self._tmpdir = tempfile.mkdtemp()
        return result

    def test_ctor_defaults(self):
        import os
        here = os.path.abspath('.')
        values = self._makeValues()
        indexer = self._getTargetClass()(values)
        self.assertEqual(indexer.path, here)
        self.assertFalse(indexer.options.verbose)
        self.assertEqual(indexer.options.index_name, 'simple')
        self.assertFalse(indexer.options.keep_tempdir)

    def test_ctor_uses_global_options_as_default(self):
        options = self._makeOptions(path='/tmp/foo',
                                    verbose=True,
                                    keep_tempdir=True,
                                   )
        indexer = self._getTargetClass()(options)
        self.assertEqual(indexer.path, '/tmp/foo')
        self.assertTrue(indexer.options.verbose)
        self.assertTrue(indexer.options.keep_tempdir)

    def test_ctor_invalid_path_doesnt_raise(self):
        indexer = self._makeOne('--path=/nonesuch')
        self.assertEqual(indexer.path, '/nonesuch')

    def test_blather_not_verbose(self):
        def _dont_go_here(*args):
            assert 0, args
        indexer = self._makeOne('--quiet',
                                logger=_dont_go_here)
        indexer.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        logged = []
        indexer = self._makeOne('--verbose',
                                logger=logged.append)
        indexer.blather('foo')
        self.assertEqual(logged, ['foo'])

    def test_make_index_invalid_path_raises(self):
        indexer = self._makeOne('--path=/nonesuch')
        self.assertRaises(ValueError, indexer.make_index)

    def test_make_index_index_dir_exists_raises(self):
        import os
        tmpdir = self._makeTempdir()
        os.makedirs(os.path.join(tmpdir, 'exists'))
        indexer = self._makeOne('--path=%s' % tmpdir, '--index-name=exists')
        self.assertRaises(ValueError, indexer.make_index)

    def test_make_index_empty_raises(self):
        tmpdir = self._makeTempdir()
        indexer = self._makeOne('--path=%s' % tmpdir)
        self.assertRaises(ValueError, indexer.make_index)

    def test_make_index_only_non_distributions_raises(self):
        import os
        tmpdir = self._makeTempdir()
        with open(os.path.join(tmpdir, 'not-a-distribution.txt'), 'wb') as f:
            f.write(b'MOVE ALONG')
            f.flush()
        os.makedirs(os.path.join(tmpdir, 'subdir'))
        indexer = self._makeOne('--path=%s' % tmpdir)
        self.assertRaises(ValueError, indexer.make_index)

    def test_make_index_w_distribution(self):
        import os
        import tarfile
        from compoze._compat import BytesIO
        tmpdir = self._makeTempdir()
        filename = os.path.join(tmpdir, 'testpackage-3.14.tar.gz')
        archive = tarfile.TarFile(filename, mode='w')
        buffer = BytesIO()
        buffer.writelines([b'Metadata-Version: 1.0\n',
                           b'Name: testpackage\n',
                           b'Version: 3.14\n',
                          ])
        size = buffer.tell()
        buffer.seek(0)
        info = tarfile.TarInfo('PKG-INFO')
        info.size = size
        archive.addfile(info, buffer)
        archive.close()
        indexer = self._makeOne('--path=%s' % tmpdir)

        indexer.make_index()

        with open(os.path.join(tmpdir, 'simple', 'index.html')) as f:
            top = f.read()
        self.assertTrue('<h1>Package Index</h1>' in top)
        self.assertTrue(
                '<li><a href="testpackage">testpackage</a></li>' in top)
        with open(os.path.join(tmpdir, 'simple', 'testpackage', 'index.html')
                 ) as f:
            sub = f.read()
        self.assertTrue('<h1>testpackage Distributions</h1>' in sub)
        self.assertTrue(
                '<li><a href="../../testpackage-3.14.tar.gz">'
                'testpackage-3.14.tar.gz</a></li>' in sub)

    def test__extractNameVersion_non_archive(self):
        import tempfile
        non_archive = tempfile.NamedTemporaryFile()
        non_archive.write(b'This is a test.\n')
        non_archive.flush()
        tested = self._makeOne()
        self.assertEqual(tested._extractNameVersion(non_archive.name),
                         (None, None))

    def test__extractNameVersion_empty_archive(self):
        import sys
        import tarfile
        import tempfile
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        if sys.version_info[:2] < (2, 7): # 2.6 can't open empty in write mode
            archive = tarfile.TarFile(fileobj=tfile)
        else:                             # 2.7 can't open empty in read mode
            archive = tarfile.TarFile(fileobj=tfile, mode='w')
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         (None, None))

    def test__extractNameVersion_archive_no_egg_info_or_setup(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        buffer = BytesIO()
        buffer.writelines([b'README\n',
                          ])
        size = buffer.tell()
        buffer.seek(0)
        info = tarfile.TarInfo('README.txt')
        info.size = size
        archive.addfile(info, buffer)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         (None, None))

    def test__extractNameVersion_archive_w_pkg_info(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        buffer = BytesIO()
        buffer.writelines([b'Metadata-Version: 1.0\n',
                           b'Name: testpackage\n',
                           b'Version: 3.14\n',
                          ])
        size = buffer.tell()
        buffer.seek(0)
        info = tarfile.TarInfo('testpackage.egg-info/PKG-INFO')
        info.size = size
        archive.addfile(info, buffer)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         ('testpackage', '3.14'))

    def test__extractNameVersion_archive_w_pkg_info_version_first(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        buffer = BytesIO()
        buffer.writelines([b'Metadata-Version: 1.0\n',
                           b'Version: 3.14\n',
                           b'Name: testpackage\n',
                          ])
        size = buffer.tell()
        buffer.seek(0)
        info = tarfile.TarInfo('testpackage.egg-info/PKG-INFO')
        info.size = size
        archive.addfile(info, buffer)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         ('testpackage', '3.14'))

    def test__extractNameVersion_archive_w_nested_setup(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        dinfo = tarfile.TarInfo('testpackage')
        dinfo.type = tarfile.DIRTYPE
        dinfo.mode = 0o777
        archive.addfile(dinfo)
        buffer = BytesIO()
        buffer.write(_DUMMY_SETUP)
        size = buffer.tell()
        buffer.seek(0)
        finfo = tarfile.TarInfo('testpackage/setup.py')
        finfo.size = size
        archive.addfile(finfo, buffer)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         ('testpackage', '3.14'))


    def test__extractNameVersion_archive_w_mulitiple_nested_setups(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        from compoze._compat import must_encode
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        def add_tar_dir(path):
            dinfo = tarfile.TarInfo(path)
            dinfo.type = tarfile.DIRTYPE
            dinfo.mode = 0o777
            archive.addfile(dinfo)
        def add_setup(path):
            buffer = BytesIO()
            buffer.write(_DUMMY_SETUP.replace(b'testpackage',
                                              must_encode(path)))
            size = buffer.tell()
            buffer.seek(0)
            finfo = tarfile.TarInfo('%s/setup.py' % path)
            finfo.size = size
            archive.addfile(finfo, buffer)
        add_tar_dir('testpackage')
        add_tar_dir('testpackage/dir1')
        add_setup('testpackage/dir1')
        add_tar_dir('testpackage/dir2')
        add_setup('testpackage/dir2')
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         ('testpackage/dir1', '3.14'))



    def test__extractNameVersion_archive_w_muli_nested_setup_root_setup(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        from compoze._compat import must_encode
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        def add_tar_dir(path):
            dinfo = tarfile.TarInfo(path)
            dinfo.type = tarfile.DIRTYPE
            dinfo.mode = 0o777
            archive.addfile(dinfo)
        def add_setup(path):
            buffer = BytesIO()
            buffer.write(_DUMMY_SETUP.replace(b'testpackage',
                                              must_encode(path)))
            size = buffer.tell()
            buffer.seek(0)
            finfo = tarfile.TarInfo('%s/setup.py' % path)
            finfo.size = size
            archive.addfile(finfo, buffer)
        add_tar_dir('testpackage')
        add_setup('testpackage')
        add_tar_dir('testpackage/dir1')
        add_setup('testpackage/dir1')
        add_tar_dir('testpackage/dir2')
        add_setup('testpackage/dir2')
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         ('testpackage', '3.14'))


    def test__extractNameVersion_archive_w_setup_at_root(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        dinfo = tarfile.TarInfo('testpackage')
        dinfo.type = tarfile.DIRTYPE
        dinfo.mode = 0o777
        archive.addfile(dinfo)
        buffer = BytesIO()
        buffer.write(_DUMMY_SETUP)
        size = buffer.tell()
        buffer.seek(0)
        finfo = tarfile.TarInfo('setup.py')
        finfo.size = size
        archive.addfile(finfo, buffer)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         ('testpackage', '3.14'))

    def test__extractNameVersion_archive_w_erroring_setup(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        dinfo = tarfile.TarInfo('testpackage')
        dinfo.type = tarfile.DIRTYPE
        dinfo.mode = 0o777
        archive.addfile(dinfo)
        buffer = BytesIO()
        buffer.write(_ERRORING_SETUP)
        size = buffer.tell()
        buffer.seek(0)
        finfo = tarfile.TarInfo('setup.py')
        finfo.size = size
        archive.addfile(finfo, buffer)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         (None, None))

    def test__extractNameVersion_archive_w_noout_setup(self):
        import tarfile
        import tempfile
        from compoze._compat import BytesIO
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        dinfo = tarfile.TarInfo('testpackage')
        dinfo.type = tarfile.DIRTYPE
        dinfo.mode = 0o777
        archive.addfile(dinfo)
        buffer = BytesIO()
        buffer.write(_NOOUT_SETUP)
        size = buffer.tell()
        buffer.seek(0)
        finfo = tarfile.TarInfo('setup.py')
        finfo.size = size
        archive.addfile(finfo, buffer)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         (None, None))

_DUMMY_SETUP = b"""\
print('testpackage')
print('3.14')
"""

_ERRORING_SETUP = b"""\
import sys
sys.exit(1)
"""

_NOOUT_SETUP = b"""\
"""
