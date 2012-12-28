import optparse
import os
import shutil
import sys

from compoze._compat import StringIO

ARCHIVE_EXTS = ('tar.gz', 'tgz', 'zip', 'tar.bz2', 'tbz')


def is_archive(f):
    for x in ARCHIVE_EXTS:
        if f.endswith('.'+x):
            return True
    return False


class Pooler(object):
    """ Move archives into a common pool directory; symlink back into path.
    """

    def __init__(self, global_options, *argv, **kw):

        argv = list(argv)
        parser = optparse.OptionParser(
            usage="%prog pool [OPTIONS] pool_dir\n\n  " +
                   self.__doc__.strip())

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
            help="Path to process")

        self.usage = parser.format_help()

        options, args = parser.parse_args(argv)

        self.options = options
        self.pool_dir = None
        if len(args) == 1:
            self.pool_dir = args[0]

        self.release_dir = os.path.abspath(options.path)
        self._logger = kw.get('logger', _print)

    def blather(self, text):
        if self.options.verbose:
            self._logger(text)

    def listArchives(self):
        all = []
        pending = []
        archives = ([], [])
        for filename in os.listdir(self.release_dir):
            full = os.path.join(self.release_dir, filename)
            if is_archive(full) and os.path.isfile(full):
                if not os.path.islink(full):
                    pending.append(filename)
                all.append(filename)
        return all, pending

    def move_to_pool(self):
        """ Move archives the pool directory and create symlinks.

        Ignore any archives which are already symlinks.
        """
        if self.pool_dir is None:
            msg = StringIO()
            msg.write('No pool_dir!\n\n')
            msg.write(self.usage)
            raise ValueError(msg.getvalue())

        all, pending = self.listArchives()
        if len(all) == 0:
            raise ValueError('No non-link archives in release dir: %s'
                                % self.release_dir)

        if not os.path.exists(self.pool_dir):
            self.blather('Created new pool dir %s' % self.pool_dir)
            os.makedirs(self.pool_dir)

        if not os.path.isdir(self.pool_dir):
            raise ValueError('Pool dir is not a directory: %s'
                                % self.pool_dir)

        for archive in pending:
            source = os.path.join(self.release_dir, archive)
            target = os.path.join(self.pool_dir, archive)
            if not os.path.exists(target):
                shutil.move(source, target)
                self.blather('Moved %s to %s' % (source, target))
            if os.path.exists(source):
                os.remove(source)
            os.symlink(target, source)

        return all, pending

    def __call__(self): #pragma NO COVERAGE
        """ Delegate to :meth:`move_to_pool` and report results.
        """
        try:
            all, pending = self.move_to_pool()
            self.blather(
                "Updated %i out of %i archives" % (len(pending), len(all)))
        except ValueError as e:
            self.blather(str(e))

def _print(text): #pragma NO COVERAGE
    print(text)

def main(): #pragma NO COVERAGE
    try:
        update_pool = Pooler(sys.argv[1:])
        update_pool()
    except ValueError as e:
        print(str(e))
        sys.exit(1)

if __name__ == '__main__': #pragma NO COVERAGE
    main()
