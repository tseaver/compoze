Querying Distributions
======================

The :command:`compoze show` command displays information about
any :term:`source distribution` available in a given :term:`package index`
matching a set of :term:`requirement` specifications.

.. code-block:: sh

   $ bin/compoze show someproject

As with other tools based on :mod:`distutils`, :command:`compoze show`
will respect any version constraint on a :term:`requirement`:

.. code-block:: sh

   $ bin/compoze show "someproject>=2.1"

By default, :command:`compoze show` uses the ``simple`` API of the Python
Package Index (http://pypi.python.org/simple) to find
:term:`source distribution` archives.  You can override this default with the
URL of a different :term:`package index`:

.. code-block:: sh

   $ bin/compoze show --index-url=http://dist.repoze.org/simple someproject

You can supply more than one index URL, and more than one :term:`requirement`:

.. code-block:: sh

   $ bin/compoze show \
        --index-url=http://example.com/index \
        --index-url=http://another.example.com/index \
        someproject "another_project==3.2.1"

You can also use :command:`compoze show` to display information about any
available :term:`source distribution` for each project already installed
in your Python's ``site-packges``:

.. code-block:: sh

   $ bin/compoze show --fetch-site-packages

See :ref:`compoze_show_options` for the full command-line reference.


Fetching Distributions
======================

The :command:`compoze fetch` command retrieves a :term:`source distribution` 
from a :term:`package index` for each :term:`requirement` specified.

.. code-block:: sh

   $ bin/compoze fetch someproject

As with other tools based on :mod:`distutils`, :command:`compoze fetch`
will respect any version constraint on a :term:`requirement`:

.. code-block:: sh

   $ bin/compoze fetch "someproject>=2.1"

By default, :command:`compoze fetch` saves the retrieved files in the current
directory.  You can override that default using the ``--path`` option:

.. code-block:: sh

   $ bin/compoze fetch --path=/tmp/index someproject

By default, :command:`compoze fetch` uses the ``simple`` API of the Python
Package Index (http://pypi.python.org/simple) to find
:term:`source distribution` archives.  You can override this default with 
the URL of a different :term:`package index`:

.. code-block:: sh

   $ bin/compoze fetch --index-url=http://dist.repoze.org/simple someproject

You can supply more than one index, and more than one :term:`requirement`:

.. code-block:: sh

   $ bin/compoze fetch \
        --index-url=http://example.com/index \
        --index-url=http://another.example.com/index \
        someproject "another_project==3.2.1"

You can also use :command:`compoze fetch` to retrieve a :term:`source
distribution` for each egg already installed in your Python's
``site-packges``:

.. code-block:: sh

   $ bin/compoze fetch --fetch-site-packages

See :ref:`compoze_fetch_options` for the full command-line reference.


Building a Package Index
========================

:command:`compoze index` makes a PyPI-like package index of all archives
in the target directory:

.. code-block:: sh

   $ bin/compoze index

By default, :command:`compoze index` uses the current directory as the base
directory for the index.  You can override this default using the ``--path``
option:

.. code-block:: sh

   $ bin/compoze index --path=/tmp/downloads

By default, :command:`compose index` creates the index a subdirectory named
``simple`` in the target path.  You can override that name using the
``--index-name`` option:

.. code-block:: sh

   $ bin/compoze index --index-name=other

One common use case is to capture the "known good set" represented
by a given Python environment.  In this case, you want both to download
the distributions corresponding to the projects installed in site-packages,
and also make a package index from them:

.. code-block:: sh

   $ bin/compoze \
        fetch --fetch-site-packages --path kgs \
        index --path kgs

See :ref:`compoze_index_options` for the full command-line reference.


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

See :ref:`compoze_pool_options` for the full command-line reference.
