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
        self.assertEqual(lines[:2], ['This is the first line of text file 1.',
                                     'This is the second line of text file 1.'])

    def test_extract(self):
        import os
        archive = self._makeOne()
        name = self._fixtureFiles()[1]['name']
        target = self._makeTempdir()
        lines = archive.extract(name, target)
        path = os.path.join(target, name)
        expected = ('This is the first line of text file 2.\n'
                    'This is the second line of text file 2.\n')
        self.assertEqual(open(path).read(), expected)

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
            self.failUnless(os.path.isdir(os.path.join(target, prefix)))

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
        for data in self._fixtureFiles():
            archive.add(data['path'], data['name'])
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
        for data in self._fixtureFiles():
            archive.add(data['path'], data['name'])
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
        self.failUnless(isinstance(_getArchiver(fname), TarArchive))

    def test_tgz(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import TarArchive
        fname = self._getFilename('folder.tgz')
        self.failUnless(isinstance(_getArchiver(fname), TarArchive))

    def test_bz2(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import TarArchive
        fname = self._getFilename('folder.bz2')
        self.failUnless(isinstance(_getArchiver(fname), TarArchive))

    def test_zip(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import ZipArchive
        fname = self._getFilename('folder.zip')
        self.failUnless(isinstance(_getArchiver(fname), ZipArchive))

    def test_egg(self):
        from compoze.indexer import _getArchiver
        from compoze.indexer import ZipArchive
        fname = self._getFilename('folder.egg')
        self.failUnless(isinstance(_getArchiver(fname), ZipArchive))


class IndexerTests(unittest.TestCase):

    _tmpdir = None

    def tearDown(self):
        if self._tmpdir is not None:
            import shutil
            shutil.rmtree(self._tmpdir)

    def _getTargetClass(self):
        from compoze.indexer import Indexer
        return Indexer

    def _makeOne(self, *args, **kw):
        logger = kw.pop('logger', None)
        from optparse import Values
        default = kw.copy()
        default.setdefault('verbose', False)
        values = Values(default)
        values.path = '.'
        if logger is not None:
            return self._getTargetClass()(values, logger=logger, *args)
        return self._getTargetClass()(values, *args)

    def _makeTempdir(self):
        import tempfile
        result = self._tmpdir = tempfile.mkdtemp()
        return result

    def test_ctor_invalid_path(self):
        self.assertRaises(ValueError, self._makeOne, '--path=/nonesuch')

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
        f = open(os.path.join(tmpdir, 'not-a-distribution.txt'), 'w')
        f.write('MOVE ALONG')
        f.flush()
        f.close()
        os.makedirs(os.path.join(tmpdir, 'subdir'))
        indexer = self._makeOne('--path=%s' % tmpdir)
        self.assertRaises(ValueError, indexer.make_index)

    def test_make_index_w_distribution(self):
        import os
        import StringIO
        import tarfile
        tmpdir = self._makeTempdir()
        filename = os.path.join(tmpdir, 'testpackage-3.14.tar.gz')
        archive = tarfile.TarFile(filename, mode='w')
        buffer = StringIO.StringIO()
        buffer.writelines(['Metadata-Version: 1.0\n',
                           'Name: testpackage\n',
                           'Version: 3.14\n',
                          ])
        size = buffer.tell()
        buffer.seek(0)
        info = tarfile.TarInfo('PKG-INFO')
        info.size = size
        archive.addfile(info, buffer)
        archive.close()
        indexer = self._makeOne('--path=%s' % tmpdir)

        indexer.make_index()

        top = open(os.path.join(tmpdir, 'simple', 'index.html')).read()
        self.failUnless('<h1>Package Index</h1>' in top)
        self.failUnless(
                '<li><a href="testpackage">testpackage</a></li>' in top)
        sub = open(os.path.join(tmpdir, 'simple', 'testpackage', 'index.html')
                  ).read()
        self.failUnless('<h1>testpackage Distributions</h1>' in sub)
        self.failUnless(
                '<li><a href="../../testpackage-3.14.tar.gz">'
                'testpackage-3.14.tar.gz</a></li>' in sub)

    def test__extractNameVersion_non_archive(self):
        import tempfile
        non_archive = tempfile.NamedTemporaryFile()
        non_archive.write('This is a test.\n')
        non_archive.flush()
        tested = self._makeOne()
        self.assertEqual(tested._extractNameVersion(non_archive.name),
                         (None, None))

    def test__extractNameVersion_archive_no_egg_info_or_setup(self):
        import tarfile
        import tempfile
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile)
        archive.close()
        tfile.flush()
        self.assertEqual(tested._extractNameVersion(tfile.name),
                         (None, None))

    def test__extractNameVersion_archive_w_pkg_info(self):
        import StringIO
        import tarfile
        import tempfile
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        buffer = StringIO.StringIO()
        buffer.writelines(['Metadata-Version: 1.0\n',
                           'Name: testpackage\n',
                           'Version: 3.14\n',
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
        import StringIO
        import tarfile
        import tempfile
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        buffer = StringIO.StringIO()
        buffer.writelines(['Metadata-Version: 1.0\n',
                           'Version: 3.14\n',
                           'Name: testpackage\n',
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
        import StringIO
        import tarfile
        import tempfile
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        dinfo = tarfile.TarInfo('testpackage')
        dinfo.type = tarfile.DIRTYPE
        dinfo.mode = 0777
        archive.addfile(dinfo)
        buffer = StringIO.StringIO()
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

    def test__extractNameVersion_archive_w_setup_at_root(self):
        import StringIO
        import tarfile
        import tempfile
        tested = self._makeOne()
        tfile = tempfile.NamedTemporaryFile(suffix='.tgz')
        archive = tarfile.TarFile(fileobj=tfile, mode='w')
        dinfo = tarfile.TarInfo('testpackage')
        dinfo.type = tarfile.DIRTYPE
        dinfo.mode = 0777
        archive.addfile(dinfo)
        buffer = StringIO.StringIO()
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

_DUMMY_SETUP = """\
print 'testpackage'
print '3.14'
"""
