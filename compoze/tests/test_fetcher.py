import unittest

class CompozePackageIndexTests(unittest.TestCase):

    def _getTargetClass(self):
        from compoze.fetcher import CompozePackageIndex
        return CompozePackageIndex

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        cpi = self._makeOne()
        self.assertEqual(cpi.debug_msgs, [])
        self.assertEqual(cpi.info_msgs, [])
        self.assertEqual(cpi.warn_msgs, [])

    def test_debug(self):
        cpi = self._makeOne()
        cpi.debug('foo')
        self.assertEqual(cpi.debug_msgs, [('foo', ())])

    def test_info(self):
        cpi = self._makeOne()
        cpi.info('foo')
        self.assertEqual(cpi.info_msgs, [('foo', ())])

    def test_warn(self):
        cpi = self._makeOne()
        cpi.warn('foo')
        self.assertEqual(cpi.warn_msgs, [('foo', ())])

class FetcherTests(unittest.TestCase):

    _tmpdir = None

    def tearDown(self):
        if self._tmpdir is not None:
            import shutil
            shutil.rmtree(self._tmpdir)

    def _getTargetClass(self):
        from compoze.fetcher import Fetcher
        return Fetcher

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

    def test_ctor_empty_argv_raises(self):
        self.assertRaises(ValueError, self._makeOne, argv=[])

    def test_ctor_no_download_invalid_path_raises(self):
        self.assertRaises(ValueError, self._makeOne,
                          '--fetch-site-packages',
                          '--path=%s' % __file__,
                         )

    def test_ctor_valid_path_existing(self):
        path = self._makeTempDir()
        fetcher = self._makeOne('--fetch-site-packages',
                                '--path=%s' % path)
        self.assertEqual(fetcher.path, path)

    def test_ctor_valid_path_non_existing_creates(self):
        import os
        path = self._makeTempDir()
        target = os.path.join(path, 'target')
        fetcher = self._makeOne('--fetch-site-packages',
                                '--path=%s' % target)
        self.failUnless(os.path.isdir(target))
        self.assertEqual(fetcher.path, target)

    def test_ctor_default_index_url_is_cheeseshop(self):
        fetcher = self._makeOne('--fetch-site-packages')
        self.assertEqual(fetcher.options.index_urls,
                         ['http://pypi.python.org/simple'])

    def test_ctor_default_logger(self):
        from compoze.fetcher import _print
        fetcher = self._makeOne('--fetch-site-packages')
        self.failUnless(fetcher._logger is _print)

    def test_ctor_explicit_logger(self):
        fetcher = self._makeOne('--fetch-site-packages', logger=self)
        self.failUnless(fetcher._logger is self)

    def test_ctor_index_factory(self):
        from compoze.fetcher import CompozePackageIndex
        fetcher = self._makeOne('--fetch-site-packages')
        self.failUnless(fetcher.index_factory is CompozePackageIndex)

    def test_ctor_explicit_index_url(self):
        fetcher = self._makeOne('--fetch-site-packages',
                               '--index-url=http://dist.repoze.org/nonesuch',
                              )
        self.assertEqual(fetcher.options.index_urls,
                         ['http://dist.repoze.org/nonesuch'])

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

    def test_blather_not_verbose(self):
        def _dont_go_here(*args):
            assert 0, args
        fetcher = self._makeOne('--fetch-site-packages',
                                 '--quiet',
                                 logger=_dont_go_here)
        fetcher.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        logged = []
        fetcher = self._makeOne('--fetch-site-packages',
                                 '--verbose',
                                 logger=logged.append)
        fetcher.blather('foo')
        self.assertEqual(logged, ['foo'])

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


class DummyDistribution(object):

    def __init__(self, name, tmpdir=None):
        self.name = name
        self.tmpdir = tmpdir

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
