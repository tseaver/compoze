##############################################################################
#
# Copyright (c) 2007-2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = '0.4.1'

import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
 
setup(name='compoze',
      version=__version__,
      description='Build package indexes',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: System :: Installation/Setup",
        ],
      keywords='web application server repoze',
      author="Agendaless Consulting",
      author_email="reopze-dev@lists.repoze.org",
      dependency_links=['http://dist.repoze.org'],
      url="http://www.repoze.org/compoze",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require = [
               ],
      install_requires=[
               'setuptools >= 0.6c7',
               'pkginfo',
               ],
      test_suite="compoze.tests",
      entry_points = {
        'console_scripts': [
         'compoze = compoze.compozer:main',
         ],
        'compoze_commands': [
         'fetch = compoze.fetcher:Fetcher',
         'index = compoze.indexer:Indexer',
         'show = compoze.informer:Informer',
         'pool = compoze.pooler:Pooler',
        ],
      },
)
