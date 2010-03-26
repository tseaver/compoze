import unittest

class _CommandFaker:

    _orig_COMMANDS = None

    def tearDown(self):
        if self._orig_COMMANDS is not None:
            self._updateCommands(True, **self._orig_COMMANDS)

    def _updateCommands(self, clear=False, **kw):
        from compoze.compozer import _COMMANDS
        orig = _COMMANDS.copy()
        if clear:
            _COMMANDS.clear()
        _COMMANDS.update(kw)
        self._orig_COMMANDS = orig

class Test_get_description(unittest.TestCase, _CommandFaker):

    def _callFUT(self, dotted_or_ep):
        from compoze.compozer import get_description
        return get_description(dotted_or_ep)

    def test_nonesuch(self):
        self.assertRaises(KeyError, self._callFUT, 'nonesuch')

    def test_command_class_wo_docstring(self):
        class Dummy:
            pass
        self._updateCommands(dummy=Dummy)
        self.assertEqual(self._callFUT('dummy'), '')

    def test_command_class_w_docstring(self):
        class Dummy:
            "Dummy Command"
        self._updateCommands(dummy=Dummy)
        self.assertEqual(self._callFUT('dummy'), 'Dummy Command')

class CompozerTests(unittest.TestCase, _CommandFaker):

    _tempdir = None

    def tearDown(self):
        if self._tempdir is not None:
            import shutil
            shutil.rmtree(self._tempdir)

    def _getTargetClass(self):
        from compoze.compozer import Compozer
        return Compozer

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeTempdir(self):
        import tempfile
        self._tempdir = tempfile.mkdtemp()
        return self._tempdir

    def test_ctor_empty_argv_raises(self):
        self.assertRaises(ValueError, self._makeOne, argv=[])

    def test_ctor_non_command_first_raises(self):
        self.assertRaises(ValueError, self._makeOne, argv=['nonesuch'])

    def test_ctor_command_first_no_args(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        compozer = self._makeOne(argv=['dummy'])
        self.assertEqual(len(compozer.commands), 1)
        command = compozer.commands[0]
        self.failUnless(isinstance(command, Dummy))
        self.assertEqual(command.args, ())

    def test_ctor_command_first_w_args(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        compozer = self._makeOne(argv=['dummy', 'bar', 'baz'])
        self.assertEqual(len(compozer.commands), 1)
        command = compozer.commands[0]
        self.assertEqual(command.args, ('bar', 'baz'))

    def test_ctor_command_multiple_w_args(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        class Other(Dummy):
            pass
        self._updateCommands(dummy=Dummy, other=Other)
        compozer = self._makeOne(argv=['dummy', 'bar', 'baz', 'other', 'qux'])
        self.assertEqual(len(compozer.commands), 2)
        command = compozer.commands[0]
        self.failUnless(isinstance(command, Dummy))
        self.assertEqual(command.args, ('bar', 'baz'))
        command = compozer.commands[1]
        self.failUnless(isinstance(command, Other))
        self.assertEqual(command.args, ('qux',))

    def test_ctor_default_options(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        compozer = self._makeOne(argv=['dummy'])
        self.failUnless(compozer.options.verbose)
        self.assertEqual(compozer.options.path, '.')
        self.assertEqual(compozer.options.config_file, None)

    def test_ctor_quiet(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        compozer = self._makeOne(argv=['--quiet', 'dummy'])
        self.failIf(compozer.options.verbose)

    def test_ctor_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        compozer = self._makeOne(argv=['--verbose', 'dummy'])
        self.failUnless(compozer.options.verbose)

    def test_ctor_config_file(self):
        import os
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        dir = self._makeTempdir()
        fn = os.path.join(dir, 'test.cfg')
        f = open(fn, 'w')
        f.writelines(['[global]\n',
                      'path = /tmp/foo\n',
                     ])
        f.flush()
        f.close()
        compozer = self._makeOne(argv=['--config-file', fn, 'dummy'])
        self.assertEqual(compozer.options.config_file, fn)
        self.assertEqual(compozer.options.path, '/tmp/foo')

    def test_ctor_helpcommands(self):
        class Dummy:
            """Dummy command"""
        class Other(Dummy):
            """OTher command"""
        self._updateCommands(True, dummy=Dummy, other=Other)
        logged = []
        compozer = self._makeOne(argv=['--help-commands'],
                                 logger=logged.append)
        self.assertEqual(len(logged), 5)
        self.assertEqual(logged[0], 'Valid commands are:')
        self.assertEqual(logged[1], ' dummy')
        self.assertEqual(logged[2], '    ' + Dummy.__doc__)
        self.assertEqual(logged[3], ' other')
        self.assertEqual(logged[4], '    ' + Other.__doc__)

    def test__call___w_commands(self):
        class Dummy:
            called = False
            def __init__(self, options, *args):
                pass
            def __call__(self):
                if self.called:
                    raise ValueError
                self.called = True
        class Other(Dummy):
            pass
        self._updateCommands(dummy=Dummy, other=Other)
        compozer = self._makeOne(argv=['dummy', 'bar', 'baz', 'other', 'qux'])
        compozer()
        self.failUnless(compozer.commands[0].called)
        self.failUnless(compozer.commands[1].called)

    def test_error(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['dummy'],
                                 logger=logged.append)
        compozer.error('foo')
        self.assertEqual(logged, ['foo'])

    def test_error_not_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['--verbose', 'dummy'],
                                 logger=logged.append)
        compozer.error('foo')
        self.assertEqual(logged, ['foo'])

    def test_error_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['--verbose', 'dummy'],
                                 logger=logged.append)
        compozer.error('foo')
        self.assertEqual(logged, ['foo'])

    def test_blather_not_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        def _dont_go_here(*args):
            assert 0, args
        compozer = self._makeOne(argv=['--quiet', 'dummy'],
                                 logger=_dont_go_here)
        compozer.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['--verbose', 'dummy'],
                                 logger=logged.append)
        compozer.blather('foo')
        self.assertEqual(logged, ['foo'])

class Test_main(unittest.TestCase, _CommandFaker):

    def _callFUT(self, argv):
        from compoze.compozer import main
        return main(argv)

    def test_simple(self):
        called = {}
        class Dummy:
            def __init__(self, options, *args):
                pass
            def __call__(self):
                if self.__class__.__name__ in called:
                    raise ValueError
                called[self.__class__.__name__] = True
        class Other(Dummy):
            pass
        self._updateCommands(dummy=Dummy, other=Other)
        self._callFUT(argv=['dummy', 'bar', 'baz', 'other', 'qux'])
        self.failUnless('Dummy' in called)
        self.failUnless('Other' in called)
