Command-Line Reference
======================


.. _compoze_options:

:command:`compoze`
------------------

Usage:

.. code-block:: sh

   $ compoze [GLOBAL OPTIONS] [subcommand [SUBCOMMAND OPTIONS]]*

Global options:

.. program:: compoze

.. cmdoption:: -h, --help

   Show usage and exit.

.. cmdoption:: -s, --help-commands

   Print help on the available sub-commands.

.. cmdoption:: -c CONFIG_FILE, --config-file=CONFIG_FILE

   Parse options from an INI-style config file.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output.

.. cmdoption:: -v, --verbose

   Print more informative output.

.. cmdoption:: -p PATH, --path=PATH

   Use ``PATH`` as the default path for subcommands.


.. _compoze_fetch_options:

:command:`compoze fetch` Subcommand
-----------------------------------

Usage:

.. code-block:: sh

   $ compoze [GLOBAL OPTIONS] fetch [OPTIONS] [REQUIREMENT]*

Options:

.. program:: compoze fetch

.. cmdoption:: -h, --help

   Show usage and exit.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).

.. cmdoption:: -p PATH, --path=PATH

   Fetch :term:`source distribution` archives into ``PATH``
   (overrides global option).

.. cmdoption:: -u INDEX_URL, --index-url=INDEX_URL

   Add ``INDEX_URL`` to the list of indexes to consult when searching for
   a :term:`source distribution`.  May be repeated.  If not passed, default
   to searching PyPI (http://pypi.python.org/simple).

.. cmdoption:: -l FIND_LINKS_URL, --find-link=FIND_LINKS_URL

   Add ``FIND_LINKS_URL`` to the list of pages in which to search for links
   to :term:`source distribution` archives.  May be repeated.

.. cmdoption:: -f, --fetch-site-packages

   In addition to any :term:`requirement` specified on the command
   line, fetch :term:`source distribution` archives for each
   :term:`project` installed in the current Python environment.

.. cmdoption:: -b, --include-binary-eggs

   Search :term:`binary distribution` archives in addition to
   :term:`source distribution` archives for each :term:`requirement`.
   Disabled by default.

.. cmdoption:: -k, --keep-tempdir

   Don't remove the temporary directory created during the indexing
   operation (normally useful only for debugging the command).


.. _compoze_index_options:

:command:`compoze index` Subcommand
-----------------------------------

Usage:

.. code-block:: sh

   $ compoze [GLOBAL OPTIONS] index [OPTIONS]

Options:

.. program:: compoze index

.. cmdoption:: -h, --help

   Show usage and exit.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).

.. cmdoption:: -p PATH, --path=PATH

   Index :term:`source distribution` archives in ``PATH``.
   (overrides global option).

.. cmdoption:: -n INDEX_NAME, --index-name=INDEX_NAME

   Use ``INDEX_NAME`` as the name of the index subdirectory inside the
   directory being indexed.  Defaults to "simple".

.. cmdoption:: -k, --keep-tempdir

   Don't remove the temporary directory created during the indexing
   operation (normally useful only for debugging the command).


.. _compoze_pool_options:

:command:`compoze pool` Subcommand
----------------------------------

Usage:

.. code-block:: sh

   $ compoze [GLOBAL OPTIONS] pool [OPTIONS] POOL_DIR

Options:

.. program:: compoze pool

.. cmdoption:: -h, --help

   Show usage and exit.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).

.. cmdoption:: -p PATH, --path=PATH

   Move :term:`source distribution` archives from ``PATH`` into ``POOL_DIR``,
   and create symlinks in ``PATH`` (overrides global option).


.. _compoze_show_options:

:command:`compoze show` Subcommand
----------------------------------

Usage:

.. code-block:: sh

   $ compoze [GLOBAL OPTIONS] show [OPTIONS] [REQUIREMENT]*

Options:

.. program:: compoze show

.. cmdoption:: -h, --help

   Show usage and exit.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).

.. cmdoption:: -u INDEX_URL, --index-url=INDEX_URL

   Add ``INDEX_URL`` to the list of indexes to consult when searching for
   a :term:`source distribution`.  May be repeated.  If not passed, default
   to searching PyPI (http://pypi.python.org/simple).

.. cmdoption:: -f, --fetch-site-packages

   In addition to any :term:`requirement` specified on the command
   line, show information about :term:`source distribution` archives for
   each :term:`project` installed in the current Python environment.

.. cmdoption:: -o, --show-only-best

   Show information only for the "best" :term:`source distribution`
   for each :term:`requirement`.  By default, show information for
   each :term:`source distribution` matching a given :term:`requirement`.

.. cmdoption:: -b, --include-binary-eggs

   Search :term:`binary distribution` archives in addition to
   :term:`source distribution` archives for each :term:`requirement`.
   Disabled by default.

.. cmdoption:: -d, --include-develop-eggs

   Search :term:`development egg` projects in addition to
   :term:`source distribution` archives for each :term:`requirement`.
   Disabled by default.
