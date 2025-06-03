import json
import requests
import traceback

API_URL = "http://localhost:5000/api/query"
RESULTS_URL = "http://localhost:5000/api/query/{}/results?page={}&page_size={}"

with open("backend/test/outputs/ajid2cid.json", "r", encoding="utf-8") as f:
    ajid2cid = json.load(f)

with open("LeCaRD/data/query/query.json", "r", encoding="utf-8") as f:
    queries = [json.loads(line) for line in f]

predictions = {}

for q in queries:
    user_query = {
        "query": q["q"],
        "ay": q["crime"],
        "qw": "",
        "ajmc": "",
        "fymc": "",
        "spry": "",
        "dsr": "",
    }
    try:
        print(f"Processing ridx={q['ridx']}")
        resp = requests.post(API_URL, json={"user_query": user_query})
        if resp.status_code != 200:
            print(
                f"Query failed for {q['ridx']}, status={resp.status_code}, resp={resp.text}"
            )
            continue
        query_id = resp.json().get("query_id")
        if not query_id:
            print(f"No query_id for {q['ridx']}, resp={resp.text}")
            continue

        # 分页获取，直到收集到100个候选
        page = 1
        page_size = 100
        ajids = []
        seen = set()
        while len(ajids) < 100:
            try:
                resp = requests.get(RESULTS_URL.format(query_id, page, page_size))
                if resp.status_code != 200:
                    print(
                        f"Result fetch failed for {q['ridx']} page {page}, status={resp.status_code}, resp={resp.text}"
                    )
                    break
                results = resp.json().get("results", [])
                if not results:
                    print(f"No more results for {q['ridx']} at page {page}")
                    break
                for doc in results:
                    print(f"{doc['ajId']}: score={doc.get('score')}")
                    ajid = doc.get("ajId")
                    if ajid in ajid2cid and ajid not in seen:
                        ajids.append(ajid)
                        seen.add(ajid)
                        if len(ajids) == 100:
                            break
                if len(results) < page_size:
                    print(f"Results less than page_size for {q['ridx']} at page {page}")
                    break  # 没有更多结果
                page += 1
            except Exception as e:
                print(f"Exception in results fetch for {q['ridx']} page {page}: {e}")
                traceback.print_exc()
                break

        predictions[str(q["ridx"])] = [ajid2cid[ajid] for ajid in ajids]
        # 结果 reverse 一下，用于测试
        predictions[str(q["ridx"])].reverse()
        print(f"ridx={q['ridx']} collected {len(ajids)} candidates")
    except Exception as e:
        print(f"Exception in query ridx={q['ridx']}: {e}")
        traceback.print_exc()

with open("backend/test/prediction/bm25_top100.json", "w", encoding="utf-8") as f:
    json.dump(predictions, f, ensure_ascii=False, indent=2)
