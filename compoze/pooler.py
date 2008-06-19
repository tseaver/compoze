import optparse
import os
import shutil
import sys

ARCHIVE_EXTS = ('tar.gz', 'tgz', 'zip', 'tar.bz2', 'tbz')


def isarchive(f):
    for x in ARCHIVE_EXTS:
        if f.endswith('.'+x):
            return True
    return False


class NoArchivesException(Exception):
    pass


class Pooler(object):
    '''Move all archives into a common pool directory and symlink back the
    results.
    '''

    def __init__(self, global_options, *argv):

        argv = list(argv)
        parser = optparse.OptionParser(
            usage="%prog pool [OPTIONS] pool_dir\n\n  " + __doc__.strip())

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

        self.parser = parser
        self.options = options
        self.args = args

    def __call__(self):
        if len(self.args) == 0:
            self.parser.print_help()
            return
        try:
            all, pending = self.moveToPool(self.args[0])
            print "Updated %i out of %i archives" % (len(pending), len(all))
        except NoArchivesException, err:
            print "Couldn't find any archives in '%s'" % self.releasedir

    def _blather(self, text):
        if self.options.verbose:
            print text

    @property
    def releasedir(self):
        return os.path.abspath(os.curdir)

    @property
    def archives(self):
        all = []
        pending = []
        archives = ([], [])
        for f in os.listdir(self.releasedir):
            full = os.path.join(self.releasedir, f)
            if isarchive(full) and os.path.isfile(full):
                if not os.path.islink(full):
                    pending.append(f)
                all.append(f)
        return all, pending

    def moveToPool(self, pooldir):
        all, pending = self.archives
        if len(all) == 0:
            raise NoArchivesException()

        for f in pending:
            full = os.path.join(self.releasedir, f)
            name = f.split('-', 2)[0]
            poolpath = os.path.join(pooldir, name.lower())
            if not os.path.exists(poolpath):
                os.makedirs(poolpath)
                self._blather('Created new pool dir %s' % poolpath)
            archivepath = os.path.join(poolpath, f)
            if not os.path.exists(archivepath):
                shutil.move(full, archivepath)
                self._blather('Moved %s to %s' % (full, archivepath))
            if os.path.exists(full):
                os.remove(full)
            os.symlink(archivepath, full)
        return all, pending


def main():
    try:
        update_pool = Pooler(sys.argv[1:])
    except ValueError, e:
        print str(e)
        sys.exit(1)
    update_pool()

if __name__ == '__main__':
    main()
