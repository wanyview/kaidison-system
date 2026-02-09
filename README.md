# KAIdison 脑机接口知识胶囊系统

## 项目概述

KAIdison 系统是基于知识胶囊(DATM)技术构建的脑机接口(BCI)知识管理系统，为天津大学 MBC (脑机接口研究中心)提供全面的技术路线管理、学术文献评估和案例知识库服务。

## 核心特性

### 🧠 胶囊类型体系

| 胶囊类型 | 描述 | 应用场景 |
|---------|------|---------|
| **技术路线胶囊** | 侵入式/非侵入式/数字孪生的参数模型 | 技术选型、方案对比 |
| **论文胶囊** | 学术文献的 DATM 评分版 | 学术研究、文献调研 |
| **案例胶囊** | 手术/康复/伦理案例 | 临床参考、伦理决策 |
| **实验数据胶囊** | EEG/神经元信号数据 | 数据共享、分析研究 |
| **大学知识胶囊** | 天津大学、复旦大学研究成果 | 跨学科研究、学术合作 |

### 📚 大学知识库

基于以下项目的知识已汇入系统：
- **TIER咖啡知识沙龙** - 天津大学×复旦大学 联合研究
- **Matrix-BNUHS** - 附中矩阵知识库
- **AIdison** - 脑机接口助手

详见: [UNIVERSITY_IMPORT.md](./UNIVERSITY_IMPORT.md)

### 📊 DATM 评分体系

```
DATM = {
  Truth (科学性)     → 技术的科学依据 (0-100)
  Goodness (安全性)  → 安全性评估 (0-100)
  Beauty (美学)      → 用户体验/界面 (0-100)
  Intelligence (实用性) → 实用价值 (0-100)
}
```

### 🔗 知识图谱

- **技术路线关系网络** - 侵入式 ↔ 非侵入式 ↔ 数字孪生
- **机构关联网络** - 天津大学、复旦大学、中科院等
- **学者网络** - 领域专家、论文作者、项目参与者

### 👥 汇报体系

| 角色 | 职责 |
|------|------|
| **曹操** | 汇报总结、战略规划、决策支持 |
| **KAI** | 执行落地、技术实现、系统运维 |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.md

# 启动服务
python -m kai.main

# 访问文档
open http://localhost:8000/docs
```

## 项目结构

```
projects/kaidison-system/
├── README.md           # 项目介绍
├── ARCHITECTURE.md     # 架构设计
├── API.md              # 接口文档
├── UNIVERSITY_IMPORT.md # 大学知识库汇入
├── requirements.md     # 依赖清单
├── examples/           # 示例代码
│   ├── capsule_creation.py
│   ├── datm_scoring.py
│   └── knowledge_graph.py
└── src/
    ├── main.py
    ├── models/
    ├── services/
    └── routers/
```

## 技术栈

- **后端**: Python/FastAPI
- **数据库**: PostgreSQL + Neo4j
- **前端**: React/TypeScript
- **部署**: Docker/Kubernetes

## 许可证

MIT License
