import optparse
import os
import pkg_resources
import shutil
import sys
import tempfile
import StringIO

from setuptools.package_index import PackageIndex


class CompozePackageIndex(PackageIndex):

    def __init__(self, *args, **kwargs):
        PackageIndex.__init__(self, *args, **kwargs)
        self.debug_msgs = []
        self.info_msgs = []
        self.warn_msgs = []

    def debug(self, msg, *args):
        self.debug_msgs.append((msg, args))

    def info(self, msg, *args):
        self.info_msgs.append((msg, args))

    def warn(self, msg, *args):
        self.warn_msgs.append((msg, args))


class Fetcher:
    """Download distributions for given requirements
    """
    index_factory = CompozePackageIndex # allow shimming for testing

    def __init__(self, global_options, *argv, **kw):
        argv = list(argv)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] app_egg_name [other_egg_name]*")

        parser.add_option(
            '-p', '--path',
            action='store',
            dest='path',
            default=global_options.path,
            help="Specify the path in which to store the fetched dists")

        parser.add_option(
            '-u', '--index-url',
            action='append',
            dest='index_urls',
            default=[],
            help="Add a candidate index used to find distributions")

        parser.add_option(
            '-l', '--find-link',
            action='append',
            dest='find_links',
            default=[],
            help="Add a find-link url")

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
            msg.write('fetch: Either specify requirements, or else '
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
        logger = kw.get('logger')
        if logger is None:
            logger = _print
        self._logger = logger

    def blather(self, text):
        if self.options.verbose:
            self._logger(text)

    def download_distributions(self):

        # First, collect best sdist candidate for the requirement
        # from each index into a self.tmpdir

        # XXX ignore same-name problem for now

        self.blather('=' * 50)
        self.blather('Scanning indexes for requirements')
        self.blather('=' * 50)
        results = {}
        for index_url in self.options.index_urls:
            self.blather('Package index: %s' % index_url)
            index = self.index_factory(index_url=index_url)

            source_only = self.options.source_only

            for rqmt in self.requirements:
                if results.get(rqmt, False):
                    continue
                dist = index.fetch_distribution(rqmt, self.tmpdir,
                                                source=source_only)
                self.blather('  Searched for %s; found: %s'
                              % (rqmt, (dist is not None)))
                results[rqmt] = (dist is not None)

        if self.options.find_links:
            self.blather('=' * 50)
            self.blather('Scanning find-links for requirements')
            index = self.index_factory()
            for find_link in self.options.find_links:
                index.add_find_links([find_link])
                self.blather('  ' + find_link)
            self.blather('=' * 50)

            for rqmt in self.requirements:
                if results.get(rqmt, False):
                    continue
                dist = index.fetch_distribution(rqmt, self.tmpdir,
                                                source=source_only)
                self.blather('  Searched for %s; found: %s'
                              % (rqmt, (dist is not None)))
                results[rqmt] = (dist is not None)

        self.blather('=' * 50)
        self.blather('Merging indexes')
        self.blather('=' * 50)

        local_index = os.path.join(self.tmpdir)
        local = self.index_factory(index_url=local_index,
                                   search_path=(), # ignore installed!
                                  )

        for rqmt in self.requirements:
            dist = local.fetch_distribution(rqmt,
                                            self.tmpdir,
                                            force_scan=True)
            if dist is not None:
                shutil.copy(dist.location, self.path)

        self.blather('=' * 50)
        self.blather('Final Results')
        self.blather('=' * 50)

        found = [k for k, v in results.items() if v]
        notfound = [k for k, v in results.items() if not v]
        self.blather('Found eggs:')
        for x in found:
            self.blather('  ' + str(x))
        self.blather('Not found eggs:')
        for x in notfound:
            self.blather('  ' + str(x))

    def __call__(self):

        self.tmpdir = tempfile.mkdtemp(dir='.')
        try:
            self.download_distributions()
        finally:
            if not self.options.keep_tempdir:
                shutil.rmtree(self.tmpdir)

    def _expandRequirements(self, args):
        args = list(args)
        if self.options.fetch_site_packages:
            for dist in pkg_resources.working_set:
                args.append('%s == %s' % (dist.project_name, dist.version))

        self.requirements = list(pkg_resources.parse_requirements(args))

def _print(text):
    print text


def main():
    try:
        fetcher = Fetcher(sys.argv[1:])
    except ValueError, e:
        print str(e)
        sys.exit(1)
    fetcher()

if __name__ == '__main__':
    main()
