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

from bndl_elastic.client import elastic_client, resource_from_conf
from elasticsearch.helpers import bulk


def _refresh_index(job, name, hosts=None):
    with elastic_client(job.ctx, hosts=hosts) as client:
        client.indices.refresh(name)


def execute_bulk(ctx, actions, hosts=None, **kwargs):
    '''
    Perform actions on Elastic in bulk.
    
    http://elasticsearch-py.readthedocs.io/en/master/helpers.html#elasticsearch.helpers.bulk
    provides more details on the expected format.
    
    :param ctx: bndl.compute.context.ComputeContext
        The ComputeContext to use for getting the Elastic client.
    :param actions: iterable
        An iterable of actions to execute.
    :param hosts: str or iterable (optional)
        Hosts which serve as contact points for the Elastic client.
    :param kwargs: 
        Keyword arguments passed on to the elasticsearch bulk function.
        Default values are read from ctx.conf['bndl_elastic.bulk_*'].
    '''
    kwargs.setdefault('chunk_size', ctx.conf['bndl_elastic.bulk_chunk_size'])
    kwargs.setdefault('max_chunk_bytes', ctx.conf['bndl_elastic.bulk_max_chunk_bytes'])
    kwargs.setdefault('request_timeout', ctx.conf['bndl_elastic.bulk_timeout'])
    with elastic_client(ctx, hosts=hosts) as client:
        stats = bulk(client, actions, stats_only=True, **kwargs)
        return (stats[0],)


def elastic_bulk(self, refresh_index=None, hosts=None, **kwargs):
    '''
    Perform actions on Elastic in bulk.
    
    http://elasticsearch-py.readthedocs.io/en/master/helpers.html#elasticsearch.helpers.bulk
    provides more details on the expected format.
    
    :param refresh_index: str (optional)
        Comma separated name of the indices to refresh or None to skip.
    :param hosts: str or iterable (optional)
        Hosts which serve as contact points for the Elastic client.
    :param kwargs: 
        Keyword arguments passed on to the elasticsearch bulk function.
        Default values are read from ctx.conf['bndl_elastic.bulk_*'].
    '''
    exec_bulk = self.map_partitions(partial(execute_bulk, self.ctx, hosts=hosts, **kwargs))
    if refresh_index:
        exec_bulk.cleanup = partial(_refresh_index, name=refresh_index, hosts=hosts)
    return exec_bulk


def _elastic_bulk(actions, index=None, doc_type=None, refresh=False, hosts=None, **kwargs):
    return actions.elastic_bulk(refresh_index=index if refresh else None, hosts=hosts, **kwargs)


def elastic_index(self, index=None, doc_type=None, refresh=False, hosts=None, **kwargs):
    '''
    Index documents into Elastic.
    
    :param index: str (optional)
        Name of the index.
    :param doc_type: str (optional)
        Name of the document type.
    :param refresh: bool (optional)
        Whether to refresh the index.
    :param hosts: str or iterable (optional)
        Hosts which serve as contact points for the Elastic client.
    :param kwargs:
        Keyword arguments passed on to the elasticsearch bulk function.
        Default values are read from ctx.conf['bndl_elastic.bulk_*'].
    '''
    index, doc_type = resource_from_conf(self.ctx.conf, index, doc_type)
    return _elastic_bulk(self.map(lambda doc: {
        '_op_type': 'index',
        '_index': index,
        '_type': doc_type,
        '_source': doc,
    }), index, doc_type, refresh, hosts, **kwargs)


def elastic_create(self, index=None, doc_type=None, refresh=False, hosts=None, **kwargs):
    '''
    Create documents in Elastic from a dataset of key (document id), value
    (document) pairs. Documents are only indexed if the document id doesn't
    exist yet.
    
    :param index: str (optional)
        The index name.
    :param doc_type: str (optional)
        The document type name.
    :param refresh: bool (optional)
        Whether to refresh the index afterwards.
    :param hosts: str or iterable (optional)
        Hosts which serve as contact points for the Elastic client.
    :param kwargs:
        Keyword arguments passed on to the elasticsearch bulk function.
        Default values are read from ctx.conf['bndl_elastic.bulk_*'].
    '''
    index, doc_type = resource_from_conf(self.ctx.conf, index, doc_type)
    return _elastic_bulk(self.starmap(lambda doc_id, doc: {
        '_op_type': 'create',
        '_index': index,
        '_type': doc_type,
        '_id': doc_id,
        '_source': doc,
    }), index, doc_type, refresh, hosts, **kwargs)


def elastic_update(self, index=None, doc_type=None, refresh=False, hosts=None, **kwargs):
    '''
    Update documents in Elastic search from a dataset of key (document id),
    value ((partial) document) pairs.
    
    :param index: str (optional)
        The index name.
    :param doc_type: str (optional)
        The document type name.
    :param refresh: bool (optional)
        Whether to refresh the index afterwards.
    :param hosts: str or iterable (optional)
        Hosts which serve as contact points for the Elastic client.
    :param kwargs:
        Keyword arguments passed on to the elasticsearch bulk function.
        Default values are read from ctx.conf['bndl_elastic.bulk_*'].
    '''
    index, doc_type = resource_from_conf(self.ctx.conf, index, doc_type)
    return _elastic_bulk(self.starmap(lambda doc_id, doc: {
        '_op_type': 'update',
        '_index': index,
        '_type': doc_type,
        '_id': doc_id,
        'doc': doc,
    }), index, doc_type, refresh, hosts, **kwargs)


def elastic_upsert(self, index=None, doc_type=None, refresh=False, hosts=None, **kwargs):
    '''
    Upsert (update or create) documents in Elastic search from a dataset of key
    (document id), value ((partial) document) pairs.
    
    :param index: str (optional)
        The index name.
    :param doc_type: str (optional)
        The document type name.
    :param refresh: bool (optional)
        Whether to refresh the index afterwards.
    :param hosts: str or iterable (optional)
        Hosts which serve as contact points for the Elastic client.
    :param kwargs:
        Keyword arguments passed on to the elasticsearch bulk function.
        Default values are read from ctx.conf['bndl_elastic.bulk_*'].
    '''
    index, doc_type = resource_from_conf(self.ctx.conf, index, doc_type)
    return _elastic_bulk(self.starmap(lambda doc_id, doc: {
        '_op_type': 'update',
        '_index': index,
        '_type': doc_type,
        '_id': doc_id,
        'doc': doc,
        'doc_as_upsert': True
    }), index, doc_type, refresh, hosts, **kwargs)


def elastic_delete(self, index=None, doc_type=None, refresh=False, hosts=None, **kwargs):
    '''
    Delete documents from Elastic given their ids as dataset.
    
    :param index: str (optional)
        The index to delete the documents from.
    :param doc_type: str (optional)
        The document type to delete the documents from.
    :param refresh: bool (optional)
        Whether to refresh the index afterwards.
    :param hosts: str or iterable (optional)
        Hosts which serve as contact points for the Elastic client.
    :param kwargs:
        Keyword arguments passed on to the elasticsearch bulk function.
        Default values are read from ctx.conf['bndl_elastic.bulk_*'].
    '''
    index, doc_type = resource_from_conf(self.ctx.conf, index, doc_type)
    return _elastic_bulk(self.map(lambda doc_id: {
        '_op_type': 'delete',
        '_index': index,
        '_type': doc_type,
        '_id': doc_id,
    }), index, doc_type, refresh, hosts, **kwargs)
