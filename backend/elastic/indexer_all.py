import os
import json
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm
from backend.config import (
    ELASTICSEARCH_HOSTS,
    INDEX_NAME,
    DOCUMENT_PATH_JSON,
    COMMON_CHARGE_JSON,
    CONTROVERSIAL_CHARGE_JSON,
    DOCUMENTS_DIR,
)


def load_document_paths():
    """
    返回每个文书的路径、案件类型、retrial分组id（如有）、同组所有ajId（如有）
    """
    with open(DOCUMENT_PATH_JSON, "r", encoding="utf-8") as f:
        doc_paths = json.load(f)
    all_items = []
    # single
    for path in doc_paths.get("single", []):
        all_items.append(
            {
                "path": path,
                "case_type": "single",
                "retrial_group_id": None,
                "group_paths": [path],
            }
        )
    # retrial
    for retrial_group in doc_paths.get("retrial", []):
        group_id = retrial_group[0].split("/")[0]  # 用文件夹名做group_id
        for path in retrial_group:
            all_items.append(
                {
                    "path": path,
                    "case_type": "retrial",
                    "retrial_group_id": group_id,
                    "group_paths": retrial_group,
                }
            )
    return all_items


def load_charge_labels():
    """
    返回 path -> {"labels": [...], "case_charge_type": ...} 的标签和类型映射
    """
    with open(COMMON_CHARGE_JSON, "r", encoding="utf-8") as f:
        common = json.load(f)
    with open(CONTROVERSIAL_CHARGE_JSON, "r", encoding="utf-8") as f:
        controversial = json.load(f)
    label_map = {}
    for charge, paths in common.items():
        for path in paths:
            if path not in label_map:
                label_map[path] = {"labels": [], "case_charge_type": "common"}
            label_map[path]["labels"].append(charge)
    for charge, paths in controversial.items():
        for path in paths:
            if path not in label_map:
                label_map[path] = {"labels": [], "case_charge_type": "controversial"}
            label_map[path]["labels"].append(charge)
    return label_map


def get_ajid_from_path(path):
    """
    从文书路径读取ajid
    """
    abs_path = os.path.join(DOCUMENTS_DIR, path)
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        return doc.get("ajId")
    except Exception:
        return None


def build_group_ajid_map(doc_items):
    """
    构建 retrial_group_id -> [ajid, ...] 的映射
    """
    group_map = {}
    for item in doc_items:
        if item["retrial_group_id"]:
            ajid = get_ajid_from_path(item["path"])
            if ajid:
                group_map.setdefault(item["retrial_group_id"], []).append(ajid)
    return group_map


def create_index(es):
    """
    创建ES索引，包含所有需要的字段
    """
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(
            index=INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "ajId": {"type": "keyword"},  # 案件ID
                        "ajName": {
                            "type": "text",
                            "analyzer": "ik_smart",
                        },  # 案件名称
                        "ajjbqk": {
                            "type": "text",
                            "analyzer": "ik_smart",
                        },  # 案件基本情况
                        "cpfxgc": {
                            "type": "text",
                            "analyzer": "ik_smart",
                        },  # 裁判分析过程
                        "pjjg": {"type": "text", "analyzer": "ik_smart"},  # 判决结果
                        "qw": {"type": "text", "analyzer": "ik_smart"},  # 全文
                        "writId": {"type": "keyword"},  # 文书ID
                        "writName": {
                            "type": "text",
                            "analyzer": "ik_smart",
                        },  # 文书名称
                        "labels": {
                            "type": "keyword"
                        },  # 标签列表: ["盗窃罪", "故意伤害罪"]
                        "case_charge_type": {
                            "type": "keyword"
                        },  # 案件类型: "common" 或 "controversial"
                        "case_type": {
                            "type": "keyword"
                        },  # 案件类型: "single" 或 "retrial"
                        "retrial_group_id": {"type": "keyword"},  # retrial分组ID
                        "group_ajids": {"type": "keyword"},  # 同组所有案件ID列表
                    }
                },
            },
        )


def generate_docs(doc_items, label_map, group_ajid_map):
    for item in doc_items:
        rel_path = item["path"]
        abs_path = os.path.join(DOCUMENTS_DIR, rel_path)
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                doc = json.load(f)
            try:
                ajId = doc.get("ajId")
            except KeyError:
                ajId = get_ajid_from_path(rel_path)
                print(f"Warning: Missing ajId in {rel_path}, using fallback method")
            group_ajids = []
            if item["retrial_group_id"]:
                group_ajids = group_ajid_map.get(item["retrial_group_id"], [])
            label_info = label_map.get(
                rel_path, {"labels": [], "case_charge_type": None}
            )
            yield {
                "_index": INDEX_NAME,
                "_id": ajId,
                "_source": {
                    "ajId": ajId,
                    "ajName": doc.get("ajName"),
                    "ajjbqk": doc.get("ajjbqk"),
                    "cpfxgc": doc.get("cpfxgc"),
                    "pjjg": doc.get("pjjg"),
                    "qw": doc.get("qw"),
                    "writId": doc.get("writId"),
                    "writName": doc.get("writName"),
                    "labels": label_info["labels"],
                    "case_charge_type": label_info["case_charge_type"],
                    "case_type": item["case_type"],
                    "retrial_group_id": item["retrial_group_id"],
                    "group_ajids": group_ajids if group_ajids else [ajId],
                },
            }
        except Exception as e:
            print(f"Error processing {rel_path}: {e}")


if __name__ == "__main__":
    es = Elasticsearch(hosts=ELASTICSEARCH_HOSTS)
    doc_items = load_document_paths()
    label_map = load_charge_labels()
    group_ajid_map = build_group_ajid_map(doc_items)
    create_index(es)
    print(f"Found {len(doc_items)} documents. Start importing...")
    for ok, _ in tqdm(
        helpers.streaming_bulk(es, generate_docs(doc_items, label_map, group_ajid_map)),
        total=len(doc_items),
        desc="Importing",
    ):
        pass
    print("数据导入完成！")
