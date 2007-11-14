repoze.project README

  Overview

    This package provides a convenient mechanism for creating standalone
    instances of repoze applications.

  Usage

    Installing 'repoze.project' via 'easy_install' (it doesn't
    depend on any other 'repoze' packages), creates a script,
    'repozeproject', in the scripts directory of your Python.

    Run this script to create a separate environment, with the
    given 'repoze' application (and its dependencies) installed.
    For instance, to install 'repoze.plone' into a new '/tmp/plone'
    directory:

      $ bin/easy_install -i http://dist.repoze.org/simple repoze.project
      $ bin/repozeproject --path=/tmp/plone repoze.plone

    You can also ask to have extra eggs installed.

      $ bin/repozeproject --path=/tmp/plone \
        repoze.plone some.package anotherpackage

    By default, those eggs will be installed from the 'repoze'
    package index;  if you want to use the Cheeseshop, prefix the
    package name with 'pypi:', e.g.::

      $ bin/repozeproject --path=/tmp/plone repoze.plone pypi:cheesy

    If left unspecified, the target path will be the current directory.
    E.g.::

      $ mkdir /tmp/plone2
      $ cd /tmp/plone2
      $ /path/to/environment/bin/repozeproject repoze.plone

  Theory of Operation

    'repozeproject' works as follows:

     - It uses the 'virtualenv' package to create a new "virtual"
       Python environment in the target directory, with an empty
       'site-packages' directory.

     - It then installs the eggs specified by the remaining arguments
       into the 'site-packages' of that environment, linking them into
       the 'easyinstall.pth' file there, so that they are on the
       'PYTHONPATH'.

     - Finally, it introspects the egg corresponding to the
       first-named argument ('repoze.plone' in the example above)
       for an entry point of type 'repoze.initproject'.  If found,
       it runs that entry point, which can then create additional
       files or directories in the environment.

       In the case of a Zope2-based project, this might include:

       o Creating empty 'etc', 'var', and 'log' directories.

       o Generating config files ('etc/zope.conf', 'etc/site.zcml',
         'etc/paste.ini') using skeleton templates from the egg.

       o Creating additional convenience scripts not alreay generated
         during package installation.

       This last step is enabled by default;  to disable it, pass
       '--no-initialize-environment' on the command line to
       'repozeproject'.
