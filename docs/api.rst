API Documentation for :mod:`compoze`
====================================

.. _compozer_module:

:mod:`compoze.compozer`
-----------------------

.. automodule:: compoze.compozer

  .. autoclass:: Compozer

    .. automethod:: parse_arguments

    .. automethod:: __call__

See :ref:`compoze_options` for command line options which are global, i.e.
not specific to any of the subcommands.


.. _fetcher_module:

:mod:`compoze.fetcher`
-----------------------

.. automodule:: compoze.fetcher

  .. autoclass:: Fetcher

    .. automethod:: download_distributions

    .. automethod:: __call__

See :ref:`compoze_fetch_options` for command line options for this
subcommand.

.. _index_module:

:mod:`compoze.index`
-----------------------

.. automodule:: compoze.index

  .. autoclass:: CompozePackageIndex


.. _indexer_module:

:mod:`compoze.indexer`
-----------------------

.. automodule:: compoze.indexer

  .. autoclass:: Indexer

    .. automethod:: make_index

    .. automethod:: __call__

See :ref:`compoze_index_options` for command line options for this
subcommand.


.. _informer_module:

:mod:`compoze.informer`
-----------------------

.. automodule:: compoze.informer

  .. autoclass:: Informer

    .. automethod:: show_distributions

    .. automethod:: __call__

See :ref:`compoze_show_options` for command line options for this
subcommand.


.. _pooler_module:

:mod:`compoze.pooler`
-----------------------

.. automodule:: compoze.pooler

  .. autoclass:: Pooler

    .. automethod:: move_to_pool

    .. automethod:: __call__

See :ref:`compoze_pool_options` for command line options for this
subcommand.
