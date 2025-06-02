from elasticsearch import Elasticsearch
from backend.config import ELASTICSEARCH_HOSTS

_es_client = None

def get_es_client():
    """
    获取全局唯一的 Elasticsearch client 实例
    """
    global _es_client
    if _es_client is None:
        _es_client = Elasticsearch(hosts=ELASTICSEARCH_HOSTS)
    return _es_client