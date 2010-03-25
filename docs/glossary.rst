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

   project
        A named collection of releases of a given Python library or
        application, packaged using :mod:`distutils` or one of its
        derivatives.

   requirement
        A string specifying a :mod:`distutils: :term:`project` name.
        Can be optionally restricted to a given version or range of versions.

   source distribution
        An archive of the sources of a particular version of a
        :term:`project`, produced using :command:`python setup.py sdist`.
