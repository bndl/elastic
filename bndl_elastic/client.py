from collections import Sequence
from functools import lru_cache
from urllib.parse import urlparse
import contextlib
import queue

from bndl.net.connection import gethostbyname
from bndl.util.pool import ObjectPool
from elasticsearch.client import Elasticsearch
from elasticsearch.connection_pool import ConnectionPool, RoundRobinSelector
import netifaces


def resource_from_conf(conf, index=None, doc_type=None):
    if index is None:
        index = conf.get('bndl_elastic.index')
    if doc_type is None:
        doc_type = conf.get('bndl_elastic.doc_type')
    return index, doc_type


@lru_cache()
def _get_hosts(ctx, *hosts):
    if not hosts:
        hosts = set()
        for worker in ctx.workers:
            hosts |= worker.ip_addresses()
    if not hosts:
        hosts = ctx.node.ip_addresses()
    if isinstance(hosts, str):
        hosts = [hosts]
    if isinstance(hosts, Sequence) and len(hosts) == 1 and isinstance(hosts[0], str):
        hosts = hosts[0].split(',')
    return tuple(sorted(hosts))




@lru_cache(1024)
def parse_hostname(url):
    if url.startswith('inet[/') and url.endswith(']'):
        url = url[6:-1]
    if '://' not in url:
        url = '//' + url
    return urlparse(url).hostname



class NodeLocalSelectorClass(RoundRobinSelector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_addresses = {
            addr['addr']
            for af in (netifaces.AF_INET, netifaces.AF_INET6)
            for iface in netifaces.interfaces()
            for addr in netifaces.ifaddresses(iface).get(af, ())
        }


    def select(self, connections):
        for connection in connections:
            addr = gethostbyname(parse_hostname(connection.host))
            if addr in self.local_addresses:
                return connection
        return super().select(connections)


class NodeLocalConnectionPool(ConnectionPool):
    def __init__(self, *args, **kwargs):
        assert 'selector_class' not in kwargs
        kwargs['selector_class'] = NodeLocalSelectorClass
        super().__init__(*args, **kwargs)



@contextlib.contextmanager
def elastic_client(ctx, hosts=None):
    # get hold of the dict of pools (keyed by hosts)
    pools = getattr(elastic_client, 'pools', None)
    if not pools:
        elastic_client.pools = pools = {}

    # determine contact points, either given or ip addresses of the workers
    hosts = _get_hosts(ctx, *(hosts or ctx.conf.get('bndl_elastic.hosts') or ()))

    # check if there is a cached client object
    pool = pools.get(hosts)
    # or create one if not
    if not pool:
        timeout = ctx.conf['bndl_elastic.timeout']
        max_retries = ctx.conf['bndl_elastic.max_retries']
        retry_on_timeout = ctx.conf['bndl_elastic.retry_on_timeout']
        def create():
            return Elasticsearch(
                hosts,
                timeout=timeout,
                max_retries=max_retries,
                retry_on_timeout=retry_on_timeout,
                connection_pool_class=NodeLocalConnectionPool
            )

        pools[hosts] = pool = ObjectPool(create, max_size=4)

    # take a session from the pool, yield it to the caller
    # and put the session back in the pool
    session = pool.get()

    try:
        yield session
    finally:
        try:
            pool.put(session)
        except queue.Full:
            session.shutdown()
