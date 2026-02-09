# 大学知识库汇入文档

基于天津大学和复旦大学的知识已汇入KAIdison系统。

## 1. 机构数据

```python
INSTITUTION_NODES = {
    "tju": {
        "name": "天津大学",
        "type": "university",
        "domain": "engineering",
        "research_focus": ["人工智能", "脑机接口", "自动化"],
        "collaborations": ["复旦大学", "南开大学"]
    },
    "fdu": {
        "name": "复旦大学",
        "type": "university", 
        "domain": "medical",
        "research_focus": ["神经科学", "临床医学", "认知科学"],
        "collaborations": ["天津大学", "上海交通大学"]
    }
}
```

## 2. 知识胶囊示例（TIER咖啡知识沙龙）

```python
TIER_CAPSULES = {
    "coffee_brewing": {
        "title": "咖啡冲煮技术",
        "type": "knowledge",
        "source": {
            "university": "天津大学|复旦大学",
            "author": "TIER知识团队",
            "date": "2026-01-15"
        },
        "datm": {
            "truth": 0.88,
            "goodness": 0.92,
            "beauty": 0.85,
            "intelligence": 0.90
        },
        "tags": ["咖啡", "冲煮", "萃取", "天津大学", "复旦大学"]
    },
    "coffee_culture": {
        "title": "咖啡文化与历史",
        "type": "knowledge",
        "source": {
            "university": "复旦大学",
            "author": "历史研究组",
            "date": "2026-01-10"
        },
        "datm": {
            "truth": 0.90,
            "goodness": 0.85,
            "beauty": 0.95,
            "intelligence": 0.88
        },
        "tags": ["咖啡", "文化", "历史", "复旦大学"]
    },
    "bcic_technology": {
        "title": "脑机接口技术路线",
        "type": "technical_route",
        "source": {
            "university": "天津大学",
            "author": "BCI研究团队",
            "date": "2026-02-01"
        },
        "datm": {
            "truth": 0.92,
            "goodness": 0.88,
            "beauty": 0.80,
            "intelligence": 0.94
        },
        "tags": ["脑机接口", "BCI", "天津大学", "技术路线"]
    }
}
```

## 3. 知识图谱关系

```python
INSTITUTION_CAPSULES = {
    "天津大学": ["bcic_technology", "coffee_brewing"],
    "复旦大学": ["coffee_culture", "coffee_brewing"]
}

COLLABORATION_NETWORK = [
    {"from": "天津大学", "to": "复旦大学", "type": "research", "project": "TIER咖啡知识沙龙"},
    {"from": "天津大学", "to": "复旦大学", "type": "ai", "project": "KAIdison脑机接口系统"}
]
```

---

*汇入时间: 2026-02-09*
*来源: TIER咖啡知识沙龙, Matrix-BNUHS, AIdison*
