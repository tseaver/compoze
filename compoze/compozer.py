""" compoze -- build a new Python package index from source distributions

"""
import getopt
import optparse
import os
import pkg_resources
import shutil
import sys
import tarfile
import tempfile

from setuptools.package_index import PackageIndex

class Compozer:

    def __init__(self, argv=None):
    
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] app_egg_name [other_egg_name]*")

        parser.add_option(
            '-p', '--path',
            action='store',
            dest='path',
            default='.',
            help="Specify the path in which to build the index")

        parser.add_option(
            '-n', '--index-name',
            action='store',
            dest='index_name',
            default='simple',
            help="Specify the name of the index subdirectory")

        parser.add_option(
            '-u', '--index-url',
            action='append',
            dest='index_urls',
            default=[],
            help="Add a candidate index used to find distributions")

        parser.add_option(
            '-f', '--fetch-site-packages',
            action='store_true',
            dest='fetch_site_packages',
            default=False,
            help="Fetch requirements used in site-packages")

        parser.add_option(
            '-d', '--download',
            action='store_true',
            dest='download',
            default=True,
            help="Download candidate distributions")

        parser.add_option(
            '-b', '--include-binary-eggs',
            action='store_false',
            dest='source_only',
            default=True,
            help="Include binary distributions")

        parser.add_option(
            '-D', '--no-download',
            action='store_false',
            dest='download',
            help="Do not download candidate distributions")

        parser.add_option(
            '-m', '--make-index',
            action='store_true',
            dest='make_index',
            default=True,
            help="Make a package index in target directory")

        parser.add_option(
            '-M', '--no-make-index',
            action='store_false',
            dest='make_index',
            help="Do not make a package index in target directory")

        parser.add_option(
            '-q', '--quiet',
            action='store_false',
            dest='verbose',
            help="Run quietly")

        parser.add_option(
            '-v', '--verbose',
            action='store_true',
            dest='verbose',
            default=True,
            help="Show progress")

        parser.add_option(
            '-k', '--keep-tempdir',
            action='store_true',
            dest='keep_tempdir',
            default=False,
            help="Keep temporary directory")

        options, args = parser.parse_args(argv)

        if (options.download and
            not options.fetch_site_packages and
            len(args) == 0):
            parser.print_help(sys.stderr)
            sys.exit(1)

        if len(options.index_urls) == 0:
            options.index_urls = ['http://pypi.python.org/simple']

        self.options = options
        self._expandRequirements(args)

        path = os.path.abspath(os.path.expanduser(options.path))

        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.isdir(path):
            print >> sys.stderr, 'Not a directory: %s' % path
            sys.exit(1)

        self.path = path

    def __call__(self):

        self.tmpdir = tempfile.mkdtemp(dir='.')
        try:
            if self.options.download:
                self.download_distributions()

            if self.options.make_index:
                self.make_index()
        finally:
            if not self.options.keep_tempdir:
                shutil.rmtree(self.tmpdir)

    def download_distributions(self):

        # First, collect best sdist candidate for the requirment from each 
        # index into a self.tmpdir
        # XXX ignore same-name problem for now

        for index_url in self.options.index_urls:
            self._blather('=' * 50)
            self._blather('Package index: %s' % index_url)
            self._blather('=' * 50)
            index = PackageIndex(index_url=index_url)

            source_only = self.options.source_only
            for rqmt in self.requirements:
                self._blather('Fetching: %s' % rqmt)
                dist = index.fetch_distribution(rqmt, self.tmpdir,
                                                source=source_only)
                self._blather('Found: %s' % dist)

        self._blather('=' * 50)
        self._blather('Merging indexes')
        self._blather('=' * 50)

        local_index = os.path.join(self.tmpdir)
        local = PackageIndex(index_url=local_index ,
                             search_path=(), # ignore installed!
                            )

        for rqmt in self.requirements:
            self._blather('Resolving: %s' % rqmt)
            dist = local.fetch_distribution(rqmt, '.', force_scan=True)
            if dist is not None:
                self._blather('Found: %s' % dist)
                shutil.copy(dist.location, self.path)
            else:
                print 'Not found: %s' % rqmt

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
            projects.setdefault(project, []).append((revision, candidate))

        items = projects.items()
        items.sort()

        if os.path.exists(index_dir):
            print >> sys.stderr, 'Index directory exists: %s' % index_dir
            sys.exit(1)

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

    def _expandRequirements(self, args):
        args = list(args)
        if self.options.fetch_site_packages:
            for dist in pkg_resources.working_set:
                args.append('%s == %s' % (dist.key, dist.version))

        self.requirements = list(pkg_resources.parse_requirements(args))

    def _extractNameVersion(self, filename):

        self._blather('Parsing: %s' % filename)
        tgz = tarfile.TarFile.gzopen(filename, 'r')
        try:
            names = tgz.getnames()
            for name in names:

                if name.endswith('PKG-INFO'):

                    project, version = None, None

                    for line in tgz.extractfile(name).readlines():
                        key, value = line.split(':', 1)

                        if key == 'Name':
                            project = value.strip()
                            if version is not None:
                                return project, version

                        elif key == 'Version':
                            version = value.strip()
                            if project is not None:
                                return project, version

                elif name == 'setup.py':
                    tgz.extract(name, self.tmpdir)

            # no PKG-INFO found, do it the hard way.
            command = ('cd %s/%s && %s setup.py --name --version'
                                    % (self.tmpdir, names[0], sys.executable))
            popen = subprocess.Popen(command,
                                     stdout=subprocess.PIPE,
                                     shell=True,
                                    )
            output = popen.communicate()[0]
            return output.splitlines()[:2]
        finally:
            tgz.close()

def main():
    compozer = Compozer(sys.argv[1:])
    compozer()

if __name__ == '__main__':
    main()
