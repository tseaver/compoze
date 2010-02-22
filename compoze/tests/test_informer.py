import unittest

class InformerTests(unittest.TestCase):

    _tmpdir = None

    def tearDown(self):
        if self._tmpdir is not None:
            import shutil
            shutil.rmtree(self._tmpdir)

    def _getTargetClass(self):
        from compoze.informer import Informer
        return Informer

    def _makeOne(self, *args, **kw):
        from optparse import Values
        logger = kw.pop('logger', None)
        default = kw.copy()
        default.setdefault('verbose', False)
        values = Values(default)
        values.path = '.'
        if logger is not None:
            return self._getTargetClass()(values, logger=logger, *args)
        return self._getTargetClass()(values, *args)

    def _makeTempDir(self):
        import tempfile
        if self._tmpdir is None:
            self._tmpdir = tempfile.mkdtemp()
        return self._tmpdir

    def _makeDirs(self):
        import os
        tmpdir = self._makeTempDir()
        target = os.path.join(tmpdir, 'target')
        os.makedirs(target)
        path = os.path.join(self._tmpdir, 'path')
        os.makedirs(path)
        cheeseshop = os.path.join(tmpdir, 'cheeseshop')
        os.makedirs(cheeseshop)
        return target, path, cheeseshop

    def _makeIndex(self, *rqmts, **kw):
        from pkg_resources import DEVELOP_DIST
        target = kw.get('target', '')
        develop = kw.get('develop', ())
        distros = []
        for rqmt in rqmts:
            if rqmt.project_name in develop:
                dist = DummyDistribution(rqmt.project_name, target,
                                         precedence=DEVELOP_DIST)
            else:
                dist = DummyDistribution(rqmt.project_name, target)
            distros.append((rqmt.project_name, dist))
        return DummyIndex(distros)

    def test_ctor_empty_argv_raises(self):
        self.assertRaises(ValueError, self._makeOne, argv=[])

    def test_ctor_index_factory(self):
        from compoze.index import CompozePackageIndex
        fetcher = self._makeOne('--fetch-site-packages')
        self.failUnless(fetcher.index_factory is CompozePackageIndex)

    def test_ctor_default_index_url_is_cheeseshop(self):
        informer = self._makeOne('--fetch-site-packages')
        self.assertEqual(informer.options.index_urls,
                         ['http://pypi.python.org/simple'])

    def test_ctor_default_logger(self):
        from compoze.informer import _print
        informer = self._makeOne('--fetch-site-packages')
        self.failUnless(informer._logger is _print)

    def test_ctor_explicit_logger(self):
        informer = self._makeOne('--fetch-site-packages', logger=self)
        self.failUnless(informer._logger is self)

    def test_blather_not_verbose(self):
        def _dont_go_here(*args):
            assert 0, args
        informer = self._makeOne('--fetch-site-packages',
                                 '--quiet',
                                 logger=_dont_go_here)
        informer.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        logged = []
        informer = self._makeOne('--fetch-site-packages',
                                 '--verbose',
                                 logger=logged.append)
        informer.blather('foo')
        self.assertEqual(logged, ['foo'])

    def test_show_distributions_skips_develop_dists(self):
        import re
        from pkg_resources import Requirement
        logged = []
        target, path, cheeseshop_path = self._makeDirs()
        compoze = Requirement.parse('compoze')
        nose = Requirement.parse('nose')
        cheeseshop = self._makeIndex(compoze, nose,
                                     target=cheeseshop_path,
                                     develop=('compoze',))
        local = self._makeIndex(compoze, target=target)
        def _factory(index_url, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        informer = self._makeOne('--verbose', 'compoze', 'nose',
                                 logger=logged.append)
        informer.index_factory = _factory
        informer.tmpdir = target

        informer.show_distributions()

        log = '\n'.join(logged)
        skipped = re.compile(r'Skipping.*<compoze')
        found = re.compile(r'nose: /tmp/.*/cheeseshop/nose')
        self.failUnless(skipped.search(log))
        self.failUnless(found.search(log))

    def test_show_distributions_skips_multi_develop_dists(self):
        import re
        from pkg_resources import Requirement
        logged = []
        target, path, cheeseshop_path = self._makeDirs()
        compoze = Requirement.parse('compoze')
        nose = Requirement.parse('nose')
        cheeseshop = self._makeIndex(compoze, compoze, nose,
                                     target=cheeseshop_path,
                                     develop=('compoze',))
        local = self._makeIndex(compoze, target=target)
        def _factory(index_url, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        informer = self._makeOne('--verbose', 'compoze', 'nose',
                                 logger=logged.append)
        informer.index_factory = _factory
        informer.tmpdir = target

        informer.show_distributions()

        log = '\n'.join(logged)
        skipped = re.compile(r'Skipping.*<compoze')
        found = re.compile(r'nose: /tmp/.*/cheeseshop/nose')
        self.failUnless(skipped.search(log))
        self.failUnless(found.search(log))

    def test_show_distributions_multiple_no_only_best(self):
        import re
        from pkg_resources import Requirement
        logged = []
        target, path, cheeseshop_path = self._makeDirs()
        nose = Requirement.parse('nose')
        nose2 = Requirement.parse('nose')
        cheeseshop = self._makeIndex(nose, nose2,
                                     target=cheeseshop_path,
                                    )
        def _factory(index_url, search_path=None):
            assert index_url == 'http://pypi.python.org/simple'
            assert search_path is None
            return cheeseshop
        informer = self._makeOne('--verbose',
                                 'nose',
                                 logger=logged.append)
        informer.index_factory = _factory
        informer.tmpdir = target

        informer.show_distributions()

        log = '\n'.join(logged)
        found = re.findall(r'nose: /tmp/.*/cheeseshop/nose', log)
        self.assertEqual(len(found), 2)

    def test_show_distributions_multiple_w_only_best(self):
        import re
        from pkg_resources import Requirement
        logged = []
        target, path, cheeseshop_path = self._makeDirs()
        nose = Requirement.parse('nose')
        nose2 = Requirement.parse('nose')
        cheeseshop = self._makeIndex(nose, nose2,
                                     target=cheeseshop_path,
                                    )
        def _factory(index_url, search_path=None):
            assert index_url == 'http://pypi.python.org/simple'
            assert search_path is None
            return cheeseshop
        informer = self._makeOne('--verbose', '--show-only-best',
                                 'nose',
                                 logger=logged.append)
        informer.index_factory = _factory
        informer.tmpdir = target

        informer.show_distributions()

        log = '\n'.join(logged)
        found = re.findall(r'nose: /tmp/.*/cheeseshop/nose', log)
        self.assertEqual(len(found), 1)


class DummyDistribution(object):

    def __init__(self, name, tmpdir=None, precedence=None):
        self.name = name
        self.tmpdir = tmpdir
        self.precedence = precedence

    def _get_location(self):
        import os
        result = os.path.join(self.tmpdir, self.name) 
        f = open(result, 'wb')
        f.write(self.name)
        f.flush()
        f.close()
        return result
    location = property(_get_location,)


class DummyIndex:

    def __init__(self, distros):
        mapping = self._mapping = {}
        for name, distro in distros:
            found = mapping.setdefault(distro.name, [])
            found.append(distro)

    def prescan(self):
        pass

    def find_packages(self, rqmt):
        pass

    def __getitem__(self, key):
        return self._mapping[key]
