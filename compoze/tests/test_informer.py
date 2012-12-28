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

    def _makeValues(self, **kw):
        from optparse import Values
        return Values(kw.copy())

    def _makeOptions(self, **kw):
        default = kw.copy()
        default.setdefault('verbose', False)
        values = self._makeValues(**default)
        values.path = '.'
        return values

    def _makeOne(self, *args, **kw):
        logger = kw.pop('logger', None)
        options = self._makeOptions(**kw)
        if logger is not None:
            return self._getTargetClass()(options, logger=logger, *args)
        return self._getTargetClass()(options, *args)

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

    def test_ctor_defaults(self):
        values = self._makeValues()
        informer = self._getTargetClass()(values)
        self.assertEqual(informer.requirements, [])
        self.assertFalse(informer.options.verbose)
        self.assertEqual(informer.options.index_urls,
                         ['http://pypi.python.org/simple'])
        self.assertFalse(informer.options.fetch_site_packages)
        self.assertFalse(informer.options.only_best)
        self.assertTrue(informer.options.source_only)
        self.assertFalse(informer.options.develop_ok)
        self.assertEqual(informer.options.use_versions, False)
        self.assertEqual(informer.options.versions_section, None)
        self.assertEqual(informer.options.config_file_data, {})

    def test_ctor_uses_global_options_as_default(self):
        g_options = self._makeOptions(path='/tmp/foo',
                                      verbose=True,
                                      index_urls=['http://example.com/simple'],
                                      fetch_site_packages=True,
                                      source_only=False,
                                      keep_tempdir=True,
                                      use_versions=True,
                                      versions_section='SECTION',
                                      config_file_data={'foo': 'bar'},
                                     )
        informer = self._getTargetClass()(g_options)
        self.assertTrue(informer.options.verbose)
        self.assertEqual(informer.options.index_urls,
                         ['http://example.com/simple'])
        self.assertTrue(informer.options.fetch_site_packages)
        self.assertTrue(informer.options.use_versions)
        self.assertEqual(informer.options.versions_section, 'SECTION')
        self.assertEqual(informer.options.config_file_data, {'foo': 'bar'})
        self.assertFalse(informer.options.source_only)

    def test_ctor_index_factory(self):
        from compoze.index import CompozePackageIndex
        informer = self._makeOne()
        self.assertTrue(informer.index_factory is CompozePackageIndex)

    def test_ctor_explicit_index_url(self):
        informer = self._makeOne('--index-url=http://example.com/simple',
                               )
        self.assertEqual(informer.options.index_urls,
                         ['http://example.com/simple'])

    def test_ctor_use_versions_no_versions_section(self):
        informer = self._makeOne('--use-versions')
        self.assertTrue(informer.options.use_versions)
        self.assertEqual(informer.options.versions_section, 'versions')

    def test_ctor_versions_section_no_use_versions(self):
        informer = self._makeOne('--versions-section=SECTION')
        self.assertTrue(informer.options.use_versions)
        self.assertEqual(informer.options.versions_section, 'SECTION')

    def test_ctor_default_logger(self):
        from compoze.informer import _print
        informer = self._makeOne('--fetch-site-packages')
        self.assertTrue(informer._logger is _print)

    def test_ctor_explicit_logger(self):
        informer = self._makeOne('--fetch-site-packages', logger=self)
        self.assertTrue(informer._logger is self)

    def test_ctor_w_versions(self):
        VERSIONS = {'versions': {'foo': '1.2.3'}}
        g_options = self._makeOptions(use_versions=True,
                                      config_file_data=VERSIONS,
                                     )
        informer = self._getTargetClass()(g_options)
        self.assertEqual(len(informer.requirements), 1)
        self.assertEqual(informer.requirements[0].project_name, 'foo')
        self.assertEqual(informer.requirements[0].specs, [('==', '1.2.3')])
        self.assertEqual(informer.requirements[0].extras, ())

    def test_ctor_w_versions_and_range(self):
        VERSIONS = {'versions': {'bar': '< 2.3dev'}}
        g_options = self._makeOptions(use_versions=True,
                                      config_file_data=VERSIONS,
                                     )
        informer = self._getTargetClass()(g_options)
        self.assertEqual(len(informer.requirements), 1)
        self.assertEqual(informer.requirements[0].project_name, 'bar')
        self.assertEqual(informer.requirements[0].specs, [('<', '2.3dev')])
        self.assertEqual(informer.requirements[0].extras, ())

    def test_ctor_w_versions_and_extra(self):
        VERSIONS = {'versions': {'baz|qux': '0.3'}}
        g_options = self._makeOptions(use_versions=True,
                                      config_file_data=VERSIONS,
                                     )
        informer = self._getTargetClass()(g_options)
        self.assertEqual(len(informer.requirements), 1)
        self.assertEqual(informer.requirements[0].project_name, 'baz')
        self.assertEqual(informer.requirements[0].specs, [('==', '0.3')])
        self.assertEqual(informer.requirements[0].extras, ('qux',))

    def test_blather_not_verbose(self):
        def _dont_go_here(*args):
            assert 0, args
        informer = self._makeOne('--quiet', logger=_dont_go_here)
        informer.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        logged = []
        informer = self._makeOne('--verbose', logger=logged.append)
        informer.blather('foo')
        self.assertEqual(logged, ['foo'])

    def test_show_distributions_empty_argv_raises(self):
        informer = self._makeOne(argv=[])
        self.assertRaises(ValueError, informer.show_distributions)

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
        self.assertTrue(skipped.search(log))
        self.assertTrue(found.search(log))

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
        self.assertTrue(skipped.search(log))
        self.assertTrue(found.search(log))

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
        self.project_name = name
        self.tmpdir = tmpdir
        self.precedence = precedence

    def _get_location(self):
        import os
        from compoze._compat import must_encode
        result = os.path.join(self.tmpdir, self.project_name) 
        f = open(result, 'wb')
        f.write(must_encode(self.project_name))
        f.flush()
        f.close()
        return result
    location = property(_get_location,)


class DummyIndex:

    def __init__(self, distros):
        mapping = self._mapping = {}
        for name, distro in distros:
            found = mapping.setdefault(distro.project_name, [])
            found.append(distro)

    def prescan(self):
        pass

    def find_packages(self, rqmt):
        pass

    def __getitem__(self, key):
        return self._mapping[key]
