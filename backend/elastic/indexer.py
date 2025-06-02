import os
import json
import re
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm

# 配置
ELASTICSEARCH_HOSTS = ["http://localhost:9200"]
INDEX_NAME = "legal_cases"
CANDIDATES_DIR = "LeCaRD/data/candidates"
DOCUMENTS_DIR = "corpus/documents"
COMMON_CHARGE_JSON = "corpus/common_charge.json"
CONTROVERSIAL_CHARGE_JSON = "corpus/controversial_charge.json"


def build_ajid_label_map():
    label_map = {}
    with open(COMMON_CHARGE_JSON, "r", encoding="utf-8") as f:
        common = json.load(f)
    for charge, paths in common.items():
        for path in paths:
            abs_path = os.path.join(DOCUMENTS_DIR, path)
            try:
                with open(abs_path, "r", encoding="utf-8") as fdoc:
                    doc = json.load(fdoc)
                ajId = doc.get("ajId") or doc.get("ajid")
                if ajId:
                    label_map.setdefault(ajId, set()).add(charge)
            except Exception as e:
                print(f"Error reading {abs_path}: {e}")
    with open(CONTROVERSIAL_CHARGE_JSON, "r", encoding="utf-8") as f:
        controversial = json.load(f)
    for charge, paths in controversial.items():
        for path in paths:
            abs_path = os.path.join(DOCUMENTS_DIR, path)
            try:
                with open(abs_path, "r", encoding="utf-8") as fdoc:
                    doc = json.load(fdoc)
                ajId = doc.get("ajId") or doc.get("ajid")
                if ajId:
                    label_map.setdefault(ajId, set()).add(charge)
            except Exception as e:
                print(f"Error reading {abs_path}: {e}")
    return {k: list(v) for k, v in label_map.items()}


def extract_spry(text):
    # 只允许2-8位汉字/中点，且后面必须是分隔符或结尾
    pattern = r"(审判长|审判员|人民陪审员|书记员|代理审判员|代理书记员|助理审判员)[：:\s]*([\u4e00-\u9fa5·]{2,8})(?=[，。；：:、,.\s]|$)"
    results = []
    for role, name in re.findall(pattern, text):
        # 严格限制姓名长度和内容
        if 2 <= len(name) <= 8 and all(
            c not in name
            for c in "的有归案参加指定材料证言供述意见处罚家中初犯行为事实提出无视承担犯罪血液损伤陈述"
        ):
            results.append(f"{role}:{name}")
    return list(set(results))


def extract_fymc(text):
    # 只匹配以地名/常见前缀开头，且前面是句首、标点、空格、换行，后面是分隔符或结尾
    prefix = (
        r"(?:中华人民共和国)?"
        r"(?:最高|高级|中级|基层|铁路|海事|军事|知识产权|"
        r"[\u4e00-\u9fa5]{2,10}(?:省|市|自治区|县|区|旗|自治州|直辖市|特别行政区))"
    )
    pattern = (
        r"(?<![^\s，。；：:、,\n])"  # 前面不能是汉字或字母数字
        + prefix
        + r"[\u4e00-\u9fa5]{0,20}?(?:人民法院|法院|人民法庭|法庭)"
        r"(?=[，。；：:、,.\s]|$)"
    )
    results = []
    for name in re.findall(pattern, text):
        name = name.strip("，。；：:、,. \n")
        # 排除明显无效内容
        if 6 <= len(name) <= 30 and not any(
            x in name for x in ["本院", "通过", "和", "或"]
        ):
            results.append(name)
    return list(set(results))


def extract_dsr(text):
    roles = [
        "被告人",
        "被害人",
        "原告",
        "被告",
        "上诉人",
        "被上诉人",
        "申请人",
        "被申请人",
        "证人",
        "被告单位",
        "被害单位",
        "受害人",
        "诉讼代理人",
        "辩护人",
    ]
    unit_suffix = r"(?:公司|单位|医院|学校|集团|厂|店|中心|协会|银行|分局|分公司|支行|分院|分所|分队|分部)"
    # 人名2-4位汉字/中点，且后面必须是分隔符或结尾
    person_pattern = (
        rf"({'|'.join(roles)})[:：\s]*([\u4e00-\u9fa5·]{{2,4}})(?=[，。；：:、,.\s]|$)"
    )
    # 单位名2-30位且以后缀结尾，且后面必须是分隔符或结尾
    unit_pattern = rf"({'|'.join(roles)})[:：\s]*([\u4e00-\u9fa5A-Za-z0-9（）()]{2,30}{unit_suffix})(?=[，。；：:、,.\s]|$)"
    # 排除词
    exclude_words = "的|有|归案|参加|指定|材料|证言|供述|意见|处罚|家中|初犯|行为|事实|辩护人|提出|无视|承担|犯罪|血液|损伤|陈述|处罚|证实|意见|家中|初犯|行为|事实|参加|指定|提出|无视|承担|犯罪|血液|损伤|陈述|处罚|供述|事实|材料|证实"

    results = []
    # 人名
    for role, name in re.findall(person_pattern, text):
        # 严格限制姓名长度和内容
        if 2 <= len(name) <= 4 and not re.search(rf"({exclude_words})", name):
            results.append(f"{role}:{name}")
    # 单位名
    for role, name in re.findall(unit_pattern, text):
        if 2 <= len(name) <= 30 and not re.search(rf"({exclude_words})", name):
            results.append(f"{role}:{name}")
    return list(set(results))


