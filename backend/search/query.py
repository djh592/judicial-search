import time
import uuid
from typing import Optional, List


class QueryParams:
    """
    检索参数对象，封装前端传来的所有检索条件
    """

    def __init__(
        self,
        query: str = "",
        qw: Optional[str] = None,  # 全文检索
        ajmc: Optional[str] = None,  # 案件名称
        ay: Optional[List[str]] = None,  # 案由（支持多个）
        fymc: Optional[str] = None,  # 法院名称
        spry: Optional[str] = None,  # 审判人员
        dsr: Optional[str] = None,  # 当事人
    ):
        self.query = query
        self.qw = qw
        self.ajmc = ajmc
        self.ay = ay or []
        self.fymc = fymc
        self.spry = spry
        self.dsr = dsr

    @classmethod
    def from_dict(cls, d):
        ay = d.get("ay")
        # 支持传入字符串或列表
        if isinstance(ay, str):
            ay = [ay]
        elif ay is None:
            ay = []
        return cls(
            query=d.get("query", ""),
            qw=d.get("qw"),
            ajmc=d.get("ajmc"),
            ay=ay,
            fymc=d.get("fymc"),
            spry=d.get("spry"),
            dsr=d.get("dsr"),
        )

    def to_es_query(self):
        """
        转换为ES检索DSL
        """
        must = []
        should = []
        filters = []

        # 案由 should 匹配加分，不做严格过滤
        if self.ay:
            should.append({"terms": {"labels": self.ay, "boost": 5}})

        # 主查询
        if self.query:
            must.append(
                {
                    "multi_match": {
                        "query": self.query,
                        "fields": [
                            "ajjbqk^3",
                            "cpfxgc^2",
                            "pjjg",
                            "qw",
                            "ajName^5",
                            "writName^5",
                        ],
                        "type": "best_fields",
                    },
                }
            )
        if self.qw:
            must.append(
                {
                    "multi_match": {
                        "query": self.qw,
                        "fields": [
                            "ajjbqk",
                            "cpfxgc",
                            "pjjg",
                            "qw",
                        ],
                    },
                }
            )
        if self.ajmc:
            should.append({"match": {"ajName": self.ajmc}})

        # 法院名称
        if self.fymc:
            should.append({"match": {"fymc": {"query": self.fymc, "boost": 6}}})

        # 审判人员
        if self.spry:
            should.append({"match": {"spry": {"query": self.spry, "boost": 5}}})

        # 当事人
        if self.dsr:
            should.append({"match": {"dsr": {"query": self.dsr, "boost": 5}}})

        query_body = {
            "query": {
                "bool": {
                    "must": must if must else [{"match_all": {}}],
                },
            }
        }
        if filters:
            query_body["query"]["bool"]["filter"] = filters
        if should:
            query_body["query"]["bool"]["should"] = should

        return query_body


class Query:
    """
    检索请求对象，封装一次检索的参数和结果
    """

    def __init__(self, params: QueryParams):
        self.id = f"q_{uuid.uuid4().hex[:10]}"
        self.params = params  # QueryParams对象
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.total_results = 0
        self.results = []  # (doc_id, score)
        self.es_query = None  # ES查询DSL
        self.version = 1
