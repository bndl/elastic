============
BNDL Elastic
============

BNDL Elastic exposes loading from and saving to functionality of the
`python driver <https://github.com/elastic/elasticsearch-py>`_ for
`Elasticsearch <https://www.elastic.co/>`_.

Master branch build status: |travis| |codecov|

.. |travis| image:: https://travis-ci.org/bndl/elastic.svg?branch=master
   :target: https://travis-ci.org/bndl/elastic

.. |codecov| image:: https://codecov.io/gh/bndl/elastic/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/bndl/elastic/branch/master

---------------------------------------------------------------------------------------------------

BNDL Elastic can be installed through pip::

    pip install bndl-elastic

The main features of BNDL Elastic are loading from, saving to and deleting from Elasticsearch::

    dataset = ctx.elastic_search(index, doc_type, **kwargs)
    dataset.elastic_index(index, doc_type)
    dataset.elastic_create(index, doc_type)
    dataset.elastic_update(index, doc_type)
    dataset.elastic_upsert(index, doc_type)
    dataset.elastic_delete(index, doc_type)

``elastic_{index, create, update, upsert, delete}`` have the (expected) semantics as the
corresponding ``_op_type`` in the bulk communication with Elasticsearch.
