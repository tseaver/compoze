""" compoze -- build a new Python package index from source distributions

"""
import optparse
import os
import pkg_resources
import sys


def _resolve(dotted_or_ep):
    """ Resolve a dotted name or setuptools entry point to a callable.
    """
    return pkg_resources.EntryPoint.parse('x=%s' % dotted_or_ep).load(False)

_COMMANDS = {}

for entry in pkg_resources.iter_entry_points('compoze_commands'):

    klass = entry.load(False)

    if entry.name in _COMMANDS:
        raise ValueError('Clash on compoze command: %s' % entry.name)

    _COMMANDS[entry.name] = klass

class Compozer:

    def __init__(self, argv=None):
    
        mine = []
        queue = [(None, mine)]
        self.commands = []

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

        parser = optparse.OptionParser(
            usage="%prog [GLOBAL_OPTOINS] [command [COMMAND_OPTIONS]* [COMMAND_ARGS]]")

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

        options, args = parser.parse_args(mine)

        self.options = options

        if options.help_commands:
            keys = _COMMANDS.keys()
            keys.sort()
            val = 'Valid commands are: ' + ' '.join(keys)
            raise ValueError(val)

        for command_name, args in queue:
            if command_name is not None:
                command = _COMMANDS[command_name](self.options, *args)
                self.commands.append(command)

        if not self.commands:
            raise ValueError('No commands specified')

    def __call__(self):

        for command in self.commands:
            command()

    def blather(self, text):
        if self.options.verbose:
            print text


def main():
    try:
        compozer = Compozer(sys.argv[1:])
    except ValueError, e:
        print str(e)
        sys.exit(1)
    compozer()

if __name__ == '__main__':
    main()
