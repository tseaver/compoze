Configuration File Reference
============================

In addition to the :doc:`command line syntax <commandline>`, you can pass
options to :command:`compoze` via one or more configuration files:

.. code-block:: sh

   $ bin/compoze --config-file=file1.cfg --config-file=file2.cfg

Each configuration file is expected to be an INI-style file, including
either or both a :ref:`[globals] <config_global>` section and a
:ref:`[versions] <config_versions>` section.
   
If multiple configuration files are specified (i.e., by repeating the
``config-file`` option), then values configured in later files override those
configured in earlier files.


.. _config_global:

The ``[globals]`` Section
-------------------------

This section provides values for options which are global across
:command:`compoze` subcommands.  The allowed names and values are similar
to the long-form options specified in :ref:`compoze_options`, except that
the leading ``--`` is elided.  For example:

.. code-block:: ini

   [globals]
   path = /path/to/index
   index-url =
    http://example.com/simple
    http://example.com/complex
   verbose = false

The following command-line options are redundant or meaningless in
a configuration file, and hence are not supported:

- ``--help``
- ``--help-commands``
- ``--config-file``
- ``--quiet`` (use ``verbose = false``)


.. _config_versions:

The ``[versions]`` Section
--------------------------

Each key in this section corresponds to a :term:`project`, and defines
a restriction on which :term:`release` (s) should be consulted / fetched.

The syntax for a project pinned to a single version is:

.. code-block:: ini

   projectname = x.y.z

Projects can also be pinned to a range of releases, using the normal
:mod:`pkg_resources` version specifiers.

.. code-block:: ini

   fooproject = <x.y.z
   barproject = >=x.y.z
   quxproject = >=x.y.z,<a.b

In this case, the first equals sign after the project name is **not** part
of the specifier:  it merely separates the project name from the actual
specifier.

Projects defined in this section can also define optional :term:`extra`
tags:

.. code-block:: ini

   fooproject|qux = <x.y.z
   barproject|baz,spam = >=x.y.z

The ``|`` symbol divides the project name from a comma-separated list of
:term:`extra` tags to be included.
