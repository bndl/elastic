from bndl.compute.context import ComputeContext
from bndl.compute.dataset import Dataset
from bndl.util.conf import CSV, String
from bndl.util.funcs import as_method
from bndl_elastic.bulk import elastic_bulk, elastic_create, \
    elastic_index, elastic_update, elastic_delete, elastic_upsert
from bndl_elastic.client import elastic_client
from bndl_elastic.dataset import ElasticSearchDataset


# Configuration
hosts = CSV()
index = String()
doc_type = String()


# Bndl API extensions
ComputeContext.elastic_client = elastic_client
ComputeContext.elastic_search = as_method(ElasticSearchDataset)

Dataset.elastic_bulk = elastic_bulk
Dataset.elastic_index = elastic_index
Dataset.elastic_create = elastic_create
Dataset.elastic_update = elastic_update
Dataset.elastic_upsert = elastic_upsert
Dataset.elastic_delete = elastic_delete
