""" compoze index -- build a Python package index in a directory

"""
import optparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
import StringIO

from setuptools.package_index import PackageIndex

class TarArchive:
    def __init__(self, filename):
        self.filename = filename
        self.tar = tarfile.open(filename, 'r')

    def names(self):
        return self.tar.getnames()
        
    def lines(self, name):
        return [ x.rstrip() for x in self.tar.extractfile(name).readlines() ]

    def extract(self, name, tempdir):
        return self.tar.extract(name, tempdir)

    def close(self):
        self.tar.close()

class ZipArchive:
    closed = False
    def __init__(self, filename):
        self.filename = filename
        self.zipf = zipfile.ZipFile(filename, 'r')

    def names(self):
        if self.closed:
            raise IOError('closed')
        return self.zipf.namelist()
        
    def lines(self, name):
        if self.closed:
            raise IOError('closed')
        return self.zipf.read(name).split('\n')

    def extract(self, name, tempdir):
        if self.closed:
            raise IOError('closed')
        data = self.zipf.read(name)
        thedir = os.path.split(name)[0]
        os.makedirs(os.path.join(tempdir, thedir))
        fn = os.path.join(tempdir, name)
        f = open(fn, 'wb')
        f.write(data)
            
    def close(self):
        self.zipf.close()
        self.closed = True


_ARCHIVERS = [('.tar.gz', TarArchive),
              ('.tgz', TarArchive),
              ('.bz2', TarArchive),
              ('.zip', ZipArchive),
              ('.egg', ZipArchive),
             ]

def _getArchiver(filename):
    for suffix, archiver in _ARCHIVERS:
        if filename.endswith(suffix):
            return archiver(filename)

class Indexer:

    def __init__(self, global_options, *argv):
    
        argv = list(argv)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] app_egg_name [other_egg_name]*")

        parser.add_option(
            '-p', '--path',
            action='store',
            dest='path',
            default=global_options.path,
            help="Specify the path in which to build the index")

        parser.add_option(
            '-n', '--index-name',
            action='store',
            dest='index_name',
            default='simple',
            help="Specify the name of the index subdirectory")

        parser.add_option(
            '-q', '--quiet',
            action='store_false',
            dest='verbose',
            help="Run quietly")

        parser.add_option(
            '-v', '--verbose',
            action='store_true',
            dest='verbose',
            default=global_options.verbose,
            help="Show progress")

        parser.add_option(
            '-k', '--keep-tempdir',
            action='store_true',
            dest='keep_tempdir',
            default=False,
            help="Keep temporary directory")

        options, args = parser.parse_args(argv)

        self.options = options

        path = os.path.abspath(os.path.expanduser(options.path))

        if not os.path.isdir(path):
            msg = StringIO.StringIO()
            msg.write('Not a directory: %s\n\n' % path)
            msg.write(parser.format_help())
            raise ValueError(msg.getvalue())

        self.path = path

    def __call__(self):

        self.tmpdir = tempfile.mkdtemp(dir='.')
        try:
            self.make_index()
        finally:
            if not self.options.keep_tempdir:
                shutil.rmtree(self.tmpdir)

    def make_index(self, path=None):

        if path is None:
            path = self.path

        index_dir = os.path.join(path, self.options.index_name)
        self._blather('=' * 50)
        self._blather('Building index: %s' % index_dir)
        self._blather('=' * 50)

        projects = {}

        candidates = os.listdir(path)
        for candidate in candidates:
            cname = os.path.join(path, candidate)
            if not os.path.isfile(cname):
                continue
            project, revision = self._extractNameVersion(cname)
            if project is not None:
                projects.setdefault(project, []).append((revision, candidate))

        items = projects.items()
        items.sort()

        if os.path.exists(index_dir):
            raise ValueError('Index directory exists: %s' % index_dir)

        os.makedirs(index_dir)
        index_html = os.path.join(index_dir, 'index.html')
        top = open(index_html, 'w')
        top.writelines(['<html>\n',
                        '<body>\n',
                        '<h1>Package Index</h1>\n',
                        '<ul>\n'])

        for key, value in items:
            self._blather('Project: %s' % key)
            dirname = os.path.join(index_dir, key)
            os.makedirs(dirname)
            top.write('<li><a href="%s">%s</a>\n' % (key, key))

            sub_html = os.path.join(index_dir, key, 'index.html')
            sub = open(sub_html, 'w')
            sub.writelines(['<html>\n',
                            '<body>\n',
                            '<h1>%s Distributions</h1>\n' % key,
                            '<ul>\n'])

            for revision, archive in value:
                self._blather('  -> %s, %s' % (revision, archive))
                sub.write('<li><a href="../../%s">%s</a>\n'
                                % (archive, archive))

            sub.writelines(['</ul>\n',
                            '</body>\n',
                            '</html>\n'])
            sub.close()

        top.writelines(['</ul>\n',
                        '</body>\n',
                        '</html>\n'])
        top.close()

    def _blather(self, text):
        if self.options.verbose:
            print text

    def _extractNameVersion(self, filename):
        # -> (project, version)
        self._blather('Parsing: %s' % filename)

        archive = _getArchiver(filename)
        if archive is None:
            self._blather('Unknown archive -- ignored')
            return None, None

        try:
            names = archive.names()
            has_setup = False
            for name in names:

                if name.endswith('PKG-INFO'):

                    project, version = None, None

                    for line in archive.lines(name):
                        key, value = line.split(':', 1)

                        if key == 'Name':
                            project = value.strip()
                            if version is not None:
                                return project, version

                        elif key == 'Version':
                            version = value.strip()
                            if project is not None:
                                return project, version
                elif name.endswith('/setup.py'):
                    has_setup = True

            # no PKG-INFO found, do it the hard way.
            if has_setup:
                tmpdir = tempfile.mkdtemp()
                try:
                    for name in names:
                        archive.extract(name, tmpdir)
                    command = ('cd %s/%s && %s setup.py --name --version'
                                % (tmpdir, names[0], sys.executable))
                    popen = subprocess.Popen(command,
                                             stdout=subprocess.PIPE,
                                             shell=True,
                                            )
                    output = popen.communicate()[0]
                    return tuple(output.splitlines()[:2])
                finally:
                    shutil.rmtree(tmpdir)
            return None, None
        finally:
            archive.close()

def main():
    try:
        indexer = Indexer(sys.argv[1:])
    except ValueError, e:
        print str(e)
        sys.exit(1)
    indexer()

if __name__ == '__main__':
    main()
