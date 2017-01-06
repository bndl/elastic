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

from bndl.rmi import InvocationException
from bndl_elastic.tests import ElasticTest


class IndexTest(ElasticTest):
    def test_index(self):
        # create
        inserts = self.ctx.range(100).with_value(lambda i: {'name': str(i)})
        saved = inserts.elastic_create(refresh=True).sum()
        self.refresh()
        self.assertEqual(saved, 100)
        scan = self.ctx.elastic_search()
        self.assertEqual(scan.count(), 100)

        # update
        updates = self.ctx.range(100).with_value(lambda i: {'number': i})
        updated = updates.elastic_update(refresh=True).sum()
        self.refresh()
        self.assertEqual(updated, 100)
        self.assertEqual(scan.count(), 100)
        hits = scan.collect()
        self.assertEqual(list(range(100)), sorted(int(hit['_id']) for hit in hits))
        self.assertEqual(list(range(100)), sorted(int(hit['_source']['name']) for hit in hits))
        self.assertEqual(list(range(100)), sorted(hit['_source']['number'] for hit in hits))

        # upsert
        upserts = self.ctx.range(200).with_value(lambda i: {'text': str(i)})
        upserted = upserts.elastic_upsert(refresh=True).sum()
        self.refresh()
        self.assertEqual(upserted, 200)
        self.assertEqual(scan.pluck('_source').filter(lambda hit: 'name' in hit).count(), 100)
        self.assertEqual(scan.pluck('_source').filter(lambda hit: 'number' in hit).count(), 100)
        self.assertEqual(scan.pluck('_source').filter(lambda hit: 'text' in hit).count(), 200)
        self.assertEqual(scan.pluck('_id').map(int).sort().collect(), list(range(200)))

        # create again
        creates = self.ctx.range(200, 300).with_value(lambda i: {'text': str(i)})
        created = creates.elastic_create(refresh=True).sum()
        self.refresh()
        self.assertEqual(created, 100)
        self.assertEqual(scan.pluck('_source').filter(lambda hit: 'name' in hit).count(), 100)
        self.assertEqual(scan.pluck('_source').filter(lambda hit: 'number' in hit).count(), 100)
        self.assertEqual(scan.pluck('_source').filter(lambda hit: 'text' in hit).count(), 300)
        self.assertEqual(scan.pluck('_id').map(int).sort().collect(), list(range(300)))

        # create failure
        with self.assertRaises(InvocationException):
            self.ctx.range(300).with_value({'text':'x'}).elastic_create().execute()

        # delete
        deleted = self.ctx.range(100, 200).elastic_delete(refresh=True).sum()
        self.refresh()
        self.assertEqual(deleted, 100)
        self.assertEqual(scan.pluck('_id').map(int).sort().collect(),
                         list(range(100)) + list(range(200, 300)))
        scan.pluck('_id').elastic_delete(refresh=True).execute()
        self.assertEqual(scan.count(), 0)
