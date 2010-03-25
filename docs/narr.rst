Querying Distributions
======================

The :command:`compoze show` command displays information about
any :term:`source distribution` available in a given index matching a set of
:term:`requirement` specifications.

For instance, to show information about any :term:`source distribution`
for version 2.1 or later of :mod:`myproject`:

.. code-block:: sh

   $ bin/compoze show \
        --index-url=http://dist.repoze.org/simple \
        "myproject>=2.1"

If you do not supply an index URL, :command:`compoze show` uses the Python
Package Index (http://pypi.python.org/pypi) by default:

.. code-block:: sh

   $ bin/compoze show --path=/tmp/index someproject

You can supply more than one index, and more than one :term:`requirement`:

.. code-block:: sh

   $ bin/compoze show \
        --index-url=http://example.com/index \
        --index-url=http://another.example.com/index \
        someproject "another_project==3.2.1"


Example: Querying already-installed projects
--------------------------------------------

You can also use :command:`compoze show` to display information about any
available :term:`source distribution` for each project already installed
in your Python's ``site-packges``:

.. code-block:: sh

   $ bin/compoze show --fetch-site-packages


Fetching Distributions
======================

The :command:`compoze fetch` command retrieves a :term:`source distribution` 
for each :term:`requirement` specified.

For instance, to fetch a :term:`source distribution` for version 2.1 or later
of :mod:`myproject`:

.. code-block:: sh

   $ bin/compoze fetch \
        --path=/tmp/index \
        --index-url=http://dist.repoze.org/simple \
        "myproject>=2.1"

If you do not supply an index URL, :command:`compoze fetch` uses the ``simple``
API (http://pypi.python.org/simple) of the Python Package Index (browseable
at http://pypi.python.org/pypi):

.. code-block:: sh

   $ bin/compoze fetch --path=/tmp/index someproject

You can supply more than one index, and more than one :term:`requirement`:

.. code-block:: sh

   $ bin/compoze fetch \
        --path=/tmp/index \
        --index-url=http://example.com/index \
        --index-url=http://another.example.com/index \
        someproject "another_project==3.2.1"

If you do not supply a path, :command:`compoze fetch` uses the current
directory.


Example: Fetching distributions for already-installed projects
--------------------------------------------------------------

You can also use :command:`compoze fetch` to retrieve a :term:`source
distribution` for each egg already installed in your Python's
``site-packges``:

.. code-block:: sh

   $ bin/compoze fetch --path=/tmp/foo --fetch-site-packages


Building a Package Index
========================

:command:`compoze index` makes a PyPI-like package index of all archives
in the target directory:

.. code-block:: sh

   $ bin/compoze index --path=/tmp/downloads

By default, the index is created as a subdirectory named ``simple`` in
the target path.  You can override that name:

.. code-block:: sh

   $ bin/compoze index --path=/tmp/downloads --index-name=other


Example:  Creating a package index for already-installed projects
-----------------------------------------------------------------

One common use case is to capture the "known good set" represented
by a given Python environment.  In this case, you want both to download
the distributions corresponding to the projects installed in site-packages,
and also make a package index from them:

.. code-block:: sh

   $ bin/compoze \
        fetch --fetch-site-packages --path kgs \
        index --path kgs


Consolidating Package Indexes
=============================

After fetching muliple package sets into separate directories (e.g., for
projects which use the same frameworks, or for mutliple deployments of
a single project), you may find that many of the :term:`source distribution`
archives overlap between the indexes you have created, wasting disk space.
:command:`compoze pool` allows you to consolidate these index directories
into a shared "pool" directory, leaving behind symbolic links.

.. code-block:: sh

   $ mkdir /path/to/pool
   $ bin/compoze pool --path=/path/to/projectA /path/to/pool
   $ bin/compoze pool --path=/path/to/projectB /path/to/pool
