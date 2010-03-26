import unittest

class FetcherTests(unittest.TestCase):

    _tmpdir = None

    def tearDown(self):
        if self._tmpdir is not None:
            import shutil
            shutil.rmtree(self._tmpdir)

    def _getTargetClass(self):
        from compoze.fetcher import Fetcher
        return Fetcher

    def _makeValues(self, **kw):
        from optparse import Values
        return Values(kw.copy())

    def _makeOptions(self, path='.', default_verbose=False, *args, **kw):
        default = kw.copy()
        default.setdefault('verbose', default_verbose)
        values = self._makeValues(**default)
        values.path = path
        return values

    def _makeOne(self, *args, **kw):
        options = self._makeOptions('.', False, *args, **kw)
        logger = kw.pop('logger', None)
        if logger is not None:
            return self._getTargetClass()(options, logger=logger, *args)
        return self._getTargetClass()(options, *args)

    def _makeTempDir(self):
        import tempfile
        result = self._tmpdir = tempfile.mkdtemp()
        return result

    def _makeDirs(self):
        import os
        tmpdir = self._makeTempDir()
        target = os.path.join(tmpdir, 'target')
        os.makedirs(target)
        path = os.path.join(self._tmpdir, 'path')
        os.makedirs(path)
        return target, path

    def _makeIndex(self, *rqmts, **kw):
        target = kw.get('target')
        return DummyIndex(
                dict([(x, DummyDistribution(x.project_name, target))
                            for x in rqmts]))

    def test_ctor_defaults(self):
        import os
        values = self._makeValues()
        fetcher = self._getTargetClass()(values)
        path = os.path.abspath(os.path.expanduser('.'))
        self.assertEqual(fetcher.path, path)
        self.failIf(fetcher.options.verbose)
        self.assertEqual(fetcher.options.index_urls,
                         ['http://pypi.python.org/simple'])
        self.assertEqual(fetcher.options.find_links, [])
        self.failIf(fetcher.options.fetch_site_packages)
        self.failUnless(fetcher.options.source_only)
        self.failIf(fetcher.options.keep_tempdir)

    def test_ctor_uses_global_options_as_default(self):
        g_options = self._makeOptions(path='/tmp/foo',
                                      verbose=True,
                                      index_urls=['http://example.com/simple'],
                                      find_links=['http://example.com/links'],
                                      fetch_site_packages=True,
                                      source_only=False,
                                      keep_tempdir=True,
                                     )
        fetcher = self._getTargetClass()(g_options)
        self.assertEqual(fetcher.path, '/tmp/foo')
        self.assertEqual(fetcher.options.index_urls,
                         ['http://example.com/simple'])
        self.assertEqual(fetcher.options.find_links,
                         ['http://example.com/links'])
        self.failUnless(fetcher.options.fetch_site_packages)
        self.failIf(fetcher.options.source_only)
        self.failUnless(fetcher.options.keep_tempdir)

    def test_ctor_invalid_path_doesnt_raise(self):
        import os
        path = os.path.abspath(os.path.expanduser(__file__))
        fetcher = self._makeOne('--path=%s' % __file__)
        self.assertEqual(fetcher.path, path)

    def test_ctor_valid_path_existing(self):
        path = self._makeTempDir()
        fetcher = self._makeOne('--path=%s' % path)
        self.assertEqual(fetcher.path, path)

    def test_ctor_valid_path_non_existing_doesnt_create(self):
        import os
        path = self._makeTempDir()
        target = os.path.join(path, 'target')
        fetcher = self._makeOne('--path=%s' % target)
        self.assertEqual(fetcher.path, target)
        self.failIf(os.path.isdir(target))

    def test_ctor_explicit_index_url(self):
        fetcher = self._makeOne('--index-url=http://example.com/simple',
                               )
        self.assertEqual(fetcher.options.index_urls,
                         ['http://example.com/simple'])

    def test_ctor_find_links(self):
        fetcher = self._makeOne('--find-links=http://example.com/links',
                               )
        self.assertEqual(fetcher.options.find_links,
                         ['http://example.com/links'])

    def test_ctor_w_simple_requirement(self):
        fetcher = self._makeOne('compoze')
        self.assertEqual(len(fetcher.requirements), 1)
        self.assertEqual(fetcher.requirements[0].project_name, 'compoze')
        self.assertEqual(fetcher.requirements[0].specs, [])
        self.assertEqual(fetcher.requirements[0].extras, ())

    def test_ctor_w_versioned_requirement(self):
        fetcher = self._makeOne('compoze==0.1')
        self.assertEqual(len(fetcher.requirements), 1)
        self.assertEqual(fetcher.requirements[0].project_name, 'compoze')
        self.assertEqual(fetcher.requirements[0].specs, [('==', '0.1')])
        self.assertEqual(fetcher.requirements[0].extras, ())

    def test_ctor_w_multiversioned_requirement(self):
        fetcher = self._makeOne('compoze>=0.1,<=0.3dev')
        self.assertEqual(len(fetcher.requirements), 1)
        self.assertEqual(fetcher.requirements[0].project_name, 'compoze')
        self.assertEqual(fetcher.requirements[0].specs,
                         [('>=', '0.1'), ('<=', '0.3dev')])
        self.assertEqual(fetcher.requirements[0].extras, ())

    def test_ctor_w_requirement_single_extra(self):
        fetcher = self._makeOne('compoze[nonesuch]')
        self.assertEqual(len(fetcher.requirements), 1)
        self.assertEqual(fetcher.requirements[0].project_name, 'compoze')
        self.assertEqual(fetcher.requirements[0].specs, [])
        self.assertEqual(fetcher.requirements[0].extras, ('nonesuch',))

    def test_ctor_w_requirement_multiple_extra(self):
        fetcher = self._makeOne('compoze[nonesuch,bother]')
        self.assertEqual(len(fetcher.requirements), 1)
        self.assertEqual(fetcher.requirements[0].project_name, 'compoze')
        self.assertEqual(fetcher.requirements[0].specs, [])
        self.assertEqual(fetcher.requirements[0].extras,
                         ('nonesuch', 'bother'))

    def test_ctor_default_logger(self):
        from compoze.fetcher import _print
        fetcher = self._makeOne()
        self.failUnless(fetcher._logger is _print)

    def test_ctor_explicit_logger(self):
        fetcher = self._makeOne(logger=self)
        self.failUnless(fetcher._logger is self)

    def test_ctor_index_factory(self):
        from compoze.index import CompozePackageIndex
        fetcher = self._makeOne()
        self.failUnless(fetcher.index_factory is CompozePackageIndex)

    def test_blather_not_verbose(self):
        def _dont_go_here(*args):
            assert 0, args
        fetcher = self._makeOne('--quiet', logger=_dont_go_here)
        fetcher.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        logged = []
        fetcher = self._makeOne('--verbose', logger=logged.append)
        fetcher.blather('foo')
        self.assertEqual(logged, ['foo'])

    def test_download_distributions_no_rqmts_or_fsp_raises(self):
        fetcher = self._makeOne(argv=[])
        self.assertRaises(ValueError, fetcher.download_distributions)

    def test_download_distributions_invalid_path_raises(self):
        fetcher = self._makeOne('--path=%s' % __file__, 'compoze')
        self.assertRaises(ValueError, fetcher.download_distributions)

    def test_download_distributes_valid_path_non_existing_creates(self):
        import os
        from pkg_resources import Requirement
        root = self._makeTempDir()
        target = os.path.join(root, 'target')
        os.makedirs(target)
        path = os.path.join(root, 'path')
        self.failIf(os.path.isdir(path))
        #os.makedirs(path) NOT!  we want download_distributions to make it.
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex(rqmt)
        local = self._makeIndex(rqmt, target=target)
        def _factory(index_url, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path, 'compoze')
        self.failIf(os.path.isdir(path))
        fetcher.index_factory = _factory
        fetcher.tmpdir = target
        fetcher.download_distributions()
        self.failUnless(os.path.isdir(path))

    def test_download_distributions_no_find_links(self):
        import os
        from pkg_resources import Requirement
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex(rqmt)
        local = self._makeIndex(rqmt, target=target)
        def _factory(index_url, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path, 'compoze')
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failUnless(os.path.isfile(os.path.join(path, 'compoze')))

    def test_download_distributions_w_missing_dist(self):
        import os
        from pkg_resources import Requirement
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex()
        local = self._makeIndex(target=target)
        def _factory(index_url, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path, 'compoze')
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failIf(os.path.isfile(os.path.join(path, 'compoze')))

    def test_download_distributions_w_dist_on_both_indexes(self):
        import os
        from pkg_resources import Requirement
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex(rqmt)
        other = self._makeIndex(rqmt)
        local = self._makeIndex(rqmt, target=target)
        def _factory(index_url, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url == 'http://example.com/simple':
                assert search_path is None
                return other
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path,
                                '--index=http://pypi.python.org/simple',
                                '--index=http://example.com/simple',
                                'compoze')
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(other._fetched_with, [])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failUnless(os.path.isfile(os.path.join(path, 'compoze')))

    def test_download_distributions_w_dist_not_on_first_index(self):
        import os
        from pkg_resources import Requirement
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex()
        other = self._makeIndex(rqmt)
        local = self._makeIndex(rqmt, target=target)
        def _factory(index_url, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url == 'http://example.com/simple':
                assert search_path is None
                return other
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path,
                                '--index=http://pypi.python.org/simple',
                                '--index=http://example.com/simple',
                                'compoze')
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(other._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failUnless(os.path.isfile(os.path.join(path, 'compoze')))

    def test_download_distributions_w_find_links_dist_in_index(self):
        import os
        from pkg_resources import Requirement
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex(rqmt)
        local = self._makeIndex(rqmt, target=target)
        findlinks = self._makeIndex()
        def _factory(index_url=None, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            if index_url is None:
                assert search_path is None
                return findlinks
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path,
                                '--find-link=http://example.com/',
                                'compoze')
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(findlinks._fetched_with, [])
        self.assertEqual(findlinks._find_links, ['http://example.com/'])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failUnless(os.path.isfile(os.path.join(path, 'compoze')))

    def test_download_distributions_w_find_links_dist_not_in_index(self):
        import os
        from pkg_resources import Requirement
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex()
        local = self._makeIndex(rqmt, target=target)
        findlinks = self._makeIndex(rqmt)
        def _factory(index_url=None, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            if index_url is None:
                assert search_path is None
                return findlinks
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path,
                                '--find-link=http://example.com/',
                                'compoze')
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(findlinks._fetched_with,
                         [(rqmt, target, False, True, False)])
        self.assertEqual(findlinks._find_links, ['http://example.com/'])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failUnless(os.path.isfile(os.path.join(path, 'compoze')))

    def test_download_distributions_w_cheeseshop_raises(self):
        import os
        from pkg_resources import Requirement
        logged = []
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex()
        def _fetch_distribution(rqmt, target_dir, force_scan=False,
                                source=False, develop_ok=False):
            cheeseshop._fetched_with.append(
                    (rqmt, target_dir, force_scan, source, develop_ok))
            raise AttributeError
        cheeseshop.fetch_distribution = _fetch_distribution
        local = self._makeIndex(rqmt, target=target)
        def _factory(index_url=None, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path,
                                'compoze', logger=logged.append)
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failUnless(os.path.isfile(os.path.join(path, 'compoze')))
        self.assertEqual(logged, ['  Error fetching: compoze'])

    def test_download_distributions_w_local_raises(self):
        import os
        from pkg_resources import Requirement
        target, path = self._makeDirs()
        rqmt = Requirement.parse('compoze')
        cheeseshop = self._makeIndex(rqmt, target=target)
        local = self._makeIndex()
        def _fetch_distribution(rqmt, target_dir, force_scan=False,
                                source=False, develop_ok=False):
            local._fetched_with.append(
                    (rqmt, target_dir, force_scan, source, develop_ok))
            raise AttributeError
        local.fetch_distribution = _fetch_distribution
        def _factory(index_url=None, search_path=None):
            if index_url == 'http://pypi.python.org/simple':
                assert search_path is None
                return cheeseshop
            if index_url ==  target:
                assert search_path is ()
                return local
            raise ValueError(index_url)
        fetcher = self._makeOne('--quiet', '--path=%s' % path,
                                'compoze')
        fetcher.index_factory = _factory
        fetcher.tmpdir = target

        fetcher.download_distributions()

        self.assertEqual(cheeseshop._fetched_with,
                         [(rqmt, target, False, True, False)])

        self.assertEqual(local._fetched_with,
                         [(rqmt, target, True, False, False)])

        self.failIf(os.path.isfile(os.path.join(path, 'compoze')))



class DummyDistribution(object):

    def __init__(self, name, tmpdir=None, precedence=None):
        self.project_name = name
        self.tmpdir = tmpdir
        self.precedence = precedence

    def _get_location(self):
        import os
        result = os.path.join(self.tmpdir, self.project_name) 
        f = open(result, 'wb')
        f.write(self.project_name)
        f.flush()
        f.close()
        return result
    location = property(_get_location,)

class DummyIndex:

    def __init__(self, mapping):
        self._mapping = mapping
        self._fetched_with = []
        self._find_links = []

    def fetch_distribution(self, rqmt, target_dir,
                           force_scan=False, source=False, develop_ok=False):
        self._fetched_with.append(
                    (rqmt, target_dir, force_scan, source, develop_ok))
        return self._mapping.get(rqmt)

    def add_find_links(self, links):
        self._find_links.extend(links)
