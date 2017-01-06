# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        for _ in range(3):
            with self.ctx.elastic_client() as client:
                client.indices.refresh()
            time.sleep(1)
