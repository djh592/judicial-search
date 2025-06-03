# 司法搜索引擎大作业

姓名：丁俊辉

学号：2021011145

## 项目简介

本项目实现了一个面向中文司法文书的专业搜索引擎，支持关键词检索、类似案例检索、标签抽取与展示、查询推荐等功能，并提供了完整的前后端界面。系统基于 [LeCaRD](https://github.com/myx666/LeCaRD) 数据集和全国裁判文书，采用 Elasticsearch 作为底层检索引擎，前端基于 React + MUI 实现，后端为 Python Flask。

## 项目结构

```
judicial-search/
├── backend/                # 后端服务（Flask + Elasticsearch）
│   ├── app.py              # 后端主入口
│   ├── config.py           # 配置文件
│   ├── elastic/            # ES相关代码（索引、标签抽取等）
│   ├── search/             # 检索与查询逻辑
│   └── test/               # 评测与预测脚本
├── corpus/                 # 文书数据及标签
│   ├── documents/          # 文书原文（需自行下载解压）
│   ├── common_charge.json  # 常见罪名标签
│   ├── controversial_charge.json # 争议罪名标签
│   ├── document_path.json  # 文书路径映射
│   └── test.py             # 数据处理测试
├── frontend/               # 前端（React + MUI）
│   ├── src/                # 前端源码
│   ├── public/             # 静态资源
│   ├── package.json        # 前端依赖
│   └── README.md           # 前端说明
├── ik/                     # Elasticsearch IK分词插件
├── LeCaRD/                 # LeCaRD数据集及评测工具
│   ├── data/               # LeCaRD数据
│   ├── metrics.py          # 官方评测脚本
│   └── ...                 # 其它辅助文件
├── docker-compose.yml      # 一键部署配置
├── .gitignore
├── assets/
└── README.md               # 项目说明（本文件）
```

## 实现模块

### 1. Elasticsearch 搜索引擎

使用 Docker 部署，包含了 Elasticsearch 的 8.4.1 版本，[analysis-ik](https://github.com/infinilabs/analysis-ik) 分词器和 Kibana（用于调试）。analysis-ik 分词器的 stopword 和专有名词来自 LeCaRD。

通过后端将文档加载到 Elasticsearch 中，包含 LeCaRD 的 10718 个文档，主要字段如下：

- `ajid`：案件 ID
- `ajjbqk`：案件基本情况
- `cpfxgc`：裁判分析过程
- `pjjg`：判决结果
- `qw`：案件全文
- `writId`：文书 ID
- `writName`：文书名称
- `labels`：案由标签
- `fymc`：法院名称
- `spry`：审判人员
- `dsr`：当事人

前 7 个字段是从 LeCaRD 的法律文书文件中直接获取的。`labels` 来自语料库的 `common_charge.json` 和 `controversial_charge.json` 通过读取语料库为对应字段打上标签。

`fymc`、`spry` 和 `dsr` 是我通过正则表达式抽取的标签，目的是实现多标签的查询。由于正则表达式的功能有限，这部分无法保证 100% 精确，因此我并没有将抽到的标签作为 keyword，而是经过分词后进行模糊匹配，不过相对的这部分匹配的权重会调高（见下一节后端的实现）。

除此之外，我还设计了几个用来进行搜索推荐的字段（后缀为 `_suggest`），内容和原字段相同，只是用作推荐。

这部分代码见 `backend/elastic/indexer.py`，我在其中实现了对 LeCaRD 数据的处理，`fymc`、`spry` 和 `dsr` 标签的抽取和将数据导入 Elasticsearch 的工作。

### 2. 后端

后端的主要作用是沟通前端和 Elasticsearch 搜索引擎，大致的工作过程如下：

- 用户在前端填写表单，建立一个查询请求
- 前端按照 API 约定将查询请求发给后端
- 后端将前端的请求（json 格式）转换成 Elasticsearch 的 DSL，在 Elasticsearch 中完成查询
- 后端返回给前端一个 `query_id`，前端利用 `query_id` 可以按页获取查询结果

后端会完成一部分查询参数的调优（见 `backend/search/query.py`：

```python
class QueryParams:
    """
    检索参数对象，封装前端传来的所有检索条件
    """
    ...
    
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
```

可以看到，部分参数的权重被适当条高了。我的设计是优先匹配更重要的文本，已经用户特意通过标签搜索的文本，这有助于将用户期望的结果排到更前面。

后端还实现了 `QueryManager`，它的功能是缓存前端的请求（类似 Redis 的功能），让用户可以通过 `query_id` 随时请求该查询的不同内容。经过特定的时间（一小时）或者后端缓存容量满后，`query_id` 就会失效。我通过这种方法实现最基本的请求管理功能。

后端与前端的交互功能通过 Flask 实现。考虑到任务的需求比较简单，我希望尽量使用轻量的框架简化实现，Flask 是一个相对不错的选择，相关代码在 `backend/app.py` 中。

### 3. 前端

前端的作用是和用户进行交互，交互方式如下：

- 用户访问主页，填写表单获得查询内容
- 用户提交查询，通过后端获得 `query_id`，路由到查询结果页面
- 用户在查询结果页面获得分页后的查询结果
- 用户点击查询结果，路由到结果的详情页面，查看完整的文档

综上，前端只需要实现主页、查询结果页面和详情页面。我使用 React + Typescript 进行开发，使用 MUI 设计界面。

主页的展示如下：

![Screenshot 2025-06-03 204404](assets/Screenshot%202025-06-03%20204404.png)

查询结果页面展示如下：

![Screenshot 2025-06-03 204526](assets/Screenshot%202025-06-03%20204526.png)

详情页面展示如下：

![Screenshot 2025-06-03 204719](assets/Screenshot%202025-06-03%20204719.png)

## 关键功能

### 1. 关键词检索

搜索页面的默认搜索框可以进行所有字段的模糊匹配查询，支持全文、字段、标签等多维度关键词检索。

如果想要特定字段的查询，可打开高级检索功能：

![Screenshot 2025-06-03 205331](assets/Screenshot%202025-06-03%20205331.png)

### 2. 类似案例检索

全文检索支持 `.txt` 和 `.docx` 两种格式的文件，可上传案例文本，检索相似案件，也可以手动输入全文：

![Screenshot 2025-06-03 205545](assets/Screenshot%202025-06-03%20205545.png)

![Screenshot 2025-06-03 205557](assets/Screenshot%202025-06-03%20205557.png)

结果：

![Screenshot 2025-06-03 213749](assets/Screenshot%202025-06-03%20213749.png)

### 3. 标签抽取与展示

自动抽取法院、案由、审判人员、当事人等标签，支持标签筛选。

案由查询匹配 Elasticsearch 中的 `label` 字段，由于 `label` 是 keyword，可以通过后端请求 Elasticsearch 获得所有可能的 `label` ：

![Screenshot 2025-06-03 210024](assets/Screenshot%202025-06-03%20210024.png)

案件名称查询专门匹配 `ajName` 字段，法院名称、审判人员和当事人匹配。

这里演示一下匹配法院：

![Screenshot 2025-06-03 210808](assets/Screenshot%202025-06-03%20210808.png)

![Screenshot 2025-06-03 210849](assets/Screenshot%202025-06-03%20210849.png)

### 4. 查询推荐/补全

输入时实时给出案件名称等补全建议。

普通检索的搜索框支持查询的推荐功能：

![Screenshot 2025-06-03 214320](assets/Screenshot%202025-06-03%20214320.png)

输入文字后，前端会把内容发给后端，后端通过 Elasticsearch 的推荐功能查找推荐信息，再返回给前端显示出来。

## 测试结果和样例分析

### 1. 测试结果

使用 LeCaRD 的 metrics.py 进行测试，结果如下：

```sh
(judicial-search) djh592@DJH592:~/dev/ir/judicial-search$ python LeCaRD/metrics.py   --pred backend/test/prediction   --label LeCaRD/data/label/label_top30_dict.json
[[0.15704517351602573, 0.4951986445979235, 0.5392342054888827], [0.16707439824376702, 0.4984785869453877, 0.608637820767543], [0.176615480848611, 0.5087344376857388, 0.6582402521942317]]
(judicial-search) djh592@DJH592:~/dev/ir/judicial-search$ python LeCaRD/metrics.py   --pred backend/test/prediction   --label LeCaRD/data/label/label_top30_dict.json --m MAP
[0.44701778337043, 0.49497887695717235, 0.48790553182500973]
```

输出内容中，每个数组中间的元素（代表 BM25 的结果）就是我的搜索引擎得到的结果。

可以看到 NDCG 在 k 为 10, 20, 30 的时候，结果分别为 0.4951986445979235，0.4984785869453877，0.5087344376857388。MAP 为 0.49497887695717235。

对比 LeCaRD 中 BM25 算法的结果：

```sh
(judicial-search) djh592@DJH592:~/dev/ir/judicial-search$ python LeCaRD/metrics.py   --pred LeCaRD/data/prediction   --label LeCaRD/data/label/label_top30_dict.json
[[0.15704517351602573, 0.4917897340918521, 0.5392342054888827], [0.16707439824376702, 0.531733955946452, 0.608637820767543], [0.176615480848611, 0.5605551812930932, 0.6582402521942317]]
(judicial-search) djh592@DJH592:~/dev/ir/judicial-search$ python LeCaRD/metrics.py   --pred LeCaRD/data/prediction   --label LeCaRD/data/label/label_top30_dict.json --m MAP
[0.44701778337043, 0.4754828307167766, 0.48790553182500973]
```

我的评测结果与之接近。

### 2. 样例分析

关键词检索承兑汇票：

![Screenshot 2025-06-03 222448](assets/Screenshot%202025-06-03%20222448.png)

可以检索出金融、诈骗之类的案件。

![Screenshot 2025-06-03 222511](assets/Screenshot%202025-06-03%20222511.png)

翻到第五页，结果仍然相关。

![Screenshot 2025-06-03 222536](assets/Screenshot%202025-06-03%20222536.png)

查询详细的案情，通过全文查找：

![Screenshot 2025-06-03 222956](assets/Screenshot%202025-06-03%20222956.png)

可以在第一个结果中查到完全匹配的信息：

![Screenshot 2025-06-03 223028](assets/Screenshot%202025-06-03%20223028.png)

![Screenshot 2025-06-03 223121](assets/Screenshot%202025-06-03%20223121.png)

## 环境准备与运行方法

### 1. Python 环境配置

本项目推荐使用 Conda 管理 Python 环境。你可以直接使用项目根目录下的 `environment.yml` 文件创建环境：

```sh
conda env create -f environment.yml
conda activate judicial-search
```

如需更新依赖，可运行：

```sh
conda env update -f environment.yml
```

### 2. 数据准备

1. 下载全国文书数据集（[下载链接](https://drive.google.com/file/d/1vQdX1MegFVtmoh0XCd4max5PBkep7qOh/view?usp=sharing)），解压到 `corpus/` 目录下。

2. 克隆 LeCaRD 数据集到项目根目录：

   ```sh
   git clone https://github.com/myx666/LeCaRD.git
   ```

3. 下载 LeCaRD 候选集文档：

   ```sh
   cd LeCaRD
   unzip data/candidates/candidates1.zip -d data/candidates
   unzip data/candidates/candidates2.zip -d data/candidates
   ```

### 3. 启动服务

1. 启动 Elasticsearch（推荐用 docker-compose）：

   ```sh
   docker-compose build
   docker-compose up -d
   ```

2. 导入案例信息到 ES 索引：

   ```sh
   python -m backend.elastic.indexer
   ```

3. 启动后端服务：

   ```sh
   python -m backend.app
   ```

4. 启动前端服务：

   ```sh
   cd frontend
   npm install
   npm start
   ```

   前端启动后可访问 [http://localhost:3000/](http://localhost:3000/) 使用系统。

---

## 数据集与字段说明

- **LeCaRD 数据集**：详见 [LeCaRD/README.md](LeCaRD/README.md)
- **主要字段**：
  - `ajid`：案件ID
  - `qw`：案件全文
  - `ajjbqk`：案件基本情况
  - `cpfxgc`：裁判分析过程
  - `pjjg`：判决结果
  - `labels`：案由标签
  - `fymc`：法院名称
  - `spry`：审判人员
  - `dsr`：当事人

---

## 评测方法

1. 检索时返回案件ID（`ajid`），通过 LeCaRD 的 candidates 文件夹映射到 candidate id。

   ```
   python -m backend.test.build_ajid2cid
   ```

2. 生成搜索引擎的预测文件

   ```
   python -m backend.test.generate_prediction
   ```

3. 使用 LeCaRD 官方评测脚本 `metrics.py` 进行性能评测：

   ```
   python LeCaRD/metrics.py --pred backend/test/prediction --label LeCaRD/data/label/label_top30_dict.json
   ```

   评测指标包括 NDCG、MAP 等，详见 LeCaRD 官方文档。

## 参考资料

- [LeCaRD 数据集](https://github.com/myx666/LeCaRD)
- [LeCaRD 论文](https://dl.acm.org/doi/abs/10.1145/3404835.3463250)
- [中国裁判文书网](https://wenshu.court.gov.cn/)
- [Elasticsearch 官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [React](https://react.dev/)、[Material UI](https://mui.com/)