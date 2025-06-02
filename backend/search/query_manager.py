import time
from collections import OrderedDict
from backend.elastic.client import get_es_client
from backend.config import INDEX_NAME
from backend.search.query import QueryParams, Query

# 最大缓存查询数量
MAX_QUERIES = 1000

# 查询过期时间（秒）
QUERY_TTL = 3600  # 1小时


class QueryManager:
    """
    查询管理器，负责管理所有检索请求及其结果缓存
    """

    def __init__(self):
        self.queries = OrderedDict()
        self.results_cache = {}  # (query_id, page, page_size) -> 结果

    def create_query(self, params: QueryParams):
        """创建新查询并执行"""
        if len(self.queries) >= MAX_QUERIES:
            self._evict_oldest()
        query = Query(params)
        es_response = self._execute_es_query(params)
        query.total_results = es_response["hits"]["total"]["value"]
        query.results = [
            (hit["_id"], hit["_score"]) for hit in es_response["hits"]["hits"]
        ]
        query.es_query = es_response["_query"]
        self.queries[query.id] = query
        return query.id

    def get_results(self, query_id, page=1, page_size=10):
        """获取查询结果（带缓存）"""
        if query_id not in self.queries:
            return None
        query = self.queries[query_id]
        query.last_accessed = time.time()
        cache_key = (query_id, page, page_size)
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
        start = (page - 1) * page_size
        end = start + page_size
        page_ids_scores = query.results[start:end]
        page_ids = [doc_id for doc_id, _ in page_ids_scores]
        docs = self._get_docs_by_ids(page_ids)
        # 构建 id->score 映射
        id2score = {doc_id: score for doc_id, score in page_ids_scores}
        processed_docs = self._process_results(docs, id2score)
        response = {
            "page": page,
            "total_pages": (query.total_results + page_size - 1) // page_size,
            "results": processed_docs,
        }
        self.results_cache[cache_key] = response
        return response

    def get_query(self, query_id):
        """获取查询元数据"""
        if query_id in self.queries:
            query = self.queries[query_id]
            query.last_accessed = time.time()
            return {
                "id": query.id,
                "params": vars(query.params),
                "created_at": query.created_at,
                "last_accessed": query.last_accessed,
                "total_results": query.total_results,
                "version": query.version,
            }
        return None

    def update_query(self, query_id, new_params: QueryParams):
        """更新查询参数并重新检索"""
        if query_id not in self.queries:
            return None
        query = self.queries[query_id]
        new_query = Query(new_params)
        new_query.version = query.version + 1
        es_response = self._execute_es_query(new_params)
        new_query.total_results = es_response["hits"]["total"]["value"]
        new_query.results = [
            (hit["_id"], hit["_score"]) for hit in es_response["hits"]["hits"]
        ]
        new_query.es_query = es_response["_query"]
        self.queries[query_id] = new_query
        self._clear_query_cache(query_id)
        return new_query.id

    def _execute_es_query(self, params: QueryParams):
        """构建并执行ES查询"""
        es = get_es_client()
        body = params.to_es_query()
        body["size"] = 1000

        # # 写入日志
        # import json

        # with open("es_query.log", "a", encoding="utf-8") as f:
        #     f.write(json.dumps(body, ensure_ascii=False))
        #     f.write("\n")

        response = es.search(index=INDEX_NAME, body=body)
        response["_query"] = body
        return response

    def _get_docs_by_ids(self, doc_ids):
        """从ES批量获取文档详情"""
        if not doc_ids:
            return []
        es = get_es_client()
        response = es.mget(index=INDEX_NAME, body={"ids": doc_ids})
        return [
            {"id": doc["_id"], **doc["_source"]}
            for doc in response["docs"]
            if doc.get("found")
        ]

    def _process_results(self, docs, id2score=None):
        wanted_fields = [
            "ajId",
            "ajName",
            "ajjbqk",
            "cpfxgc",
            "pjjg",
            "qw",
            "writId",
            "writName",
            "labels",
            "fymc",  # 新增：法院名称
            "spry",  # 新增：审判人员
            "dsr",  # 新增：当事人
        ]
        results = []
        for doc in docs:
            item = {k: doc.get(k, "") for k in wanted_fields}
            if id2score is not None:
                item["score"] = id2score.get(doc["id"], None)
            results.append(item)
        return results

    def _clear_query_cache(self, query_id):
        """清除查询相关缓存"""
        keys_to_delete = [key for key in self.results_cache if key[0] == query_id]
        for key in keys_to_delete:
            del self.results_cache[key]

    def _evict_oldest(self):
        """淘汰最久未使用的查询"""
        if not self.queries:
            return
        oldest_id = min(self.queries.values(), key=lambda q: q.last_accessed).id
        self._clear_query_cache(oldest_id)
        del self.queries[oldest_id]

    def clean_expired(self):
        """清理过期查询"""
        current_time = time.time()
        expired_ids = [
            qid
            for qid, query in self.queries.items()
            if current_time - query.last_accessed > QUERY_TTL
        ]
        for qid in expired_ids:
            self._clear_query_cache(qid)
            del self.queries[qid]

    def get_document_by_ajid(self, ajid):
        es = get_es_client()
        resp = es.search(
            index=INDEX_NAME, body={"query": {"term": {"ajId": ajid}}, "size": 1}
        )
        hits = resp.get("hits", {}).get("hits", [])
        if not hits:
            return None
        doc = hits[0]["_source"]
        doc["id"] = hits[0]["_id"]
        return doc

    def get_all_labels(self):
        es = get_es_client()
        resp = es.search(
            index=INDEX_NAME,
            body={
                "size": 0,
                "aggs": {"all_labels": {"terms": {"field": "labels", "size": 10000}}},
            },
        )
        buckets = resp.get("aggregations", {}).get("all_labels", {}).get("buckets", [])
        return [b["key"] for b in buckets]

    def suggest(self, field, prefix, size=10):
        es = get_es_client()
        suggest_body = {
            "suggest": {
                "my-suggest": {
                    "prefix": prefix,
                    "completion": {"field": f"{field}_suggest", "size": size},
                }
            }
        }
        resp = es.search(index=INDEX_NAME, body=suggest_body)
        options = resp.get("suggest", {}).get("my-suggest", [])[0].get("options", [])
        return [opt["text"] for opt in options]


# 全局查询管理器实例
query_manager = QueryManager()


def get_query_manager():
    """获取全局查询管理器实例"""
    return query_manager
