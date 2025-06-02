import os

# 项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 数据路径配置
CORPUS_DIR = os.path.join(PROJECT_ROOT, "corpus")
DOCUMENTS_DIR = os.path.join(CORPUS_DIR, "documents")
DOCUMENT_PATH_JSON = os.path.join(CORPUS_DIR, "document_path.json")
COMMON_CHARGE_JSON = os.path.join(CORPUS_DIR, "common_charge.json")
CONTROVERSIAL_CHARGE_JSON = os.path.join(CORPUS_DIR, "controversial_charge.json")

# Elasticsearch配置
ELASTICSEARCH_HOSTS = ["http://localhost:9200"]
INDEX_NAME = "legal_cases"

# Flask配置
FLASK_DEBUG = True
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000