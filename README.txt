compoze README

  Overview

    This package provides a script for creating setuptools-compatible
    package indexes using packages downloaded from other indexes.

  Installation

    Installing 'compoze' via 'easy_install' (it doesn't
    depend on any other 'repoze' packages), creates a script,
    'compoze', in the scripts directory of your Python::

      $ bin/easy_install -i http://dist.repoze.org/simple compoze

  Fetching Distributions

    The 'compoze fetch' command is useful for retrieving distutils
    distributions matching a set requirment specifications, e.g::

      $ bin/compoze fetch --path=/tmp/index \
                    --index-url=http://dist.repoze.org/simple \
                    repoze.grok "repoze.project>=2.1"

    If you do not supply an index URL, 'compoze' uses the Python
    Package Index (the "cheeseshop") by default::

      $ bin/compoze fetch --path=/tmp/index someproject

    You can supply more than one "source" index::

      $ bin/compoze fetch --path=/tmp/index \
                    --index-url=http://example.com/index \
                    --index-url=http://another.example.com/index \
                    someproject another_project

    If you do not supply a path, 'compoze fetch' uses the current
    directory.

  Example: Recreating the Package Set Already Installed

    You can also ask to have 'compoze' fetch distributions for the eggs
    already installed in site-packges::

      $ bin/compoze fetch --path=/tmp/plone --fetch-site-packages

  Building a Package Index

    'compoze index' will make a PyPI-like package index in the
    target directory::

      $ bin/compoze index --path=/tmp/downloads

  Example:  Creating a Package Index for the Versions Already Installed

    One common use case is to capture the "known good set" represented
    by a given Python environment.  In this case, you want both to download
    the distributions corresponding to the projects installed in site-packages,
    and also make a package index from them::

      $ bin/compoze fetch --fetch-site-packages --path kgs \
                    index --path kgs
