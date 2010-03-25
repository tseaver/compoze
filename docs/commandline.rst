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

.. cmdoption:: -s, --help-commands

   Print help on the available sub-commands.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output.

.. cmdoption:: -v, --verbose

   Print more informative output.

.. cmdoption:: -p, --path

   Default path for subcommand target.


.. _compoze_fetch_options:

:command:`compoze fetch` Subcommand
-----------------------------------

Usage:

.. code-block:: sh

   $ compoze [GLOBAL OPTIONS] fetch [OPTIONS] [REQUIREMENT]*

Options:

.. program:: compoze fetch

.. cmdoption:: -p, --path=DIRECTORY

   Fetch :term:`source distribution` archives into this directory
   (overrides global option).

.. cmdoption:: -u, --index-url

   Index from which to retrieve any :term:`source distribution` archives
   (may be repeated).

.. cmdoption:: -l, --find-link

   Extra URL to search for links to :term:`source distribution` archives
   (may be repeated).

.. cmdoption:: -f, --fetch-site-packages

   In addition to any :term:`requirement` (s) specified on the command
   line, fetch a :term:`source distribution` archives for each
   :term:`project` installed in the current Python environment.

.. cmdoption:: -b, --include-binary-eggs

   Search :term:`binary distribution` archives in addition to
   :term:`source distribution` archives for each :term:`requirement`.
   Disabled by default.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).

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

.. cmdoption:: -p, --path=DIRECTORY

   Index :term:`source distribution` archives in this directory
   (overrides global option).

.. cmdoption:: -n, --index-name

   Override the name of the index subdirectory.  (Defaults to ``simple``).

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).

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

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).

.. cmdoption:: -p, --path=DIRECTORY

   Move :term:`source distribution` archives from this directory to the
   pool (overrides global option).


.. _compoze_show_options:

:command:`compoze show` Subcommand
----------------------------------

Usage:

.. code-block:: sh

   $ compoze [GLOBAL OPTIONS] show [OPTIONS] [REQUIREMENT]*

Options:

.. program:: compoze show

.. cmdoption:: -u, --index-url

   Index from which to retrieve any :term:`source distribution` archives
   (may be repeated).

.. cmdoption:: -f, --fetch-site-packages

   In addition to any :term:`requirement` (s) specified on the command
   line, show information about :term:`source distribution` archives for
   each :term:`project` installed in the current Python environment.

.. cmdoption:: -o, --show-only-best

   Show information only for the "best" :term:`source distribution`
   for each :term:`requirement`.  By default, show information for
   any :term:`source distribution` found for each requirement.

.. cmdoption:: -b, --include-binary-eggs

   Search :term:`binary distribution` archives in addition to
   :term:`source distribution` archives for each :term:`requirement`.
   Disabled by default.

.. cmdoption:: -d, --include-develop-eggs

   Search :term:`development egg` projects in addition to
   :term:`source distribution` archives for each :term:`requirement`.
   Disabled by default.

.. cmdoption:: -q, --quiet

   Suppress all non-essential output (overrides global option).

.. cmdoption:: -v, --verbose

   Print more informative output (overrides global option).
