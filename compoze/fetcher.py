import optparse
import os
import pkg_resources
import shutil
import sys
import tempfile
import StringIO

from compoze.index import CompozePackageIndex


class Fetcher:
    """ Download distributions for a set of :mod:`setuptools` requirements.
    """
    index_factory = CompozePackageIndex # allow shimming for testing

    def __init__(self, global_options, *argv, **kw):
        argv = list(argv)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] [REQUIREMENT]*")

        parser.add_option(
            '-q', '--quiet',
            action='store_false',
            dest='verbose',
            help="Run quietly")

        parser.add_option(
            '-v', '--verbose',
            action='store_true',
            dest='verbose',
            default=getattr(global_options, 'verbose', False),
            help="Show progress")

        parser.add_option(
            '-p', '--path',
            action='store',
            dest='path',
            default=getattr(global_options, 'path', '.'),
            help="Specify the path in which to store the fetched dists")

        parser.add_option(
            '-u', '--index-url',
            metavar='INDEX_URL',
            action='append',
            dest='index_urls',
            default=getattr(global_options, 'index_urls', []),
            help="Add a candidate index used to find distributions")

        parser.add_option(
            '-l', '--find-links',
            metavar='FIND_LINKS_URL',
            action='append',
            dest='find_links',
            default=getattr(global_options, 'find_links', []),
            help="Add a find-links url")

        parser.add_option(
            '-f', '--fetch-site-packages',
            action='store_true',
            dest='fetch_site_packages',
            default=getattr(global_options, 'fetch_site_packages', False),
            help="Fetch requirements used in site-packages")

        parser.add_option(
            '-b', '--include-binary-eggs',
            action='store_false',
            dest='source_only',
            default=getattr(global_options, 'source_only', True),
            help="Include binary distributions")

        parser.add_option(
            '-k', '--keep-tempdir',
            action='store_true',
            dest='keep_tempdir',
            default=getattr(global_options, 'keep_tempdir', False),
            help="Keep temporary directory")

        self.usage = parser.format_help()
        options, args = parser.parse_args(argv)

        if len(options.index_urls) == 0:
            options.index_urls = ['http://pypi.python.org/simple']

        self.options = options
        self._expandRequirements(args)

        path = os.path.abspath(os.path.expanduser(options.path))

        self.path = path
        self._logger = kw.get('logger', _print)

    def error(self, text):
        self._logger(text)

    def blather(self, text):
        if self.options.verbose:
            self._logger(text)

    def download_distributions(self):
        """ Collect best sdist candidate for each requirement into a tempdir.

        Search each index and find-links URL provided in command options.

        Report results using the logger.
        """
        # XXX ignore same-name problem for now

        if (not self.options.fetch_site_packages and
            len(self.requirements) == 0):
            msg = StringIO.StringIO()
            msg.write('fetch: Either specify requirements, or else '
                                    '--fetch-site-packages .\n\n')
            msg.write(self.usage)
            raise ValueError(msg.getvalue())

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if not os.path.isdir(self.path):
            msg = StringIO.StringIO()
            msg.write('Not a directory: %s\n\n' % self.path)
            msg.write(self.usage)
            raise ValueError(msg.getvalue())

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
                try:
                    dist = index.fetch_distribution(rqmt, self.tmpdir,
                                                    source=source_only)
                except Exception, e:
                    self.error('  Error fetching: %s' % rqmt)
                    self.blather('    %s' % e)
                    results[rqmt] = False
                else:
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
            try:
                dist = local.fetch_distribution(rqmt,
                                                self.tmpdir,
                                                force_scan=True)
            except Exception:
                dist = None
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

    def __call__(self): #pragma NO COVERAGE
        """ Call :meth:`download_distributions` and clean up.
        """
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

        self.requirements = [x for x in pkg_resources.parse_requirements(args)
                                 if x.project_name != 'Python']

def _print(text): #pragma NO COVERAGE
    print text


def main(): #pragma NO COVERAGE
    try:
        fetcher = Fetcher(sys.argv[1:])
        fetcher()
    except ValueError, e:
        print str(e)
        sys.exit(1)

if __name__ == '__main__': #pragma NO COVERAGE
    main()
