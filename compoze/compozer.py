""" Generic command line driver.

Register sub-commands by querying :mod:`setuptools` entry points for the
group ``compoze_commands``.
"""
from ConfigParser import ConfigParser
import optparse
import pkg_resources
import textwrap
import sys

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
            action='store',
            dest='config_file',
            default=None,
            help="Configuration file")

        parser.add_option(
            '-p', '--path',
            action='store',
            dest='path',
            default='.',
            help="Path for indexing")

        options, args = parser.parse_args(mine)

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
        if op.config_file is not None:
            cp = UnhosedConfigParser()
            cp.read(op.config_file)
            for s_name in cp.sections():
                if s_name == 'global':
                    if cp.has_option('global', 'path'):
                        self.options.path = cp.get('global', 'path')
                    if cp.has_option('global', 'verbose'):
                        self.options.verbose = cp.getboolean('global',
                                                             'verbose')
                else:
                    s_data = cf_data[s_name] = {}
                    for o_name in cp.options(s_name):
                        s_data[o_name] = cp.get(s_name, o_name)

    def _print(self, text): # pragma NO COVERAGE
        print text

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
    except InvalidCommandLine, e: #pragma NO COVERAGE
        print str(e)
        sys.exit(1)

if __name__ == '__main__': #pragma NO COVERAGE
    main()
