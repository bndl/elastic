import time

from bndl.compute.tests import DatasetTest
from elasticsearch.client import Elasticsearch


class ElasticTest(DatasetTest):
    index = 'bndl_elastic_test'
    doc_type = 'test_doctype'

    def setUp(self):
        super().setUp()
        self.ctx.conf['bndl_elastic.index'] = self.index
        self.ctx.conf['bndl_elastic.doc_type'] = self.doc_type
        self.ctx.conf['bndl_elastic.hosts'] = '127.0.0.1'

        with self.ctx.elastic_client() as client:
            client.indices.delete(self.index, ignore=404)
            client.indices.create(self.index, body=dict(settings=dict(index=dict(number_of_replicas=0))))
            client.indices.refresh(self.index)

    def tearDown(self):
        super().tearDown()
#         with self.ctx.elastic_client() as client:
#             client.indices.delete(self.index)

    def refresh(self):
        with self.ctx.elastic_client() as client:
            client.indices.refresh()
        time.sleep(1)
