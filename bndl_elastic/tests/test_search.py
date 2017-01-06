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

from functools import partial

from bndl_elastic.tests import ElasticTest


class SearchTest(ElasticTest):
    def setUp(self):
        super().setUp()
        with self.ctx.elastic_client() as client:
            for i in range(100):
                client.index(self.index, self.doc_type, {
                    'name': str(i),
                    'number': i,
                }, id=i)

            client.indices.refresh(self.index)

    def test_search(self):
        dset = self.ctx.elastic_search(self.index, self.doc_type)
        self.assertEqual(dset.count(), 100)
        hits = dset.collect()
        ids = [hit['_id'] for hit in hits]
        names = [hit['_source']['name'] for hit in hits]
        self.assertEqual(len(set(ids)), 100)
        self.assertSequenceEqual(ids, names)

        read = partial(self.ctx.elastic_search, self.index, self.doc_type)
        self.assertEqual(read(q='10').count(), 1)
        self.assertEqual(read(query={
            'query': { 'range': { 'number': { 'gte': 20, 'lt': 50 } } }
        }).count(), 30)
