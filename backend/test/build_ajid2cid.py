import os
import json

base_path = "LeCaRD/data/candidates"
output_dir = "backend/test/outputs"
os.makedirs(output_dir, exist_ok=True)

doc2id = {}
id2doc = {}

for root, dirs, files in os.walk(base_path):
    for file in files:
        if not file.endswith(".json"):
            continue
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                info = json.load(f)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
            ajid = info.get("ajid") or info.get("ajId")
            cid = file.split(".")[0]
            if ajid:
                doc2id[ajid] = cid
                id2doc[cid] = ajid

print(f"Total ajid2cid: {len(doc2id)}, cid2ajid: {len(id2doc)}")

with open(os.path.join(output_dir, "ajid2cid.json"), "w", encoding="utf-8") as f:
    json.dump(doc2id, f, ensure_ascii=False, indent=2)
with open(os.path.join(output_dir, "cid2ajid.json"), "w", encoding="utf-8") as f:
    json.dump(id2doc, f, ensure_ascii=False, indent=2)