def create_index(es):
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    es.indices.create(
        index=INDEX_NAME,
        body={
            "settings": {
                "index": {
                    "similarity": {"custom_bm25": {"type": "BM25", "k1": 2.0, "b": 0.3}}
                }
            },
            "mappings": {
                "properties": {
                    "ajId": {"type": "keyword"},
                    "ajName": {
                        "type": "text",
                        "analyzer": "ik_smart",
                        "similarity": "custom_bm25",
                    },
                    "ajName_suggest": {"type": "completion"},  # 新增
                    "fymc": {"type": "text", "analyzer": "ik_smart"},
                    "fymc_suggest": {"type": "completion"},  # 新增
                    "spry": {"type": "text", "analyzer": "ik_smart"},
                    "spry_suggest": {"type": "completion"},  # 新增
                    "dsr": {"type": "text", "analyzer": "ik_smart"},
                    "dsr_suggest": {"type": "completion"},  # 新增
                    "ajjbqk": {
                        "type": "text",
                        "analyzer": "ik_smart",
                        "similarity": "custom_bm25",
                    },
                    "cpfxgc": {
                        "type": "text",
                        "analyzer": "ik_smart",
                        "similarity": "custom_bm25",
                    },
                    "pjjg": {
                        "type": "text",
                        "analyzer": "ik_smart",
                        "similarity": "custom_bm25",
                    },
                    "qw": {
                        "type": "text",
                        "analyzer": "ik_smart",
                        "similarity": "custom_bm25",
                    },
                    "writId": {"type": "keyword"},
                    "writName": {"type": "text", "analyzer": "ik_smart"},
                    "labels": {"type": "keyword"},
                }
            },
        },
    )


def generate_docs(label_map):
    for root, dirs, files in os.walk(CANDIDATES_DIR):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                doc = json.load(f)
            ajId = doc.get("ajId") or doc.get("ajid")
            if not ajId:
                print(f"Warning: {fname} missing ajId")
                continue
            labels = label_map.get(ajId, [])
            text = " ".join(
                [
                    doc.get("qw", ""),
                    doc.get("ajjbqk", ""),
                    doc.get("cpfxgc", ""),
                    doc.get("pjjg", ""),
                    doc.get("ajName", ""),
                    doc.get("writName", ""),
                ]
            )
            fymc = extract_fymc(text)
            spry = extract_spry(text)
            dsr = extract_dsr(text)
            yield {
                "_index": INDEX_NAME,
                "_id": ajId,
                "_source": {
                    "ajId": ajId,
                    "ajName": doc.get("ajName"),
                    "ajName_suggest": doc.get("ajName"),  # 新增
                    "ajjbqk": doc.get("ajjbqk"),
                    "cpfxgc": doc.get("cpfxgc"),
                    "pjjg": doc.get("pjjg"),
                    "qw": doc.get("qw"),
                    "writId": doc.get("writId"),
                    "writName": doc.get("writName"),
                    "labels": labels,
                    "fymc": fymc,
                    "fymc_suggest": fymc,  # 新增
                    "spry": spry,
                    "spry_suggest": spry,  # 新增
                    "dsr": dsr,
                    "dsr_suggest": dsr,  # 新增
                },
            }


if __name__ == "__main__":
    es = Elasticsearch(
        hosts=ELASTICSEARCH_HOSTS,
        timeout=60,  # 请求超时时间（秒）
        max_retries=3,  # 可选：重试次数
        retry_on_timeout=True,  # 可选：超时重试
    )
    label_map = build_ajid_label_map()
    create_index(es)
    files = []
    for root, dirs, fs in os.walk(CANDIDATES_DIR):
        for f in fs:
            if f.endswith(".json"):
                files.append(os.path.join(root, f))
    print(f"Found {len(files)} candidate documents. Start importing...")
    for ok, _ in tqdm(
        helpers.streaming_bulk(es, generate_docs(label_map)),
        total=len(files),
        desc="Importing",
    ):
        pass
    print("LeCaRD候选文档导入完成！")
