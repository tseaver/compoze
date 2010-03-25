import optparse
import pkg_resources
import sys
import StringIO

from compoze.index import CompozePackageIndex

class Informer:
    index_factory = CompozePackageIndex # allow shimming for testing

    def __init__(self, global_options, *argv, **kw):
    
        argv = list(argv)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] app_egg_name [other_egg_name]*")

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
            '-o', '--show-only-best',
            action='store_true',
            dest='only_best',
            default=False,
            help="Show only 'best' distribution satisfying each requirement")

        parser.add_option(
            '-b', '--include-binary-eggs',
            action='store_false',
            dest='source_only',
            default=True,
            help="Include binary distributions")

        parser.add_option(
            '-d', '--include-develop-eggs',
            action='store_true',
            dest='develop_ok',
            default=False,
            help="Include development distributions")

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

        options, args = parser.parse_args(argv)

        if (not options.fetch_site_packages and
            len(args) == 0):
            msg = StringIO.StringIO()
            msg.write('show: Either specify requirements, or else'
                                    '--fetch-site-packages .\n\n')
            msg.write(parser.format_help())
            raise ValueError(msg.getvalue())

        if len(options.index_urls) == 0:
            options.index_urls = ['http://pypi.python.org/simple']

        self.options = options
        self._expandRequirements(args)
        self._logger = kw.get('logger', _print)

    def blather(self, text):
        if self.options.verbose:
            self._logger(text)

    def show_distributions(self):
        """ Show available distributions for each index.
        """
        for index_url in self.options.index_urls:
            self.blather('=' * 50)
            self.blather('Package index: %s' % index_url)
            self.blather('=' * 50)
            index = self.index_factory(index_url=index_url)
            index.prescan()

            for rqmt in self.requirements:
                index.find_packages(rqmt)
                self.blather('Candidates: %s' % rqmt)
                for dist in self._findAll(index, rqmt):
                    self.blather('%s: %s' % (dist.name, dist.location))

        self.blather('=' * 50)

    def __call__(self): #pragma NO COVERAGE
        """ Delegate to :meth:`show_distributions`.
        """
        self.show_distributions()

    def _expandRequirements(self, args):
        args = list(args)
        if self.options.fetch_site_packages:
            for dist in pkg_resources.working_set:
                args.append('%s == %s' % (dist.key, dist.version))

        self.requirements = list(pkg_resources.parse_requirements(args))

    def _findAll(self, index, rqmt):
        skipped = {}
        for dist in index[rqmt.key]:

            if (dist.precedence == pkg_resources.DEVELOP_DIST
                    and not self.options.develop_ok):
                if dist not in skipped:
                    self.blather("Skipping development or system egg: %s"
                                   % dist)
                    skipped[dist] = 1
            else:
                if (dist in rqmt and
                     (dist.precedence <= pkg_resources.SOURCE_DIST
                                    or not self.options.source_only)):
                    yield dist

                    if self.options.only_best:
                        break


def _print(text): #pragma NO COVERAGE
    print text

def main(): #pragma NO COVERAGE
    try:
        informer = Informer(sys.argv[1:])
    except ValueError, e:
        print str(e)
        sys.exit(1)
    informer()

if __name__ == '__main__': #pragma NO COVERAGE
    main()
