""" Generic command line driver.

Register sub-commands by querying :mod:`setuptools` entry points for the
group ``compoze_commands``.
"""
import optparse
import pkg_resources
import textwrap
import sys

from compoze._compat import ConfigParser

class InvalidCommandLine(ValueError):
    pass

class NotACommand(object):
    def __init__(self, bogus):
        self.bogus = bogus
    def __call__(self):
        raise InvalidCommandLine('Not a command: %s' % self.bogus)

_COMMANDS = {}

for entry in pkg_resources.iter_entry_points('compoze_commands'):

    klass = entry.load(False)

    if entry.name in _COMMANDS: #pragma NO COVERAGE
        raise ValueError('Clash on compoze command: %s' % entry.name)

    _COMMANDS[entry.name] = klass


def get_description(command):
    klass = _COMMANDS[command]
    doc = getattr(klass, '__doc__', '')
    if doc is None:
        return ''
    return ' '.join([x.lstrip() for x in doc.split('\n')])


class Compozer:
    """ Driver for the :command:`compoze` command-line script. 
    """
    def __init__(self, argv=None, logger=None):
        self.commands = []
        if logger is None:
            logger = self._print
        self.logger = logger
        self.parse_arguments(argv)

    def parse_arguments(self, argv=None):
        """ Parse subcommands and their options from an argv list.
        """
        mine = []
        queue = [(None, mine)]

        def _recordCommand(arg):
            current, current_args = queue[-1]
            if arg is not None:
                queue.append((arg, []))

        for arg in argv:
            if arg in _COMMANDS:
                _recordCommand(arg)
            else:
                queue[-1][1].append(arg)

        _recordCommand(None)

        usage= "%prog [GLOBAL_OPTIONS] " \
               "[command [COMMAND_OPTIONS]* [COMMAND_ARGS]]"
        parser = optparse.OptionParser(usage=usage)

        parser.add_option(
            '-s', '--help-commands',
            action='store_true',
            dest='help_commands',
            help="Show command help")

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
            '-c', '--config-file',
            action='append',
            dest='config_files',
            default=[],
            help="Add a configuration file")

        parser.add_option(
            '-p', '--path',
            action='store',
            dest='path',
            default='.',
            help="Path for indexing")

        parser.add_option(
            '-u', '--index-url',
            metavar='INDEX_URL',
            action='append',
            dest='index_urls',
            default=[],
            help="Add a candidate index used to find distributions")

        parser.add_option(
            '-l', '--find-links',
            metavar='FIND_LINKS_URL',
            action='append',
            dest='find_links',
            default=[],
            help="Add a find-links url")

        parser.add_option(
            '-f', '--fetch-site-packages',
            action='store_true',
            dest='fetch_site_packages',
            default=False,
            help="Fetch requirements used in site-packages")

        parser.add_option(
            '-V', '--use-versions',
            action='store_true',
            dest='use_versions',
            default=False,
            help="Use versions from config file?")

        parser.add_option(
            '-S', '--versions-section',
            action='store',
            dest='versions_section',
            default=None,
            help="Use versions from alternate section of file")

        parser.add_option(
            '-b', '--include-binary-eggs',
            action='store_false',
            dest='source_only',
            default=True,
            help="Include binary distributions")

        parser.add_option(
            '-k', '--keep-tempdir',
            action='store_true',
            dest='keep_tempdir',
            default=False,
            help="Keep temporary directory")

        options, args = parser.parse_args(mine)

        if len(options.index_urls) == 0:
            options.index_urls = ['http://pypi.python.org/simple']

        if options.use_versions and options.versions_section is None:
            options.versions_section = 'versions'

        if options.versions_section is not None:
            options.use_versions = True

        self.options = options

        for arg in args:
            self.commands.append(NotACommand(arg))
            options.help_commands = True

        if options.help_commands:
            keys = _COMMANDS.keys()
            keys.sort()
            self.error('Valid commands are:')
            for x in keys:
                self.error(' %s' % x)
                doc = get_description(x)
                if doc:
                    self.error(textwrap.fill(doc,
                                             initial_indent='    ',
                                             subsequent_indent='    '))
            return

        self._parseConfigFile()

        for command_name, args in queue:
            if command_name is not None:
                command = _COMMANDS[command_name](self.options, *args)
                self.commands.append(command)

    def __call__(self):
        """ Invoke sub-commands parsed by :meth:`parse_arguments`.
        """
        if not self.commands:
            raise InvalidCommandLine('No commands specified')

        for command in self.commands:
            command()

    def _parseConfigFile(self):
        op = self.options
        cf_data = op.config_file_data = {}
        if op.config_files:
            cp = UnhosedConfigParser()
            cp.read(op.config_files)
            for s_name in cp.sections():
                if s_name == 'global':
                    if cp.has_option('global', 'path'):
                        op.path = cp.get('global', 'path')
                    if cp.has_option('global', 'verbose'):
                        op.verbose = cp.getboolean('global', 'verbose')
                    if cp.has_option('global', 'index-url'):
                        text = cp.get('global', 'index-url')
                        urls = [x.strip() for x in text.splitlines()]
                        op.index_urls = filter(None, urls)
                    if cp.has_option('global', 'find-links'):
                        text = cp.get('global', 'find-links')
                        urls = [x.strip() for x in text.splitlines()]
                        op.find_links = filter(None, urls)
                    if cp.has_option('global', 'fetch-site-packages'):
                        op.fetch_site_packages = cp.getboolean('global',
                                                       'fetch-site-packages')
                    if cp.has_option('global', 'include-binary-eggs'):
                        op.source_only = cp.getboolean('global',
                                                       'include-binary-eggs')
                    if cp.has_option('global', 'keep-tempdir'):
                        op.keep_tempdir = cp.getboolean('global',
                                                        'keep-tempdir')
                else:
                    s_data = cf_data[s_name] = {}
                    for o_name in cp.options(s_name):
                        s_data[o_name] = cp.get(s_name, o_name)

    def _print(self, text): # pragma NO COVERAGE
        print(text)

    def error(self, text):
        self.logger(text)

    def blather(self, text):
        if self.options.verbose:
            self.logger(text)

class UnhosedConfigParser(ConfigParser):

    def optionxform(self, key):
        # no damned case flattening!
        return key

def main(argv=sys.argv[1:]):
    try:
        compozer = Compozer(argv)
        compozer()
    except InvalidCommandLine as e: #pragma NO COVERAGE
        print(str(e))
        sys.exit(1)

if __name__ == '__main__': #pragma NO COVERAGE
    main()
