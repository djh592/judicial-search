from elasticsearch import Elasticsearch
from backend.config import ELASTICSEARCH_HOSTS, INDEX_NAME

if __name__ == "__main__":
    es = Elasticsearch(hosts=ELASTICSEARCH_HOSTS)
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"Index '{INDEX_NAME}' deleted.")
    else:
        print(f"Index '{INDEX_NAME}' does not exist.")