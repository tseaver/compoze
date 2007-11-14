compoze README

  Overview

    This package provides a script for creating setuptools-compatible
    package indexes using packages downloaded from other indexes.

  Installation

    Installing 'compoze' via 'easy_install' (it doesn't
    depend on any other 'repoze' packages), creates a script,
    'compoze', in the scripts directory of your Python::

      $ bin/easy_install -i http://dist.repoze.org/simple compoze

  Simple Usage

    Run this script, passing a series of distutils requirment
    specifications, e.g::

      $ bin/compoze --path=/tmp/index \
                    --index-url=http://dist.repoze.org/simple \
                    compoze

    If you do not supply an index URL, 'compoze' uses the Python
    Package Index (the "cheeseshop") by default::

      $ bin/compoze --path=/tmp/index someproject

  Using Multiple Source Indexes

    You can supply more than one "source" index::

      $ bin/compoze --path=/tmp/index \
                    --index-url=http://example.com/index \
                    --index-url=http://another.example.com/index \
                    someproject another_project

  Recreating the Package Set Already Installed

    You can also ask to have 'compoze' fetch distributions for the eggs
    already installed in site-packges::

      $ bin/compoze --path=/tmp/plone --fetch-site-packages

  Building the Index In Place

    If left unspecified, the target path will be the current directory.
    E.g.::

      $ mkdir /tmp/myindex
      $ cd /tmp/myindex
      $ /path/to/environment/bin/compoze --fetch-site-packages

  Splitting Downloads from Index Creation

    By default, 'compoze' first downloads the specified distribution(s),
    and then makes a new package index.  You can turn either of these steps
    off, e.g. to download distributions without making the index::

      $ bin/compoze --no-make-index --path=/tmp/downloads someproject

    or to make an index in an existing directory full of distributions::

      $ bin/compoze --no-download --path=/tmp/downloads
