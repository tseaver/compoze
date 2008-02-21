""" compoze fetch -- download distributions for given requirements

"""
import optparse
import os
import pkg_resources
import shutil
import sys
import tempfile
import StringIO

from setuptools.package_index import PackageIndex

class Fetcher:

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
            '-b', '--include-binary-eggs',
            action='store_false',
            dest='source_only',
            default=True,
            help="Include binary distributions")

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

        if (not options.fetch_site_packages and
            len(args) == 0):
            msg = StringIO.StringIO()
            msg.write('fetch: Either specify requirements, or else'
                                    '--fetch-site-packages .\n\n')
            msg.write(parser.format_help())
            raise ValueError(msg.getvalue())

        if len(options.index_urls) == 0:
            options.index_urls = ['http://pypi.python.org/simple']

        self.options = options
        self._expandRequirements(args)

        path = os.path.abspath(os.path.expanduser(options.path))

        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.isdir(path):
            msg = StringIO.StringIO()
            msg.write('Not a directory: %s\n\n' % path)
            msg.write(parser.format_help())
            raise ValueError(msg.getvalue())

        self.path = path

    def __call__(self):

        self.tmpdir = tempfile.mkdtemp(dir='.')
        try:
            self.download_distributions()
        finally:
            if not self.options.keep_tempdir:
                shutil.rmtree(self.tmpdir)

    def download_distributions(self):

        # First, collect best sdist candidate for the requirement from each 
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

    def _blather(self, text):
        if self.options.verbose:
            print text

    def _expandRequirements(self, args):
        args = list(args)
        if self.options.fetch_site_packages:
            for dist in pkg_resources.working_set:
                args.append('%s == %s' % (dist.key, dist.version))

        self.requirements = list(pkg_resources.parse_requirements(args))


def main():
    try:
        fetcher = Fetcher(sys.argv[1:])
    except ValueError, e:
        print str(e)
        sys.exit(1)
    fetcher()

if __name__ == '__main__':
    main()
