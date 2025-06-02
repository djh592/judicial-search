# 司法搜索引擎大作业

## 项目简介

本项目实现了一个面向中文司法文书的专业搜索引擎，支持关键词检索、类似案例检索、标签抽取与展示、查询推荐等功能，并提供了完整的前后端界面。系统基于 [LeCaRD](https://github.com/myx666/LeCaRD) 数据集和全国裁判文书，采用 Elasticsearch 作为底层检索引擎，前端基于 React + MUI 实现，后端为 Python Flask。

---

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
└── README.md               # 项目说明（本文件）
```

---

## 主要功能

- **关键词检索**：支持全文、字段、标签等多维度关键词检索。
- **类似案例检索**：可上传案例文本，检索相似案件。
- **标签抽取与展示**：自动抽取法院、案由、审判人员、当事人等标签，支持标签筛选与高亮。
- **查询推荐/补全**：输入时实时给出案件名称等补全建议。
- **结构化与语义化展示**：案件详情页结构化展示案件要素。
- **性能评测**：支持在 LeCaRD 验证集上自动评测 BM25 等检索算法性能。

---

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
   npm run dev
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

   评测指标包括 NDCG、MAP、P@5、P@10 等，详见 LeCaRD 官方文档。

---

## 参考资料

- [LeCaRD 数据集](https://github.com/myx666/LeCaRD)
- [LeCaRD 论文](https://dl.acm.org/doi/abs/10.1145/3404835.3463250)
- [中国裁判文书网](https://wenshu.court.gov.cn/)
- [Elasticsearch 官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [React](https://react.dev/)、[Material UI](https://mui.com/)