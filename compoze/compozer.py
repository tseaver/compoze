""" compoze -- command driver

"""
import optparse
import pkg_resources
import textwrap
import sys

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

    def __init__(self, argv=None, logger=None):

        mine = []
        queue = [(None, mine)]
        self.commands = []
        if logger is None:
            logger = self._print
        self.logger = logger

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
            '-p', '--path',
            action='store',
            dest='path',
            default='.',
            help="Path for indexing")

        options, args = parser.parse_args(mine)

        self.options = options

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

        for command_name, args in queue:
            if command_name is not None:
                command = _COMMANDS[command_name](self.options, *args)
                self.commands.append(command)

        if not self.commands:
            raise ValueError('No commands specified')

    def __call__(self):

        for command in self.commands:
            command()

    def _print(self, text): # pragma NO COVERAGE
        print text

    def error(self, text):
        self.logger(text)

    def blather(self, text):
        if self.options.verbose:
            self.logger(text)


def main(argv=sys.argv[1:]):
    try:
        compozer = Compozer(argv)
    except ValueError, e: #pragma NO COVERAGE
        print str(e)
        sys.exit(1)
    compozer()

if __name__ == '__main__': #pragma NO COVERAGE
    main()
