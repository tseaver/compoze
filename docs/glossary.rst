Glossary
========

.. glossary::

   binary distribution
        An archive of the installable files of a particular version of a
        :term:`project`, produced using one of the
        :command:`python setup.py bdist_*` commands.

   development egg
        An checkout of the development sources of of a :term:`project`,
        added to Python's system path using the
        :command:`python setup.py develop` command.

   extra
        Additional "tags" on a requirement, indicating a dependency on
        optional features of the :term:`project`.  See the `pkg_resources
        Requirements Parsing
        <http://peak.telecommunity.com/DevCenter/PkgResources#id11>`_
        documentation for more.

   package index
        A web page listing projects known to the index, where each
        :term:`project` has a separate URL listing distributions (source
        or binary) in the index for each :term:`release` of the
        :term:`project`.  This is the format of the ``simple`` API
        of the Python Package Index:  http://pypi.python.org/simple/

   project
        A named collection of releases of a given Python library or
        application, packaged using :mod:`distutils` or one of its
        derivatives.

   release
        A numbered version of a :term:`project` released as software,
        normally as one or more distributions (source or binary).

   requirement
        A string specifying a :mod:`distutils` :term:`project` name.
        Can be optionally restricted to a given version or range of versions.

   source distribution
        An archive of the sources of a particular version of a
        :term:`project`, produced using :command:`python setup.py sdist`.


References
----------

Many of these terms derive their semantics from the following documentation:

- :mod:`distutils` reference,
  http://docs.python.org/distutils

- :mod:`pkg_resources` reference,
  http://peak.telecommunity.com/DevCenter/PkgResources

- :mod:`setuptools` reference,
  http://peak.telecommunity.com/DevCenter/setuptools
